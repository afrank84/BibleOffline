import os
import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET

# Function to display error messages with copy-to-clipboard functionality
def show_error_with_copy(title, message):
    def copy_to_clipboard():
        root_win.clipboard_clear()
        root_win.clipboard_append(message)
        root_win.update()  # Keep the clipboard content after the window is closed
        messagebox.showinfo("Copied", "Error message copied to clipboard.")
    
    error_window = tk.Toplevel(root_win)
    error_window.title(title)
    error_window.geometry("400x200")
    error_window.resizable(False, False)

    error_label = tk.Label(error_window, text=message, wraplength=380, justify="left", font=("Helvetica", 12))
    error_label.pack(pady=10, padx=10)

    copy_button = tk.Button(error_window, text="Copy to Clipboard", command=copy_to_clipboard, font=("Helvetica", 12))
    copy_button.pack(pady=10)

    close_button = tk.Button(error_window, text="Close", command=error_window.destroy, font=("Helvetica", 12))
    close_button.pack(pady=10)

# GUI setup
root_win = tk.Tk()
root_win.title("Franks Super Cool Bible Search Thingy!")
root_win.geometry("1920x1080")
root_win.resizable(True, True)

# Function to toggle split-screen mode
def toggle_split_screen():
    global right_frame, right_output_text, right_version_var, right_version_dropdown, right_book_lookup
    try:
        if right_frame:
            paned_window.forget(right_frame)
            right_frame = None
        else:
            # Create the right frame and add it to the paned window
            right_frame = tk.Frame(paned_window, width=960, height=1080)
            paned_window.add(right_frame)

            # Prevent the frame from shrinking to fit its contents
            right_frame.pack_propagate(False)

            # Create an inner frame with padding
            inner_frame = tk.Frame(right_frame)
            inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Add a spacer to push dropdown down
            spacer = tk.Frame(inner_frame, height=229)
            spacer.pack()

            # Dropdown for the right side
            right_version_var = tk.StringVar(value=default_display)
            right_version_dropdown = tk.OptionMenu(inner_frame, right_version_var, *dropdown_options, command=on_version_change_right)
            right_version_dropdown.config(font=("Helvetica", 16))
            right_version_dropdown.pack(fill=tk.X, pady=(0, 10))

            # Output text for the right side
            right_output_scrollbar = tk.Scrollbar(inner_frame)
            right_output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            right_output_text = tk.Text(inner_frame, wrap=tk.WORD, font=("Georgia", 18), yscrollcommand=right_output_scrollbar.set)
            right_output_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            right_output_scrollbar.config(command=right_output_text.yview)


            # Synchronize the right side with the current state of the left side
            current_query = search_entry.get().strip()
            if current_query:
                parts = current_query.split()
                if len(parts) in [2, 3]:
                    book_name = parts[0]
                    chapter = parts[1]
                    verse = parts[2] if len(parts) == 3 else None
                    synchronize_right_side(book_name, chapter, verse)
    except Exception as e:
        print(f"Toggle error: {e}")

# Create a menu bar
menu_bar = tk.Menu(root_win)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Translation", command=lambda: messagebox.showinfo("File", "Open Translation clicked"))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root_win.destroy)
menu_bar.add_cascade(label="File", menu=file_menu)

# View menu
view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Toggle Split Screen", command=toggle_split_screen)
menu_bar.add_cascade(label="View", menu=view_menu)

# About menu
about_menu = tk.Menu(menu_bar, tearoff=0)
about_menu.add_command(label="Version", command=lambda: messagebox.showinfo("Version", "Bible Offline\nVersion 1.0"))
menu_bar.add_cascade(label="About", menu=about_menu)

# Attach the menu bar to the root window
root_win.config(menu=menu_bar)

