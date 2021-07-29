import json
import os.path
import pandas as pd
from argparse import Namespace
from tqdm import tqdm

# Our module
from stanzaAPIs.nlpprocessor import NLPProcessor


class DataProcessor:
    """ Process data """

    def __init__(self):
        self.debug = False
        self.args = Namespace(
            storyFilename='shareAnIdea',
            # storyFilename='HamiltonIdeas',
            infrastructures=['hard', 'soft'],
            categories=['People', 'Service', 'Communities', 'Culture', 'Transport', 'Building', 'Space', 'Utilities'],
            infCategories={'hard': ['Transport', 'Building', 'Space', 'Utilities'],
                           'soft': ['People', 'Service', 'Communities', 'Culture']}
        )

        self.columns = ["id", "infrastructure", "category", "story", "hash",
                        "taggedWords", "taggedPhrases", "taggedTriples"]

        self.isUpdate = True
        self.isFilter = False
        self.storyDF = None

    def process_nlp_texts(self):
        """Read all stories as a list and also remove all the punctuation and tab and double quote """
        if self.isUpdate:
            nlp_processor = NLPProcessor(self.args.storyFilename)
            nlp_processor.tag_with_stanford_nlp()
            self.storyDF = nlp_processor.write_outputs()
        else:
            path = os.path.join('data', 'text', self.args.storyFilename, 'nlpTags',
                                'text-StanfordNLP.json')
            self.storyDF = pd.read_json(path)

    def __classifyCategory(self):
        def _countFrequencyV2(_story, _keyTerms):
            """ Return a list of key terms used in the story by counting the number of tagged word"""
            _termFreq = []
            storyTags = _story['taggedWords']
            for keyTerm in _keyTerms:
                try:
                    # foundTags = list(filter(lambda storyWnord: storyWord['word'].lower() == keyTerm, storyTags))
                    foundTags = [storyTag for storyTag in storyTags if storyTag['word'].lower() == keyTerm]
                    if len(foundTags) > 0:
                        _termFreq.append((keyTerm, len(foundTags)))
                except Exception as ex:
                    print("Error occurs at ", keyTerm)
            _termFreq.sort(key=lambda tup: tup[1], reverse=True)  # Sort by freq
            return _termFreq

        try:
            # Read the glossary of terms
            path = os.path.join('data', 'glossaryTerms',
                                self.glossaryTermCollectionFilename + '-category.json')
            glossaryTermDF = pd.read_json(path)
            categoryTerms = {}
            # Initialise the category terms
            for category in self.args.categories:
                categoryTerms[category] = []
            # Go through each story and categorize the story with word occurrences
            storyCategories = []
            storyInfrastructures = []
            for i, story in self.storyDF.iterrows():
                # Story Category
                storyCategory = []
                for category in self.args.categories:
                    keyTerms = glossaryTermDF.query('category == "' + category + '"')['glossaryTerms'].iloc[0]
                    termFreq = _countFrequencyV2(story, keyTerms)
                    # Add the frequency of key term
                    categoryTerms[category].append(termFreq)
                    if len(termFreq) > 0:
                        storyCategory.append(category)
                storyCategories.append(storyCategory)
                # Story Infrastructures
                storyInfrastructure = []
                # Check if any category falls within infrastructure
                for infrastructure in self.args.infrastructures:
                    # Check if any story category belong hard/soft infrastructures
                    if bool(set(storyCategory).intersection(set(self.args.infCategories[infrastructure]))):
                        storyInfrastructure.append(infrastructure)
                # No infrastructure
                if len(storyInfrastructure) == 0:
                    storyInfrastructure.append('none')
                storyInfrastructures.append(storyInfrastructure)
            # End of the loop iteration for stories
            # Update the dataframe columns
            for category in self.args.categories:
                self.storyDF[category + '_terms'] = categoryTerms[category]
            # Story categories
            self.storyDF['category'] = storyCategories
            # Story infrastructures
            self.storyDF['infrastructure'] = storyInfrastructures
            self.storyDF = self.storyDF[self.columns]  # reorder the columns
            # Write all categorized stories to csv
            path = os.path.join('data', 'story', self.storyCategorizationFilename + '.csv')
            self.storyDF.to_csv(path_or_buf=path, encoding='utf-8', index=False)
            # # Write to a json file
            path = os.path.join('data', 'story', self.storyCategorizationFilename + '.json')
            self.storyDF.to_json(path, orient='records')
        except Exception as ex:
            print("Error at " + self.args.storyFilename + '.txt')

    def __generateChordMatrix(self):
        """ Collect the story number for each category and generate the matrix for chord chart """
        path = os.path.join('data', 'story', self.storyCategorizationFilename + '.json')
        with open(path) as jsonFile:
            storyCategories = json.load(jsonFile)
            matrix = []
            for category1 in self.args.categories:
                vector = []
                for category2 in self.args.categories:
                    if category1 != category2:
                        filteredStoryCategories = list(
                            filter(lambda story: (category1 in story['category']) and (category2 in story['category']),
                                   storyCategories))
                        vector.append(len(filteredStoryCategories))
                    else:  # Empty for the same category
                        vector.append(0)
                matrix.append(vector)
            print("Chord Matrix:", matrix)
            path = os.path.join('data', 'story', self.storyCategorizationFilename + '-matrix.json')
            with open(path, 'w') as outfile:
                json.dump(matrix, outfile)

    def __mappingGlossaryTermStories(self):
        """ For each term, collect a list of stories that uses the term"""
        path = os.path.join('data', 'glossaryTerms',
                            self.glossaryTermCollectionFilename + '-category.json')
        glossaryTermDF = pd.read_json(path)
        path = os.path.join('data', 'story', self.storyCategorizationFilename + '.json')
        storyCategories = pd.read_json(path)
        print("Starting mapping glossary of terms")
        glossaryTermStories = []
        for i, glossaryTerm in glossaryTermDF.iterrows():
            infrastructure = glossaryTerm['infrastructure']
            category = glossaryTerm['category']
            keyTerms = glossaryTerm['glossaryTerms']
            # Create the mask to filter
            categoryMask = storyCategories['category'].apply(lambda storyCategory: category in storyCategory)
            # keep only stories that include the category
            selectedStoriesDF = storyCategories[categoryMask]
            for keyTerm in keyTerms:
                # Go through each story and check if the 'freq_category_term' contains the key term
                storyIDs = []
                for j, selectedStory in selectedStoriesDF.iterrows():
                    foundFreqTerms = [freqTerm for freqTerm in selectedStory[category + '_terms'] if
                                      freqTerm[0] == keyTerm]
                    if len(foundFreqTerms) > 0:
                        storyIDs.append(selectedStory['id'])
                glossaryTermStories.append({'term': keyTerm, "infrastructure": infrastructure, "category": category,
                                            'count': len(storyIDs), 'story_ids': storyIDs})
            if (i % 100) == 0:
                print("Mapping the glossary of terms at index " + str(i))

        glossaryTermStoriesDF = pd.DataFrame(glossaryTermStories)
        path = os.path.join('data', 'story', self.glossaryTermMapFile + '.csv')
        glossaryTermStoriesDF.to_csv(path_or_buf=path, encoding='utf-8', index=False)
        # # Write to a json file
        path = os.path.join('data', 'story', self.glossaryTermMapFile + '.json')
        glossaryTermStoriesDF.to_json(path, orient='records')

    def process(self):
        try:
            stateBar = tqdm(desc='Process Texts', total=1)
            # JSON object 'hard_terms' and 'soft_terms' store the key terms for hard/soft infrastructure
            self.process_nlp_texts()
            # stateBar.update()
            # self.__classifyCategory()
            # stateBar.update()
            # self.__generateChordMatrix()
            # stateBar.update()
            # self.__mappingGlossaryTermStories()
            # stateBar.update()
        except Exception as ex:
            print("Errors!!! Something went wrong", ex)


if __name__ == '__main__':
    # Generate the glossary of terms and identify key infrastructure terms
    data_processor = DataProcessor()
    data_processor.process()
