import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import mysql.connector
import os
import rep  # Ensure rep.py is present in the same directory

# Database Configuration
DB_CONFIG_TASKS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'tasks'
}

def connect_to_database():
    try:
        connection = mysql.connector.connect(**DB_CONFIG_TASKS)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

def fetch_tasks_from_db(table_name):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = f"SELECT task_name, task_type, file_name, submission_date FROM `{table_name}_tasks`"
        cursor.execute(query)
        tasks = cursor.fetchall()
        cursor.close()
        connection.close()
        return tasks
    return []

def download_all_docs(task_name, table_name):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = f"SELECT file_name, file_data FROM `{table_name}_tasks` WHERE task_name = %s"
        cursor.execute(query, (task_name,))
        files = cursor.fetchall()

        folder_selected = filedialog.askdirectory(title="Select Download Folder")
        if not folder_selected:
            messagebox.showwarning("Download Cancelled", "No folder selected. Download cancelled.")
            return

        for file_name, file_data in files:
            file_path = os.path.join(folder_selected, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_data)

        cursor.close()
        connection.close()

        messagebox.showinfo("Success", f"All files for task '{task_name}' have been downloaded to '{folder_selected}'.")

def open_report_page():
    try:
        new_root = tk.Tk()
        app = rep.ReportApp(new_root)
        app.view_task_details()
        new_root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open report page: {e}")

def open_task_view_page(org_name, section_name):
    table_name = f"{org_name.lower().replace(' ', '_')}_{section_name.lower().replace(' ', '_')}"
    root = tk.Tk()
    root.title(f"View Tasks - {org_name} - {section_name}")
    root.geometry("1000x600")

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tasks = fetch_tasks_from_db(table_name)

    grouped_tasks = {}
    for task_name, task_type, file_name, submission_date in tasks:
        if task_name not in grouped_tasks:
            grouped_tasks[task_name] = {"task_type": task_type, "file_names": [], "submission_date": submission_date}
        grouped_tasks[task_name]["file_names"].append(file_name)

    columns = ("No", "Task Name", "Task Type", "File Name", "Submission Date", "Download", "View")
    tree = ttk.Treeview(frame, columns=columns, show="headings", xscrollcommand=h_scrollbar.set,
                        yscrollcommand=v_scrollbar.set)

    h_scrollbar.config(command=tree.xview)
    v_scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=140)

    idx = 1
    for task_name, task_data in grouped_tasks.items():
        task_type = task_data["task_type"]
        file_names = task_data["file_names"]
        submission_date = task_data["submission_date"]
        first_entry = True

        for file_name in file_names:
            if first_entry:
                tree.insert("", "end", values=(idx, task_name, task_type, file_name, submission_date, "Download", "View"),
                            iid=f"{task_name}_{idx}")
                first_entry = False
            else:
                tree.insert("", "end", values=("", "", "", file_name, "", "", ""),
                            iid=f"{task_name}_file_{idx}")

            idx += 1

    tree.pack(fill=tk.BOTH, expand=True)

    def on_item_click(event):
        selected_item = tree.selection()
        if selected_item:
            column = tree.identify_column(event.x)
            if column == "#6":  # Download button
                task_name = tree.item(selected_item, "values")[1]
                if task_name:
                    download_all_docs(task_name, table_name)
            elif column == "#7":  # View button
                root.destroy()  # Close current window
                open_report_page()

    tree.bind("<ButtonRelease-1>", on_item_click)

    cancel_button = tk.Button(root, text="Cancel", command=root.destroy)
    cancel_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    open_task_view_page("example_org", "example_section")
