// Display the category frequency with a tree map using Plotly
function TreeMap(categoryTermData, rootTitle) {
    const dataset = categoryTermData;
    const width = 600, height = 450;
    const categories = ["Space", "Transport", "Building", "People", "Others"];
    const categoryNames = {
        "Space": "Public Space", "Transport": "Transport", "Building": "Building",
        "People": "People and Communities", "Others": "Miscellaneous", "Pronouns": "Pronouns"
    };
    const categoryColors = {
        "Space": "rgb(51, 102, 204)", "Transport": "rgb(255, 127, 14)",
        "Building": "rgb(127, 127, 127)", "People": "rgb(231, 186, 82)",
        "Others": "rgb(102, 170, 0)",
    }
    let termMaps = {};

    console.log(dataset);

    // Convert the data for hierarchical data
    function mapToData() {
        let root = rootTitle;
        let labels = [root];
        let parents = [""];
        let values = [];
        let colors = [""];
        let total = dataset.reduce((acc, cur) => acc += cur['percent'], 0)
        values.push(total);

        for (let category of categories) {
            try {
                let categoryTerm = dataset.find(c => c['category'] === category);
                let parent = categoryNames[category];
                let color = categoryColors[category];
                labels.push(parent);
                parents.push(root);
                values.push(categoryTerm['percent']);
                colors.push(color);
                termMaps[parent] = {data: categoryTerm, color: color};
            } catch (ex) {
                console.error(ex.message);
            }
        }

        return [labels, parents, values, colors];
    }


    function _createUI() {
        const [labels, parents, values, colors] = mapToData();
        $('#categoryChart').empty(); // Clear the chart
        let data = [{
            type: "treemap",
            branchvalues: "total",
            outsidetextfont: {"size": 0},
            labels: labels,
            parents: parents,
            values: values,
            marker: {colors: colors},
            pathbar: {"visible": false},
            textinfo: "label",
            textfont: {size: 18}
        }];
        let layout = {
            width: width,
            height: height,
            margin:{
              l:50,
              r:50,
              t:20,
              b:80
            },
            uniformtext: {
                mode: "show",
                minsize: 12
            }
        };
        let config = {responsive: true};
        let chart = document.getElementById('categoryChart');
        Plotly.newPlot('categoryChart', data, layout, config);

        chart.on('plotly_click', function (data) {
            if (data.points.length > 0) {
                let label = data.points[0].label;
                console.log('clicking on ' + label);
                let termData = termMaps[label];
                let barChart = new BarChart(termData['data'], termData['color'],
                    label + " Theme");
            }
        });


    }


    _createUI();

}
