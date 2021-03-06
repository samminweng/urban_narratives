# Frontend
Frontend provide a visualisation of analyzed results from the backend by using a set of open source libraries (Bootstrap, JQuery, Google chart, D3 and Plotly). 
Frontend contains the dataset collected by backend and the visualisation Javascript webpages. To run frontend, open the below page with Chrome browsers:

> Cascade View: categoryTermChartV2.html

> Tree View: patternWordTree.html

## Folder Structures:
* Datasets 
NLP dataset includes the public comments and linguistic meta-data processed by Stanford NLPCore Toolkit.
  - `/data/categoryTerm/commonThemes/categoryTerm.json`: the datasource for Cascade View
  - `/data/pattern/patterns.json`: the datasource for Tree View
    
* Website pages 
  - `categoryTermChartV2.html`: the webpage of Cascade View
  - `patternWordTree.html`: the webpage of Tree View
    
* Javascript
  - `/js/categoryTermChart`: Javascript functions for Cascade View
  - `/js/patternWordTree`: Javascript functions for Tree View

* Styles:
    - `/css`: CSS style sheets for Cascade and Tree views 

* Third-party library:
   - `/lib`: all the required libraries have been downloaded to `lib` folder, including Bootstrap (v5), D3.js (v5), JQuery (v3.5.1), JQuery mark.js (v.9), Google chart, pagination.js (v2.1.5) and plotly (v2.3.0).   
