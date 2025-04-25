# tasks1.py
import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
import datetime
from tkcalendar import Calendar
import json  # For storing multiple files in a single blob

DB_CONFIG_TASKS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'tasks'
}

DB_CONFIG_USERMANAGEMENT = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'usermanagement'
}

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

def connect_to_database(config):
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

def fetch_task_details(table_name, task_name):
    connection = connect_to_database(DB_CONFIG_TASKS)
    if connection:
        cursor = connection.cursor()
        query = f"""
            SELECT task_name, task_type, submission_date 
            FROM `{table_name}_tasks` 
            WHERE task_name = %s 
            ORDER BY id DESC LIMIT 1
        """
        cursor.execute(query, (task_name,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result:
            return result[0], result[1], result[2]
    return "Unknown Task", "Unknown Type", "No Date"

def add_files(file_listbox, root):
    files = filedialog.askopenfilenames()
    for file in files:
        file_listbox.insert(tk.END, file)
    root.focus_force()

def remove_selected(file_listbox):
    selected_items = file_listbox.curselection()
    for index in reversed(selected_items):
        file_listbox.delete(index)

import re
import json
import datetime
from tkinter import messagebox
from mysql.connector import Error

def sanitize_column_name(name):
    """Sanitize a string so it's safe for MySQL column names."""
    return re.sub(r'\W+', '_', name).lower()

def confirm_action(task_name, task_type, file_listbox, table_name, root, submission_date, username):
    print(f"[DEBUG] Raw Username: {username}")
    files = file_listbox.get(0, tk.END)
    if not files:
        messagebox.showerror("Error", "Please select at least one file.")
        return

    try:
        # Debug print - show username and its sanitized version
        print(f"[DEBUG] Raw Username: {username}")
        sanitized_username = sanitize_column_name(username)
        print(f"[DEBUG] Sanitized Username (used as column): {sanitized_username}")

        submitted_at_column = f"{sanitized_username}_submitted_at"

        connection = connect_to_database(DB_CONFIG_TASKS)
        if connection:
            cursor = connection.cursor()

            # Get task ID
            get_id_query = f"SELECT id FROM `{table_name}_tasks` WHERE task_name = %s ORDER BY id DESC LIMIT 1"
            cursor.execute(get_id_query, (task_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Task ID not found.")
                return
            task_id = result[0]

            # Create submissions table if not exists
            submission_table = f"{table_name}_submissions"
            create_table_query = f"CREATE TABLE IF NOT EXISTS `{submission_table}` (id INT PRIMARY KEY)"
            cursor.execute(create_table_query)

            # Check and add columns if they don't exist
            check_column_query = """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s AND column_name = %s
            """
            cursor.execute(check_column_query, (DB_CONFIG_TASKS['database'], submission_table, sanitized_username))
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE `{submission_table}` ADD COLUMN `{sanitized_username}` BLOB")

            cursor.execute(check_column_query, (DB_CONFIG_TASKS['database'], submission_table, submitted_at_column))
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE `{submission_table}` ADD COLUMN `{submitted_at_column}` DATETIME")

            # Convert files to JSON string (with binary-safe encoding)
            file_contents = {}
            for file_path in files:
                file_name = file_path.split("/")[-1]
                with open(file_path, 'rb') as f:
                    file_contents[file_name] = f.read().decode('latin1')

            submission_blob = json.dumps(file_contents)
            current_time = datetime.datetime.now()

            # Insert or update
            insert_query = f"""
                INSERT INTO `{submission_table}` (id, `{sanitized_username}`, `{submitted_at_column}`)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `{sanitized_username}` = VALUES(`{sanitized_username}`),
                    `{submitted_at_column}` = VALUES(`{submitted_at_column}`)
            """
            cursor.execute(insert_query, (task_id, submission_blob, current_time))

            connection.commit()
            cursor.close()
            connection.close()

        messagebox.showinfo("Success", f"Files submitted to task '{task_name}' successfully.")
        root.destroy()

    except Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")

def open_task_file_adder(org_name, section_name, task_name, username):  # Accept username here
    print(f"[DEBUG] open_task_file_adder received username: {username}")
    table_name = f"{org_name.lower().replace(' ', '_')}_{section_name.lower().replace(' ', '_')}"
    task_name, task_type, submission_date = fetch_task_details(table_name, task_name)

    root = tk.Tk()
    root.title(f"Add Files - {org_name} - {section_name}")
    root.configure(bg="#223344")
    center_window(root, 600, 450)
    root.attributes("-topmost", True)

    title_label = tk.Label(root, text=f"{org_name} - {section_name}", font=("Arial", 16, "bold"), fg="white", bg="#223344")
    title_label.pack(pady=5, fill=tk.X)

    display_frame = tk.Frame(root, bg="#223344")
    display_frame.pack(fill=tk.X, padx=20, pady=5)
    tk.Label(display_frame, text="Task Name:", font=("Arial", 12, "bold"), fg="white", bg="#223344").pack(side=tk.LEFT)
    tk.Label(display_frame, text=task_name, font=("Arial", 12), fg="white", bg="#223344").pack(side=tk.LEFT, padx=10)

    type_frame = tk.Frame(root, bg="#223344")
    type_frame.pack(fill=tk.X, padx=20, pady=5)
    tk.Label(type_frame, text="Task Type:", font=("Arial", 12, "bold"), fg="white", bg="#223344").pack(side=tk.LEFT)
    tk.Label(type_frame, text=task_type, font=("Arial", 12), fg="white", bg="#223344").pack(side=tk.LEFT, padx=10)

    date_frame = tk.Frame(root, bg="#223344")
    date_frame.pack(fill=tk.X, padx=20, pady=5)
    tk.Label(date_frame, text="Submission Date:", font=("Arial", 12, "bold"), fg="white", bg="#223344").pack(side=tk.LEFT)
    tk.Label(date_frame, text=submission_date, font=("Arial", 12), fg="white", bg="#223344").pack(side=tk.LEFT, padx=10)

    file_listbox_frame = tk.Frame(root, bg="#223344")
    file_listbox_frame.pack(fill=tk.X, padx=20, pady=5)
    tk.Label(file_listbox_frame, text="Selected Files:", font=("Arial", 12, "bold"), fg="white", bg="#223344").pack(side=tk.LEFT)

    file_listbox = tk.Listbox(file_listbox_frame, width=50, height=8, selectmode=tk.MULTIPLE)
    file_listbox.pack(side=tk.LEFT)

    add_button = tk.Button(root, text="Add Files", font=("Arial", 12), command=lambda: add_files(file_listbox, root))
    add_button.pack(pady=10)

    remove_button = tk.Button(root, text="Remove Selected", font=("Arial", 12), command=lambda: remove_selected(file_listbox))
    remove_button.pack(pady=5)

    submit_button = tk.Button(root, text="Submit Files", font=("Arial", 12, "bold"), bg="green",
                              command=lambda: confirm_action(task_name, task_type, file_listbox, table_name, root, submission_date, username))
    submit_button.pack(pady=10)

    root.mainloop()

