import os.path
import pandas as pd
from stanza.server import CoreNLPClient  # Import Stanford NLP core
from stanzaAPIs.nlpTagger import NLPTagger
from stanzaAPIs.textUtil import TextUtil


class NLPProcessor:

    # Constructor
    def __init__(self, _story_filename):
        # Create the nlp pipeline
        self.story_filename = _story_filename
        self.text_df = TextUtil.tag(self.story_filename)
        print("Load the texts")

    def write_outputs(self):
        """ Write text DF to csv/json file"""
        path = os.path.join('data', 'text', self.story_filename, 'nlp', 'text-StanfordNLP.csv')
        self.text_df.to_csv(path_or_buf=path, encoding='utf-8', index=False)
        # # Write to a json file
        path = os.path.join('data', 'text', self.story_filename, 'nlp', 'text-StanfordNLP.json')
        self.text_df.to_json(path, orient='records')
        print("Write text df to {path}".format(path=path))
        return self.text_df

    # Tag words with pos and dependencies
    def tag_with_stanford_nlp(self):
        try:
            tagger = NLPTagger(self.story_filename, self.text_df)
            tagger.tag_words()
            # tagger.tagSentiment()
            tagger.tag_semantic_features()  # phrases, triples, entities
            self.text_df = tagger.text_df
        except Exception as ex:
            print("Errors!!! Something went wrong", ex)

    # Use Vader sentiment analyzer to compute the sentiments of the sentence.
    def tagSentimentWithVader(self):
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # Vader sentiment analysis
        with CoreNLPClient(
                annotators=['tokenize', 'ssplit'],
                timeout=30000, inputFormat='text',
                memory='8G') as client:
            storySentiments = []
            # Create a SentimentIntensityAnalyzer object. 
            analyzer = SentimentIntensityAnalyzer()
            for i, story in self.text_df.iterrows():
                sentenceSentiment = []
                try:
                    ann = client.annotate(story['story'])
                    for sentenceId, sentence in enumerate(ann.sentence):
                        # print(sentence)
                        text = " ".join([token.word for token in sentence.token])
                        # The polarity_scores contains pos, neg, neu, and compound scores.
                        # 'compound' score is the normalized, weighted score 
                        # We can use the compound score to determine the positive, negative or neutral of the sentence 
                        sentiment_dict = analyzer.polarity_scores(text)
                        sentiment = ""
                        # Use 'compound' score tpo decide the sentence's sentiment as positive, negative and neutral 
                        if sentiment_dict['compound'] >= 0.05:
                            if sentiment_dict['compound'] >= 0.9:
                                sentiment = 'Very positive'
                            else:
                                sentiment = 'Positive'
                        elif sentiment_dict['compound'] <= -0.05:
                            if sentiment_dict['compound'] <= -0.9:
                                sentiment = 'Very negative'
                            else:
                                sentiment = 'Negative'
                        else:
                            sentiment = 'Neutral'
                        ## Sentence-level sentiment results    
                        sentenceSentiment.append(
                            {'sentId': sentenceId, 'sentiment': sentiment, 'scores': sentiment_dict})
                except:
                    print("Error at ", story)
                ### Add Vader sentence-level sentiment results                
                storySentiments.append(sentenceSentiment)
        self.text_df['storySentimentVader'] = storySentiments
        pd.set_option('display.max_columns', None)  # Show all the columns
        print(self.text_df.head())


# if __name__ == '__main__':
#     version = '4'
#     storyFilename = 'commonThemes_quotesOnly'
#     nlpProcessor = StanfordNLPProcessor(storyFilename, version)
#     nlpProcessor.tagWithStanfordNLP()
#     nlpProcessor.tagSentimentWithVader()
#     storyDF = nlpProcessor.writeOutputs()
#     pd.set_option('display.max_columns', None)  # Show all the columns
#     print(storyDF.head())
