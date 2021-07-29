'use restrict';

// Create a div to display the sentence
function TextView(_text) {
    const text = _text;
    let container = $('<div> "' + text['sentence'].map(word => word['word']).join(" ") + '"</div>');
    this.getContainer = function () {
        return container;
    };
}
