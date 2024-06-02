import pymongo
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dyplom"]
collection = db["officers"]

# Retrieve data from the collection
officers = list(collection.find())

# Calculate the rating for each officer
def calculate_rating(evaluations):
    total_score = 0
    count = 0
    for year, evaluation in evaluations.items():
        scores = evaluation['evaluations'].values()
        total_score += sum(scores)
        count += len(scores)
    return total_score / count if count != 0 else 0

# Add ratings to each officer
for officer in officers:
    officer['rating'] = calculate_rating(officer['years_of_service'])

# Sort officers by rating
sorted_officers = sorted(officers, key=lambda x: x['rating'], reverse=True)

# Function to refresh the main Treeview
def refresh_main_treeview():
    for row in tree.get_children():
        tree.delete(row)
    sorted_officers = sorted(collection.find(), key=lambda x: calculate_rating(x['years_of_service']), reverse=True)
    for officer in sorted_officers:
        tree.insert("", "end", text=officer["_id"], values=(officer["name"], officer["rank"], officer["specialty"], officer["rating"]))

# Function to update data in MongoDB
def update_officer(officer_id, field, value):
    collection.update_one({"_id": officer_id}, {"$set": {field: value}})
    refresh_main_treeview()

# Function to show detailed info of an officer
def show_officer_details(event):
    for widget in details_frame.winfo_children():
        widget.destroy()

    selected_item = tree.selection()[0]
    officer_id = tree.item(selected_item, "text")
    officer = collection.find_one({"_id": officer_id})

    if officer:
        details_label = tk.Label(details_frame, text="Officer Details", font=('Arial', 14))
        details_label.grid(row=0, column=0, columnspan=2)

        row_idx = 1
        for key, value in officer.items():
            if key != "_id" and key != "years_of_service":
                tk.Label(details_frame, text=key.capitalize()).grid(row=row_idx, column=0, sticky='w')
                value_entry = tk.Entry(details_frame)
                value_entry.grid(row=row_idx, column=1, sticky='w')
                value_entry.insert(0, value)
                value_entry.bind("<FocusOut>", lambda e, k=key, v=value_entry: update_officer(officer_id, k, v.get()))
                row_idx += 1

        tk.Label(details_frame, text="Years of Service", font=('Arial', 12, 'bold')).grid(row=row_idx, column=0, columnspan=2, sticky='w')
        row_idx += 1
        for year, data in officer['years_of_service'].items():
            tk.Label(details_frame, text=year).grid(row=row_idx, column=0, sticky='w')
            assignments = ', '.join(data['assignments'])
            courses = ', '.join(data['courses'])
            evaluations = ', '.join([f"{k}: {v}" for k, v in data['evaluations'].items()])

            tk.Label(details_frame, text="Assignments").grid(row=row_idx+1, column=0, sticky='w')
            assignments_entry = tk.Entry(details_frame)
            assignments_entry.grid(row=row_idx+1, column=1, sticky='w')
            assignments_entry.insert(0, assignments)
            assignments_entry.bind("<FocusOut>", lambda e, y=year, a=assignments_entry: update_officer(officer_id, f"years_of_service.{y}.assignments", a.get().split(', ')))

            tk.Label(details_frame, text="Courses").grid(row=row_idx+2, column=0, sticky='w')
            courses_entry = tk.Entry(details_frame)
            courses_entry.grid(row=row_idx+2, column=1, sticky='w')
            courses_entry.insert(0, courses)
            courses_entry.bind("<FocusOut>", lambda e, y=year, c=courses_entry: update_officer(officer_id, f"years_of_service.{y}.courses", c.get().split(', ')))

            tk.Label(details_frame, text="Evaluations").grid(row=row_idx+3, column=0, sticky='w')
            evaluations_entry = tk.Entry(details_frame)
            evaluations_entry.grid(row=row_idx+3, column=1, sticky='w')
            evaluations_entry.insert(0, evaluations)
            evaluations_entry.bind("<FocusOut>", lambda e, y=year, ev=evaluations_entry: update_officer(officer_id, f"years_of_service.{y}.evaluations", dict(eval.split(': ') for eval in ev.get().split(', '))))

            row_idx += 4

# Create a Tkinter window
root = tk.Tk()
root.title("Officers Ratings")

# Create a Treeview widget
tree = ttk.Treeview(root, columns=("name", "rank", "specialty", "rating"), show='headings')
tree.heading("name", text="Name")
tree.column("name", anchor=tk.W, width=200)
tree.heading("rank", text="Rank")
tree.column("rank", anchor=tk.W, width=100)
tree.heading("specialty", text="Specialty")
tree.column("specialty", anchor=tk.W, width=200)
tree.heading("rating", text="Rating")
tree.column("rating", anchor=tk.W, width=100)

# Insert data into the Treeview
for officer in sorted_officers:
    tree.insert("", "end", text=officer["_id"], values=(officer["name"], officer["rank"], officer["specialty"], officer["rating"]))

tree.bind("<Double-1>", show_officer_details)
tree.pack(fill=tk.BOTH, expand=True)

# Frame to display detailed information
details_frame = tk.Frame(root)
details_frame.pack(fill=tk.BOTH, expand=True)

# Run the Tkinter event loop
root.mainloop()
