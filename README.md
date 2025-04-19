# Bible Offline Search Application

This repository contains a Python-based offline Bible search application. The main script, `main.py`, provides a graphical user interface (GUI) for searching and exploring the King James Version (KJV) Bible in XML format.

Credit to https://github.com/thiagobodruk/bible for Providing Bibles in easy to read format.

## Features

- **Verse Lookup**: Search for specific Bible verses by providing the book, chapter, and (optionally) the verse.
- **Full Bible Search**: Search for a word or phrase across the entire Bible, with results displayed along with highlighted matches.
- **Autocomplete for Book Names**: Suggests book names as you type, making it easier to input queries.
- **Dynamic GUI**: A user-friendly interface built using the `Tkinter` library for desktop applications.

## How It Works

### File Dependencies
- `en_kjv.xml`: The XML file containing the full text of the King James Version of the Bible. This file is parsed and loaded at runtime.

### Functionalities

#### 1. **Verse Lookup**
   - Input Format: `Book Chapter [Verse]` (e.g., "John 3 16").
   - If a valid book name and chapter (and optionally a verse) are provided, the application displays the corresponding Bible text.
   - If the input is invalid or the requested book/chapter/verse is not found, an error message is shown.

#### 2. **Full Bible Search**
   - Input: Any word or phrase (case-insensitive).
   - Searches the entire Bible for occurrences of the input query.
   - Displays the results with the matching word/phrase highlighted.

#### 3. **Autocomplete Feature**
   - Provides suggestions for book names as you type.
   - Helps ensure that book names are entered correctly.

### GUI Components
- **Verse Search Entry**: An input field for looking up specific verses.
- **Full Bible Search Entry**: An input field for searching the entire Bible for a word or phrase.
- **Output Display**: A text area where the results of the search are displayed, with highlights for matched words/phrases.
- **Error Handling**: User errors (e.g., invalid book names or input formats) are shown as pop-up messages.

### Technologies Used
- **Python Standard Library**:
  - `tkinter`: For building the graphical user interface.
  - `xml.etree.ElementTree`: For parsing the XML representation of the Bible.
- **Dependencies**: Ensure that `en_kjv.xml` is available in the same directory as `main.py`.

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/afrank84/BibleOffline.git
   cd BibleOffline
   ```

2. Ensure that `en_kjv.xml` is in the same directory as `main.py`.

3. Run the application:
   ```bash
   python main.py
   ```

4. Use the interface to:
   - Look up specific verses by entering `Book Chapter [Verse]` in the top input box.
   - Search for words/phrases throughout the Bible using the lower input box.
   - View the results in the output text area.

5. Exit the application by pressing the `Escape` key or closing the window.

## Future Enhancements
- Add support for multiple Bible translations.
- Include additional search filters (e.g., search by testament or book only).
- Improve the user interface with modern GUI libraries (e.g., PyQt or Kivy).
