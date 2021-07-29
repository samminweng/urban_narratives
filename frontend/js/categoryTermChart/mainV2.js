'use strict';
const rootTitle = {'commonThemes': 'Shared An Idea', 'HamiltonIdeas': 'Hamilton Public Places Policy'}
const titles = {"HamiltonIdeas" : "Hamilton Citizen Space", "commonThemes": "Christchurch Common Urban Themes"}
// Document ready function
$(function () {
    let corpus = 'commonThemes';    // let corpus = 'HamiltonIdeas';
    let category = 'Transport';
    // Get the query string of a URL
    // https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams
    let urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('corpus')){
        corpus = urlParams.get('corpus');
    }else if (urlParams.has('category')){
        category = urlParams.get('category');
    }

    let categoryTermFile = 'data/categoryTerm/'+ corpus +'/categoryTerm.json';

    // Load patterns
    $.when(
        $.getJSON(categoryTermFile, {format: "json"})
    ).done(function (data) {
        const categoryTermData = data;
        // console.log(categoryTermData);
        $.when(new SunBurst(categoryTermData, category)).done(function(){
            // alert("Finished");
            $("#progress").empty();
        });
        // $.when(new TreeMap(categoryTermData, rootTitle[corpus])).done(function(){
        //     // alert("Finished");
        //     $("#progress").empty();
        // });


        // Update the title
        $("#categoryChartTitle").text(titles[corpus]);

    });
});
