import tkinter as tk
from tkinter import messagebox
import mysql.connector
import signup  # Import signup script
import homepage  # Import homepage script for redirection

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'UserManagement'
}

# Global variable to store the logged-in username
logged_in_user = None


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_right = int(screen_width / 2 - width / 2)
    root.geometry(f'{width}x{height}+{position_right}+{position_top}')


def check_login_credentials(username, password):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return bool(user)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return False


def get_sanitized_table_name(org_name):
    # Sanitize table name to avoid issues with special characters
    return org_name.lower().replace(' ', '_').replace('.', '_').replace('-', '_')


def open_login_page():
    global logged_in_user

    root = tk.Tk()
    root.title("Login Page")
    root.configure(bg="#223344")  # Use the same navy-like color scheme

    window_width, window_height = 600, 400
    center_window(root, window_width, window_height)

    label_font = ("Arial", 16, "bold")
    button_font = ("Arial", 14, "bold")

    # Title
    tk.Label(root, text=">> LOGIN <<", font=("Arial", 22, "bold"), fg="#FFD700", bg="#223344").place(x=230, y=30)

    # Username label and entry
    tk.Label(root, text="Username", font=label_font, fg="white", bg="#223344").place(x=100, y=100)
    username_entry = tk.Entry(root, width=30, font=("Arial", 14))
    username_entry.place(x=250, y=100)

    # Password label and entry
    tk.Label(root, text="Password", font=label_font, fg="white", bg="#223344").place(x=100, y=140)
    password_entry = tk.Entry(root, width=30, font=("Arial", 14), show="*")
    password_entry.place(x=250, y=140)

    # Signup button
    def open_signup():
        root.destroy()
        signup.open_signup_page()

    signup_button = tk.Button(root, text="SIGN UP", font=button_font, bg="#FFD700", fg="black", command=open_signup)
    signup_button.place(x=250, y=180)

    # Login function
    def login():
        global logged_in_user
        username, password = username_entry.get(), password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill both username and password")
            return
        if check_login_credentials(username, password):
            logged_in_user = username  # Save the username temporarily
            messagebox.showinfo("Login", f"Login Successful! Welcome, {logged_in_user}")
            print(f"Logged in as: {logged_in_user}")  # Print username for verification
            root.destroy()
            homepage.open_homepage(logged_in_user)  # Pass username to homepage
        else:
            messagebox.showerror("Error", "Invalid username or password")

    # Login and Close buttons
    tk.Button(root, text="Login", font=button_font, bg="#FFD700", fg="black", command=login).place(x=250, y=220)
    tk.Button(root, text="Close", font=button_font, bg="#FFD700", fg="black", command=root.destroy).place(x=400, y=220)

    root.mainloop()


if __name__ == "__main__":
    open_login_page()
