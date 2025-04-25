import tkinter as tk
from tkinter import messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# Database Configuration (Simulated)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "TuViZa@2345",
    "database": "tasks",
}


# Function to connect to the database (simulated)
def connect_to_database():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None


# Function to fetch task table names based on search text (simulated)
def fetch_task_tables(search_text=""):
    # Here we simulate task tables names (as no actual tables)
    simulated_tables = [
        "a.p.s.i.t_task1", "a.p.s.i.t_task2", "a.p.s.i.t_exam",
        "math_task1", "math_task2", "math_quiz", "english_task1",
        "english_task2", "science_task1", "science_quiz"
    ]
    return [table for table in simulated_tables if table.lower().startswith(search_text.lower())]


# Function to generate random task statistics (simulated)
def generate_random_task_stats(table_name):
    # Generate random statistics for task views, attempts, and late submissions
    views = random.randint(50, 200)
    attempts = random.randint(30, 150)
    late_submissions = random.randint(10, 50)

    return {
        "name": table_name,
        "views": views,
        "attempts": attempts,
        "late_submissions": late_submissions
    }


# Function to update the chart based on search input
def update_chart():
    search_text = search_var.get().lower()
    table_names = fetch_task_tables(search_text)

    task_data = [generate_random_task_stats(table) for table in table_names]

    plot_chart(task_data)


# Function to plot the bar chart
def plot_chart(task_list):
    ax.clear()

    if not task_list:
        ax.set_title("No tasks found")
        canvas.draw()
        return

    x_labels = [task["name"] for task in task_list]
    views = [task["views"] for task in task_list]
    attempts = [task["attempts"] for task in task_list]
    late_submissions = [task["late_submissions"] for task in task_list]

    x = range(len(task_list))
    ax.bar([i - 0.2 for i in x], views, width=0.2, label="Views", color="blue")
    ax.bar(x, attempts, width=0.2, label="Attempts", color="green")
    ax.bar([i + 0.2 for i in x], late_submissions, width=0.2, label="Late Submissions", color="red")

    ax.set_xlabel("Task Name")
    ax.set_ylabel("Number of Students")
    ax.set_title("Task Statistics")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.legend()
    canvas.draw()


# Create main window
root = tk.Tk()
root.title("Task Statistics")
root.geometry("1600x750")

# Search Bar
search_var = tk.StringVar()
search_frame = tk.Frame(root, bg="#A4D07B")
search_frame.pack(fill="x", pady=5)

search_label = tk.Label(search_frame, text="Search Task:", bg="#A4D07B", font=("Arial", 12))
search_label.pack(side="left", padx=10)

search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 12), width=30)
search_entry.pack(side="left", padx=5)
search_entry.bind("<KeyRelease>", lambda event: update_chart())

# Matplotlib Figure for Bar Chart
fig, ax = plt.subplots(figsize=(12, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill="both", expand=True)

# Initial Chart Display
update_chart()

# Run the application
root.mainloop()
