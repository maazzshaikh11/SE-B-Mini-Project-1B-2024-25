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


def upskilling_management(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Upskilling Management")
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

    info1_label = Label(dashboard_window, text="Upskilling Management", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Monitor your employee's skill development here", fg='#3468C0',
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
    search_by.set("Name")  # Default search by Name

    search_by_label = Label(search_frame, text="Search By:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    search_by_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')

    db_columns = ["Employee_Name", "Designation", "Certification", "Sponsored_By_Organization"]
    display_columns = ["Name of the employee", "Designation", "Certification", "Sponsored by organization"]
    search_by_menu = ttk.Combobox(search_frame, textvariable=search_by, values=display_columns, font=font_entry,
                                  width=20)
    search_by_menu.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    search_button = Button(search_frame, text="Search", bg='#007BFF', fg='white', font=font_button,
                           command=lambda: search_upskilling())
    search_button.grid(row=0, column=4, padx=10, pady=5)

    reset_button = Button(search_frame, text="Reset", bg='#6C757D', fg='white', font=font_button,
                          command=lambda: load_upskilling())
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

    # Form for adding/editing upskilling records
    form_frame = Frame(dashboard_window, bg="#FFDD95")
    form_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # Row 1
    Label(form_frame, text="Employee Name:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=0, padx=5,
                                                                                               pady=5, sticky='e')
    name_entry = Entry(form_frame, font=font_entry, width=25)
    name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Designation:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=2, padx=5,
                                                                                             pady=5, sticky='e')
    designation_entry = Entry(form_frame, font=font_entry, width=25)
    designation_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    # Row 2
    Label(form_frame, text="Certification:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=0, padx=5,
                                                                                               pady=5, sticky='e')
    certification_entry = Entry(form_frame, font=font_entry, width=25)
    certification_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Sponsored by Organization:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1,
                                                                                                           column=2,
                                                                                                           padx=5,
                                                                                                           pady=5,
                                                                                                           sticky='e')

    sponsored_var = StringVar()
    sponsored_var.set("NO")  # Default value
    sponsored_frame = Frame(form_frame, bg="#FFDD95")
    sponsored_frame.grid(row=1, column=3, padx=5, pady=5, sticky='w')

    Radiobutton(sponsored_frame, text="YES", variable=sponsored_var, value="YES", bg="#FFDD95", font=font_entry).pack(
        side=LEFT, padx=5)
    Radiobutton(sponsored_frame, text="NO", variable=sponsored_var, value="NO", bg="#FFDD95", font=font_entry).pack(
        side=LEFT, padx=5)

    # Store the ID for updates/deletes
    upskilling_id = StringVar()

    # CRUD Functions
    def clear_form():
        name_entry.delete(0, END)
        designation_entry.delete(0, END)
        certification_entry.delete(0, END)
        sponsored_var.set("NO")
        upskilling_id.set("")  # Clear the hidden ID

    def validate_form():
        # Basic validation
        if not name_entry.get().strip():
            messagebox.showerror("Validation Error", "Employee Name is required")
            return False

        if not designation_entry.get().strip():
            messagebox.showerror("Validation Error", "Designation is required")
            return False

        if not certification_entry.get().strip():
            messagebox.showerror("Validation Error", "Certification is required")
            return False

        return True

    def save_upskilling():
        if not validate_form():
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # If we have an upskilling_id, it's an update
            if upskilling_id.get():
                query = """
                UPDATE upskilling SET 
                Employee_Name=%s, Designation=%s, Certification=%s, Sponsored_By_Organization=%s
                WHERE id=%s
                """
                values = (
                    name_entry.get(), designation_entry.get(), certification_entry.get(),
                    sponsored_var.get(), upskilling_id.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Upskilling record updated successfully!")
            else:
                # It's a new record
                query = """
                INSERT INTO upskilling
                (Employee_Name, Designation, Certification, Sponsored_By_Organization)
                VALUES (%s, %s, %s, %s)
                """
                values = (
                    name_entry.get(), designation_entry.get(), certification_entry.get(),
                    sponsored_var.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Upskilling record added successfully!")

            conn.commit()
            clear_form()
            load_upskilling()  # Refresh the table

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_upskilling():
        # Get the selected item directly from the tree
        selected_item = tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select an upskilling record to delete")
            return

        # Get the ID from the selected item
        up_id = selected_item[0]

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this upskilling record?")
        if not confirm:
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = "DELETE FROM upskilling WHERE id=%s"
            cursor.execute(query, (up_id,))
            conn.commit()
            messagebox.showinfo("Success", "Upskilling record deleted successfully!")
            clear_form()
            load_upskilling()  # Refresh the table

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def load_upskilling():
        # Clear the treeview
        for item in tree.get_children():
            tree.delete(item)

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = """
            SELECT id, Employee_Name, Designation, Certification, Sponsored_By_Organization 
            FROM upskilling
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                # Store the ID as the item ID in the tree, but don't display it
                display_values = row[1:]
                tree.insert("", "end", iid=row[0], values=display_values)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_upskilling():
        search_text = search_entry.get().strip()
        # Map display column name to database column name
        display_to_db = {
            "Name of the employee": "Employee_Name",
            "Designation": "Designation",
            "Certification": "Certification",
            "Sponsored by organization": "Sponsored_By_Organization"
        }
        search_column = display_to_db[search_by.get()]

        if not search_text:
            load_upskilling()  # If search is empty, load all
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
            query = f"""
            SELECT id, Employee_Name, Designation, Certification, Sponsored_By_Organization 
            FROM upskilling 
            WHERE {search_column} LIKE %s
            """
            cursor.execute(query, (f"%{search_text}%",))
            rows = cursor.fetchall()

            for row in rows:
                # Store the ID as the item ID in the tree, but don't display it
                display_values = row[1:]
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

        # Get the upskilling ID (stored as the item ID)
        up_id = selected_item[0]
        upskilling_id.set(up_id)

        # Get values from the treeview
        values = tree.item(selected_item, "values")

        # Clear form and populate with selected values
        clear_form()
        name_entry.insert(0, values[0])
        designation_entry.insert(0, values[1])
        certification_entry.insert(0, values[2])
        sponsored_var.set(values[3])

    # Bind the treeview selection event
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Button frame
    button_frame = Frame(dashboard_window, bg="#FFDD95")
    button_frame.grid(row=6, column=0, columnspan=3, pady=10)

    save_button = Button(button_frame, text="Save", bg='#28A745', fg='white', font=font_button,
                         command=save_upskilling)
    save_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Delete", bg='#DC3545', fg='white', font=font_button,
                           command=delete_upskilling)
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
            CREATE TABLE IF NOT EXISTS upskilling (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Employee_Name VARCHAR(100) NOT NULL,
                Designation VARCHAR(100) NOT NULL,
                Certification VARCHAR(100) NOT NULL,
                Sponsored_By_Organization ENUM('YES', 'NO') DEFAULT 'NO'
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

    # Load upskilling data on startup
    load_upskilling()


if __name__ == "__main__":
    window = Tk()
    upskilling_management(window)
    window.mainloop()