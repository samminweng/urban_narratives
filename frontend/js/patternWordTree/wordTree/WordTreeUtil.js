class WordTreeUtil {
    // Emoji list https://unicode.org/emoji/charts/full-emoji-list.html#25fd
    static categoryIcons =
        {
            "Space": '\u{1F3DE}',
            "Transport": '\u{1F6B4}',
            "Building": '\u{1F3E2}',
            "People": '\u{1F46A}',
            "Others": ''
        };

    // Return the category name + icon
    static getCategoryLabel(category) {
        return this.capitalize(category) + this.categoryIcons[category];
    }

    // Return the subject + verb label
    static getSubjectVerbLabel(subjectVerb){
        let words = subjectVerb.split("+");
        return this.capitalize(words[0]) + " " + words[1];
    }

// Shuffle the texts
    static shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

// Capitalized the first char
    static capitalize(word) {
        return word.charAt(0).toUpperCase() + word.slice(1);
    }

// Convert the phrase words to a string
    static convertPhraseToString(phrase) {
        return phrase.map(word => word['word']).join(" ");
    }


}
