# Urban Narratives
This repository provides a prototype of a demo system (backend and frontend) to construct a demo website that visualise and explore large amount of public comments collected from a public consultation exercise called “Share an Idea” undertaken in Christchurch New Zealand after the 2011 earthquake.


Our implementation comprises backend and frontend. The backend is implemented in a mix of Python and Java to extract linguistic features from the texts with Stanford NLPCore toolkit  (v.4.2.0), and collect and analyze the linguistic features. Stanford NLPCore toolkit is a Java NLP framework that provides commonly used natural language processing functionalities. In our case study, we make use of its sentence splitting, word tokenizer, part-of-speech tagger, lemmatization, dependency parser, and open information extractor (see [Stanford NLPCore toolkit](https://github.com/stanfordnlp/CoreNLP)). The frontend is implemented in Javascript to provide a visualisation of analyzed results from the backend by using a set of open source libraries (Bootstrap, JQuery, Google chart, D3 and Plotly).

In terms of data workflow, the backend takes raw texts collected from the dataset as inputs and extracts linguistic features from the texts with Stanford NLPCore toolkit and then identifies core words and aggregates texts, linguistic features as output. The output of the backend is stored as a file in JSON format for data exchange. The frontend loads the JSON file from the backend, populates the dataset and feeds into the graphical library (D3, Google chart, Plotly, etc) to produce the interactive visualisation on the web page.


# Required Software

* Chrome
* Python (3.6)
* Java (1.11)
* Stanford NLPCore Toolkit (4.2.0)
* Python packages: pandas, stanza, tqdm

# Build Instruction
Please refer to `README` in `backend` and `frontend` folders respectively.


