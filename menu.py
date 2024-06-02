import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.geometry("400x300")

        # Центрируем фрейм с кнопками
        self.center_frame = ttk.Frame(root)
        self.center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Кнопки меню
        self.cadet_button = ttk.Button(self.center_frame, text="Open Cadet Management", command=self.open_cadet_management)
        self.cadet_button.pack(pady=10)

        self.officer_button = ttk.Button(self.center_frame, text="Open Officer Management", command=self.open_officer_management)
        self.officer_button.pack(pady=10)

        self.distribution_button = ttk.Button(self.center_frame, text="Виконати розподіл курсантів", command=self.perform_distribution)
        self.distribution_button.pack(pady=10)

        self.exit_button = ttk.Button(self.center_frame, text="Exit", command=root.quit)
        self.exit_button.pack(pady=10)

    def open_cadet_management(self):
        subprocess.run([sys.executable, "graph.py"])

    def open_officer_management(self):
        subprocess.run([sys.executable, "officer_management.py"])

    def perform_distribution(self):
        messagebox.showinfo("Distribution", "Виконати розподіл курсантів функція буде реалізована тут.")

    def show_about(self):
        messagebox.showinfo("About", "This is a sample application.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
