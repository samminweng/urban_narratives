'use strict';

function WordTree(_patterns) {
    const patterns = _patterns;
    const displayCategories = {
        "Space": "Public Space",
        "Building": "Building",
        "Transport": "Transport",
        "People": "People and Communities"
    }
    // The matcher for the word and phrases
    let textMap = {
        'I/We': [],         // An array of sentences
        'Verb': new Map(), // Key: subject verb, values: a list of sentences
        'Category': new Map(), // key: category (Space, Transport, Building, People), values: an list of sentences
        'Term': new Map(),        // Key: term, values : a list of sentences
        'ObjectPhrase': new Map()// key: phrase word, value: a list of sentences
    }

    // Populate an array of data for word tree
    function populateTreeTable() {
        // Main entry of the function
        let treeData =
            [
                ['id', 'childLabel', 'parent', 'weight', {role: 'style'}],
                [0, 'I/We', -1, 1, 'black'] // Root: subject
            ];
        let id = 0;
        let rootId = id;
        let allSentences = [];
        for (const pattern of patterns) {
            const verb = pattern['title'].replace("I/We ", "");
            // Add the verb to tree data
            treeData.push([++id, verb, rootId, 1, 'black']);
            let verbSentences = [];
            const pId = id;
            for (const category of pattern['categories']) {
                // Add the category to tree data
                treeData.push([++id, displayCategories[category['category']], pId, 1, 'blue']);
                let categorySentences = [];
                const cId = id;
                try {
                    // Add the term to tree data
                    for (const [term, sentences] of Object.entries(category['terms'])) {
                        // Add the term to tree data
                        treeData.push([++id, term, cId, 1, 'black']);
                        textMap['Term'].set(term+":"+sentences.length, sentences);
                        const tId = id;
                        for(const sentence of sentences){
                            // Add the object phrases
                            const objectPhrase = sentence['objectPhrase'].map(w => w['word']).join(" ")
                            treeData.push([++id, objectPhrase, tId, 1, 'green']);
                            textMap['ObjectPhrase'].set(objectPhrase+":1", [sentence]);
                        }
                        categorySentences = categorySentences.concat(sentences);
                    }
                } catch (err) {
                    console.error(err);
                }
                textMap['Category'].set(displayCategories[category['category']]+":"+categorySentences.length, categorySentences);
                verbSentences = verbSentences.concat(categorySentences);
            }
            textMap['Verb'].set(verb+":"+verbSentences.length, verbSentences);
            allSentences = allSentences.concat(verbSentences);
        }
        textMap['I/We'] = allSentences;
        // console.log(textMap);
        // console.log(treeTable);
        return treeData;
    }


    // Draw google word tree
    function drawChart() {
        // Main entry of 'drawChart' function
        $('#wordTreeChart').empty();
        let treeData = populateTreeTable();
        let treeTable = new google.visualization.arrayToDataTable(treeData);
        let treeOption = new WordTreeOption();
        let treeChart = new google.visualization.WordTree(document.getElementById('wordTreeChart'));
        treeChart.draw(treeTable, treeOption.Options);
        // Register the select event
        google.visualization.events.addListener(treeChart, 'select', function (d) {
            let selector = treeChart.getSelection();
            console.log(selector);
            // let words = selector.word.toLowerCase();
            let word = selector.word;
            let weight = selector.weight;
            let key = word + ":" + weight;
            if (word === 'I/We') {
                new TextListView(textMap[word]);// Display the all stories
            }else if (textMap['Verb'].has(key)) {
                new TextListView(textMap['Verb'].get(key));// Display the all stories
            } else if (textMap['Category'].has(key)) {
                new TextListView(textMap['Category'].get(key));// Display the all stories
            } else if (textMap['Term'].has(key)) {
                new TextListView(textMap['Term'].get(key));
            } else if (textMap['ObjectPhrase'].has(key)) {
                new TextListView(textMap['ObjectPhrase'].get(key));
            }
            return false;
        });
        new TextListView(textMap["I/We"]);// Display the all stories
    }

    function _createUI() {
        // // Create the google chart onload event
        google.charts.load('current', {packages: ['wordtree']});
        google.charts.setOnLoadCallback(drawChart);
    }

    _createUI();
}


