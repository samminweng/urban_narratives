function CircleChart(categoryTermData) {
    const dataset = categoryTermData;
    const width = 600, height = 400;
    const PronounColor = '#1f77b4';
    const BubbleColor = '#ddd';
    const SelectedColor = '#ff7f0e';

    const color = function (d) {
        let parents = d.ancestors();
        if (parents && parents.find(p => p.data.name === "Pronouns")) {
            return PronounColor;
        }
        return d.children ? "none" : BubbleColor;
    }


    const pack = function (data) {
        return d3.pack()
            .size([width, height])
            .padding(3)
            (d3.hierarchy(data)
                .sum(d => d.value)
                .sort((a, b) => b.value - a.value));
    }


    // Create the data for circle chart
    function mapDatasetToData() {

        let data = {name: "root", children: [], type: "root"};
        for (let categoryTerm of dataset) {
            try{
                if (categoryTerm['category'] === "Pronouns") {
                    let childNodes = []
                    for (let objectPhrase of categoryTerm['objects']) {
                        childNodes.push({
                            name: objectPhrase['category'], value: objectPhrase['percent'],
                            terms: objectPhrase, type: "object"
                        })
                    }
                    data.children.push({name: categoryTerm['category'], children: childNodes, type: "pronouns"})
                } else {
                    data.children.push({
                        name: categoryTerm['category'], value: categoryTerm['percent'],
                        terms: categoryTerm, type: "subject"
                    });
                }
            }catch(ex){
                console.error(ex.message);
            }

        }
        return data;
    }


    function _createUI() {
        let data = mapDatasetToData();
        const root = pack(data);
        // console.log(root);
        $("#categoryChart").empty();    // Clear the bubble chart
        // console.log(dataset['objectPhrases']);
        const svg = d3.select("#categoryChart").append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .style("overflow", "visible")
            .attr("text-anchor", "middle");
        const node = svg.append("g")
            .attr("pointer-events", "all")
            .selectAll("g")
            .data(root.descendants())
            .join("g")
            .attr("transform", d => `translate(${d.x},${d.y})`);

        node.append("circle")
            .attr("class", "circle")
            .attr("r", d => d.r)
            .attr("stroke", d => d.children ? "#bbb" : "none")
            .attr("fill", d => color(d))
            .style("opacity", d => {
                let parents = d.ancestors();
                if (parents && parents.find(p => p.data.name === "Pronouns")) {
                    return 0.2;
                }
                return 1;
            }).on("click", function (d, i, j) {
            if (d.data.terms) {
                // // Reset all the circles to BubbleColor
                d3.selectAll(".circle").style("fill", function (c) {
                    return color(c);
                });
                let selected = d3.select(this).node();
                // console.log(selected);
                selected.style.setProperty("fill", SelectedColor);

                const termData = d.data.terms;
                const isSubject = d.data.type === "subject";
                // console.log(termData);
                let barChart = new BarChart(termData, isSubject);
            }
        }).append("svg:title")
            .text(function(d){
                let category = d.data.name !== "Pronouns" ? d.data.name : "I/We/You";
                if("value" in d.data){
                    return category + " (" + d.data.value.toFixed(1) + "%)"
                }
                return category;
            } );

        const leafs = node.filter(d => d.data.type === "subject" || d.data.type === "object");
        leafs.append("text")
            .selectAll("tspan")
            .data(d => [d])
            .join("tspan")
            .attr("x", 0)
            .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 0.8}em`)
            .attr("class", d => {
                if(d.data.name === "Others"){
                    return " others";
                }
                if (d.data.type === "subject") {
                    return "category";
                }else if (d.data.type === "object"){
                    if(d.data.name === "Others"){
                        return " others subCategory";
                    }
                    return "subCategory";
                }
            })

            .on("click", function (d, i, j) {
                if (d.data.terms) {
                    // // Reset all the circles to BubbleColor
                    d3.selectAll(".circle").style("fill", function (c) {
                        return color(c);
                    });
                    let selected = d3.select(this.parentNode.parentNode).selectAll(".circle").node();
                    // console.log(selected);
                    selected.style.setProperty("fill", SelectedColor);
                    const termData = d.data.terms;
                    const isSubject = d.data.type === "subject";
                    let barChart = new BarChart(termData, isSubject);
                }
            })
            .text(function (d) {
                // console.log(d);
                return d.data.name;
            }).append("svg:title")
            .text(function(d){
                let category = d.data.name !== "Pronouns" ? d.data.name : "I/We/You";
                if("value" in d.data){
                    return category + " (" + d.data.value.toFixed(1) + "%)"
                }
                return category;
            } );


        // Add the pronoun
        const parent = node.filter(d => {
            // console.log(d);
            return d.data.name === "Pronouns";
        });
        parent.append("text").append("tspan")
            .attr("x", 0)
            // .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 0.8}em`)
            .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 2.5}em`)
            .attr("class", "category")
            .text(d => "I / We / You");

        return;
    }

    _createUI();
}
