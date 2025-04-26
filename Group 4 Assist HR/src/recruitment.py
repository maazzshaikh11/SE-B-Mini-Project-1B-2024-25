from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
from tkcalendar import DateEntry


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


def recruitment_management(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Recruitment")
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

    info1_label = Label(dashboard_window, text="Recruitment", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Monitor your organization's hiring process here", fg='#3468C0',
                        bg='#FFDD95',
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
    search_by.set("Role")  # Default search by Role

    search_by_label = Label(search_frame, text="Search By:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    search_by_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')

    columns = ("Role", "Hiring_Status", "Due_Date")
    display_columns = ("Role", "Hiring Status", "Due Date")
    search_by_menu = ttk.Combobox(search_frame, textvariable=search_by, values=display_columns, font=font_entry,
                                  width=15)
    search_by_menu.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    search_button = Button(search_frame, text="Search", bg='#007BFF', fg='white', font=font_button,
                           command=lambda: search_recruitment())
    search_button.grid(row=0, column=4, padx=10, pady=5)

    reset_button = Button(search_frame, text="Reset", bg='#6C757D', fg='white', font=font_button,
                          command=lambda: load_recruitment())
    reset_button.grid(row=0, column=5, padx=10, pady=5)

    # Treeview
    tree = ttk.Treeview(dashboard_window, columns=display_columns, show="headings")

    for i, col in enumerate(display_columns):
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree_scroll_y = Scrollbar(dashboard_window, orient="vertical", command=tree.yview)
    tree_scroll_x = Scrollbar(dashboard_window, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=tree_scroll_y.set, xscroll=tree_scroll_x.set)

    tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    tree_scroll_y.grid(row=3, column=3, sticky='ns')
    tree_scroll_x.grid(row=4, column=0, columnspan=3, sticky='ew')

    # Form for adding/editing recruitment records
    form_frame = Frame(dashboard_window, bg="#FFDD95")
    form_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # Role
    Label(form_frame, text="Role:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=0, padx=5, pady=5,
                                                                                      sticky='e')
    role_entry = Entry(form_frame, font=font_entry)
    role_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # Hiring Status
    Label(form_frame, text="Hiring Status:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=2, padx=5,
                                                                                               pady=5, sticky='e')

    status_var = StringVar()
    status_options = ["Vacant", "Interview Scheduled", "Hired"]
    status_var.set("Vacant")  # Default value
    status_dropdown = ttk.Combobox(form_frame, textvariable=status_var, values=status_options, font=font_entry,
                                   width=15)
    status_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    # Due Date
    Label(form_frame, text="Due Date:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=0, padx=5,
                                                                                          pady=5, sticky='e')
    due_date_entry = DateEntry(form_frame, width=20, background='darkblue', foreground='white', borderwidth=2,
                               font=font_entry)
    due_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    # Store the ID for updates/deletes
    recruitment_id = StringVar()

    # CRUD Functions
    def clear_form():
        role_entry.delete(0, END)
        status_var.set("Vacant")
        due_date_entry.delete(0, END)
        recruitment_id.set("")  # Clear the hidden ID

    def validate_form():
        # Basic validation
        if not role_entry.get().strip():
            messagebox.showerror("Validation Error", "Role is required")
            return False

        # Ensure due date is not empty
        try:
            due_date = due_date_entry.get_date()
        except:
            messagebox.showerror("Validation Error", "Valid due date is required")
            return False

        return True

    def save_recruitment():
        if not validate_form():
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Format the date
            due_date = due_date_entry.get_date().strftime('%Y-%m-%d')

            # If we have a recruitment_id, it's an update
            if recruitment_id.get():
                query = """
                UPDATE recruitment SET 
                Role=%s, Hiring_Status=%s, Due_Date=%s
                WHERE id=%s
                """
                values = (
                    role_entry.get(), status_var.get(), due_date,
                    recruitment_id.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Recruitment record updated successfully!")
            else:
                # It's a new record
                query = """
                INSERT INTO recruitment
                (Role, Hiring_Status, Due_Date)
                VALUES (%s, %s, %s)
                """
                values = (
                    role_entry.get(), status_var.get(), due_date
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Recruitment record added successfully!")

            conn.commit()
            clear_form()
            load_recruitment()  # Refresh the table

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_recruitment():
        # Get the selected item directly from the tree
        selected_item = tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a recruitment record to delete")
            return

        # Get the ID from the selected item
        rec_id = selected_item[0]

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this recruitment record?")
        if not confirm:
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = "DELETE FROM recruitment WHERE id=%s"
            cursor.execute(query, (rec_id,))
            conn.commit()
            messagebox.showinfo("Success", "Recruitment record deleted successfully!")
            clear_form()
            load_recruitment()  # Refresh the table

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def load_recruitment():
        # Clear the treeview
        for item in tree.get_children():
            tree.delete(item)

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = "SELECT id, Role, Hiring_Status, Due_Date FROM recruitment"
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                # Format the date for display
                date_obj = row[3]
                if isinstance(date_obj, datetime):
                    formatted_date = date_obj.strftime('%d %b %Y')
                else:
                    formatted_date = str(date_obj)

                # Store the ID as the item ID in the tree, but don't display it
                display_values = [row[1], row[2], formatted_date]
                tree.insert("", "end", iid=row[0], values=display_values)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_recruitment():
        search_text = search_entry.get().strip()
        search_column = search_by.get().replace(" ", "_")  # Convert display name to DB column name

        if not search_text:
            load_recruitment()  # If search is empty, load all
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
            if search_column == "Due_Date":
                # Handle date search differently
                query = f"SELECT id, Role, Hiring_Status, Due_Date FROM recruitment WHERE DATE_FORMAT(Due_Date, '%d %b %Y') LIKE %s OR DATE_FORMAT(Due_Date, '%Y-%m-%d') LIKE %s"
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            else:
                query = f"SELECT id, Role, Hiring_Status, Due_Date FROM recruitment WHERE {search_column} LIKE %s"
                cursor.execute(query, (f"%{search_text}%",))

            rows = cursor.fetchall()

            for row in rows:
                # Format the date for display
                date_obj = row[3]
                if isinstance(date_obj, datetime):
                    formatted_date = date_obj.strftime('%d %b %Y')
                else:
                    formatted_date = str(date_obj)

                display_values = [row[1], row[2], formatted_date]
                tree.insert("", "end", iid=row[0], values=display_values)

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

        # Get the recruitment ID (stored as the item ID)
        rec_id = selected_item[0]
        recruitment_id.set(rec_id)

        # Get values from the treeview
        values = tree.item(selected_item, "values")

        # Clear form and populate with selected values
        clear_form()
        role_entry.insert(0, values[0])
        status_var.set(values[1])

        # Parse the date string and set it in the date entry
        try:
            # Try to parse date format like "12th February 2025"
            date_str = values[2]
            # If date has format like 12th Feb 2025, convert to proper datetime
            # We need to handle different potential date formats
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    query = "SELECT Due_Date FROM recruitment WHERE id=%s"
                    cursor.execute(query, (rec_id,))
                    date_from_db = cursor.fetchone()[0]

                    if isinstance(date_from_db, datetime):
                        due_date_entry.set_date(date_from_db)
                    else:
                        # Set today as fallback
                        due_date_entry.set_date(datetime.today())
                except:
                    # Set today as fallback
                    due_date_entry.set_date(datetime.today())
                finally:
                    cursor.close()
                    conn.close()
        except:
            # Set today as fallback
            due_date_entry.set_date(datetime.today())

    # Bind the treeview selection event
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Button frame
    button_frame = Frame(dashboard_window, bg="#FFDD95")
    button_frame.grid(row=6, column=0, columnspan=3, pady=10)

    save_button = Button(button_frame, text="Save", bg='#28A745', fg='white', font=font_button,
                         command=save_recruitment)
    save_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Delete", bg='#DC3545', fg='white', font=font_button,
                           command=delete_recruitment)
    delete_button.grid(row=0, column=1, padx=10)

    clear_button = Button(button_frame, text="Clear Form", bg='#FFC107', fg='black', font=font_button,
                          command=clear_form)
    clear_button.grid(row=0, column=2, padx=10)

    # Configure grid weights
    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)
    dashboard_window.grid_rowconfigure(3, weight=1)  # Make the treeview expandable

    # Check if database is properly set up, if not create the table
    def check_db_setup():
        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Check if the table exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recruitment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Role VARCHAR(100) NOT NULL,
                Hiring_Status ENUM('Vacant', 'Interview Scheduled', 'Hired') DEFAULT 'Vacant',
                Due_Date DATE
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

    # Load recruitment data on startup
    load_recruitment()


if __name__ == "__main__":
    window = Tk()
    recruitment_management(window)
    window.mainloop()