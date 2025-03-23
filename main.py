import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET

# Load and parse the KJV XML
tree = ET.parse('en_kjv.xml')
root = tree.getroot()

# Map shorthand book ID to full book name
book_lookup = {b.get('n'): b for b in root.findall('b')}
book_names = list(book_lookup.keys())  # "Genesis", "Exodus", etc.

# Search function
def lookup_verse():
    query = search_entry.get().strip()
    parts = query.split()
    
    if len(parts) not in [2, 3]:
        messagebox.showerror("Invalid Input", "Use format: Book Chapter [Verse]")
        return

    book_name = parts[0]
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

# GUI setup
root_win = tk.Tk()
root_win.title("KJV Bible")
root_win.attributes('-fullscreen', True)

search_entry = tk.Entry(root_win, font=("Helvetica", 20))
search_entry.pack(fill=tk.X, padx=20, pady=10)
search_entry.bind("<Return>", lambda e: lookup_verse())

output_text = tk.Text(root_win, wrap=tk.WORD, font=("Georgia", 18))
output_text.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

root_win.bind("<Escape>", lambda e: root_win.destroy())

root_win.mainloop()
