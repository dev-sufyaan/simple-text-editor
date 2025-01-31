import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tk_font
from tkinter.scrolledtext import ScrolledText
import re
import enchant

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Text Editor")
        self.root.geometry("800x600")
        self.root.configure(bg="#F3F3F3")

        # Initialize variables
        self.file_path = None
        self.saved = True
        self.spell_checker = None
        self.word_wrap_var = tk.BooleanVar(value=False)
        self.spell_check_var = tk.BooleanVar(value=True)

        self.create_widgets()
        self.create_menus()
        self.apply_styles()
        self.bind_events()
        self.init_spell_checker()

    def init_spell_checker(self):
        try:
            self.spell_checker = enchant.Dict("en_US")
        except enchant.Error:
            messagebox.showerror("Spell Check Error",
                "Spell checker dictionary not found. "
                "Please install aspell-en (Linux) or equivalent for your OS.")
            self.spell_check_var.set(False)

    def create_widgets(self):
        # Text area
        self.text_area = ScrolledText(self.root,
                                      undo=True,
                                      font=("Segoe UI", 12),
                                      padx=5,
                                      pady=5,
                                      bg="#FFFFFF",
                                      fg="#262626")
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # Configure misspelling tag
        self.text_area.tag_config("misspelling",
                                  underline=True, foreground="#FF0000")

        # Status bar
        self.status_bar = tk.Label(self.root, text="Line 1  Column 0",
                                   font=("Segoe UI", 9),
                                   bg="#F3F3F3",
                                   fg="#1A1A1A",
                                   anchor="e")
        self.status_bar.pack(fill=tk.X, padx=10, pady=(0, 5))

    def create_menus(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y")

        # Format menu
        format_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap_var, command=self.toggle_word_wrap)
        format_menu.add_checkbutton(label="Spell Check", variable=self.spell_check_var, command=self.toggle_spell_check)
        format_menu.add_command(label="Font Settings", command=self.font_settings)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def apply_styles(self):
        self.text_area.config(borderwidth=0, highlightthickness=0)
        style = tk_font.Font(family="Segoe UI", size=9)
        self.root.option_add("*Font", style)

    def bind_events(self):
        self.text_area.bind("<<TextChange>>", self.on_text_change)
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.root.bind("<KeyRelease>", self.update_status_bar, add="+")

    def new_file(self, event=None):
        if not self.saved:
            response = messagebox.askyesnocancel("New File", "Do you want to save changes?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        self.text_area.delete(1.0, tk.END)
        self.set_title()
        self.file_path = None
        self.saved = True

    def open_file(self, event=None):
        if not self.saved:
            response = messagebox.askyesnocancel("Open File", "Do you want to save changes?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                    self.file_path = file_path
                    self.set_title()
                    self.saved = True
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_file(self, event=None):
        if self.file_path:
            self.save_content()
        else:
            self.save_as()

    def save_as(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.save_content()

    def save_content(self):
        try:
            content = self.text_area.get(1.0, tk.END)
            with open(self.file_path, 'w') as file:
                file.write(content)
            self.set_title()
            self.saved = True
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_title(self):
        if self.file_path:
            title = f"{self.file_path.split('/')[-1]} - Smart Text Editor"
        else:
            title = "Untitled - Smart Text Editor"
        self.root.title(title)

    def toggle_word_wrap(self):
        if self.word_wrap_var.get():
            self.text_area.config(wrap=tk.WORD)
        else:
            self.text_area.config(wrap=tk.NONE)

    def toggle_spell_check(self):
        if self.spell_check_var.get() and self.spell_checker:
            self.check_spelling()
        else:
            self.text_area.tag_remove("misspelling", "1.0", tk.END)

    def font_settings(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Font Settings")

        current_font = tk_font.Font(font=self.text_area.cget("font"))
        font_families = sorted(tk_font.families())

        family_var = tk.StringVar(value=current_font.cget("family"))
        tk.Label(font_window, text="Font Family:").pack(anchor=tk.W)
        family_menu = tk.OptionMenu(font_window, family_var, *font_families)
        family_menu.pack(anchor=tk.W, fill=tk.X)

        size_var = tk.IntVar(value=current_font.cget("size"))
        tk.Label(font_window, text="Font Size:").pack(anchor=tk.W)
        tk.Scale(font_window, from_=8, to=40, variable=size_var, orient=tk.HORIZONTAL).pack(anchor=tk.W, fill=tk.X)

        styles = {
            "Bold": tk.BooleanVar(value=current_font.cget("weight") == "bold"),
            "Italic": tk.BooleanVar(value=current_font.cget("slant") == "italic"),
            "Underline": tk.BooleanVar(value=current_font.cget("underline"))
        }
        for style in styles:
            tk.Checkbutton(font_window, text=style, variable=styles[style]).pack(anchor=tk.W)

        tk.Button(font_window, text="Apply", command=lambda: self.apply_font(
            family_var.get(),
            size_var.get(),
            styles["Bold"].get(),
            styles["Italic"].get(),
            styles["Underline"].get()
        )).pack(pady=5)

    def apply_font(self, family, size, bold, italic, underline):
        try:
            self.text_area.config(font=(family, size,
                                 "bold" if bold else "normal",
                                 "italic" if italic else "roman",
                                 "underline" if underline else "normal"))
        except tk_font.FontError as e:
            messagebox.showerror("Error", str(e))

    def check_spelling(self):
        self.text_area.tag_remove("misspelling", "1.0", tk.END)
        text_content = self.text_area.get("1.0", "end-1c")
        words = re.findall(r"\b[a-zA-Z']+\b", text_content)

        for word in words:
            if not self.spell_checker.check(word.lower()):
                start = self.text_area.search(r"\b{}\b".format(re.escape(word)), "1.0", tk.END, nocase=True)
                while start:
                    end = f"{start}+{len(word)}c"
                    self.text_area.tag_add("misspelling", start, end)
                    start = self.text_area.search(r"\b{}\b".format(re.escape(word)), end, tk.END, nocase=True)

    def on_text_change(self, event=None):
        if self.file_path:
            self.saved = False
            self.root.title(f"*{self.root.title()}")
        if self.spell_check_var.get() and self.spell_checker:
            self.root.after(300, self.check_spelling)

    def update_status_bar(self, event=None):
        line, column = self.text_area.index(tk.INSERT).split(".")
        self.status_bar.config(text=f"Line {line}  Column {column}")

    def show_about(self):
        messagebox.showinfo("About", "Smart Text Editor v1.0\nCreated by Sufyaan\nAll done!")

if __name__ == "__main__":
    root = tk.Tk()
    TextEditor(root)
    root.mainloop()