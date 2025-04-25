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


def payroll_management(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Payroll Management")
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

    info1_label = Label(dashboard_window, text="Payroll Management", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Manage your organization's payroll here", fg='#3468C0', bg='#FFDD95',
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

    columns = ("Name", "Full_CTC", "In_hand", "Allowance", "Bonus", "Status")
    display_columns = ("Name", "Full CTC", "In-hand", "Allowance", "Bonus", "Status")
    search_by_menu = ttk.Combobox(search_frame, textvariable=search_by, values=display_columns, font=font_entry,
                                  width=15)
    search_by_menu.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    search_button = Button(search_frame, text="Search", bg='#007BFF', fg='white', font=font_button,
                           command=lambda: search_payroll())
    search_button.grid(row=0, column=4, padx=10, pady=5)

    reset_button = Button(search_frame, text="Reset", bg='#6C757D', fg='white', font=font_button,
                          command=lambda: load_payroll())
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

    # Form for adding/editing payroll
    form_frame = Frame(dashboard_window, bg="#FFDD95")
    form_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    # Row 1
    Label(form_frame, text="Name:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=0, padx=5, pady=5,
                                                                                      sticky='e')
    name_entry = Entry(form_frame, font=font_entry)
    name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Full CTC:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=0, column=2, padx=5,
                                                                                          pady=5, sticky='e')
    ctc_entry = Entry(form_frame, font=font_entry)
    ctc_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    # Row 2
    Label(form_frame, text="In-hand:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=0, padx=5,
                                                                                         pady=5, sticky='e')
    inhand_entry = Entry(form_frame, font=font_entry)
    inhand_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Allowance:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=1, column=2, padx=5,
                                                                                           pady=5, sticky='e')
    allowance_entry = Entry(form_frame, font=font_entry)
    allowance_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')

    # Row 3
    Label(form_frame, text="Bonus:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=2, column=0, padx=5, pady=5,
                                                                                       sticky='e')
    bonus_entry = Entry(form_frame, font=font_entry)
    bonus_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

    Label(form_frame, text="Status:", fg='#3468C0', bg='#FFDD95', font=font_info2).grid(row=2, column=2, padx=5, pady=5,
                                                                                        sticky='e')

    status_var = StringVar()
    status_values = ["Active", "On Leave", "Resigned", "Terminated"]
    status_var.set("Active")  # Default value
    status_dropdown = ttk.Combobox(form_frame, textvariable=status_var, values=status_values, font=font_entry, width=15)
    status_dropdown.grid(row=2, column=3, padx=5, pady=5, sticky='w')

    # Store the ID for updates/deletes
    payroll_id = StringVar()

    # CRUD Functions
    def clear_form():
        name_entry.delete(0, END)
        ctc_entry.delete(0, END)
        inhand_entry.delete(0, END)
        allowance_entry.delete(0, END)
        bonus_entry.delete(0, END)
        status_var.set("Active")
        payroll_id.set("")  # Clear the hidden ID

    def validate_form():
        # Basic validation
        if not name_entry.get().strip():
            messagebox.showerror("Validation Error", "Name is required")
            return False

        # Validate numeric fields
        try:
            # Remove currency symbols and commas for validation
            if ctc_entry.get().strip():
                clean_ctc = ctc_entry.get().strip().replace('$', '').replace(',', '')
                float(clean_ctc)
            if inhand_entry.get().strip():
                clean_inhand = inhand_entry.get().strip().replace('$', '').replace(',', '')
                float(clean_inhand)
            if allowance_entry.get().strip():
                clean_allowance = allowance_entry.get().strip().replace('$', '').replace(',', '')
                float(clean_allowance)
            if bonus_entry.get().strip():
                clean_bonus = bonus_entry.get().strip().replace('$', '').replace(',', '')
                float(clean_bonus)
        except ValueError:
            messagebox.showerror("Validation Error", "Monetary values must be numeric")
            return False

        return True

    def format_currency(value):
        if not value:
            return ""
        # Remove existing formatting if any
        clean_value = value.replace('$', '').replace(',', '')
        try:
            # Format as currency
            amount = float(clean_value)
            return f"${amount:,.2f}"
        except ValueError:
            return value

    def save_payroll():
        if not validate_form():
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Format currency fields
            formatted_ctc = format_currency(ctc_entry.get())
            formatted_inhand = format_currency(inhand_entry.get())
            formatted_allowance = format_currency(allowance_entry.get())
            formatted_bonus = format_currency(bonus_entry.get())

            # If we have a payroll_id, it's an update
            if payroll_id.get():
                query = """
                UPDATE payroll_management SET 
                Name=%s, Full_CTC=%s, In_hand=%s, Allowance=%s, Bonus=%s, Status=%s
                WHERE id=%s
                """
                values = (
                    name_entry.get(), formatted_ctc, formatted_inhand,
                    formatted_allowance, formatted_bonus, status_var.get(),
                    payroll_id.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Payroll updated successfully!")
            else:
                # It's a new record
                query = """
                INSERT INTO payroll_management
                (Name, Full_CTC, In_hand, Allowance, Bonus, Status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    name_entry.get(), formatted_ctc, formatted_inhand,
                    formatted_allowance, formatted_bonus, status_var.get()
                )
                cursor.execute(query, values)
                messagebox.showinfo("Success", "Payroll added successfully!")

            conn.commit()
            clear_form()
            load_payroll()  # Refresh the table

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_payroll():
        # Get selected item
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a payroll record to delete")
            return

        # Get the payroll ID (stored as the item ID)
        selected_id = selected_item[0]

        # Confirm delete
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this payroll record?")
        if not confirm:
            return

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            query = "DELETE FROM payroll_management WHERE id=%s"
            cursor.execute(query, (selected_id,))
            conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Payroll record deleted successfully!")
                clear_form()
                load_payroll()  # Refresh the table
            else:
                messagebox.showerror("Error", "No record was deleted. The record may no longer exist.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def load_payroll():
        # Clear the treeview
        for item in tree.get_children():
            tree.delete(item)

        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Note: column names in the database use underscores
            query = "SELECT id, Name, Full_CTC, In_hand, Allowance, Bonus, Status FROM payroll_management"
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

    def search_payroll():
        search_text = search_entry.get().strip()
        search_column = search_by.get().replace(" ", "_")  # Convert display name to DB column name

        if not search_text:
            load_payroll()  # If search is empty, load all
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
            query = f"SELECT id, Name, Full_CTC, In_hand, Allowance, Bonus, Status FROM payroll_management WHERE {search_column} LIKE %s"
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

        # Get the payroll ID (stored as the item ID)
        pay_id = selected_item[0]
        payroll_id.set(pay_id)

        # Get values from the treeview
        values = tree.item(selected_item, "values")

        # Clear form and populate with selected values
        clear_form()
        name_entry.insert(0, values[0])
        ctc_entry.insert(0, values[1])
        inhand_entry.insert(0, values[2])
        allowance_entry.insert(0, values[3])
        bonus_entry.insert(0, values[4])
        status_var.set(values[5])

    # Bind the treeview selection event
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Button frame
    button_frame = Frame(dashboard_window, bg="#FFDD95")
    button_frame.grid(row=6, column=0, columnspan=3, pady=10)

    save_button = Button(button_frame, text="Save", bg='#28A745', fg='white', font=font_button, command=save_payroll)
    save_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Delete", bg='#DC3545', fg='white', font=font_button,
                           command=delete_payroll)
    delete_button.grid(row=0, column=1, padx=10)

    clear_button = Button(button_frame, text="Clear Form", bg='#FFC107', fg='black', font=font_button,
                          command=clear_form)
    clear_button.grid(row=0, column=2, padx=10)

    # Configure grid weights
    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)
    dashboard_window.grid_rowconfigure(3, weight=1)  # Make the treeview expandable

    # Load payroll data on startup
    load_payroll()

    # Check if database is properly set up, if not create the table
    def check_db_setup():
        conn = connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Check if the table exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll_management (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Full_CTC VARCHAR(50),
                In_hand VARCHAR(50),
                Allowance VARCHAR(50),
                Bonus VARCHAR(50),
                Status VARCHAR(30)
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
    payroll_management(window)
    window.mainloop()