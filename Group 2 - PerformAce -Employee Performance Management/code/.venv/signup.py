import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime
import mysql.connector
import re
import login  # Import login script to redirect back

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'UserManagement'
}


def insert_user_data(full_name, dob, contact_no, email, username, password):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO users (full_name, dob, contact_no, email, username, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (full_name, dob, contact_no, email, username, password))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.IntegrityError as err:
        if "username" in str(err):
            messagebox.showerror("Error", "Username already exists.")
        elif "email" in str(err):
            messagebox.showerror("Error", "Email already exists.")
        return False
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return False


def validate_dob(dob):
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 18:
        return "You must be at least 18 years old."
    return True


def signup(entry_name, entry_dob, entry_contact, entry_email, entry_username, entry_password, root):
    name = entry_name.get().strip()
    dob = entry_dob.get_date()
    contact = entry_contact.get().strip()
    email = entry_email.get().strip()
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not all([name, contact, email, username, password]):
        messagebox.showerror("Error", "Please fill all fields.")
        return

    dob_valid = validate_dob(dob)
    if dob_valid != True:
        messagebox.showerror("Error", dob_valid)
        return

    if not contact.isdigit() or len(contact) != 10:
        messagebox.showerror("Error", "Contact number must be 10 digits.")
        return

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        messagebox.showerror("Error", "Invalid email address.")
        return

    if insert_user_data(name, dob, contact, email, username, password):
        messagebox.showinfo("Success", "Signup Successful!")
        root.destroy()
        login.open_login_page()  # Redirect to login page


def center_window(window):
    window.update()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def open_signup_page():
    root = tk.Tk()
    root.title("Signup Page")
    root.geometry("600x400")
    root.configure(bg="#223344")

    main_frame = tk.Frame(root, bg="#223344")
    main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    labels_config = {"fg": "white", "bg": "#223344", "font": ("Arial", 12, "bold")}

    tk.Label(main_frame, text="Full Name:", **labels_config).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_name = tk.Entry(main_frame)
    entry_name.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Date of Birth:", **labels_config).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_dob = DateEntry(main_frame, date_pattern="dd/mm/yyyy")
    entry_dob.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Contact No:", **labels_config).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_contact = tk.Entry(main_frame)
    entry_contact.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Email:", **labels_config).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_email = tk.Entry(main_frame)
    entry_email.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Username:", **labels_config).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_username = tk.Entry(main_frame)
    entry_username.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Password:", **labels_config).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    entry_password = tk.Entry(main_frame, show="*")
    entry_password.grid(row=5, column=1, padx=10, pady=10)

    signup_button = tk.Button(main_frame, text="Signup", bg="gold", fg="black",
                               command=lambda: signup(entry_name, entry_dob, entry_contact, entry_email, entry_username, entry_password, root))
    signup_button.grid(row=6, column=1, pady=10)

    back_button = tk.Button(main_frame, text="Back", bg="gold", fg="black",
                             command=lambda: [root.destroy(), login.open_login_page()])
    back_button.grid(row=6, column=0, pady=10)

    center_window(root)
    root.mainloop()


if __name__ == "__main__":
    open_signup_page()
