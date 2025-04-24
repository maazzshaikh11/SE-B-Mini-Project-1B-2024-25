from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime


def employee_greviance(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Employee Grievance")
    dashboard_window.configure(background="#FFDD95")

    window_width = 1000
    window_height = 600
    screen_width = dashboard_window.winfo_screenwidth()
    screen_height = dashboard_window.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    dashboard_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    font_info1 = ('Arial', 30, 'italic')
    font_info2 = ('Arial', 15, 'italic')
    font_button = ('Arial', 15, 'bold')

    # Get employee information from the global variable set during login
    # This assumes current_employee is defined in the login module
    try:
        from __main__ import current_employee
        employee_data = current_employee
    except (ImportError, NameError):
        # Fallback if current_employee is not available
        employee_data = None

    info1_label = Label(dashboard_window, text="Employee Grievance", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Submit your grievances here", fg='#3468C0', bg='#FFDD95',
                        font=font_info2)
    info2_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    # Name Entry - Prefill with employee name if available
    name_label = Label(dashboard_window, text="Enter Your Name:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    name_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

    name_entry = Entry(dashboard_window, width=40, font=font_info2)
    if employee_data and 'employee_name' in employee_data:
        name_entry.insert(0, employee_data['employee_name'])
    name_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

    # Department Dropdown
    department_label = Label(dashboard_window, text="Select Department:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    department_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    departments = ["HR", "IT", "Finance", "Operations", "Marketing"]
    department_var = StringVar()
    department_dropdown = ttk.Combobox(dashboard_window, textvariable=department_var, values=departments, width=37,
                                       font=font_info2, state="readonly")
    department_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky='w')
    department_dropdown.set("Select Department")

    # Issue Type Dropdown
    issue_label = Label(dashboard_window, text="Select Issue Type:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    issue_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')

    issue_types = ["Workplace Conflict", "Salary Issue", "Harassment", "Leave Policy", "Other"]
    issue_var = StringVar()
    issue_dropdown = ttk.Combobox(dashboard_window, textvariable=issue_var, values=issue_types, width=37,
                                  font=font_info2, state="readonly")
    issue_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky='w')
    issue_dropdown.set("Select Issue Type")

    # Grievance Text Area
    grievance_label = Label(dashboard_window, text="Describe Your Grievance:", fg='#3468C0', bg='#FFDD95',
                            font=font_info2)
    grievance_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')

    grievance_text = Text(dashboard_window, width=60, height=10, font=font_info2)
    grievance_text.grid(row=5, column=1, padx=10, pady=10, sticky='w')

    # Function to connect to the database
    def get_db_connection():
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="CHIR2502004|",  # Replace with your MySQL password
                database="hrassistance"
            )
            return connection
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to database: {err}")
            return None

    # Function to create grievance table if it doesn't exist
    def ensure_grievance_table_exists():
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()

                # Create table if it doesn't exist
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS employee_grievances (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id INT,
                    employee_name VARCHAR(255) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    issue_type VARCHAR(50) NOT NULL,
                    grievance_text TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'Pending',
                    submitted_at DATETIME,
                    FOREIGN KEY (employee_id) REFERENCES employee_signup(id)
                )
                ''')

                connection.commit()
                cursor.close()
                connection.close()
                return True
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error creating table: {err}")
                connection.close()
                return False
        return False

    # Create the table when the module loads
    ensure_grievance_table_exists()

    # Submit Button Function
    def submit_grievance():
        name = name_entry.get()
        department = department_var.get()
        issue_type = issue_var.get()
        grievance = grievance_text.get("1.0", END).strip()

        # Validate inputs
        if not name or department == "Select Department" or issue_type == "Select Issue Type" or not grievance:
            error_label.config(text="Error: All fields are required!", fg="red")
            return

        # Get database connection
        connection = get_db_connection()
        if not connection:
            error_label.config(text="Error: Could not connect to database!", fg="red")
            return

        try:
            cursor = connection.cursor()

            # Get current timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert grievance into database
            employee_id = employee_data['id'] if employee_data and 'id' in employee_data else None

            if employee_id:
                # If employee is logged in
                query = '''
                INSERT INTO employee_grievances 
                (employee_id, employee_name, department, issue_type, grievance_text, submitted_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(query, (employee_id, name, department, issue_type, grievance, current_time))
            else:
                # If employee ID is not available
                query = '''
                INSERT INTO employee_grievances 
                (employee_name, department, issue_type, grievance_text, submitted_at) 
                VALUES (%s, %s, %s, %s, %s)
                '''
                cursor.execute(query, (name, department, issue_type, grievance, current_time))

            connection.commit()
            cursor.close()
            connection.close()

            # Clear form and show success message
            error_label.config(text="Grievance Submitted Successfully!", fg="green")
            name_entry.delete(0, END)
            if employee_data and 'employee_name' in employee_data:
                name_entry.insert(0, employee_data['employee_name'])
            else:
                name_entry.delete(0, END)
            department_var.set("Select Department")
            issue_var.set("Select Issue Type")
            grievance_text.delete("1.0", END)

        except mysql.connector.Error as err:
            error_label.config(text=f"Error: {err}", fg="red")
            connection.close()

    submit_button = Button(dashboard_window, text="Submit", fg='#f7f7f7', bg='#4CAF50', activeforeground='#4CAF50',
                           activebackground='#388E3C', command=submit_grievance, font=font_button)
    submit_button.grid(row=6, column=1, padx=10, pady=10, sticky='w')

    # Error/Success Message Label
    error_label = Label(dashboard_window, text="", fg="red", bg='#FFDD95', font=font_info2)
    error_label.grid(row=7, column=1, padx=10, pady=5, sticky='w')

    # View My Grievances Button
    # def view_my_grievances():
    #     if not employee_data or 'id' not in employee_data:
    #         messagebox.showinfo("Information", "Please login to view your grievances.")
    #         return
    #
    #     # Create a new window to display grievances
    #     view_window = Toplevel(dashboard_window)
    #     view_window.title("My Grievances")
    #     view_window.configure(background="#FFDD95")
    #
    #     # Set window size and position
    #     view_window.geometry(f"900x500+{x_position + 50}+{y_position + 50}")
    #
    #     # Create Treeview widget
    #     columns = ("ID", "Issue Type", "Department", "Status", "Submitted Date")
    #     tree = ttk.Treeview(view_window, columns=columns, show='headings')
    #
    #     # Define column headings
    #     for col in columns:
    #         tree.heading(col, text=col)
    #         tree.column(col, width=150)
    #
    #     # Add a scrollbar
    #     scrollbar = ttk.Scrollbar(view_window, orient=tk.VERTICAL, command=tree.yview)
    #     tree.configure(yscroll=scrollbar.set)
    #     scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    #     tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    #
    #     # Get grievances from database
    #     connection = get_db_connection()
    #     if connection:
    #         try:
    #             cursor = connection.cursor()
    #             query = '''
    #             SELECT id, issue_type, department, status, submitted_at
    #             FROM employee_grievances
    #             WHERE employee_id = %s
    #             ORDER BY submitted_at DESC
    #             '''
    #             cursor.execute(query, (employee_data['id'],))
    #
    #             # Insert data into treeview
    #             for row in cursor.fetchall():
    #                 tree.insert("", tk.END, values=row)
    #
    #             cursor.close()
    #             connection.close()
    #         except mysql.connector.Error as err:
    #             messagebox.showerror("Database Error", f"Error fetching grievances: {err}")
    #             connection.close()
    #
    #     # Close button
    #     close_btn = Button(view_window, text="Close",
    #                        fg='#f7f7f7', bg='#D24545',
    #                        command=view_window.destroy,
    #                        font=font_button)
    #     close_btn.pack(pady=10)
    #
    # # Add View Grievances button
    # view_button = Button(dashboard_window, text="View My Grievances", fg='#f7f7f7', bg='#3468C0',
    #                      activeforeground='#3468C0', activebackground='#FFDD95',
    #                      command=view_my_grievances, font=font_button)
    # view_button.grid(row=6, column=1, padx=(180, 10), pady=10, sticky='w')

    # Back Button
    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    back_button = Button(dashboard_window, text="Back", fg='#f7f7f7', bg='#D24545', activeforeground='#D24545',
                         activebackground='#A94438', command=lambda: feature_back(dashboard_window, parent),
                         font=font_button)
    back_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='w')

    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)

    return dashboard_window


if __name__ == "__main__":
    window = Tk()
    employee_greviance(window)
    window.mainloop()