import tkinter as tk
from tkinter import messagebox
import json

# Load the Bible (assume KJV.json is in the same folder)
with open('kjv.json', 'r') as f:
    bible = json.load(f)

# Lookup logic
def lookup_verse():
    query = search_entry.get().strip()
    parts = query.split()
    
    try:
        if len(parts) == 3:
            book, chapter, verse = parts
            text = bible[book][chapter][verse]
        elif len(parts) == 2:
            book, chapter = parts
            text = "\n".join([f"{v}: {bible[book][chapter][v]}" for v in bible[book][chapter]])
        else:
            text = "Invalid format. Use: Book Chapter [Verse]"
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, text)
    except KeyError:
        messagebox.showerror("Not found", "Could not find that verse/chapter.")

# GUI
root = tk.Tk()
root.title("KJV Bible")
root.attributes('-fullscreen', True)

# Search bar
search_entry = tk.Entry(root, font=("Helvetica", 18))
search_entry.pack(fill=tk.X, padx=20, pady=10)
search_entry.bind("<Return>", lambda e: lookup_verse())

# Output area
output_text = tk.Text(root, wrap=tk.WORD, font=("Georgia", 16))
output_text.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

# Escape to close
root.bind("<Escape>", lambda e: root.destroy())

root.mainloop()
