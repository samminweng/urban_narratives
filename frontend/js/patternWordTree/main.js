'use strict';
const patternFile = 'data/pattern/patterns.json';
// Document ready function
$(function () {
    // Load patterns
    $.when(
        $.getJSON(patternFile, {format: "json"})
    ).done(function (data) {
        const patterns = data;
        console.log(patterns);
        $.when(new WordTree(patterns)).done(function(){
            $("#progress").empty();
        });
    });
});
