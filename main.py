import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET

# Load and parse the KJV XML
tree = ET.parse('en_kjv.xml')
root = tree.getroot()

# Map shorthand book ID to full book name
book_names = [b.get('n') for b in root.findall('b')]
book_lookup = {name.lower(): b for name, b in zip(book_names, root.findall('b'))}


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
    for book in root.findall('b'):
        book_name = book.get('n')
        for chapter in book.findall('c'):
            chapter_num = chapter.get('n')
            for verse in chapter.findall('v'):
                if query in verse.text.lower():
                    results.append(f"{book_name} {chapter_num}:{verse.get('n')} — {verse.text}")

    output_text.delete(1.0, tk.END)
    if results:
        output_text.insert(tk.END, "\n\n".join(results))
    else:
        output_text.insert(tk.END, "No results found.")


# GUI setup
root_win = tk.Tk()
root_win.title("KJV Bible")
root_win.geometry("1920x1080")
root_win.resizable(True, True)

# Label and Verse Lookup Entry (Book Chapter [Verse])
verse_label = tk.Label(root_win, text="Verse Lookup (e.g., John 3 16)", font=("Helvetica", 16))
verse_label.pack(padx=20, anchor='w')

search_entry = AutocompleteEntry(book_names, root_win, font=("Helvetica", 20))
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

# Output Display
output_text = tk.Text(root_win, wrap=tk.WORD, font=("Georgia", 18))
output_text.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

root_win.bind("<Escape>", lambda e: root_win.destroy())

root_win.mainloop()
