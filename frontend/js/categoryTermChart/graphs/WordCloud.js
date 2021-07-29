// Reference link: https://bl.ocks.org/da1fujimoto/41f76b4961813d29ddfc872ad342377f
function WordCloud(_sentences) {
    const sentences = _sentences.filter(sentence => sentence['object_phrase_cloud'].length > 0);
    const margin = {
        top: 5,
        right: 10,
        bottom: 5,
        left: 10
    };
    const width = 550 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const color = d3.scaleSequential().interpolator(d3.interpolateOranges);
    function mapObjectPhraseCloud() {
        let phraseMap = new Map();// key: words, value: a list of sentences
        for (let sentence of sentences) {
            for (let objectPhrase of sentence['object_phrase_cloud']) {
                // console.log(objectPhrase);
                let phrase = objectPhrase['lemmaWords'];
                if (phrase !== "") {
                    if (!phraseMap.has(phrase)) {
                        phraseMap.set(phrase, new Set())
                    }
                    phraseMap.get(phrase).add(sentence);
                }
            }
        }
        let data = [];
        let maxCount = 0
        for (const [word, sentences] of phraseMap) {
            data.push({"word": word, "sentences": [...sentences]});
            if(sentences.length> maxCount){
                maxCount = sentences.length;
            }
        }
        // console.log(data);
        // Set up the domain of the color based on the max counts
        color.domain([99, 10*maxCount]);

        return data;
    }


    function _createUI() {
        $('#wordCloud').empty();
        $('#textList').empty();
        let data = mapObjectPhraseCloud();
        // console.log(data);
        // Create a SVG
        const svg = d3.select("#wordCloud").append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .append("g")
                      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        const wordcloud = svg.append("g")
            .attr('class', 'wordcloud')
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

        svg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + height + ")")
            .selectAll('text')
            .style('font-size', '20px')
            .style('fill', d => color(d))
            .style('font-family', 'sans-serif');

        const draw = words => {
            wordcloud.selectAll("text")
                .data(words)
                .enter().append("text")
                .attr('class', 'word')
                .style("padding", 5)
                .style("fill", (d, i) => color(i))
                .style("font-size", d => d.size + "px")
                .style("font-family", d => d.font)
                .attr("text-anchor", "middle")
                .attr("transform", d => "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")")
                // .attr("transform", d => "translate(" + [d.x, d.y] + ")")
                .text(d => d.text)
                .on("click", function (d, i, j) {
                    // Update the heading
                    $('#textList').empty();
                    // Create the list of texts
                    let textListView = new TextListView(d['sentences'], d['word']);
                });
        };

        const layout = d3.layout.cloud()
            .size([width, height])
            .timeInterval(20)
            .words(data)
            .rotate(function(d) { return 0; })
            .fontSize((d, i) => {
                let size = (d['sentences'].length - 1) * 30 + 20;
                return size;
            })
            .fontWeight(["bold"])
            .text(d => d.word === 'cbd' ? 'CBD': d.word)
            .spiral("rectangular") // "archimedean" or "rectangular"
            .on("end", draw)
            .start();
        //

    }

    _createUI();
}
