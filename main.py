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

# Search function
def lookup_verse():
    query = search_entry.get().strip()
    parts = query.split()
    
    if len(parts) not in [2, 3]:
        messagebox.showerror("Invalid Input", "Use format: Book Chapter [Verse]")
        return

    book_name = parts[0].lower()
    chapter = parts[1]
    verse = parts[2] if len(parts) == 3 else None

    if book_name not in book_lookup:
        messagebox.showerror("Not Found", f"No book named '{book_name}'")
        return

    book = book_lookup[book_name]
    chapter_elem = book.find(f"./c[@n='{chapter}']")
    if chapter_elem is None:
        messagebox.showerror("Not Found", f"Chapter {chapter} not found in {book_name}")
        return

    output_text.delete(1.0, tk.END)

    if verse:
        verse_elem = chapter_elem.find(f"./v[@n='{verse}']")
        if verse_elem is not None:
            output_text.insert(tk.END, f"{book_name} {chapter}:{verse} — {verse_elem.text}")
        else:
            messagebox.showerror("Not Found", f"Verse {verse} not found in {book_name} {chapter}")
    else:
        for v in chapter_elem.findall('v'):
            output_text.insert(tk.END, f"{book_name} {chapter}:{v.get('n')} — {v.text}\n\n")

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

def search_whole_bible():
    query = full_search_entry.get().strip().lower()
    if not query:
        messagebox.showerror("Empty Search", "Please enter a word or phrase to search.")
        return

    results = []
    output_text.delete(1.0, tk.END)
    output_text.tag_config("highlight", background="yellow", foreground="black")

    for book in root.findall('b'):
        book_name = book.get('n')
        for chapter in book.findall('c'):
            chapter_num = chapter.get('n')
            for verse in chapter.findall('v'):
                verse_text = verse.text
                if query in verse_text.lower():
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

    if output_text.compare("end-1c", "==", "1.0"):
        output_text.insert(tk.END, "No results found.")

# Label and Verse Lookup Entry (Book Chapter [Verse])
verse_label = tk.Label(root_win, text="Verse Lookup (e.g., John 3 16)", font=("Helvetica", 16))
verse_label.pack(padx=20, anchor='w')

search_entry = AutocompleteEntry([], root_win, font=("Helvetica", 20))  # Initialize with an empty list
search_entry.insert(0, "e.g., John 3 16")
search_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
search_entry.bind("<Return>", lambda e: lookup_verse())

# Label and Full Bible Search Entry
full_search_label = tk.Label(root_win, text="Search Entire Bible for Word/Phrase", font=("Helvetica", 16))
full_search_label.pack(padx=20, anchor='w')

full_search_entry = tk.Entry(root_win, font=("Helvetica", 20))
full_search_entry.insert(0, "e.g., faith")
full_search_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
full_search_entry.bind("<Return>", lambda e: search_whole_bible())

# Update dropdown menu for Bible version selection
version_label = tk.Label(root_win, text="Select Bible Version", font=("Helvetica", 16))
version_label.pack(padx=20, anchor='w')

version_dropdown = tk.OptionMenu(root_win, version_var, *dropdown_options, command=on_version_change_display)
version_dropdown.config(font=("Helvetica", 16))
version_dropdown.pack(fill=tk.X, padx=20, pady=(0, 10))

# Add a scrollbar to the output_text widget
output_frame = tk.Frame(root_win)
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
