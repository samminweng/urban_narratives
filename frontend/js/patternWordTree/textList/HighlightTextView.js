'use strict';

// Create a story div and highlight the words
function HighlightTextView(_text, _words, _isSubject) {
    const text = _text;
    const words = _words;
    const isSubject = _isSubject;
    // The container
    let container = $('<div></div>');
    this.getContainer = function () {
        return container;
    };

    // Get the pattern
    function getWordPatternV2(targetWord) {
        const sentenceWords = text['sentence'];
        let previousWord = sentenceWords.find(word => word['id'] === targetWord['id'] - 1);
        let nextWord = sentenceWords.find(word => word['id'] === targetWord['id'] + 1);
        let pattern = '';
        if (previousWord) {
            if (previousWord['ud'] === 'punct') {
                pattern = '(?<=\\' + previousWord['word'] + '\\s*)';
            } else {
                pattern = '(?<=' + previousWord['word'] + '\\s*)';
            }
        }
        pattern += targetWord['word']

        // Get the next word and use 'Lookbehind assertion' regular expression
        // x(?=y) Matches "x" only if "x" is preceded by "y".
        // Ref: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions/Assertions
        if (nextWord) {// Match the word using lookahead assertion
            if (nextWord['ud'] === 'punct') {
                // Escape char before the punctuation is needed
                pattern += '\\s*\\' + nextWord['word'];
            } else {
                // Check if the next word is like an abbreviation such as 'd 've
                if (nextWord['word'].includes("'")) {
                    // Match the word (without white space before the next word) using lookahead assertion
                    pattern += '(?=' + nextWord['word'] + ')';// Space before the next word is needed
                } else {
                    // Match the word using lookahead assertion
                    pattern += '(?=\\s*' + nextWord['word'] + ')';// Space before the next word is needed
                }
            }
        }
        return pattern;
    }

    // Highlight a word with NRC color palette or subject
    function highlightWord(targetWord, className, textContainer) {
        let pattern = getWordPatternV2(targetWord);
        // console.log(pattern);
        try {
            let regex = new RegExp(pattern, 'i');
            // Add Bootstrap tooltip
            textContainer.markRegExp(regex, {
                "className": className,
                "ignoreGroups": 0,
                "acrossElements": true, // Search through the element so that "supermarket owner" can be highlight
                "noMatch": function (term) {
                    console.error(term + " has no match.");
                    // term is the not found term
                },
                "filter": function (textNode, foundTerm, totalCounter) {
                    // textNode is the text node which contains the found term
                    // foundTerm is the found search term
                    // totalCounter is a counter indicating the total number of all marks
                    //              at the time of the function call
                    // console.log("foundTerm = ", foundTerm, " totalCounter = ", totalCounter);
                    return true; // must return either true or false
                },
                "each": function (node) {
                    // let title = taggedNLPWord['word'] + '_' + taggedNLPWord['pos'] + ': ' + taggedNLPWord['ud']
                    //     + '(' + taggedNLPWord['head'] + ', ' + taggedNLPWord['word'] + '-' + taggedNLPWord['id'] + ')';
                    // // Add tooltip to each element, e.g. data-toggle="tooltip" data-placement="top" title="Tooltip on top"
                    // node.setAttribute("data-toggle", "tooltip");
                    // node.setAttribute("data-html", "true");
                    // node.setAttribute("title", title);
                },
                done: function () {

                }
            });
        } catch (e) {
            console.error("error:" + pattern);
        }

    }


    // Highlight the dependent/head word goes through each nlp_tagged result of the story
    // The words that has dependencies to the subject: 1) the word is the subject 2) the word whose head word is the subject
    // The noun phrases are also highlight.
    function _createUI() {

        // Story div displays the texts and highlights the dependent words related to subject
        let textDiv = new TextView(text);// Tag the story text with entities
        let textContainer = textDiv.getContainer();
        // Get the subject phrase
        let subjectPhrase = text['subjectPhrase'];


        // Highlight the subject words
        for (let subjectWord of subjectPhrase) {
            highlightWord(subjectWord, "keyword", textContainer);
        }
        let verbWord = text['verb'];
        // Filter out subject phrases from object phrases
        highlightWord(verbWord, "keyword", textContainer);
        // Highlight the object phrase
        let objectPhrase = text['objectPhrase'];
        // console.log(words);
        // Highlight the object terms if needed
        let objectTerm = text['objectCategory']['term'];
        // console.log(objectTerm);
        highlightWord(objectTerm, "object-Term", textContainer);
        objectPhrase = objectPhrase.filter(word => word['id'] !== objectTerm['id']);

        let subjectIds = subjectPhrase.map(word => word['id']);
        objectPhrase = objectPhrase.filter(word => !subjectIds.includes(word['id']));
        // Filter out verbs
        objectPhrase = objectPhrase.filter(word => word['id'] !== verbWord['id']);
        // highlight the object phrase without term word
        for (let word of objectPhrase) {
            highlightWord(word, "phrase", textContainer);
        }

        container.append(textContainer);
    }

    _createUI();
}

