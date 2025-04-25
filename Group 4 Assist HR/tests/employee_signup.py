import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re


class EmployeeSignupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Signup")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")

        # Center the window
        window_width = 500
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Fonts
        self.title_font = ('Arial', 24, 'bold')
        self.label_font = ('Arial', 12)
        self.entry_font = ('Arial', 12)
        self.button_font = ('Arial', 12, 'bold')

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="Employee Signup",
            font=self.title_font,
            bg="#f0f0f0",
            fg="#333333"
        )
        self.title_label.pack(pady=(0, 20))

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.form_frame.pack(fill=tk.BOTH, expand=True)

        # Employee Gmail
        self.emp_gmail_label = tk.Label(
            self.form_frame,
            text="Employee Gmail:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="e"
        )
        self.emp_gmail_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)

        self.emp_gmail_var = tk.StringVar()
        self.emp_gmail_entry = tk.Entry(
            self.form_frame,
            textvariable=self.emp_gmail_var,
            font=self.entry_font,
            width=25
        )
        self.emp_gmail_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        # Employee Name
        self.emp_name_label = tk.Label(
            self.form_frame,
            text="Employee Name:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="e"
        )
        self.emp_name_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)

        self.emp_name_var = tk.StringVar()
        self.emp_name_entry = tk.Entry(
            self.form_frame,
            textvariable=self.emp_name_var,
            font=self.entry_font,
            width=25
        )
        self.emp_name_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        # Password
        self.password_label = tk.Label(
            self.form_frame,
            text="Password:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="e"
        )
        self.password_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.password_var,
            font=self.entry_font,
            width=25,
            show="*"
        )
        self.password_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)

        # Confirm Password
        self.confirm_password_label = tk.Label(
            self.form_frame,
            text="Confirm Password:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="e"
        )
        self.confirm_password_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)

        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.confirm_password_var,
            font=self.entry_font,
            width=25,
            show="*"
        )
        self.confirm_password_entry.grid(row=3, column=1, sticky="w", padx=10, pady=10)

        # Button Frame
        self.button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, pady=20)

        # Signup Button
        self.signup_button = tk.Button(
            self.button_frame,
            text="Sign Up",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            command=self.signup
        )
        self.signup_button.pack(side=tk.LEFT, padx=10)

        # Clear Button
        self.clear_button = tk.Button(
            self.button_frame,
            text="Clear",
            font=self.button_font,
            bg="#f44336",
            fg="white",
            padx=20,
            pady=5,
            command=self.clear_form
        )
        self.clear_button.pack(side=tk.RIGHT, padx=10)

        # Center the form
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)

    def connect_to_db(self):
        """Establish connection to MySQL database"""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="CHIR2502004|",  # Replace with your MySQL password
                database="hrassistance"  # Replace with your database name
            )
            return connection
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
            return None

    def validate_form(self):
        """Validate the form inputs"""
        # Check if any field is empty
        if not self.emp_gmail_var.get().strip():
            messagebox.showerror("Validation Error", "Employee Gmail is required")
            return False

        if not self.emp_name_var.get().strip():
            messagebox.showerror("Validation Error", "Employee Name is required")
            return False

        if not self.password_var.get():
            messagebox.showerror("Validation Error", "Password is required")
            return False

        if not self.confirm_password_var.get():
            messagebox.showerror("Validation Error", "Confirm Password is required")
            return False

        # Check if passwords match
        if self.password_var.get() != self.confirm_password_var.get():
            messagebox.showerror("Validation Error", "Passwords do not match")
            return False

        # Validate email format
        email = self.emp_gmail_var.get()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Validation Error", "Please enter a valid Gmail address")
            return False

        # Check password strength
        if len(self.password_var.get()) < 6:
            messagebox.showerror("Validation Error", "Password should be at least 6 characters long")
            return False

        return True

    def signup(self):
        """Process the signup"""
        if not self.validate_form():
            return

        conn = self.connect_to_db()
        if not conn:
            return

        cursor = conn.cursor()

        try:
            # Check if employee Gmail already exists
            cursor.execute("SELECT * FROM employee_signup WHERE employee_gmail = %s", (self.emp_gmail_var.get(),))
            if cursor.fetchone():
                messagebox.showerror("Error", "Employee Gmail already exists")
                return

            # Insert new employee
            query = """
            INSERT INTO employee_signup (employee_gmail, employee_name, password)
            VALUES (%s, %s, %s)
            """
            values = (
                self.emp_gmail_var.get(),
                self.emp_name_var.get(),
                self.password_var.get()  # In a real application, passwords should be hashed
            )

            cursor.execute(query, values)
            conn.commit()

            messagebox.showinfo("Success", "Employee registered successfully!")
            self.clear_form()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def clear_form(self):
        """Clear all form fields"""
        self.emp_gmail_var.set("")
        self.emp_name_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.emp_gmail_entry.focus()


def check_db_setup():
    """Check if database is set up properly and create table if needed"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="CHIR2502004|",  # Replace with your MySQL password
            database="hrassistance"  # Replace with your database name
        )

        cursor = conn.cursor()

        # Create employee_signup table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_signup (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_gmail VARCHAR(100) NOT NULL UNIQUE,
            employee_name VARCHAR(100) NOT NULL,
            password VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except mysql.connector.Error as err:
        messagebox.showerror("Database Setup Error", f"Error: {err}")
        return False


if __name__ == "__main__":
    # Check database setup
    if check_db_setup():
        root = tk.Tk()
        app = EmployeeSignupApp(root)
        root.mainloop()