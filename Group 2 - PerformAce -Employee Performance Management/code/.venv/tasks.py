import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
import datetime
from tkcalendar import Calendar

# Database Configuration
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

# Task types based on sectors
TASK_TYPES = {
    "Education and Research": ["Assignments", "Tests", "Projects", "Assessments"],
    "Industry and Manufacturing": ["Production", "Inspections", "Maintenance", "Scheduling"],
    "Corporate and Financial Services": ["Reports", "Audits", "Proposals", "Reviews"],
    "Health and Social Services": ["Care", "Assessments", "Referrals", "Outreach"],
    "Tourism Media and Entertainment": ["Events", "Promotions", "Reviews", "Content"],
    "Real Estate and Infrastructure": ["Listings", "Inspections", "Proposals", "Developments"],
    "Technology and Innovation": ["Development", "Testing", "Support", "Research"]
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

def fetch_sector(org_name):
    connection = connect_to_database(DB_CONFIG_USERMANAGEMENT)
    if connection:
        cursor = connection.cursor()
        query = "SELECT sector FROM organizations WHERE org_name = %s"
        cursor.execute(query, (org_name,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else None
    return None

def add_files(file_listbox, root):
    files = filedialog.askopenfilenames()
    for file in files:
        file_listbox.insert(tk.END, file)

    root.focus_force()

def remove_selected(file_listbox):
    selected_items = file_listbox.curselection()
    for index in reversed(selected_items):
        file_listbox.delete(index)

def store_task_data(task_name, task_type, file_name, file_data, table_name, submission_date):
    connection = connect_to_database(DB_CONFIG_TASKS)
    if connection:
        cursor = connection.cursor()

        try:
            # Insert task data into the tasks table
            insert_query = f"""
                INSERT INTO `{table_name}_tasks` (task_name, task_type, file_name, file_data, submission_date)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (task_name, task_type, file_name, file_data, submission_date))

            # Silently create the _submissions table if not already existing
            submissions_table = f"{table_name}_submissions"
            create_submissions_query = f"""
                CREATE TABLE IF NOT EXISTS `{submissions_table}` (
                    id INT
                )
            """
            cursor.execute(create_submissions_query)

            connection.commit()

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error inserting task or creating submissions table: {e}")
        finally:
            cursor.close()
            connection.close()

def confirm_action(task_name_entry, task_type_var, file_listbox, table_name, root, submission_date):
    task_name = task_name_entry.get().strip()
    task_type = task_type_var.get().strip()
    files = file_listbox.get(0, tk.END)

    if not task_name or not files:
        messagebox.showerror("Error", "Please provide a task name and select at least one file.")
        return

    try:
        for file_path in files:
            with open(file_path, 'rb') as file:
                file_data = file.read()

            file_name = file_path.split("/")[-1]
            store_task_data(task_name, task_type, file_name, file_data, table_name, submission_date)

        root.lift()
        messagebox.showinfo("Success", f"Task '{task_name}' has been uploaded successfully.")
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_task_manager(org_name, section_name):
    root = tk.Tk()
    root.title(f"Task Manager - {org_name} - {section_name}")
    root.configure(bg="#223344")  # Background color
    center_window(root, 600, 500)

    root.attributes("-topmost", True)

    # Title Label
    title_label = tk.Label(root, text=f"{org_name} - {section_name}", font=("Arial", 16, "bold"), fg="white", bg="#223344")
    title_label.pack(pady=5, fill=tk.X)

    # Task Name Entry
    task_name_frame = tk.Frame(root, bg="#223344")
    task_name_frame.pack(fill=tk.X, padx=20, pady=5)

    task_name_label = tk.Label(task_name_frame, text="Task Name:", font=("Arial", 12, "bold"), fg="white", bg="#223344")
    task_name_label.pack(side=tk.LEFT)

    task_name_entry = tk.Entry(task_name_frame, width=40, font=("Arial", 12))
    task_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Task Type Dropdown
    task_type_frame = tk.Frame(root, bg="#223344")
    task_type_frame.pack(fill=tk.X, padx=20, pady=5)

    task_type_label = tk.Label(task_type_frame, text="Task Type:", font=("Arial", 12, "bold"), fg="white", bg="#223344")
    task_type_label.pack(side=tk.LEFT)

    task_type_var = tk.StringVar(root)

    # Fetch sector and populate task types
    sector = fetch_sector(org_name)
    if sector in TASK_TYPES:
        task_types = TASK_TYPES[sector]
        task_type_var.set(task_types[0])  # Set default to the first task type
    else:
        task_types = ["Not Specified"]
        task_type_var.set(task_types[0])  # Default to "Not Specified"

    task_type_dropdown = tk.OptionMenu(task_type_frame, task_type_var, *task_types)
    task_type_dropdown.config(font=("Arial", 12), bg="#FFD700", fg="black")
    task_type_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # File Buttons
    task_frame = tk.Frame(root, bg="#223344")
    task_frame.pack(fill=tk.X, padx=20, pady=5)

    add_button = tk.Button(task_frame, text="Add Files", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", command=lambda: add_files(file_listbox, root))
    add_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    remove_button = tk.Button(task_frame, text="Remove Selected", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", command=lambda: remove_selected(file_listbox))
    remove_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    # File Listbox
    file_listbox = tk.Listbox(root, width=70, height=10, font=("Arial", 12), bg="white", fg="black")
    file_listbox.pack(fill=tk.BOTH, padx=20, pady=5, expand=True)

    # Submission Date Selection
    submission_date_frame = tk.Frame(root, bg="#223344")
    submission_date_frame.pack(fill=tk.X, padx=20, pady=5)

    def open_calendar():
        def select_submission_date():
            selected_date = calendar.get_date()
            selected_date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%Y").date()
            current_date = datetime.date.today()

            if selected_date_obj <= current_date:
                messagebox.showerror("Invalid Date", "Please select a date after today's date.")
            else:
                submission_date_label.config(text=f"Submission Date: {selected_date}")
                submission_date_entry.set(selected_date_obj)

            calendar_window.destroy()

        calendar_window = tk.Toplevel(root)
        calendar_window.title("Select Submission Date")

        calendar = Calendar(calendar_window, selectmode="day", date_pattern="mm/dd/yyyy", mindate=datetime.date.today())
        calendar.pack(padx=20, pady=20)

        select_button = tk.Button(calendar_window, text="Select Date", command=select_submission_date)
        select_button.pack(pady=10)

    submission_date_button = tk.Button(submission_date_frame, text="Select Submission Date", font=("Arial", 12, "bold"), bg="#FFD700", fg="black", command=open_calendar)
    submission_date_button.pack(side=tk.LEFT)

    submission_date_label = tk.Label(submission_date_frame, text="No submission date selected", font=("Arial", 12), fg="white", bg="#223344", width=40)
    submission_date_label.pack(side=tk.LEFT, padx=10)

    submission_date_entry = tk.StringVar()

    # Confirm and Cancel Buttons
    button_frame = tk.Frame(root, bg="#223344")
    button_frame.pack(fill=tk.X, padx=20, pady=10)

    confirm_button = tk.Button(button_frame, text="Confirm", font=("Arial", 14, "bold"), bg="#FFD700", fg="black",
                               command=lambda: confirm_action(task_name_entry, task_type_var, file_listbox,
                                                              f"{org_name.lower().replace(' ', '_')}_{section_name.lower().replace(' ', '_')}",
                                                              root, submission_date_entry.get()))
    confirm_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", font=("Arial", 14, "bold"), bg="#FFD700", fg="black", command=root.destroy)
    cancel_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    root.mainloop()

if __name__ == "__main__":
    open_task_manager("example_org", "example_section")