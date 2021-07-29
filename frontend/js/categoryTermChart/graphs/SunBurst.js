// Plotly sunburst chart
// https://plotly.com/javascript/sunburst-charts/
function SunBurst(categoryTermData, selectedCategory){
    const dataset = categoryTermData.filter(d => d['category'] !== "Others");
    const width = 600, height = 600;
    const infrastructures = {'Hard Infrastructure': ['Building', 'Transport', 'Space' ],
                             'Soft Infrastructure': ['People']}
    const categoryNames = {
        "Space": "Public Space", "Transport": "Transport", "Building": "Building",
        "People": "People & Communities", "Others": "Miscellaneous", 
    };

    const categories = Object.values(categoryNames);
    // console.log(categories);

    const color_map = {
        "Hard Infrastructure": '', "Soft Infrastructure": '#e6550d',
        "Space": "#9ecae1", "Transport": "#31a354",
        "Building": "#756bb1", "People": "#fdae6b",
    };




    let termMaps = {};

    // Convert the data for hierarchical data
    function mapToData() {
        const total = dataset.reduce((acc, cur) => acc += cur['percent'], 0);
        let root = "Share An Idea";
        let labels = [root];
        let parents = [""];
        let values = [];
        let colors = [""];
        let texts = [];
        // Update the percentage of the category
        // console.log(dataset);
        for(let categoryData of dataset){
            categoryData['percent'] = Math.round(categoryData['percent']/total *100);
        }
        
        // console.log(dataset);
        values.push(100);
        for(const [infrastructure, categories] of Object.entries(infrastructures)){
            // Get the inf_percent
            let inf_percent = dataset.filter(c => categories.includes(c['category'])).reduce((acc, cur) => acc += cur['percent'], 0);
            labels.push(infrastructure);
            parents.push(root);
            values.push(inf_percent);
            colors.push(color_map[infrastructure]);
            texts.push(Math.round(inf_percent*total));
            // console.log(infrastructure + ": " + inf_percent);

            for (let category of categories) {
                try {
                    let categoryTerm = dataset.find(c => c['category'] === category);
                    let categoryName = categoryNames[category];
                    // let color = categoryColors[category];
                    let categoryPercent = categoryTerm['percent'];
                    labels.push(categoryName);
                    parents.push(infrastructure);
                    values.push(categoryPercent);
                    colors.push(color_map[category]);
                    texts.push(Math.round(categoryPercent * total));
                    // Add the transport
                    if (category === selectedCategory){
                        console.log(categoryTerm);
                        // reduced the
                        let freqTerms = categoryTerm['terms'].slice(0, 5);
                        // Sum up all the term frequency
                        let freqTotal = freqTerms.reduce((acc, cur) => acc+= cur['freq'], 0);
                        // Add up to category
                        for (let termData of freqTerms){
                            let term = termData['term'];
                            let termPercent = (categoryPercent * termData['freq']) / freqTotal;
                            labels.push(term);
                            parents.push(categoryName);
                            values.push(termPercent);
                            colors.push(color_map[category]);
                            texts.push(termData['freq']);
                            termData['category'] = categoryName;
                            termMaps[term] = termData;
                        }
                    }

                } catch (ex) {
                    console.error(ex.message);
                }
            }
        }
       

        return [labels, parents, values, colors, texts];
    }

    // Capitalised the word
    function capitalize(word) {
        return word.charAt(0).toUpperCase() + word.slice(1);
    }


    function _createUI(){
        const [labels, parents, values, colors, texts] = mapToData();
        let data = [{
            type: "sunburst",
            labels: labels,
            parents: parents,
            values: values,
            text: texts,
            outsidetextfont: {size: 20},
            insidetextfont: {size:16},
            leaf: {opacity: 0.8},
            marker: {line: {width: 5}, colors: colors},
            branchvalues: 'total',
            textinfo: "label",
            hovertemplate: "<b>%{label}</b> appears in <b>%{text}</b> texts <br>" + "<extra></extra>",
        }];

        let layout = {
            margin: {l: 20, r: 0, b: 30, t: 0},
            width: width,
            height: height,
        };
        let chart = document.getElementById('categoryChart');
        chart.style.height = width + "px";
        chart.style.height = height + "px";
        Plotly.newPlot('categoryChart', data, layout, {responsive: true});
        // Add the image of legend
        $('#categoryLegend').empty();
        $('#categoryLegend').append($('<img class="img-fluid" alt="" src="images/categoryTerm/infrastructure_legend.png">'));


        // Click event
        chart.on('plotly_click', function (data) {
            if (data.points.length > 0) {
                // console.log(data.points[0]);
                // data.points[0].data.leaf.opacity = 0.8;
                let label = data.points[0].label;
                if(categories.includes(label)){
                    let category = Object.keys(categoryNames).find(c => categoryNames[c] === label)
                    // console.log(category);
                    $('#categoryChart').empty();
                    let chart = new SunBurst(categoryTermData, category);
                }else if (label in termMaps){
                    let termData = termMaps[label];
                    // console.log(termData);
                    let sentences = termData['sentences'];
                    // Create a word cloud for object phrases
                    let wordCloud = new WordCloud(sentences);
                    // Update the term title
                    $('#termTitle').text("Texts associated with "+ capitalize(label)
                                              +" under "+ termData['category'] + " theme");
                }

            }
        });


    }
    _createUI();

}
