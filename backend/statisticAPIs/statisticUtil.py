import os.path
import pandas as pd
import re


class StatisticUtil:
    # Load the glossary of terms
    # path = os.path.join('data', 'glossaryTerms', 'glossaryTermCollectionV4-category.json')
    # glossaryTermsDF = pd.read_json(path)
    categories = ['Building', 'Space', 'Transport', 'People']
    keywords = {
        'Space': ['area', 'cbd', 'city', 'center', 'centre', 'central', 'courtyard', 'piazza', 'park', 'place', 'river',
                  'square', 'space'],
        'Transport': ['avenue', 'bike', 'bus', 'car', 'cycle', 'lane', 'parking', 'rail', 'shuttle', 'station',
                      'street', 'tram', 'traffic', 'walkway', 'pedestrian'],
        'Building': ['apartment', 'building', 'hospital', 'market', 'office', 'quarter', 'retail', 'shop', 'store',
                     'garden', 'housing', 'university', 'school', 'library', 'mall', 'cafe'],
        'People': ['people', 'family', 'children', 'disability', 'community', 'shopping', 'art', 'sport', 'resident',
                   'health', 'safety', 'neighbourhood', 'tourist']
    }




    @staticmethod
    def getOtherSubjects(sortedStatistics, subjectSet):
        otherSubjects = {}
        for subject, sentences in sortedStatistics.items():
            if subject not in subjectSet:
                otherSubjects[subject] = sentences

        return dict(sorted(otherSubjects.items(), key=lambda item: len(item[1]), reverse=True))

    @staticmethod
    def categorizeSubject(category, sortedStatistics, subjectSet):
        categoryKeywords = StatisticUtil.keywords[category]
        categoryDict = {}
        for subject, sentences in sortedStatistics.items():
            subjectWords = subject.split(" ")
            matchedKeywords = [word for word in categoryKeywords if word in subjectWords]
            if len(matchedKeywords) > 0:
                matchedKeyword = matchedKeywords[0]
                if matchedKeyword not in categoryDict:
                    categoryDict[matchedKeyword] = list()
                categoryDict[matchedKeyword].extend(sentences)
                subjectSet.add(subject)
        # Sort by frequency
        return dict(sorted(categoryDict.items(), key=lambda item: len(item[1]), reverse=True))

    @staticmethod
    def collectVerbObjectPhrases(text, verbWord, statistics):
        # Process the verb
        # verbWord = verbWords[0]
        verbLemma = verbWord['lemma'].lower()
        verbPhrase = StatisticUtil.getVerbPhrase(text, verbWord)
        if verbLemma == 'be':
            beVerb = verbWord['word'].lower()
            if beVerb not in statistics['role']['verbs'][verbLemma]:
                statistics['role']['verbs'][verbLemma][beVerb] = list()
            statistics['role']['verbs'][verbLemma][beVerb].append(verbPhrase)
        else:
            if verbLemma not in statistics['role']['verbs']:
                statistics['role']['verbs'][verbLemma] = list()
            statistics['role']['verbs'][verbLemma].append(verbPhrase)
        # Get the phrase
        StatisticUtil.getObjectPhrases(text, verbWord, statistics)

    @staticmethod
    def categoryObjectPhrases(topic, phrases, objectSet):
        try:
            categoryKeywords = StatisticUtil.keywords[topic]
            categoryDict = {}
            for keyword in categoryKeywords:
                lemmaPhraseWords = list(map(lambda phraseWords: [word['lemma'].lower() for word in phraseWords], phrases))
                matchedPhrases = list(filter(lambda lemmaWords: keyword in lemmaWords, lemmaPhraseWords))
                # Map the values to a string
                matchedPhrases = list(map(lambda phrase: " ".join(phrase), matchedPhrases))
                categoryDict[keyword] = matchedPhrases
                objectSet.update(matchedPhrases)
            # Sort the phrases
            return dict(sorted(categoryDict.items(), key=lambda item: len(item[1]), reverse=True))
        except Exception:
            print("Error occurred")

    @staticmethod
    def convertPhrasesToWords(text, _taggedPhrase):
        sentId = _taggedPhrase['sentId']
        start = _taggedPhrase['start']
        end = _taggedPhrase['end']
        taggedWords = text['taggedWords']
        # sentenceWords = [taggedWord for taggedWord in text['taggedWords'] if taggedWord['sentId'] == sentId]
        phraseWords = [taggedWord for taggedWord in taggedWords if taggedWord['sentId'] == sentId
                       and start <= taggedWord['id'] <= end]
        # not taggedWord['lemma'].lower() in StatisticUtil.stop_words]
        return " ".join(list(map(lambda word: word['lemma'].lower(), phraseWords)))

    @staticmethod
    def getVerbPhrase(text, verbWord):
        taggedPhrases = text['taggedPhrases']
        sentId = verbWord['sentId']
        _verbPhrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                        taggedPhrase['sentId'] == sentId and taggedPhrase['ptb'].startswith('VP') and
                        taggedPhrase['start'] == verbWord['id']]
        if len(_verbPhrases) > 0:
            # Sort by the length
            _verbPhrases = sorted(_verbPhrases, key=lambda phrase: phrase['end'] - phrase['start'], reverse=True)
            _verbPhrase = _verbPhrases[0]
            taggedWords = text['taggedWords']
            # sentenceWords = [taggedWord for taggedWord in text['taggedWords'] if taggedWord['sentId'] == sentId]
            phraseWords = [taggedWord['word'].lower() for taggedWord in taggedWords if
                           taggedWord['sentId'] == _verbPhrase['sentId'] and
                           _verbPhrase['start'] <= taggedWord['id'] <= _verbPhrase['end']]
            return " ".join(phraseWords)
        else:
            return verbWord['lemma'].lower()

    @staticmethod
    def getSubjectNounPhrases(text, _subjectWord):
        def getNounPhrase(word):
            taggedPhrases = text['taggedPhrases']
            sentId = word['sentId']
            _nounPhrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                            taggedPhrase['sentId'] == sentId and taggedPhrase['ptb'].startswith('NP') and
                            taggedPhrase['start'] <= word['id'] <= taggedPhrase['end']]
            if len(_nounPhrases) > 0:
                # Sort by the length and get the longest noun phrase
                _nounPhrases.sort(key=lambda x: x['end'] - x['start'], reverse=True)
                return StatisticUtil.convertPhrasesToWords(text, _nounPhrases[0])
            else:
                return word['lemma'].lower()

        if _subjectWord['pennPOS'].startswith('prp') or _subjectWord['pennPOS'].startswith('dt'):
            return _subjectWord['lemma'].lower()
        else:
            return getNounPhrase(_subjectWord)

    @staticmethod
    def getWords(words):
        # filterWords = filter(lambda word: not word['lemma'].lower() in StatisticUtil.stop_words, words)
        return " ".join(map(lambda word: word['word'].lower(), words))

    @staticmethod
    def getObjectPhrases(text, verbWord, statistics):
        try:
            # Get the noun phrases
            relationId = verbWord['id']
            sentId = verbWord['sentId']
            sentenceWords = [taggedWord for taggedWord in text['taggedWords'] if taggedWord['sentId'] == sentId]
            sentence = " ".join(list(map(lambda word: word['word'], sentenceWords)))
            taggedPhrases = text['taggedPhrases']
            # Get SBAR
            clauses = [taggedPhrase for taggedPhrase in taggedPhrases if
                       taggedPhrase['sentId'] == sentId and
                       relationId < taggedPhrase['start'] <= relationId + 2 and
                       taggedPhrase['ptb'].startswith('SBAR')]
            if len(clauses) > 0:
                sortedClauses = sorted(clauses, key=lambda clause: clause['end'] - clause['start'])
                clause = sortedClauses[0]
                clauseWords = [taggedWord for taggedWord in sentenceWords if
                               clause['start'] <= taggedWord['id'] <= clause['end']]
                statistics['phrases']['CLAUSE'].append(clauseWords)
            else:
                # Get the verb phrase containing the verb
                _verbPhrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                                taggedPhrase['sentId'] == sentId and taggedPhrase['ptb'].startswith('VP') and
                                taggedPhrase['start'] == verbWord['id']]
                if len(_verbPhrases) == 0:
                    statistics['phrases']['others'].append(sentence)
                    # print("Error: Cannot find the phrase")
                    return

                _verbPhrase = _verbPhrases[0]
                # Get the noun or verb phrase inside the verb phrase
                phrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                           taggedPhrase['sentId'] == sentId and
                           _verbPhrase['start'] < taggedPhrase['start'] and
                           taggedPhrase['end'] <= _verbPhrase['end'] and
                           (taggedPhrase['ptb'].startswith('ADJP') or
                            taggedPhrase['ptb'].startswith('VP') or
                            taggedPhrase['ptb'].startswith('NP'))]
                if len(phrases) == 0:
                    statistics['phrases']['others'].append(sentence)
                    return
                # Get the longest phrase
                sortedPhrases = sorted(phrases, key=lambda _phrase: _phrase['end'] - _phrase['start'],
                                       reverse=True)
                phrase = sortedPhrases[0]
                if phrase['ptb'].startswith('AD'):
                    phraseType = phrase['ptb'][0:4]
                else:
                    phraseType = phrase['ptb'][0:2]

                # Get the leaf noun phrase
                phraseWords = [taggedWord for taggedWord in sentenceWords if
                               taggedWord['sentId'] == sentId and
                               phrase['start'] <= taggedWord['id'] <= phrase['end']]
                statistics['phrases'][phraseType].append(phraseWords)
                # StatisticUtil.getTerms(text, phraseWords, statistics)
        except Exception:
            print("Error occurred: {sentence}".format(sentence=sentence))
            # statistics['phrases']['others'].append(sentence)

    # Get the sentence of the subject
    @staticmethod
    def getSentenceBySentId(_taggedWords, sentId):
        sentenceWords = [_taggedWord for _taggedWord in _taggedWords if _taggedWord['sentId'] == sentId]
        return sentenceWords

    @staticmethod
    def getSentence(_taggedWords, _word):
        sentId = _word['sentId']
        sentenceWords = [taggedWord for taggedWord in _taggedWords if taggedWord['sentId'] == sentId]
        return " ".join(list(map(lambda word: word['word'], sentenceWords)))

    @staticmethod
    def getSentenceWords(_taggedWords, _word):
        sentId = _word['sentId']
        sentenceWords = [taggedWord for taggedWord in _taggedWords if taggedWord['sentId'] == sentId]
        return sentenceWords

    @staticmethod
    def getSubjectVerb(_taggedWords, subjectWord):
        headWordId = int(subjectWord['head'].split("-")[-1])
        headWords = [taggedWord for taggedWord in _taggedWords if
                     taggedWord['id'] == headWordId and
                     taggedWord['sentId'] == subjectWord['sentId']]
        # Head words may be verbs or nouns
        if not headWords[0]['pennPOS'].startswith('vb'):
            verbWords = [taggedWord for taggedWord in _taggedWords if
                         int(taggedWord['head'].split("-")[-1]) == headWordId and
                         taggedWord['pennPOS'].startswith('vb') and
                         (taggedWord['ud'] == 'cop' or taggedWord['ud'] == 'xcomp')]
            return verbWords
        else:
            return headWords

    # Get the XCOMP of verb
    @staticmethod
    def getXCOMP(_taggedWords, _verbWord):
        sentId = _verbWord['sentId']
        verbHead = _verbWord['word'] + '-' + str(_verbWord['id'])
        # Find the xcomp to identify 'want to see'
        _xcompWords = [taggedWord for taggedWord in _taggedWords if taggedWord['sentId'] == sentId and
                       taggedWord['ud'].startswith('xcomp') and taggedWord['head'] == verbHead]
        return _xcompWords

    @staticmethod
    def collectObjects(text, statistics):
        # Get the verbs of the subjects
        def getVerbs(_taggedWords, _subjectWord, _verbs):
            sentId = _subjectWord['sentId']
            wordId = int(_subjectWord['head'].split("-")[1])
            _verbWords = [taggedWord for taggedWord in _taggedWords if taggedWord['sentId'] == sentId and
                          taggedWord['id'] == wordId and taggedWord['lemma'] in _verbs]
            return _verbWords

        # Get the objects of the verb
        def getObjects(_taggedWords, _verbWord):
            objs = [taggedWord for taggedWord in _taggedWords if taggedWord['sentId'] == _verbWord['sentId'] and
                        taggedWord['ud'].startswith('ob') and
                        taggedWord['head'] == _verbWord['word'] + '-' + str(_verbWord['id'])]
            return objs

        def __getObjectPhrases(text, verbWord):
            # Get the noun phrases
            relationId = verbWord['id']
            sentId = verbWord['sentId']
            sentenceWords = [taggedWord for taggedWord in text['taggedWords'] if taggedWord['sentId'] == sentId]
            try:
                taggedPhrases = text['taggedPhrases']
                # Get SBAR
                clauses = [taggedPhrase for taggedPhrase in taggedPhrases if
                           taggedPhrase['sentId'] == sentId and
                           relationId < taggedPhrase['start'] <= relationId + 2 and
                           taggedPhrase['ptb'].startswith('SBAR')]
                if len(clauses) > 0:
                    sortedClauses = sorted(clauses, key=lambda clause: clause['end'] - clause['start'])
                    clause = sortedClauses[0]
                    clauseWords = [taggedWord for taggedWord in sentenceWords if
                                   clause['start'] <= taggedWord['id'] <= clause['end']]
                    return 'clause', clauseWords
                else:
                    # Get the verb phrase containing the verb
                    _verbPhrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                                    taggedPhrase['sentId'] == sentId and taggedPhrase['ptb'].startswith('VP') and
                                    taggedPhrase['start'] == verbWord['id']]
                    if len(_verbPhrases) == 0:
                        # print("Error: Cannot find the phrase")
                        return 'others', sentenceWords

                    _verbPhrase = _verbPhrases[0]
                    # Get the noun or verb phrase inside the verb phrase
                    phrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                               taggedPhrase['sentId'] == sentId and
                               _verbPhrase['start'] < taggedPhrase['start'] and
                               taggedPhrase['end'] <= _verbPhrase['end'] and
                               (taggedPhrase['ptb'].startswith('ADJP') or
                                taggedPhrase['ptb'].startswith('VP') or
                                taggedPhrase['ptb'].startswith('NP'))]
                    if len(phrases) == 0:
                        return 'others', sentenceWords
                    # Get the longest phrase
                    sortedPhrases = sorted(phrases, key=lambda _phrase: _phrase['end'] - _phrase['start'],
                                           reverse=True)
                    phrase = sortedPhrases[0]
                    if phrase['ptb'].startswith('AD'):
                        phraseType = phrase['ptb'][0:4]
                    else:
                        phraseType = phrase['ptb'][0:2]
                    # Get the leaf noun phrase
                    phraseWords = [taggedWord for taggedWord in sentenceWords if
                                   taggedWord['sentId'] == sentId and
                                   phrase['start'] <= taggedWord['id'] <= phrase['end']]
                    return phraseType, phraseWords
            except Exception:
                return ('others', sentenceWords)

        taggedWords = text['taggedWords']
        # Check if any subject is "I" or "We"
        subjectWords = [taggedWord for taggedWord in taggedWords if
                        (taggedWord['word'].lower() == 'i' or taggedWord['word'].lower() == 'we') and
                        taggedWord['ud'] == 'nsubj']
        verbs = ["want", "love", "like", "need", "think", "believe"]
        # Get the head word
        for subjectWord in subjectWords:
            verbWords = getVerbs(taggedWords, subjectWord, verbs)
            for verbWord in verbWords:
                key = subjectWord['lemma'].lower() + "+" + verbWord['lemma'].lower()
                if key not in statistics:
                    statistics[key] = list()

                sentence = StatisticUtil.getSentence(taggedWords, verbWord)
                (phraseType, objectWords) = __getObjectPhrases(text, verbWord)
                # print("{phraseType}: {words}".format(phraseType=phraseType, words=objectWords))
                statistics[key].append({"phraseType": phraseType,
                                        "phrase": " ".join(list(map(lambda word: word['word'], objectWords))),
                                        "sentence": sentence
                                        })


    @staticmethod
    # Collect some statistic data
    def basicStatistics():
        from stanza.server import CoreNLPClient  # Import Stanford NLP core

        statistics = {
            "totalSentences": 0,
            "totalTexts": 0,
            "totalSubjects": 0
        }
        cleanText = open(os.path.join('data', 'corpus', 'commonThemes_quotesOnly.txt'), 'r')
        texts = cleanText.readlines()
        subject = 'i'
        statistics['totalTexts'] = len(texts)
        with CoreNLPClient(
                annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'depparse'],
                timeout=30000, inputFormat='text',
                memory='4G') as client:
            for text in texts:
                ann = client.annotate(text)
                for sentenceId, sentence in enumerate(ann.sentence):
                    subjects = [token.word for token in sentence.token if token.word.lower() == subject]
                    if len(subjects) > 0:
                        statistics["totalSentences"] += 1
                        if subject in subjects:
                            statistics["totalSubjects"] += 1
                            break
        print("The number of texts:", statistics['totalTexts'],
              " The number of sentences: ", statistics['totalSentences'],
              " The number of texts containing '", subject, "':", statistics['totalSubjects'])


    # @staticmethod
    # # Collect the frequent terms of 'category'
    # def collectFreqTerms(textDF, category):
    #     total = len(textDF)
    #     freqs = {}
    #     for index, row in textDF.iterrows():
    #         rowCategory = row['category']
    #         if category in rowCategory:
    #             usedTerms = row[category + "_terms"]
    #             for usedTerm in usedTerms:
    #                 term = usedTerm[0]
    #                 if term in freqs:
    #                     freqs[term] += 1
    #                 else:
    #                     freqs[term] = 1
    #     sortedFreqs = dict(sorted(freqs.items(), key=lambda item: item[1], reverse=True))
    #     for term, freq in sortedFreqs.items():
    #         percent = 100 * (freq / total)
    #         print("{term}: {percent:.1f}%".format(term=term, freq=freq, percent=percent))
