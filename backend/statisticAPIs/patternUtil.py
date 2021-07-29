import os.path
import pandas as pd
import re
import random
import json
from functools import reduce


class PatternUtil:
    categories = ['Space', 'Transport', 'Building', 'People', 'Pronouns']

    @staticmethod
    def groupObjectPhrases(total, subjectCategory, terms):
        if subjectCategory != "Pronouns":
            return []

        statistics = {}
        categories = ['Space', 'Transport', 'Building', 'People', 'Others']
        for category in categories:
            statistics[category] = {}
        # Collect the statistics of object phrases
        for term in terms:
            sentences = term['sentences']
            for sentence in sentences:
                objectCategory = sentence['objectCategory']['category']
                if objectCategory != "Pronouns":
                    objectTerm = sentence['objectCategory']['term']['lemma'].lower()
                    if objectTerm not in statistics[objectCategory]:
                        statistics[objectCategory][objectTerm] = list()
                    statistics[objectCategory][objectTerm].append(sentence)
        # Sort the object terms within the category
        for category, objectTerms in statistics.items():
            statistics[category] = dict(
                sorted(objectTerms.items(), key=lambda item: len(item[1]), reverse=True))
        # print(statistics)
        groupObjectPhrases = []
        for category in categories:
            subTotal = reduce(lambda acc, sentences: acc + len(sentences), statistics[category].values(), 0)
            proportion = round(100 * (subTotal / total), 2)
            print(
                "Object category: {category} total: {total} ({percent:.1f}%)".format(category=category, total=subTotal,
                                                                                     percent=proportion))
            terms = []
            for term, sentences in statistics[category].items():
                freq = len(sentences)
                # Sort the sentence by the subject words
                sortedSentences = sorted(sentences, key=lambda s: s['subjectPhrase'][-1]['lemma'] if
                len(s['subjectPhrase']) > 0 else 'you')
                terms.append({"term": term, "sentences": sortedSentences, "freq": freq})
            groupObjectPhrases.append({"category": category, "terms": terms, "percent": proportion})
        return groupObjectPhrases

    @staticmethod
    def getPhraseWords(text, phrase):
        sentId = phrase['sentId']
        sentenceWords = list(filter(lambda word: word['sentId'] == sentId, text['taggedWords']))
        return [taggedWord for taggedWord in sentenceWords if phrase['start'] <= taggedWord['id'] <= phrase['end']]

    @staticmethod
    def extractObjectPhraseClouds(text, objectPhrase):
        wordClouds = []
        sentId = objectPhrase[0]['sentId']
        start = objectPhrase[0]['id']
        end = objectPhrase[-1]['id']
        # Get the phrases within the objectPhrase
        phrases = list(filter(lambda phrase: phrase['sentId'] == sentId and
                                             phrase['start'] >= start and phrase['end'] <= end and
                                             phrase['isLeaf'] == True and
                                             (phrase['ptb'].startswith("NP") or phrase['ptb'].startswith("ADJP")),
                              text['taggedPhrases']))
        filterPOS = ['dt', 'prp', 'cc', "cd", "sym", "hyph"]
        filterPunctuations = ['#', '$', "'", "(", ")", ",", ".", ":", "`"]
        # Add the phrase
        for phrase in phrases:
            try:
                phraseType = "NP" if phrase['ptb'].startswith("NP") else "ADJP"
                phraseWords = PatternUtil.getPhraseWords(text, phrase)
                # Remove useless words
                phraseWords = list(filter(lambda word: word['pennPOS'] not in filterPOS and
                                                       word['lemma'] not in filterPunctuations, phraseWords))
                phraseWords = phraseWords[-2:]  # Get the last two words
                lemmaWords = " ".join(list(map(lambda word: word['lemma'].lower(), phraseWords)))
                wordClouds.append({"phraseType": phraseType, "lemmaWords": lemmaWords, "phraseWords": phraseWords})
            except Exception as err:
                print("Error: {err}".format(err=err))
        return wordClouds

    @staticmethod
    def getSubjectPhrase(text, subjectWord, verbWord):
        taggedWords = text['taggedWords']
        taggedPhrases = text['taggedPhrases']
        sentId = subjectWord['sentId']
        phrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                   taggedPhrase['sentId'] == sentId and
                   taggedPhrase['start'] <= subjectWord['id'] <= taggedPhrase['end'] < verbWord['id']]
        if len(phrases) == 0:
            return []
        # Sort by the length
        nounPhrase = list(filter(lambda _phrase: _phrase['ptb'] == 'NP', phrases))
        if len(nounPhrase) > 0:
            phrases = nounPhrase
        phrases.sort(key=lambda x: x['end'] - x['start'])
        phrase = phrases[0]
        phraseWords = list(filter(lambda taggedWord: taggedWord['sentId'] == sentId and
                                                     phrase['start'] <= taggedWord['id'] <= phrase['end'],
                                  taggedWords))
        return phraseWords

    @staticmethod
    def aggregate_category_terms(sentence_list, args):
        total = len(sentence_list['S+V+O']) + len(sentence_list['V+O'])
        categories = ['Space', 'Transport', 'Building', 'People', 'Others']
        # Groupped categories
        group_categories = {}
        for category in categories:
            group_categories[category] = {}
        group_categories['Others'] = {}
        # Group the sentences by category and term
        for s in ['S+V+O', 'V+O']:
            for sentence_dict in sentence_list[s]:
                try:
                    if s == 'S+V+O':
                        if sentence_dict['subject_category']['category'] != "Pronouns":
                            category_dict = sentence_dict['subject_category']
                        else:
                            category_dict = sentence_dict['object_category']    # Use the object category for pronouns
                    else:
                        category_dict = sentence_dict['object_category']

                    category = category_dict['category']
                    if category != 'Pronouns':
                        term = category_dict['term']['lemma'].lower()
                        if term not in group_categories[category]:
                            group_categories[category][term] = list()
                        group_categories[category][term].append(sentence_dict)  # Add the sentence for categories
                # Sort the terms in each category
                except Exception as err:
                    print("Error occurred {err}".format(err=err))

        # # Sort by the frequencies of category
        for category, sentence_dict in group_categories.items():
            group_categories[category] = dict(
                sorted(sentence_dict.items(), key=lambda item: len(item[1]), reverse=True))
        # Categorize the sentences by infrastructure category
        category_terms = []
        for category in categories:
            sub_total = reduce(lambda acc, s: acc + len(s), group_categories[category].values(), 0)
            proportion = round(100 * (sub_total / total), 2)
            print("Category: {category} total: {total} ({percent:.1f}%)".format(category=category,
                                                                                total=sub_total,
                                                                                percent=proportion))
            terms = []
            for term, sentences in group_categories[category].items():
                freq = len(sentences)
                # Sort the sentence by the verb
                sorted_sentences = sorted(sentences, key=lambda s: s['verb']['lemma'])
                terms.append({"term": term, "sentences": sorted_sentences, "freq": freq})
            # # Categorize Object phrases
            # object_category = PatternUtil.groupObjectPhrases(total, category, terms)
            category_terms.append({"category": category, "terms": terms, "percent": proportion})
        category_df = pd.DataFrame(category_terms, columns=['category', 'terms', "percent"])
        # Write out to the JSON csv file
        path = os.path.join('data', 'text', args.case_name, 'categoryTerm.csv')
        category_df.to_csv(path_or_buf=path, encoding='utf-8', index=False)
        # # Write to a json file
        path = os.path.join('data', 'text', args.case_name, 'categoryTerm.json')
        category_df.to_json(path, orient='records')
        # Print
        print("Extracting subjects and write outputs to {path} completes!".format(path=path))

    # Categorize the object phrase based on the keywords
    @staticmethod
    def categorize_phrase(phrase, keywords):
        try:
            for category in ['Space', 'Transport', 'Building', 'People', 'Pronouns']:
                category_terms = list(filter(lambda word: word['lemma'].lower() in keywords[category], phrase))
                if len(category_terms) > 0:
                    return {"term": category_terms[0], "category": category}

            # Exclude list
            exclude_list = ['it', 'that', 'what', 'one', 'all', 'they', ')', 'etc']
            nouns = list(filter(lambda word: word['lemma'].lower() not in exclude_list, phrase))
            if len(nouns) > 0:
                return {"category": "Others", "term": nouns[-1]}
            else:
                return None   # Skip the sentence
        except Exception as err:
            print("Error".format(err=err))

    @staticmethod
    def checkIfSentenceExist(newSentence, sentences):  # Check if the object phrase exists in the sentences
        newObjectPhrase = " ".join(list(map(lambda word: word['word'], newSentence['objectPhrase'])))
        for sentence in sentences:
            objectPhrase = " ".join(list(map(lambda word: word['word'], sentence['objectPhrase'])))
            if objectPhrase == newObjectPhrase:
                return True
        return False

    @staticmethod
    def extractPattern(sentenceDict, args):
        # Group the sentences by pattern
        patterns = [{"name": "NP", "title": 'I/We want/need/like', "verbs": ['want', 'need', 'like'],
                     "categories": []},
                    {"name": "VP", "title": 'I/We want/need/like to do', "verbs": ['want', 'need', 'like'],
                     "categories": []},
                    {"name": "CLAUSE", "title": 'I/We think/believe that', "verbs": ['think', 'believe'],
                     "categories": []}]
        try:
            for pattern in patterns:
                sentences = list(
                    filter(lambda s: s['verb']['lemma'] in pattern['verbs'], sentenceDict[pattern["name"]]))
                categories = []
                for category in ['Space', 'Transport', 'Building', 'People']:
                    # Group the sentences by category
                    categorySentences = list(filter(lambda s: s['objectCategory']['category'] == category, sentences))
                    categorySentences = sorted(categorySentences,
                                               key=lambda sentence: sentence['verb']['lemma'].lower())
                    # Group the category sentences by terms
                    termDict = {}
                    for sentence in categorySentences:
                        term = sentence['objectCategory']['term']['lemma'].lower()
                        if term not in termDict:
                            termDict[term] = list()
                        # Check if the object phrase exists in th
                        if not PatternUtil.checkIfSentenceExist(sentence, termDict[term]):
                            termDict[term].append(sentence)
                    termDict = dict(sorted(termDict.items(), key=lambda item: len(item[1]), reverse=True))
                    categories.append({"category": category, "terms": termDict})
                pattern['categories'] = categories
            # Write out to the JSON csv file
            patternDF = pd.DataFrame(patterns, columns=['name', 'title', 'verbs', 'categories'])
            path = os.path.join('data', 'text', args.case_name, 'patterns.csv')
            patternDF.to_csv(path_or_buf=path, encoding='utf-8', index=False)
            # # Write to a json file
            path = os.path.join('data', 'text', args.case_name, 'patterns.json')
            patternDF.to_json(path, orient='records')
            # Print
            print("Extracting patterns and write outputs to data/story/patterns.json completes!")
        except Exception as err:
            print("Error:{err}".format(err=err))

    @staticmethod
    def getObjectClause(text, verbWord):
        try:
            verbId = verbWord['id']
            sentId = verbWord['sentId']
            sentenceWords = [taggedWord for taggedWord in text['taggedWords'] if taggedWord['sentId'] == sentId]
            sentence = " ".join(list(map(lambda word: word['word'], sentenceWords)))
            taggedPhrases = text['taggedPhrases']
            # Get SBAR
            clauses = [taggedPhrase for taggedPhrase in taggedPhrases if
                       taggedPhrase['sentId'] == sentId and
                       verbId < taggedPhrase['start'] <= verbId + 5 and
                       taggedPhrase['ptb'].startswith('SBAR')]
            if len(clauses) > 0:
                sortedClauses = sorted(clauses, key=lambda c: c['end'] - c['start'])
                clause = sortedClauses[0]
                clauseWords = [taggedWord for taggedWord in sentenceWords if
                               clause['start'] <= taggedWord['id'] <= clause['end']]
                return 'CLAUSE', clauseWords
            return "Others", sentenceWords
        except Exception as ex:
            print(ex)

    @staticmethod
    def getObjectPhrase(text, verbWord):
        def mapPhraseTypes(_phraseType):
            if _phraseType in ['NP', 'PP']:
                return 'NP'
            elif _phraseType in ['VP', 'S(']:
                return 'VP'
            elif _phraseType in ['ADJP']:
                return 'ADJP'
            elif _phraseType in ['CLAUSE']:
                return "CLAUSE"
            return "Others"

        MAXLENGTH = 5
        # Main entry
        try:
            # Get the noun phrases
            verbId = verbWord['id']
            sentId = verbWord['sentId']
            sentenceWords = [taggedWord for taggedWord in text['taggedWords'] if taggedWord['sentId'] == sentId]
            sentence = " ".join(list(map(lambda word: word['word'], sentenceWords)))
            taggedPhrases = text['taggedPhrases']

            # The verb is used within a noun phrase (integrated retail)
            _nounPhrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                            taggedPhrase['sentId'] == sentId and
                            taggedPhrase['ptb'].startswith('NP') and
                            taggedPhrase['start'] == verbWord['id']]
            if len(_nounPhrases) > 0:
                phraseWords = [taggedWord for taggedWord in sentenceWords if
                               taggedWord['sentId'] == sentId and
                               _nounPhrases[0]['start'] <= taggedWord['id'] <= _nounPhrases[0]['end']]
                return 'NP', phraseWords

            # Get the verb phrase containing the verb
            _verbPhrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                            taggedPhrase['sentId'] == sentId and
                            taggedPhrase['ptb'].startswith('VP') and
                            taggedPhrase['start'] == verbWord['id']]
            # Get the noun or verb phrase inside the verb phrase
            phrases = [taggedPhrase for taggedPhrase in taggedPhrases if
                       taggedPhrase['sentId'] == sentId and
                       verbWord['id'] < taggedPhrase['start'] < verbWord['id'] + MAXLENGTH]
            if len(phrases) == 0:
                # Get SBAR
                clauses = [taggedPhrase for taggedPhrase in taggedPhrases if
                           taggedPhrase['sentId'] == sentId and
                           verbId < taggedPhrase['start'] <= verbId + 5 and
                           taggedPhrase['ptb'].startswith('SBAR')]
                if len(clauses) > 0:
                    sortedClauses = sorted(clauses, key=lambda clause: clause['end'] - clause['start'])
                    clause = sortedClauses[0]
                    clauseWords = [taggedWord for taggedWord in sentenceWords if
                                   clause['start'] <= taggedWord['id'] <= clause['end']]
                    return 'CLAUSE', clauseWords
                return "Others", sentenceWords
            # Get the longest phrase
            sortedPhrases = sorted(phrases, key=lambda _phrase: _phrase['end'] - _phrase['start'],
                                   reverse=True)
            phrase = sortedPhrases[0]
            if phrase['ptb'].startswith('AD'):
                phraseType = phrase['ptb'][0:4]
            else:
                phraseType = phrase['ptb'][0:2]
            phraseType = mapPhraseTypes(phraseType)
            # Get the leaf noun phrase
            phraseWords = [taggedWord for taggedWord in sentenceWords if
                           taggedWord['sentId'] == sentId and
                           phrase['start'] <= taggedWord['id'] <= phrase['end']]
            return phraseType, phraseWords
        except Exception:
            print("Error occurred: {sentence}".format(sentence=sentence))
            return "Others", sentenceWords  # Return an empty array

    @staticmethod
    def getSentence(text, sentId):
        taggedWords = text['taggedWords']
        sentenceWords = [taggedWord for taggedWord in taggedWords if taggedWord['sentId'] == sentId]
        sentence = " ".join(list(map(lambda w: w['word'], sentenceWords)))
        for word in [',', '.', '?', '!', "'s", "n't", "'ve", ")", "N'T"]:  # Remove the space before the word
            sentence = sentence.replace(' ' + word, word)

        for word in ['(']:  # Remove the space after the word
            sentence = sentence.replace(word + " ", word)

        for word in ["-"]:  # Remove the space before and after word
            sentence = sentence.replace(" " + word + " ", word)

        # Remove all the characters
        sentence = re.compile(r'\s+\'\s+').sub("  ", sentence)

        # Remove multiple spaces
        sentence = re.compile(r"\s+").sub(" ", sentence).strip()
        return sentence
