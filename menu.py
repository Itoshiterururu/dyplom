import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pymongo import MongoClient

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.geometry("400x300")

        # Создание меню
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # Добавление пунктов меню
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Cadet Management", command=self.open_cadet_management)
        file_menu.add_command(label="Open Officer Management", command=self.open_officer_management)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def open_cadet_management(self):
        subprocess.run(["python", "graph.py"])

    def open_officer_management(self):
        subprocess.run(["python", "officer_management.py"])

    def show_about(self):
        messagebox.showinfo("About", "This is a sample application.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
