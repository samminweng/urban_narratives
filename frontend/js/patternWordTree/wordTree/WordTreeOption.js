class WordTreeOption {
    constructor(){
        this.width = 600;
        this.height = 600;
        this.margin = 10;
        $("#wordTreeChart").width(this.width).height(this.height).addClass("container");
        // Pass the phrase tree data to Google Word Tree chart
        this.options = {
            maxFontSize: 24,
            wordtree: {
                format: 'explicit',
                type: 'suffix',
                // fontName: 'Segoe UI Emoji',
                // forceIFrame: true,
                // height: this.height - this.margin,
                width: this.width - this.margin,
            }
        };

    }

    get Options(){
        return this.options;
    }

}
