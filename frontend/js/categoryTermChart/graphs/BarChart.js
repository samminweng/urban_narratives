function BarChart(_termData, _color, _title) {
    const termData = _termData;
    const color = _color;
    const title = _title;
    const MAXLENGTH = 20;
    const width = 500;
    const height = 400;
    let frequentTerms = termData['terms'].slice(0, MAXLENGTH);
    // Reverse the terms
    frequentTerms.sort((t1, t2) => t1['freq'] - t2['freq']);

    // Draw the bar chart
    function drawBarChart() {
        let dataTable = [
            ['Term', 'Frequency', {type: 'string', role: 'tooltip'}]
        ];

        for (let term of frequentTerms) {
            dataTable.push([term['term'], term['freq'],
                " (" + term['freq'] + ")"]);
        }


        // console.log(dataTable);
        let data = google.visualization.arrayToDataTable(dataTable);

        let options = {
            // title: 'Top ' + MAXLENGTH + ' Frequent Term',
            width: width,
            height: height,
            colors: [color],
            // chartArea: {width: '70%', height: '70%'},
            bars: 'horizontal', // Required for Material Bar Charts.
            bar: { groupWidth: '80%' },
            axes: {
                x: {
                    0: { label: 'Frequency', minValue: 0} // Top x-axis
                }
            },
            reverseCategories: true,
            legend: {
                position: 'none'
            },
        };
        let chart = new google.charts.Bar(document.getElementById('termChart'));
        chart.draw(data, options);

        // Add the onclick event
        google.visualization.events.addListener(chart, 'select', () => {
            let selector = chart.getSelection();
            if (selector.length > 0) {
                let row = selector[0]['row'];
                // let category = termData['category'];
                let term = frequentTerms[row];
                let sentences = term['sentences'];
                // Create a word cloud for object phrases
                let wordCloud = new WordCloud(sentences);
            }
        });
    }


    function _createUI() {
        google.charts.load('current', {packages: ['bar']});
        google.charts.setOnLoadCallback(drawBarChart);
        // Clear text list view
        // $('#wordCloud').empty();
        // $('#textList').empty();

        $('#termChartTitle').text(title);

    }

    _createUI();
}
