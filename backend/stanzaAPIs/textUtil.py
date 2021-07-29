import os.path
import hashlib  # Use hash functions
import re
import pandas as pd


class TextUtil:
    @staticmethod
    def preprocess_line(_line):
        """ Remove non-word characters """
        _line = re.sub(r'[\t\n\"]+', r' ', _line)  # Remove tab and new line
        _line = re.sub(r"’", r"'", _line)  # Replace the ’ char with a single quote
        _line = re.sub(r'"', r"'", _line)  # Replace the double quote char with a single quote
        _line = re.sub(r'\s[-]+\s', r', ', _line)  # Replace hyphen (-) with comma
        # line = re.sub(r'[^\x00-\x7F]+', r' ', line)  ## Remove non-Ascii code
        _line = re.sub(r'\s+', r' ', _line).strip()  # Replace multiple spaces with a single space
        return _line

    @staticmethod
    def check_story(_line, _stories):
        """ Check if the line has the same hash value in the texts"""
        try:
            line_hash = hashlib.sha256(_line.encode()).hexdigest()
            if len(_stories) > 0:
                for _story in _stories:
                    if _story['hash'] == line_hash:
                        print("Found duplicated line ", _line)
                        return False  # Found
            return True  # Not found
        except RuntimeError as ex:
            print("error at ", _line)

    @staticmethod
    def tag(storyFilename):
        # Read story file as a story dataframe
        text_path = os.path.join("data", "text", storyFilename + ".csv")
        text_df = pd.read_csv(text_path)
        texts = []
        for lineNo, line in text_df.iterrows():
            texts.append({'id': lineNo, 'text': line['text'], 'hash': hashlib.sha256(line['text'].encode()).hexdigest()})

        text_df = pd.DataFrame(texts)  # Store all nlp tagged results to the 'text_df' dataframe
        # Write text_df as a csv file
        path = os.path.join('data', 'text', storyFilename, 'nlp', 'texts.csv')
        text_df.to_csv(path_or_buf=path, encoding='utf-8', index=False)
        # # Write to a json file
        path = os.path.join('data', 'text', storyFilename, 'nlp', 'texts.json')
        text_df.to_json(path, orient='records')

        return text_df
