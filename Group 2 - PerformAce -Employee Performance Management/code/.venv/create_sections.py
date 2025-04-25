import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector

# Database Configuration
DB_CONFIG_SECTIONS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'sections'
}

DB_CONFIG_TASKS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'tasks'
}


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def open_create_sections_page(org_name):
    root = tk.Tk()
    root.title("Create Section")
    center_window(root, 600, 250)
    root.configure(bg="#223344")

    title_label = tk.Label(root, text=f"Create Section for Organization: {org_name}",
                           font=("Arial", 16, "bold"), bg="#223344", fg="lightblue")
    title_label.pack(pady=20)

    form_frame = tk.Frame(root, bg="#223344")
    form_frame.pack(pady=10)

    section_label = tk.Label(form_frame, text="Section Name:", font=("Arial", 12), bg="#223344", fg="white")
    section_label.grid(row=0, column=0, padx=20, pady=5, sticky="w")

    section_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
    section_entry.grid(row=0, column=1, pady=5)

    def create_section():
        section_name = section_entry.get().strip()
        if not section_name:
            messagebox.showerror("Error", "Please enter a section name")
            return

        try:
            conn_sections = mysql.connector.connect(**DB_CONFIG_SECTIONS)
            cursor_sections = conn_sections.cursor()

            table_name = f"{org_name.lower().replace(' ', '_')}_{section_name.lower().replace(' ', '_')}"
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user VARCHAR(255) NOT NULL
            )
            """
            cursor_sections.execute(create_table_query)
            conn_sections.commit()
            cursor_sections.close()
            conn_sections.close()

            # Create a corresponding table in the tasks database
            conn_tasks = mysql.connector.connect(**DB_CONFIG_TASKS)
            cursor_tasks = conn_tasks.cursor()

            create_tasks_table_query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}_tasks` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(255) NOT NULL,
                task_type VARCHAR(255) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_data LONGBLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submission_date DATE NOT NULL  -- Added the submission_date column here
            )
            """
            cursor_tasks.execute(create_tasks_table_query)
            conn_tasks.commit()
            cursor_tasks.close()
            conn_tasks.close()

            messagebox.showinfo("Success",
                                f"Section '{section_name}' and corresponding task table created successfully for '{org_name}'!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            root.destroy()

    btn_frame = tk.Frame(root, bg="#223344")
    btn_frame.pack(pady=20)

    create_btn = tk.Button(btn_frame, text="Create", font=("Arial", 12), bg="lightgray", width=10,
                           command=create_section)
    create_btn.pack(side="left", padx=10)

    cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), bg="lightgray", width=10, command=root.destroy)
    cancel_btn.pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__":
    open_create_sections_page("example_org")