# Create a PanedWindow for split-screen functionality
paned_window = tk.PanedWindow(root_win, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# Left frame for the main content
left_frame = tk.Frame(paned_window, width=960, height=1080)
paned_window.add(left_frame)

# Function to load and parse the selected Bible translation
def load_translation(file_name):
    global tree, root, book_names, book_lookup
    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
        book_names = [b.get('n') for b in root.findall('b')]
        book_lookup = {name.lower(): b for name, b in zip(book_names, root.findall('b'))}
        if 'search_entry' in globals():
            search_entry.book_list = sorted(book_names)
        messagebox.showinfo("Success", f"Loaded translation: {os.path.basename(file_name)}")
    except Exception as e:
        show_error_with_copy("Error", f"Failed to load translation: {file_name}\n{e}")

# Populate dropdown menu with available translations
def on_version_change(selected_version):
    if selected_version:
        load_translation(os.path.join("xml", selected_version))

translation_files = [f for f in os.listdir("xml") if f.endswith(".xml")]
if "en_kjv.xml" in translation_files:
    default_translation = "en_kjv.xml"
else:
    default_translation = translation_files[0] if translation_files else None

if not default_translation:
    show_error_with_copy("Error", "No translations found in the 'xml' folder.")
    exit()

# Translation display names mapping
translation_display_names = {
    "ar_svd.xml": "Arabic – Smith & Van Dyke",
    "de_schlachter.xml": "German – Schlachter",
    "el_greek.xml": "Greek – Greek Bible",
    "en_bbe.xml": "English – Bible in Basic English",
    "en_kjv.xml": "English – King James Version",
    "eo_esperanto.xml": "Esperanto – Esperanto Bible",
    "es_rvr.xml": "Spanish – Reina-Valera",
    "fi_finnish.xml": "Finnish – Finnish Bible",
    "fi_pr.xml": "Finnish – Finnish PR Translation",
    "fr_apee.xml": "French – APEE (Louis Segond)",
    "fr_bbe.xml": "French – Bible en français courant",
    "ko_ko.xml": "Korean – Korean Bible",
    "pt_aa.xml": "Portuguese – Almeida Atualizada",
    "pt_acf.xml": "Portuguese – Almeida Corrigida Fiel",
    "pt_nvi.xml": "Portuguese – Nova Versão Internacional",
    "ro_cornilescu.xml": "Romanian – Cornilescu",
    "ru_synodal.xml": "Russian – Synodal Translation",
    "vi_vietnamese.xml": "Vietnamese – Vietnamese Bible",
    "zh_cuv.xml": "Chinese – Chinese Union Version",
    "zh_ncv.xml": "Chinese – New Chinese Version",
}

# Create mapping from display names to filenames
display_to_filename = {v: k for k, v in translation_display_names.items()}
dropdown_options = sorted([translation_display_names.get(f, f) for f in translation_files])

# Default selection display
default_display = translation_display_names.get(default_translation, default_translation)
version_var = tk.StringVar(value=default_display)

def on_version_change_display(display_name):
    selected_file = display_to_filename.get(display_name, display_name)
    on_version_change(selected_file)

# Initialize right_frame globally
right_frame = None

# Global variables for the right panel's translation data
right_tree = None
right_root = None
right_book_lookup = {}  # Initialize right_book_lookup as an empty dictionary

# Function to load and parse the selected Bible translation for the right panel
def load_translation_right(file_name):
    global right_tree, right_root, right_book_lookup
    try:
        right_tree = ET.parse(file_name)
        right_root = right_tree.getroot()
        right_book_lookup = {b.get('n').lower(): b for b in right_root.findall('b')}  # Populate right_book_lookup
        messagebox.showinfo("Success", f"Loaded right panel translation: {os.path.basename(file_name)}")
    except Exception as e:
        show_error_with_copy("Error", f"Failed to load translation for the right panel: {file_name}\n{e}")

# Function to handle version change on the right side
def on_version_change_right(display_name):
    selected_file = display_to_filename.get(display_name, display_name)
    load_translation_right(os.path.join("xml", selected_file))  # Load the selected translation for the right panel
    # Trigger a search to update the right panel
    current_query = search_entry.get().strip()
    if current_query:
        parts = current_query.split(maxsplit=2)
        if len(parts) >= 2:
            book_name = parts[0]
            chapter_and_verse = parts[1]
            verse = None
            if ":" in chapter_and_verse:
                chapter, verse = chapter_and_verse.split(":", 1)
            else:
                chapter = chapter_and_verse
            synchronize_right_side(book_name, chapter, verse)

# Function to synchronize the right side with the left side's search
def synchronize_right_side(book_name, chapter, verse=None):
    if "right_output_text" not in globals():
        return  # Right panel not active

    right_output_text.delete(1.0, tk.END)

    # Validate chapter and verse
    if not chapter.isdigit() or (verse and not verse.isdigit()):
        right_output_text.insert(tk.END, "Invalid chapter or verse format.")
        return

    # Get the selected file for the right panel dropdown
    selected_display = right_version_var.get()
    selected_file = display_to_filename.get(selected_display, selected_display)
    try:
        # Lazy-load the right panel's translation data
        right_tree = ET.parse(os.path.join("xml", selected_file))
        right_root = right_tree.getroot()
        right_book_lookup = {b.get('n').lower(): b for b in right_root.findall('b')}
    except Exception as e:
        right_output_text.insert(tk.END, f"Error loading translation: {e}")
        return

    book_name = book_name.lower()
    if book_name not in right_book_lookup:
        right_output_text.insert(tk.END, f"No book named '{book_name}' found in the selected translation.")
        return

    book = right_book_lookup[book_name]
    chapter_elem = book.find(f"./c[@n='{chapter}']")
    if chapter_elem is None:
        right_output_text.insert(tk.END, f"Chapter {chapter} not found in {book_name}.")
        return

    if verse:
        # Search for the specific verse
        verse_elem = chapter_elem.find(f"./v[@n='{verse}']")
        if verse_elem is not None:
            right_output_text.insert(tk.END, f"{book_name} {chapter}:{verse} — {verse_elem.text}")
        else:
            right_output_text.insert(tk.END, f"Verse {verse} not found in {book_name} {chapter}.")
    else:
        # Display all verses in the chapter
        for v in chapter_elem.findall('v'):
            right_output_text.insert(tk.END, f"{book_name} {chapter}:{v.get('n')} — {v.text}\n\n")

# Modified lookup_verse to remove normalization logic
def lookup_verse():
    query = search_entry.get().strip()
    parts = query.split(maxsplit=2)  # Split into at most 3 parts: book, chapter[:verse], and extra

    if len(parts) < 2:
        messagebox.showerror("Invalid Input", "Use format: Book Chapter[:Verse]")
        return

    book_name = parts[0].lower()
    chapter_and_verse = parts[1]
    verse = None

    # Handle chapter and verse separated by a colon
    if ":" in chapter_and_verse:
        chapter, verse = chapter_and_verse.split(":", 1)
    else:
        chapter = chapter_and_verse

    # Validate chapter and verse
    if not chapter.isdigit() or (verse and not verse.isdigit()):
        messagebox.showerror("Invalid Input", "Chapter and verse must be numeric.")
        return

    # Check if the book exists in the lookup table
    if book_name not in book_lookup:
        messagebox.showerror("Not Found", f"No book named '{book_name}'")
        return

    book = book_lookup[book_name]
    chapter_elem = book.find(f"./c[@n='{chapter}']")
    if chapter_elem is None:
        messagebox.showerror("Not Found", f"Chapter {chapter} not found in {book_name}")
        return

    # Clear the left panel output
    output_text.delete(1.0, tk.END)

    if verse:
        # Search for the specific verse
        verse_elem = chapter_elem.find(f"./v[@n='{verse}']")
        if verse_elem is not None:
            output_text.insert(tk.END, f"{book_name} {chapter}:{verse} — {verse_elem.text}")
        else:
            messagebox.showerror("Not Found", f"Verse {verse} not found in {book_name} {chapter}")
    else:
        # Display all verses in the chapter
        for v in chapter_elem.findall('v'):
            output_text.insert(tk.END, f"{book_name} {chapter}:{v.get('n')} — {v.text}\n\n")

    # Synchronize the right side
    synchronize_right_side(book_name, chapter, verse)

# Search function
def search_whole_bible():
    query = full_search_entry.get().strip().lower()
    if not query:
        messagebox.showerror("Empty Search", "Please enter a word or phrase to search.")
        return

    results_count = 0  # Initialize results counter
    output_text.delete(1.0, tk.END)
    output_text.tag_config("highlight", background="yellow", foreground="black")

    # Clear right panel output if active
    if "right_output_text" in globals() and right_output_text:
        right_output_text.delete(1.0, tk.END)
        right_output_text.tag_config("highlight", background="yellow", foreground="black")

    # Search in the left panel's translation
    for book in root.findall('b'):
        book_name = book.get('n')
        for chapter in book.findall('c'):
            chapter_num = chapter.get('n')
            for verse in chapter.findall('v'):
                verse_text = verse.text
                if query in verse_text.lower():
                    results_count += 1  # Increment results counter
                    result_line = f"{book_name} {chapter_num}:{verse.get('n')} — {verse_text}\n\n"
                    start_index = output_text.index(tk.INSERT)
                    output_text.insert(tk.END, result_line)
                    end_index = output_text.index(tk.INSERT)

                    # Highlight all matches in the inserted line
                    line_lower = result_line.lower()
                    idx = 0
                    while True:
                        idx = line_lower.find(query, idx)
                        if idx == -1:
                            break
                        tag_start = f"{start_index}+{idx}c"
                        tag_end = f"{start_index}+{idx+len(query)}c"
                        output_text.tag_add("highlight", tag_start, tag_end)
                        idx += len(query)

    # Search in the right panel's translation if active
    if "right_root" in globals() and right_root:
        for book in right_root.findall('b'):
            book_name = book.get('n')
            for chapter in book.findall('c'):
                chapter_num = chapter.get('n')
                for verse in chapter.findall('v'):
                    verse_text = verse.text
                    if query in verse_text.lower():
                        results_count += 1  # Increment results counter
                        result_line = f"{book_name} {chapter_num}:{verse.get('n')} — {verse_text}\n\n"
                        right_start_index = right_output_text.index(tk.INSERT)
                        right_output_text.insert(tk.END, result_line)
                        right_end_index = right_output_text.index(tk.INSERT)

                        # Highlight matches in the right panel
                        right_line_lower = result_line.lower()
                        right_idx = 0
                        while True:
                            right_idx = right_line_lower.find(query, right_idx)
                            if right_idx == -1:
                                break
                            right_tag_start = f"{right_start_index}+{right_idx}c"
                            right_tag_end = f"{right_start_index}+{right_idx+len(query)}c"
                            right_output_text.tag_add("highlight", right_tag_start, right_tag_end)
                            right_idx += len(query)

    # Display "No results found" if no matches in either panel
    if results_count == 0:
        output_text.insert(tk.END, "No results found.")
        if "right_output_text" in globals() and right_output_text:
            right_output_text.insert(tk.END, "No results found.")

    # Update the results count label
    results_label.config(text=f"Total Results: {results_count}")
    results_label.pack()

# Add a label to display the total number of results
results_label = tk.Label(left_frame, text="Total Results: 0", font=("Helvetica", 16))
results_label.pack(padx=20, anchor='w')

class AutocompleteEntry(tk.Entry):
    def __init__(self, book_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.book_list = sorted(book_list)
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace_add("write", self.on_change)

        self.listbox = None

    def on_change(self, *args):
        typed = self.var.get()
        if not typed:
            self.hide_listbox()
            return

        matches = [book for book in self.book_list if book.lower().startswith(typed.lower())]
        if matches:
            self.show_listbox(matches)
        else:
            self.hide_listbox()

    def show_listbox(self, matches):
        if self.listbox:
            self.listbox.destroy()
        self.listbox = tk.Listbox(root_win, height=min(6, len(matches)), font=("Helvetica", 20), width=25)
        self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
        for match in matches:
            self.listbox.insert(tk.END, match)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def hide_listbox(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def on_select(self, event):
        if not self.listbox:
            return
        selection = self.listbox.get(self.listbox.curselection())
        self.var.set(selection)
        self.hide_listbox()
        self.icursor(tk.END)

# Label and Verse Lookup Entry (Book Chapter [Verse])
verse_label = tk.Label(left_frame, text="Verse Lookup (e.g., John 3:16)", font=("Helvetica", 16))
verse_label.pack(padx=20, anchor='w')

search_entry = AutocompleteEntry([], left_frame, font=("Helvetica", 20))  # Initialize with an empty list
search_entry.insert(0, " ")
search_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
search_entry.bind("<Return>", lambda e: lookup_verse())

# Label and Full Bible Search Entry
full_search_label = tk.Label(left_frame, text="Search Entire Bible for Word/Phrase", font=("Helvetica", 16))
full_search_label.pack(padx=20, anchor='w')

full_search_entry = tk.Entry(left_frame, font=("Helvetica", 20))
full_search_entry.insert(0, " ")
full_search_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
full_search_entry.bind("<Return>", lambda e: search_whole_bible())

# Add a button to toggle split-screen mode
split_screen_button = tk.Button(left_frame, text="Toggle Split Screen", font=("Helvetica", 16), command=toggle_split_screen)
split_screen_button.pack(pady=10)

# Update dropdown menu for Bible version selection
version_label = tk.Label(left_frame, text="Select Bible Version", font=("Helvetica", 16))
version_label.pack(padx=20, anchor='w')

version_dropdown = tk.OptionMenu(left_frame, version_var, *dropdown_options, command=on_version_change_display)
version_dropdown.config(font=("Helvetica", 16))
version_dropdown.pack(fill=tk.X, padx=20, pady=(0, 10))

# Add a scrollbar to the output_text widget
output_frame = tk.Frame(left_frame)
output_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

output_scrollbar = tk.Scrollbar(output_frame)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(output_frame, wrap=tk.WORD, font=("Georgia", 18), yscrollcommand=output_scrollbar.set)
output_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

output_scrollbar.config(command=output_text.yview)

# Load the default translation from the xml folder
load_translation(os.path.join("xml", default_translation))

root_win.bind("<Escape>", lambda e: root_win.destroy())

root_win.mainloop()
