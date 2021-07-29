// Display a list of story texts
function TextListView(_texts, _words, _isSubject) {
    const texts = _texts;
    const words = _words;
    const isSubject = _isSubject;
    // Container
    function createPagination(storyTable){
        // Create the table
        let pagination = $("<div></div>");
        // Pagination
        pagination.pagination({
            dataSource: function (done) {
                let result = [];
                for (let i = 1; i <= texts.length; i++) {
                    result.push(texts[i - 1]);
                }
                done(result);
            },
            totalNumber: texts.length,
            pageSize: 10,
            showNavigator: true,
            formatNavigator: '<span style="color: #f00"><%= currentPage %></span>/<%= totalPage %> pages, <%= totalNumber %> ideas',
            position: 'top',
            showGoInput: true,
            showGoButton: true,
            callback: function (texts, pagination) {
                storyTable.find('tbody').empty();
                for (let text of texts) {
                    let row = $('<tr class="d-flex"></tr>');
                    let col = $('<td class="col"></td>');
                    let textContainer = $('<div class="container"></div>');
                    // text View
                    let textView = new HighlightTextView(text, words, isSubject);
                    textContainer.append($('<div class="row"></div>').append(textView.getContainer()));
                    col.append(textContainer);
                    row.append(col);
                    storyTable.find('tbody').append(row);
                }
            }
        });
        return pagination;
    }

    function _createUI() {
        $('#textList').empty();
        let container = $('<div></div>');
        let storyTable = $('<table class="table table-striped">' +
            '<tbody></tbody></table>');

        let pagination = createPagination(storyTable);
        // Add the pagination
        container.append(pagination);
        container.append(storyTable);

        $('#textList').append(container);

    }

    _createUI();
}
