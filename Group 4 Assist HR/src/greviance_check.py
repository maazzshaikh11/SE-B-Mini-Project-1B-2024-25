from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime


# Function to connect to the MySQL database
def connect_to_database():
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


def grievance_check(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Grievance Check")
    dashboard_window.configure(background="#FFDD95")

    # Positioning the application
    window_width = 1000
    window_height = 600
    screen_width = dashboard_window.winfo_screenwidth()
    screen_height = dashboard_window.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    dashboard_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Setting up fonts
    font_info1 = ('Arial', 30, 'italic')
    font_info2 = ('Arial', 15, 'italic')
    font_button = ('Arial', 15, 'bold')

    # Labels
    info1_label = Label(dashboard_window, text="Grievance Check", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Check your employee's Grievance Status", fg='#3468C0', bg='#FFDD95',
                        font=font_info2)
    info2_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    # Back button function
    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    back_button = Button(dashboard_window, text="Back", fg='#f7f7f7', bg='#D24545', activeforeground='#D24545',
                         activebackground='#A94438', command=lambda: feature_back(dashboard_window, parent),
                         font=font_button)
    back_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='w')

    # Search bar
    search_label = Label(dashboard_window, text="Search:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    search_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

    search_entry = Entry(dashboard_window, font=('Arial', 12))
    search_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    # Search button
    def search_grievances():
        search_text = search_entry.get().strip().lower()

        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)

        # Fetch filtered data from database
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()

            query = """
            SELECT employee_name, department, issue_type, status, grievance_text, id, employee_id, submitted_at 
            FROM employee_grievances 
            WHERE LOWER(employee_name) LIKE %s 
            OR LOWER(department) LIKE %s 
            OR LOWER(issue_type) LIKE %s 
            OR LOWER(status) LIKE %s
            """

            search_param = f"%{search_text}%"
            cursor.execute(query, (search_param, search_param, search_param, search_param))

            for (
            employee_name, department, issue_type, status, grievance_text, id, employee_id, submitted_at) in cursor:
                tree.insert("", "end", values=(employee_name, department, issue_type, status,
                                               grievance_text[:30] + "..." if len(
                                                   grievance_text) > 30 else grievance_text, id, employee_id,
                                               submitted_at))

            cursor.close()
            connection.close()

    search_button = Button(dashboard_window, text="Search", bg='#007BFF', fg='white', font=font_info2,
                           command=search_grievances)
    search_button.grid(row=2, column=2, padx=10, pady=5, sticky='w')

    # Grievance Table
    columns = ("Employee Name", "Department", "Issue Type", "Status", "Resolution", "ID", "Employee ID", "Submitted At")
    tree = ttk.Treeview(dashboard_window, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        if col in ["ID", "Employee ID"]:
            tree.column(col, width=50)
        elif col == "Submitted At":
            tree.column(col, width=150)
        else:
            tree.column(col, width=150)

    # Hide ID and Employee ID columns (they're for internal reference)
    tree.column("ID", width=0, stretch=NO)
    tree.column("Employee ID", width=0, stretch=NO)

    # Scrollbars
    tree_scroll_y = Scrollbar(dashboard_window, orient="vertical", command=tree.yview)
    tree_scroll_x = Scrollbar(dashboard_window, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=tree_scroll_y.set, xscroll=tree_scroll_x.set)

    tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    tree_scroll_y.grid(row=3, column=3, sticky='ns')
    tree_scroll_x.grid(row=4, column=0, columnspan=3, sticky='ew')

    # Function to load all grievances from database
    def load_grievances():
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)

        # Connect to database and fetch data
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()

            query = """
            SELECT employee_name, department, issue_type, status, grievance_text, id, employee_id, submitted_at 
            FROM employee_grievances 
            ORDER BY submitted_at DESC
            """

            cursor.execute(query)

            for (
            employee_name, department, issue_type, status, grievance_text, id, employee_id, submitted_at) in cursor:
                tree.insert("", "end", values=(employee_name, department, issue_type, status,
                                               grievance_text[:30] + "..." if len(
                                                   grievance_text) > 30 else grievance_text, id, employee_id,
                                               submitted_at))

            cursor.close()
            connection.close()

    # Function to open grievance detail window
    def view_grievance_details():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a grievance to view details")
            return

        # Get the values of the selected item
        values = tree.item(selected_item[0], 'values')
        grievance_id = values[5]  # ID is at index 5

        # Create a new window for details
        detail_window = Toplevel(dashboard_window)
        detail_window.title("Grievance Details")
        detail_window.configure(background="#FFDD95")
        detail_window.geometry("600x500")

        # Connect to database to get complete details
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()

            query = """
            SELECT employee_name, department, issue_type, status, grievance_text, employee_id, submitted_at 
            FROM employee_grievances 
            WHERE id = %s
            """

            cursor.execute(query, (grievance_id,))
            result = cursor.fetchone()

            if result:
                employee_name, department, issue_type, status, grievance_text, employee_id, submitted_at = result

                # Create labels and entry fields for all details
                Label(detail_window, text="Grievance Details", font=font_info1, bg="#FFDD95", fg="#3468C0").grid(row=0,
                                                                                                                 column=0,
                                                                                                                 columnspan=2,
                                                                                                                 pady=10)

                Label(detail_window, text="Employee Name:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=1,
                                                                                                              column=0,
                                                                                                              padx=10,
                                                                                                              pady=5,
                                                                                                              sticky='w')
                name_var = StringVar(value=employee_name)
                Entry(detail_window, textvariable=name_var, font=('Arial', 12), state='readonly').grid(row=1, column=1,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky='w')

                Label(detail_window, text="Department:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=2,
                                                                                                           column=0,
                                                                                                           padx=10,
                                                                                                           pady=5,
                                                                                                           sticky='w')
                dept_var = StringVar(value=department)
                Entry(detail_window, textvariable=dept_var, font=('Arial', 12), state='readonly').grid(row=2, column=1,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky='w')

                Label(detail_window, text="Issue Type:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=3,
                                                                                                           column=0,
                                                                                                           padx=10,
                                                                                                           pady=5,
                                                                                                           sticky='w')
                issue_var = StringVar(value=issue_type)
                Entry(detail_window, textvariable=issue_var, font=('Arial', 12), state='readonly').grid(row=3, column=1,
                                                                                                        padx=10, pady=5,
                                                                                                        sticky='w')

                Label(detail_window, text="Status:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=4, column=0,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky='w')
                status_var = StringVar(value=status)
                status_combo = ttk.Combobox(detail_window, textvariable=status_var, font=('Arial', 12),
                                            values=["Pending", "In Progress", "Resolved", "Closed"])
                status_combo.grid(row=4, column=1, padx=10, pady=5, sticky='w')

                Label(detail_window, text="Grievance Text:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=5,
                                                                                                               column=0,
                                                                                                               padx=10,
                                                                                                               pady=5,
                                                                                                               sticky='w')
                grievance_text_widget = Text(detail_window, font=('Arial', 12), width=40, height=10)
                grievance_text_widget.grid(row=5, column=1, padx=10, pady=5, sticky='w')
                grievance_text_widget.insert('1.0', grievance_text)

                Label(detail_window, text="Submitted At:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=6,
                                                                                                             column=0,
                                                                                                             padx=10,
                                                                                                             pady=5,
                                                                                                             sticky='w')
                date_var = StringVar(
                    value=submitted_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(submitted_at, datetime) else str(
                        submitted_at))
                Entry(detail_window, textvariable=date_var, font=('Arial', 12), state='readonly').grid(row=6, column=1,
                                                                                                       padx=10, pady=5,
                                                                                                       sticky='w')

                # Save button function
                def save_changes():
                    # Get values from entry fields
                    new_status = status_var.get()

                    # Update database
                    update_connection = connect_to_database()
                    if update_connection:
                        update_cursor = update_connection.cursor()

                        update_query = """
                        UPDATE employee_grievances 
                        SET status = %s
                        WHERE id = %s
                        """

                        update_cursor.execute(update_query, (new_status, grievance_id))
                        update_connection.commit()

                        update_cursor.close()
                        update_connection.close()

                        messagebox.showinfo("Success", "Grievance status updated successfully!")
                        detail_window.destroy()
                        # Refresh the main list
                        load_grievances()

                # Save button
                Button(detail_window, text="Save Changes", bg='#28A745', fg='white', font=font_button,
                       command=save_changes).grid(row=7, column=1, padx=10, pady=20, sticky='e')

                # Close button
                Button(detail_window, text="Close", bg='#DC3545', fg='white', font=font_button,
                       command=detail_window.destroy).grid(row=7, column=0, padx=10, pady=20, sticky='w')

            cursor.close()
            connection.close()

    # Function to add a new grievance
    def add_grievance():
        add_window = Toplevel(dashboard_window)
        add_window.title("Add New Grievance")
        add_window.configure(background="#FFDD95")
        add_window.geometry("600x500")

        Label(add_window, text="Add New Grievance", font=font_info1, bg="#FFDD95", fg="#3468C0").grid(row=0, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=10)

        Label(add_window, text="Employee ID:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=1, column=0,
                                                                                                 padx=10, pady=5,
                                                                                                 sticky='w')
        emp_id_var = StringVar()
        Entry(add_window, textvariable=emp_id_var, font=('Arial', 12)).grid(row=1, column=1, padx=10, pady=5,
                                                                            sticky='w')

        Label(add_window, text="Employee Name:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=2, column=0,
                                                                                                   padx=10, pady=5,
                                                                                                   sticky='w')
        name_var = StringVar()
        Entry(add_window, textvariable=name_var, font=('Arial', 12)).grid(row=2, column=1, padx=10, pady=5, sticky='w')

        Label(add_window, text="Department:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=3, column=0,
                                                                                                padx=10, pady=5,
                                                                                                sticky='w')
        dept_var = StringVar()
        dept_combo = ttk.Combobox(add_window, textvariable=dept_var, font=('Arial', 12),
                                  values=["HR", "IT", "Finance", "Marketing", "Sales", "Operations"])
        dept_combo.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        Label(add_window, text="Issue Type:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=4, column=0,
                                                                                                padx=10, pady=5,
                                                                                                sticky='w')
        issue_var = StringVar()
        issue_combo = ttk.Combobox(add_window, textvariable=issue_var, font=('Arial', 12),
                                   values=["Salary Issue", "Workplace Harassment", "Unfair Appraisal",
                                           "Workload Stress", "Leave Policy", "Other"])
        issue_combo.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        Label(add_window, text="Grievance Text:", font=font_info2, bg="#FFDD95", fg="#3468C0").grid(row=5, column=0,
                                                                                                    padx=10, pady=5,
                                                                                                    sticky='w')
        grievance_text_widget = Text(add_window, font=('Arial', 12), width=40, height=10)
        grievance_text_widget.grid(row=5, column=1, padx=10, pady=5, sticky='w')

        # Save function
        def save_new_grievance():
            # Get values from entry fields
            emp_id = emp_id_var.get()
            name = name_var.get()
            dept = dept_var.get()
            issue = issue_var.get()
            grievance_text = grievance_text_widget.get('1.0', END).strip()

            # Validate input
            if not (emp_id and name and dept and issue and grievance_text):
                messagebox.showerror("Error", "All fields are required")
                return

            # Insert into database
            connection = connect_to_database()
            if connection:
                cursor = connection.cursor()

                insert_query = """
                INSERT INTO employee_grievances 
                (employee_id, employee_name, department, issue_type, grievance_text, status, submitted_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                now = datetime.now()
                cursor.execute(insert_query, (emp_id, name, dept, issue, grievance_text, "Pending", now))
                connection.commit()

                cursor.close()
                connection.close()

                messagebox.showinfo("Success", "Grievance added successfully!")
                add_window.destroy()
                # Refresh the main list
                load_grievances()

        # Save button
        Button(add_window, text="Save", bg='#28A745', fg='white', font=font_button, command=save_new_grievance).grid(
            row=6, column=1, padx=10, pady=20, sticky='e')

        # Cancel button
        Button(add_window, text="Cancel", bg='#DC3545', fg='white', font=font_button, command=add_window.destroy).grid(
            row=6, column=0, padx=10, pady=20, sticky='w')

    # Function to delete a grievance
    def delete_grievance():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a grievance to delete")
            return

        # Confirm before deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this grievance?"):
            return

        # Get the values of the selected item
        values = tree.item(selected_item[0], 'values')
        grievance_id = values[5]  # ID is at index 5

        # Delete from database
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()

            delete_query = "DELETE FROM employee_grievances WHERE id = %s"
            cursor.execute(delete_query, (grievance_id,))
            connection.commit()

            cursor.close()
            connection.close()

            messagebox.showinfo("Success", "Grievance deleted successfully!")
            # Refresh the list
            load_grievances()

    # Buttons below the table
    button_frame = Frame(dashboard_window, bg="#FFDD95")
    button_frame.grid(row=5, column=0, columnspan=3, pady=10)

    add_button = Button(button_frame, text="Add", bg='#28A745', fg='white', font=font_button, command=add_grievance)
    add_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Delete", bg='#DC3545', fg='white', font=font_button,
                           command=delete_grievance)
    delete_button.grid(row=0, column=1, padx=10)

    update_button = Button(button_frame, text="View/Update", bg='#007BFF', fg='white', font=font_button,
                           command=view_grievance_details)
    update_button.grid(row=0, column=2, padx=10)

    # Refresh button
    refresh_button = Button(button_frame, text="Refresh", bg='#6C757D', fg='white', font=font_button,
                            command=load_grievances)
    refresh_button.grid(row=0, column=3, padx=10)

    # Configure column sizes
    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)
    dashboard_window.grid_rowconfigure(3, weight=1)

    # Load grievances initially
    load_grievances()


if __name__ == "__main__":
    window = Tk()
    grievance_check(window)
    window.mainloop()