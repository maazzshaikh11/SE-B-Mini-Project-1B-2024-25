from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime


# Database connection function
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="CHIR2502004|",  # Replace with your MySQL password
            database="hrassistance"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Connection Error", f"Error: {err}")
        return None


def employee_management(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Employee Management")
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
    font_entry = ('Arial', 12)

    info1_label = Label(dashboard_window, text="Employee Management", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Manage your organization's employees here", fg='#3468C0', bg='#FFDD95',
                        font=font_info2)
    info2_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    Back = Button(dashboard_window, text="Back", fg='#f7f7f7', bg='#D24545', activeforeground='#D24545',
                  activebackground='#A94438', command=lambda: feature_back(dashboard_window, parent), font=font_button)
    Back.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='w')

    # Search functionality
    search_frame = Frame(dashboard_window, bg="#FFDD95")
    search_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky='ew')

    search_label = Label(search_frame, text="Search:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    search_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

    search_entry = Entry(search_frame, font=font_entry, width=30)
    search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    search_by = StringVar()
    search_by.set("Name")  # Default search by Name

    search_by_label = Label(search_frame, text="Search By:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    search_by_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')

    columns = ("Name", "DOB", "Department", "Role", "Education", "Marks", "Experience", "Salary", "Location")
    search_by_menu = ttk.Combobox(search_frame, textvariable=search_by, values=columns, font=font_entry, width=15)
    search_by_menu.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    search_button = Button(search_frame, text="Search", bg='#007BFF', fg='white', font=font_button,
                           command=lambda: search_employees())
    search_button.grid(row=0, column=4, padx=10, pady=5)

    reset_button = Button(search_frame, text="Reset", bg='#6C757D', fg='white', font=font_button,
                          command=lambda: load_employees())
    reset_button.grid(row=0, column=5, padx=10, pady=5)

    # Treeview
    tree = ttk.Treeview(dashboard_window, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree_scroll_y = Scrollbar(dashboard_window, orient="vertical", command=tree.yview)
    tree_scroll_x = Scrollbar(dashboard_window, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=tree_scroll_y.set, xscroll=tree_scroll_x.set)

    tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    tree_scroll_y.grid(row=3, column=3, sticky='ns')
    tree_scroll_x.grid(row=4, column=0, columnspan=3, sticky='ew')

    # Form for adding/editing employees
    form_frame = Frame(dashboard_window, bg="#FFDD95")
    form_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # Row 1
    Label(form_frame, text="Name:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=0, padx=5, pady=5,
                                                                                      sticky='e')
    name_entry = Entry(form_frame, font=font_entry)
    name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="DOB (YYYY-MM-DD):", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=2,
                                                                                                  padx=5, pady=5,
                                                                                                  sticky='e')
    dob_entry = Entry(form_frame, font=font_entry)
    dob_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Department:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=4, padx=5,
                                                                                            pady=5, sticky='e')
    dept_entry = Entry(form_frame, font=font_entry)
    dept_entry.grid(row=0, column=5, padx=5, pady=5, sticky='w')

    # Row 2
    Label(form_frame, text="Role:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=0, padx=5, pady=5,
                                                                                      sticky='e')
    role_entry = Entry(form_frame, font=font_entry)
    role_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Education (Latest):", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=2, padx=5,
                                                                                           pady=5, sticky='e')
    education_entry = Entry(form_frame, font=font_entry)
    education_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Marks (CGPA):", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=4, padx=5, pady=5,
                                                                                       sticky='e')
    marks_entry = Entry(form_frame, font=font_entry)
    marks_entry.grid(row=1, column=5, padx=5, pady=5, sticky='w')

    # Row 3
    Label(form_frame, text="Experience:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=2, column=0, padx=5,
                                                                                            pady=5, sticky='e')
    exp_entry = Entry(form_frame, font=font_entry)
    exp_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Salary:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=2, column=2, padx=5, pady=5,
                                                                                        sticky='e')
    salary_entry = Entry(form_frame, font=font_entry)
    salary_entry.grid(row=2, column=3, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Location:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=2, column=4, padx=5,
                                                                                          pady=5, sticky='e')
    location_entry = Entry(form_frame, font=font_entry)
    location_entry.grid(row=2, column=5, padx=5, pady=5, sticky='w')

    # Store the ID for updates/deletes
    employee_id = StringVar()

    # CRUD Functions
    def clear_form():
        name_entry.delete(0, END)
        dob_entry.delete(0, END)
        dept_entry.delete(0, END)
        role_entry.delete(0, END)
        education_entry.delete(0, END)
        marks_entry.delete(0, END)
        exp_entry.delete(0, END)
        salary_entry.delete(0, END)
        location_entry.delete(0, END)
        employee_id.set("")  # Clear the hidden ID

    def validate_form():
        # Basic validation
        if not name_entry.get().strip():
            messagebox.showerror("Validation Error", "Name is required")
            return False

        try:
            # Validate date format
            if dob_entry.get().strip():
                datetime.strptime(dob_entry.get().strip(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "DOB must be in YYYY-MM-DD format")
            return False

        return True

    def save_employee():
        if not validate_form():
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # If we have an employee_id, it's an update
            if employee_id.get():
                query = """
                UPDATE employee_managment SET 
                Name=%s, DOB=%s, Department=%s, Role=%s, Education=%s, 
                Marks=%s, Experience=%s, Salary=%s, Location=%s 
                WHERE id=%s
                """
                values = (
                    name_entry.get(), dob_entry.get(), dept_entry.get(),
                    role_entry.get(), education_entry.get(), marks_entry.get(),
                    exp_entry.get(), salary_entry.get(), location_entry.get(),
                    employee_id.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Employee updated successfully!")
            else:
                # It's a new record
                query = """
                INSERT INTO employee_managment
                (Name, DOB, Department, Role, Education, Marks, Experience, Salary, Location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    name_entry.get(), dob_entry.get(), dept_entry.get(),
                    role_entry.get(), education_entry.get(), marks_entry.get(),
                    exp_entry.get(), salary_entry.get(), location_entry.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Employee added successfully!")

            conn.commit()
            clear_form()
            load_employees()  # Refresh the table

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_employee():
        if not tree.selection():
            messagebox.showerror("Error", "Please select an employee to delete")
            return

        # Get the selected item ID directly from the tree
        selected_id = tree.selection()[0]

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?")
        if not confirm:
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = "DELETE FROM employee_managment WHERE id=%s"
            cursor.execute(query, (selected_id,))
            conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Employee deleted successfully!")
                clear_form()
                load_employees()  # Refresh the table
            else:
                messagebox.showwarning("Warning", "No employee was deleted. ID may not exist in database.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def load_employees():
        # Clear the treeview
        for item in tree.get_children():
            tree.delete(item)

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = "SELECT id, Name, DOB, Department, Role, Education, Marks, Experience, Salary, Location FROM employee_managment"
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                # Store the ID as the item ID in the tree, but don't display it
                tree.insert("", "end", iid=row[0], values=row[1:])

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_employees():
        search_text = search_entry.get().strip()
        search_column = search_by.get()

        if not search_text:
            load_employees()  # If search is empty, load all
            return

        # Clear the treeview
        for item in tree.get_children():
            tree.delete(item)

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Use LIKE for partial matching
            query = f"SELECT id, Name, DOB, Department, Role, Education, Marks, Experience, Salary, Location FROM employee_managment WHERE {search_column} LIKE %s"
            cursor.execute(query, (f"%{search_text}%",))
            rows = cursor.fetchall()

            for row in rows:
                # Store the ID as the item ID in the tree, but don't display it
                tree.insert("", "end", iid=row[0], values=row[1:])

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def on_tree_select(event):
        # Get selected item
        selected_item = tree.selection()
        if not selected_item:
            return

        # Get the employee ID (stored as the item ID)
        emp_id = selected_item[0]
        employee_id.set(emp_id)

        # Get values from the treeview
        values = tree.item(selected_item, "values")

        # Clear form and populate with selected values
        clear_form()
        name_entry.insert(0, values[0])
        dob_entry.insert(0, values[1])
        dept_entry.insert(0, values[2])
        role_entry.insert(0, values[3])
        education_entry.insert(0, values[4])
        marks_entry.insert(0, values[5])
        exp_entry.insert(0, values[6])
        salary_entry.insert(0, values[7])
        location_entry.insert(0, values[8])

    # Bind the treeview selection event
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Button frame
    button_frame = Frame(dashboard_window, bg="#FFDD95")
    button_frame.grid(row=6, column=0, columnspan=3, pady=10)

    save_button = Button(button_frame, text="Save", bg='#28A745', fg='white', font=font_button, command=save_employee)
    save_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Delete", bg='#DC3545', fg='white', font=font_button,
                           command=delete_employee)
    delete_button.grid(row=0, column=1, padx=10)

    clear_button = Button(button_frame, text="Clear Form", bg='#FFC107', fg='black', font=font_button,
                          command=clear_form)
    clear_button.grid(row=0, column=2, padx=10)

    # Configure grid weights
    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)
    dashboard_window.grid_rowconfigure(3, weight=1)  # Make the treeview expandable

    # Load employees on startup
    load_employees()

    # Check if database is properly set up, if not create the table
    def check_db_setup():
        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Check if the table exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_managment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                DOB DATE,
                Department VARCHAR(50),
                Role VARCHAR(50),
                Education VARCHAR(50),
                Marks VARCHAR(20),
                Experience VARCHAR(30),
                Salary VARCHAR(30),
                Location VARCHAR(100)
            )
            """)
            conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Setup Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    # Run DB setup check
    check_db_setup()


if __name__ == "__main__":
    window = Tk()
    employee_management(window)
    window.mainloop()