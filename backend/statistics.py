import csv
import hashlib
import os.path
import pandas as pd
import json
from statisticAPIs.statisticUtil import StatisticUtil
from statisticAPIs.patternUtil import PatternUtil
from functools import reduce
from argparse import Namespace


class Statistic:
    """ Process data """

    def __init__(self):
        """ Read the analysis results """
        self.args = Namespace(
            case_name='shareAnIdea',
            keywords={
                'Space': ['area', 'cbd', 'city', 'center', 'centre', 'courtyard', 'piazza', 'park', 'place',
                          'river', 'square', 'space', 'venue', 'christchurch'],
                'Transport': ['avenue', 'bike', 'bus', 'car', 'cycle', 'lane', 'parking', 'rail', 'shuttle', 'station',
                              'street', 'tram', 'traffic', 'transport', 'walkway', 'pedestrian', 'road', 'monorail',
                              'vehicle', 'truck'],
                'Building': ['apartment', 'building', 'hospital', 'market', 'office', 'quarter', 'retail', 'shop',
                             'store', 'garden', 'housing', 'university', 'school', 'library', 'mall', 'cafe', 'bar',
                             'restaurant'],
                'People': ['people', 'family', 'child', 'disability', 'community', 'shopping', 'art', 'sport',
                           'resident', 'health', 'safety', 'neighbourhood', 'tourist', 'activity', 'parent', 'owner'],
                'Pronouns': ['i', 'we', 'they', 'you', 'he', 'she', 'it', 'this', 'those', 'that', 'there', 'one',
                             'these']
            }
        )

        path = os.path.join('data', 'text', self.args.case_name, 'nlp', 'text-StanfordNLP.json')
        self.textDF = pd.read_json(path)

    # Collect the statistics for subjects
    def collect_statistics(self):
        sentence_list = {'S+V+O': [], 'V+O': [], 'Others': []}
        terms = set()
        # Search all the subject words
        for i, text in self.textDF.iterrows():
            try:
                tagged_words = text['taggedWords']
                # Collect a list of sentences
                sent_ids = list(dict.fromkeys([taggedWord['sentId'] for taggedWord in tagged_words]))
                # Find the subject in each sentence
                for sentId in sent_ids:
                    sentence_words = StatisticUtil.getSentenceBySentId(tagged_words, sentId)
                    subject_words = [taggedWord for taggedWord in sentence_words if 'subj' in taggedWord['ud']]
                    if len(subject_words) > 0:
                        for subjectWord in subject_words:
                            verb_words = StatisticUtil.getSubjectVerb(sentence_words, subjectWord)
                            if len(verb_words) > 0:
                                verb_word = verb_words[0]
                                # Process the subject + verb + object
                                subject_phrase = PatternUtil.getSubjectPhrase(text, subjectWord, verb_word)
                                if len(subject_phrase) > 0:
                                    # # Process the verb
                                    subject_category = PatternUtil.categorize_phrase(subject_phrase, self.args.keywords)
                                    phrase_type, object_phrase = PatternUtil.getObjectPhrase(text, verb_word)
                                    object_category = PatternUtil.categorize_phrase(object_phrase, self.args.keywords)
                                    object_phrase_cloud = PatternUtil.extractObjectPhraseClouds(text, object_phrase)
                                    if subject_category is not None and object_category is not None:
                                        # print(subject_phrase)
                                        sentence_list['S+V+O'].append({
                                            "textId": text['id'], "sentId": sentId, "verb": verb_word,
                                            "subject_phrase": subject_phrase, "object_phrase": object_phrase,
                                            "subject_category": subject_category,
                                            "object_category": object_category, "sentence": sentence_words,
                                            "object_phrase_cloud": object_phrase_cloud
                                        })
                                        terms.add(object_category['term']['lemma'].lower())
                                    break
                    else:
                        # Check if the sentence has only one noun phrase
                        verb_words = [tagged_word for tagged_word in sentence_words if
                                      tagged_word['pennPOS'].startswith('vb')]
                        noun_words = [taggedWord for taggedWord in sentence_words if
                                      taggedWord['pennPOS'].startswith('nn')]
                        if len(verb_words) > 0 and len(noun_words) > 0:
                            verb_word = verb_words[0]
                            phrase_type, object_phrase = PatternUtil.getObjectPhrase(text, verb_word)
                            object_category = PatternUtil.categorize_phrase(object_phrase, self.args.keywords)
                            if object_category is not None:
                                object_phrase_cloud = PatternUtil.extractObjectPhraseClouds(text, object_phrase)
                                # print(subject_phrase)
                                sentence_list['V+O'].append({
                                    "textId": text['id'], "sentId": sentId, "verb": verb_word,
                                    "subject_phrase": [], "object_phrase": object_phrase,
                                    "object_category": object_category, "sentence": sentence_words,
                                    "object_phrase_cloud": object_phrase_cloud
                                })
                                terms.add(object_category['term']['lemma'].lower())
                        else:
                            sentence_list['Others'].append(
                                {"sentence": PatternUtil.getSentence(text, sentId), "text": text['text']})
            except Exception as err:
                print("Error occurred! {err}".format(err=err))
        # Extract the subject s
        PatternUtil.aggregate_category_terms(sentence_list, self.args)

    # Extract the pattern tree for three patterns (I/We+want/like/love+something), ("I/We+want/like/love+to do
    # something) ("I/We + think/believe + clause")
    def extractPatternTree(self):
        subjects = ['i', 'we']
        verbs = ['want', 'need', 'like', 'love', 'think', 'believe']
        sentenceDict = {
            'NP': [],
            'VP': [],
            'CLAUSE': [],
            "Others": [],
            "ADJP": []
        }

        # Search all the subject words
        for i, text in self.textDF.iterrows():
            taggedWords = text['taggedWords']
            # Collect a list of sentences
            sentIds = list(dict.fromkeys([taggedWord['sentId'] for taggedWord in taggedWords]))
            # Find the subject in each sentence
            for sentId in sentIds:
                sentenceWords = StatisticUtil.getSentenceBySentId(taggedWords, sentId)
                subjectWords = [taggedWord for taggedWord in sentenceWords if 'subj' in taggedWord['ud'] and
                                taggedWord['lemma'].lower() in subjects]
                for subjectWord in subjectWords:
                    for verbWord in StatisticUtil.getSubjectVerb(sentenceWords, subjectWord):
                        if verbWord['lemma'].lower() in verbs:
                            subjectPhrase = PatternUtil.getSubjectPhrase(text, subjectWord, verbWord)
                            if len(subjectPhrase) > 0:
                                # # Process the verb
                                if verbWord['lemma'].lower() in ['think', 'believe']:
                                    phraseType, objectPhrase = PatternUtil.getObjectClause(text, verbWord)
                                else:
                                    phraseType, objectPhrase = PatternUtil.getObjectPhrase(text, verbWord)
                                objectCategory = PatternUtil.categorize_phrase(objectPhrase, self.args.keywords)
                                sentenceDict[phraseType].append({
                                    "textId": text['id'], "sentId": sentId, "verb": verbWord,
                                    "subjectPhrase": subjectPhrase, "objectPhrase": objectPhrase,
                                    "objectCategory": objectCategory, "sentence": sentenceWords
                                })
        PatternUtil.extractPattern(sentenceDict, self.args)

    # Extract the sentences for manual annotation
    def classify_text_category(self):
        text_list = list()
        for i, idea in self.textDF.iterrows():
            try:
                text_info = {'text': idea['text']}
                # Find the corresponding NLP tags from textDF
                nlp_words = idea['taggedWords']
                for category in ['space', 'transport', "building", "people"]:
                    keywords = self.args.keywords[category]
                    is_matched = False
                    matched_words = list(filter(lambda word: word['lemma'] in keywords, nlp_words))
                    if len(matched_words) > 0:
                        # Matched the category
                        is_matched = True
                    text_info[category] = category.lower() if is_matched else "non-" + category
                text_list.append(text_info)
            except RuntimeError as err:
                print(err)
        # # Write out to the JSON csv file
        path = os.path.join('data', 'transformer', self.args.case_name, 'categorized_shareAnIdea.csv')
        df = pd.DataFrame(text_list, columns=["space", "transport", "building", "people", "text"])
        df.to_csv(path, encoding='utf-8', index=False)
        # # Write to a json file
        path = os.path.join('data', 'transformer', self.args.case_name, 'categorized_shareAnIdea.json')
        df.to_json(path, orient='records')
        print("Categorize texts to data/transformer/categorized_shareAnIdea.json completes!")


if __name__ == '__main__':
    statistic = Statistic()
    #statistic.collect_statistics()
    statistic.extractPatternTree()

