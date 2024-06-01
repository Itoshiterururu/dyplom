import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

# Підключення до MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['dyplom']
cadets_collection = db['cadets']

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadet Performance Management")
        self.root.geometry("800x600")

        # Styling
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=6, background="#f0f0f0")
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Виджети для перегляду рейтингів курсантів за рік
        self.year_label = ttk.Label(root, text="Year:")
        self.year_label.pack(pady=5)
        self.year_entry = ttk.Entry(root)
        self.year_entry.pack(pady=5)
        self.view_button = ttk.Button(root, text="View Cadets by Year", command=self.view_cadets_by_year)
        self.view_button.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Specialty", "Rating"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Specialty", text="Specialty")
        self.tree.heading("Rating", text="Rating")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Виджети для перегляду деталей курсанта
        self.detail_frame = ttk.Frame(root)
        self.detail_frame.pack_forget()

        self.details_tree = ttk.Treeview(self.detail_frame, columns=("Field", "Value", "Edit"), show='headings')
        self.details_tree.heading("Field", text="Field")
        self.details_tree.heading("Value", text="Value")
        self.details_tree.heading("Edit", text="Edit")
        self.details_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.year_option = ttk.Label(self.detail_frame, text="Year:")
        self.year_option.pack(pady=5)
        self.year_var = tk.StringVar()
        self.year_menu = ttk.Combobox(self.detail_frame, textvariable=self.year_var)
        self.year_menu.pack(pady=5)
        self.year_menu.bind("<<ComboboxSelected>>", self.change_year)

        self.back_button = ttk.Button(self.detail_frame, text="Back", command=self.hide_details)
        self.back_button.pack(pady=5)

        self.save_button = ttk.Button(self.detail_frame, text="Save Changes", command=self.update_cadet)
        self.save_button.pack(pady=5)

        self.current_cadet_id = None
        self.current_year = None

        self.view_cadets_by_year()  # Початкове відображення списку курсантів за рейтингом останнього року

    def make_editable(self, item, field):
        def save_edit(event):
            new_value = entry.get()
            self.details_tree.item(item, values=(field, new_value, "Edit"))
            entry.destroy()
            self.details_tree.bind("<Double-1>", self.edit_item)
            self.update_cadet_field(field, new_value)  # Call to update the database

        old_value = self.details_tree.item(item, "values")[1]
        entry = ttk.Entry(self.detail_frame)
        entry.insert(0, old_value)
        entry.bind("<Return>", save_edit)
        entry.pack()
        bbox = self.details_tree.bbox(item, column="Value")
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

    def edit_item(self, event):
        item = self.details_tree.selection()[0]
        field = self.details_tree.item(item, "values")[0]
        self.make_editable(item, field)

    # Add update_cadet_field method to update a single field in the database
    def update_cadet_field(self, field, value):
        if not self.current_cadet_id or not self.current_year:
            return

        update_path = {}
        if field in ["Physical Fitness", "Discipline"]:
            update_path[f"years.{self.current_year}.{field.lower().replace(' ', '_')}"] = int(value)
        elif field == "Skills":
            update_path["skills"] = [skill.strip() for skill in value.split(",")]
        elif field == "Courses":
            update_path[f"years.{self.current_year}.courses"] = [course.strip() for course in value.split(",")]
        else:
            # Assuming fields like "Name" and "Specialty"
            update_path[field.lower()] = value

        cadets_collection.update_one({"_id": self.current_cadet_id}, {"$set": update_path})

    def toggle_expand(self, parent_item, subjects, scores):
        if self.details_tree.get_children(parent_item):
            for child in self.details_tree.get_children(parent_item):
                self.details_tree.delete(child)
        else:
            for subject in subjects:
                score = scores.get(subject, 0)
                child_item = self.details_tree.insert(parent_item, "end", values=(subject, score, "Edit"),
                                                      tags=(subject,))
                self.details_tree.tag_bind(child_item, "<Double-1>",
                                           lambda e, subj=subject: self.edit_subject(child_item, subj))

    def edit_subject(self, item, subject):
        old_value = self.details_tree.item(item, "values")[1]

        def save_edit(event):
            new_value = entry.get()
            self.details_tree.item(item, values=(subject, new_value, "Edit"))
            entry.destroy()
            self.update_cadet_subject(subject, new_value)

        entry = ttk.Entry(self.detail_frame)
        entry.insert(0, old_value)
        entry.bind("<Return>", save_edit)
        entry.pack()
        bbox = self.details_tree.bbox(item, column="Value")
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

    def update_cadet_subject(self, subject, value):
        if not self.current_cadet_id or not self.current_year:
            return

        cadet = cadets_collection.find_one({"_id": self.current_cadet_id})
        category = None

        for cat, scores in cadet['years'][self.current_year]['scores'].items():
            if subject in scores:
                category = cat
                break

        if category:
            update_path = {f"years.{self.current_year}.scores.{category}.{subject}": int(value)}
            cadets_collection.update_one({"_id": self.current_cadet_id}, {"$set": update_path})

    def calculate_average(self, scores):
        if scores:
            return sum(scores.values()) / len(scores)
        return 0

    def view_cadets_by_year(self):
        year = self.year_entry.get().strip() or str(max(int(y) for cadet in cadets_collection.find() for y in cadet['years'].keys()))  # Знаходження останнього року, якщо не вказано
        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, year)

        cadets = cadets_collection.find({f"years.{year}": {"$exists": True}})
        cadet_list = [(cadet['_id'], cadet['name'], cadet['specialty'], self.calculate_rating(cadet['years'][year]['scores'], cadet['years'][year]['physical_fitness'], cadet['years'][year]['discipline'])) for cadet in cadets]
        cadet_list.sort(key=lambda x: x[3], reverse=True)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for cadet in cadet_list:
            self.tree.insert("", "end", values=cadet)

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        cadet_id = self.tree.item(item, "values")[0]
        self.view_cadet_details(cadet_id)

    def view_cadet_details(self, cadet_id):
        self.current_cadet_id = cadet_id
        cadet = cadets_collection.find_one({"_id": cadet_id})

        if not cadet:
            messagebox.showerror("Error", "Cadet not found")
            return

        self.details_tree.delete(*self.details_tree.get_children())

        years = sorted(cadet['years'].keys())
        self.year_var.set(years[-1])  # Встановлення останнього року за замовчуванням
        self.year_menu['values'] = years

        self.show_cadet_details_for_year(cadet, years[-1])

        self.detail_frame.pack()

    def show_cadet_details_for_year(self, cadet, year):
        self.current_year = year
        data = cadet['years'][year]

        self.details_tree.insert("", "end", values=("ID", cadet['_id'], ""))
        self.details_tree.insert("", "end", values=("Name", cadet['name'], "Edit"), tags=("Name",))
        self.details_tree.insert("", "end", values=("Specialty", cadet['specialty'], "Edit"), tags=("Specialty",))
        self.details_tree.insert("", "end", values=("Skills", ", ".join(cadet.get('skills', [])), "Edit"),
                                 tags=("Skills",))
        year_item = self.details_tree.insert("", "end", values=("Year", year, "Select"), tags=("Year",))

        for category in data['scores']:
            category_item = self.details_tree.insert("", "end",
                                                     values=(category.capitalize() + " Scores", "", "Toggle"),
                                                     tags=(category,))
            average_score = self.calculate_average(data['scores'][category])
            self.details_tree.insert(category_item, "end", values=("Average", average_score, ""))

            self.toggle_expand(category_item, data['scores'][category].keys(), data['scores'][category])

        self.details_tree.insert("", "end", values=("Physical Fitness", data['physical_fitness'], "Edit"),
                                 tags=("Physical Fitness",))
        self.details_tree.insert("", "end", values=("Discipline", data['discipline'], "Edit"), tags=("Discipline",))
        if 'courses' in data:
            self.details_tree.insert("", "end", values=("Courses", ", ".join(data['courses']), "Edit"),
                                     tags=("Courses",))

        self.details_tree.tag_bind("Name", "<Double-1>", self.edit_item)
        self.details_tree.tag_bind("Specialty", "<Double-1>", self.edit_item)
        self.details_tree.tag_bind("Skills", "<Double-1>", self.edit_item)
        self.details_tree.tag_bind("Physical Fitness", "<Double-1>", self.edit_item)
        self.details_tree.tag_bind("Discipline", "<Double-1>", self.edit_item)
        self.details_tree.tag_bind("Courses", "<Double-1>", self.edit_item)

        self.details_tree.tag_bind("Year", "<Double-1>", self.show_year_selection)
        for category in data['scores']:
            self.details_tree.tag_bind(category, "<Double-1>",
                                       lambda e, cat=category, item=category_item: self.toggle_expand(item,
                                                                                                      data['scores'][
                                                                                                          cat].keys(),
                                                                                                      data['scores'][
                                                                                                          cat]))

    def change_year(self, event):
        if not self.current_cadet_id:
            return

        new_year = self.year_var.get()
        cadet = cadets_collection.find_one({"_id": self.current_cadet_id})
        if new_year in cadet['years']:
            self.details_tree.delete(*self.details_tree.get_children())
            self.show_cadet_details_for_year(cadet, new_year)

    def hide_details(self):
        self.detail_frame.pack_forget()

    def update_cadet(self):
        if not self.current_cadet_id:
            messagebox.showerror("Error", "No cadet selected")
            return

        updated_data = {}
        year = self.current_year

        for item in self.details_tree.get_children():
            values = self.details_tree.item(item, "values")
            if len(values) != 3:
                continue
            field, value, _ = values

            if field in ["Physical Fitness", "Discipline"]:
                updated_data[f"years.{year}.{field.lower().replace(' ', '_')}"] = int(value)
            elif field == "Skills":
                updated_data["skills"] = [skill.strip() for skill in value.split(",")]
            elif field == "Courses":
                updated_data[f"years.{year}.courses"] = [course.strip() for course in value.split(",")]
            elif field in ["OOP", "AP", "Tactics", "OZT", "KPP", "OS", "IAD", "IP", "SKVZ"]:
                for parent in self.details_tree.get_children():
                    parent_field, _ = self.details_tree.item(parent, "values")
                    if field in parent_field:
                        category = parent_field.split()[0].lower()
                        updated_data[f"years.{year}.scores.{category}.{field}"] = int(value)

        cadets_collection.update_one(
            {"_id": self.current_cadet_id},
            {"$set": updated_data}
        )
        messagebox.showinfo("Update", "Cadet updated successfully")
        self.view_cadet_details(self.current_cadet_id)  # Оновлення відображення деталей

    def calculate_rating(self, scores, physical_fitness, discipline):
        total_score = sum(scores['humanitarian'].values()) + sum(scores['military'].values()) + sum(scores['special'].values())
        total_score /= (len(scores['humanitarian']) + len(scores['military']) + len(scores['special']))
        total_score += physical_fitness
        total_score += discipline * 10  # Дисципліна має більшу вагу

        return total_score / 12  # Середнє значення

    def show_year_selection(self, event):
        item = self.details_tree.selection()[0]
        cadet = cadets_collection.find_one({"_id": self.current_cadet_id})

        def select_year(selected_year):
            self.details_tree.delete(*self.details_tree.get_children())
            self.show_cadet_details_for_year(cadet, selected_year)
            self.year_selection_menu.destroy()

        years = sorted(cadet['years'].keys())
        self.year_selection_menu = tk.Menu(self.root, tearoff=0)
        for year in years:
            self.year_selection_menu.add_command(label=year, command=lambda y=year: select_year(y))

        x, y, _, _ = self.details_tree.bbox(item, column="Value")
        self.year_selection_menu.post(self.details_tree.winfo_rootx() + x, self.details_tree.winfo_rooty() + y)


root = tk.Tk()
app = App(root)
root.mainloop()
