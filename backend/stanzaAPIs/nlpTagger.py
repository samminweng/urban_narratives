from stanza.server import CoreNLPClient  # Import Stanford NLP core
import os.path
import pandas as pd


class TagWord:
    def __init__(self, id, sentId, word, lemma, pennPOS):
        self.properties = {
            "id": id,
            "sentId": sentId,
            "word": word,
            "lemma": lemma,
            "pennPOS": pennPOS,
        }

    # For a given token, create the head node from basic dependencies
    def add_head_node(self, sentence):
        root = sentence.enhancedPlusPlusDependencies.root[0]
        tokenId = self.properties['id']
        if tokenId == root:
            self.properties['ud'] = 'root'
            self.properties['head'] = "root-0"  # Root node
        else:
            # Get the dependency edge associated with
            try:
                edges = [edge for edge in sentence.enhancedPlusPlusDependencies.edge if
                         edge.target == tokenId]
                if len(edges) > 0:
                    self.properties['ud'] = edges[0].dep
                    self.properties['head'] = sentence.token[edges[0].source - 1].word + '-' + str(
                        edges[0].source)
                    # Enhanced plus plus dependencies may have two head words
                    if len(edges) >= 2:
                        self.properties['ud1'] = edges[1].dep
                        self.properties['head1'] = sentence.token[edges[1].source - 1].word + '-' + str(
                            edges[1].source)
                else:
                    self.properties['ud'] = ''
                    self.properties['head'] = ''
                    raise Exception('Cannot find the dependencies at tokenId = ', tokenId)
            except Exception as ex:
                print("error at ", ex)

    def toJSON(self):
        return self.properties


class NLPTagger:
    def __init__(self, _text_filename, _text_df):
        self.text_filename = _text_filename
        self.text_df = _text_df

    # Tag words with NLP metadata
    def tag_words(self):
        # Start nlp core client
        with CoreNLPClient(
                annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'parse', 'depparse'],
                inputFormat='text',
                prettyPrint=False,
                memory='4G'
        ) as client:

            text_tagged_words = []
            for i, text in self.text_df.iterrows():
                try:
                    tagged_words = []
                    ann = client.annotate(text['text'])
                    for sentId, sentence in enumerate(ann.sentence):
                        for tokenId, token in enumerate(sentence.token):
                            tagged_word = TagWord(tokenId + 1, sentId, token.word, token.lemma, token.pos.lower())
                            tagged_word.add_head_node(sentence)
                            tagged_words.append(tagged_word.toJSON())
                except Exception as ex:
                    print("Error at ", i, " ", text, " Error: ", ex)
                text_tagged_words.append(tagged_words)
        self.text_df['taggedWords'] = text_tagged_words
        # Write storyDF as a csv file
        path = os.path.join('data', 'text', self.text_filename, 'nlp', 'tagged_words.csv')
        self.text_df.to_csv(path_or_buf=path, encoding='utf-8', index=False)
        # Write to a json file
        path = os.path.join('data', 'text', self.text_filename, 'nlp', 'tagged_words.json')
        self.text_df.to_json(path, orient='records')
        # Tag sentiment for each word in the text

    def tagSentiment(self):
        # text = "Chris Manning is a nice person. Chris wrote a simple sentence. He also gives oranges to people."
        storySentiments = []
        with CoreNLPClient(
                annotators=['tokenize', 'ssplit', 'pos', 'parse', 'sentiment'],
                inputFormat='text',
                memory='4G') as client:
            for i, story in self.text_df.iterrows():
                sentenceSentiment = []
                try:
                    ann = client.annotate(story['story'])
                    for sentenceId, sentence in enumerate(ann.sentence):
                        wordSentiment = []  # Word-level sentiment results
                        for tokenId, token in enumerate(sentence.token):
                            wordSentiment.append({'id': tokenId + 1, 'word': token.word, 'sentiment': token.sentiment})
                        # Sentence-level sentiment results
                        sentenceSentiment.append({'sentId': sentenceId, 'sentiment': sentence.sentiment,
                                                  'wordSentiment': wordSentiment})
                except Exception as ex:
                    print("Error at ", story)
                storySentiments.append(sentenceSentiment)
        self.text_df['storySentimentStanfordNLP'] = storySentiments
        # Write storyDF as a csv file
        path = os.path.join('data', 'story', 'nlpTags', self.text_filename + '-sentiments.csv')
        self.text_df.to_csv(path_or_buf=path, encoding='utf-8', index=False)
        # Write to a json file
        path = os.path.join('data', 'story', 'nlpTags', self.text_filename + '-sentiments.json')
        self.text_df.to_json(path, orient='records')

    # Include phrases, triples, entities
    def tag_semantic_features(self):
        # Read the tagged constituents from Stanford NLP constituent parser
        path = os.path.join('stanfordNLP', 'NLPParserIntelliJ', 'data', self.text_filename,
                            'semantics_StanfordNLP.json')
        annotated_nlp_df = pd.read_json(path)
        self.text_df['taggedPhrases'] = annotated_nlp_df['taggedPhrases']
        # Read the tagged relation triples from Stanford NLP Open IE information parser
        self.text_df['taggedTriples'] = annotated_nlp_df['taggedTriples']
        # Read the tagged entity
        self.text_df['taggedEntities'] = annotated_nlp_df['taggedEntities']


