# Backend
Backend consists of datasets, Python modules and Java module. To build the backend, run

> python3 dataprocessing.py
> 
> python3 statistics.py

## Datasets
- `glossaryTerms` folder stores the glossary of terms in relation to urban infrastructures.
- `text` folder stores inputs and outputs of backend.


## Python modules

- `stanzaAPIs` module invokes StanfordNLPCore library to process texts and Process the texts with Stanford NLP toolkits to produce NLP meta-data and collect all NLP meta-data to 
- `statisticAPIs` module aggregates and interprets NLP meta-data (from `dataprocessing.py`) and output the JSON file required by visualisation.

### Main entry of Python modules

* `dataprocessing.py` provide the main entry class to `stanzaAPIs` module
    - Input: `/data/text/shareAnIdea/shareAnIdea.csv`
    - Output: `/data/text/shareAnIdea/nlp/text-stanfordNLP.json`

* `statistics.py` provides the main entry class to `statisticAPIs`
    - Input: /data/text/shareAnIdea/nlp/text-stanfordNLP.json
    - Output: /data/text/shareAnIdea/categoryTerm.json
              /data/text/shareAnIdea/patterns.json
      
## Java module

* `stanfordNLP` module invokes StanfordNLPCore library to take texts as input, and produces entity, phrases, and subject-object relations.
    - Input: /data/shareAnIdea/texts.json
    - Output: /data/shareAnIdea/semantics_StanfordNLP.json
  
