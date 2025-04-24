from tkinter import *
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from employee_greviance import employee_greviance


def create_login(parent):
    login_window = Toplevel(parent)
    # login_window.geometry("460x440")
    login_window.title("Employee Signin")
    login_window.configure(background="#FFDD95")

    # Positioning the application
    window_width = 460
    window_height = 480

    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()

    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)

    login_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Setting up the icon for the window
    # icon = PhotoImage(file='logo.png')
    # login_window.iconphoto(True, icon)

    # Setting up the font
    font_login = ('Arial', 30, 'italic')
    font_username = ('Arial', 13, 'bold')
    font_password = ('Arial', 13, 'bold')
    font_login_button = ('Arial', 13, 'bold')
    font_button = ("Arial", 10, "bold")

    # Setting up the "login" label
    login_label = Label(login_window,
                        text="LOGIN",
                        fg='#3468C0',
                        bg='#FFDD95',
                        font=font_login)
    login_label.pack(padx=50, pady=50)

    # Email Label
    email_label = Label(login_window,
                        text="Employee Gmail:",
                        fg='#3468C0',
                        bg='#FFDD95',
                        font=font_username,
                        anchor="w")
    email_label.pack(padx=10, pady=4, anchor="w")

    # Setting up the text field for the email field
    email_field = Entry(login_window,
                        width=50,
                        justify="left",
                        # anchor="w"
                        )
    email_field.pack(pady=7, padx=(7, 0), anchor="w")

    # Password Label
    Password_label = Label(login_window,
                           text="Password:",
                           fg='#3468C0',
                           bg='#FFDD95',
                           font=font_password,
                           anchor="w")
    Password_label.pack(padx=10, pady=4, anchor="w")

    # Setting up the text field for the password field
    Password_field = Entry(login_window,
                           width=50,
                           justify="left",
                           # anchor="w",
                           show="*"
                           )
    Password_field.pack(pady=7, padx=(7, 0), anchor="w")

    # Function to verify login credentials
    def verify_login():
        email = email_field.get()
        password = Password_field.get()

        # Validate inputs
        if not email or not password:
            messagebox.showerror("Login Error", "Please enter both email and password")
            return

        try:
            # Connect to MySQL database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="CHIR2502004|",  # Replace with your MySQL password
                database="hrassistance"
            )

            cursor = connection.cursor()

            # Query to check if credentials match using email instead of name
            query = "SELECT * FROM employee_signup WHERE employee_gmail = %s AND password = %s"
            cursor.execute(query, (email, password))

            # Fetch the result
            result = cursor.fetchone()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            if result:
                # Store employee data in a global variable or session
                global current_employee
                current_employee = {
                    "id": result[0],
                    "employee_gmail": result[1],
                    "employee_name": result[2]
                }

                messagebox.showinfo("Success", f"Welcome, {result[2]}!")  # Using employee_name from the result
                feature_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid email or password")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    # Setting up the dashboard window function
    def feature_dashboard():
        login_window.withdraw()  # Hide the main window
        dashboard_window = employee_greviance(login_window)
        if dashboard_window:
            dashboard_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(login_window, dashboard_window))

    def close_windows(main_window, popup_window):
        popup_window.destroy()
        main_window.destroy()

    # Setting up the login button
    Login = Button(login_window,
                   text="Login",
                   foreground='#f7f7f7',
                   background='#D24545',
                   activeforeground='#E43A19',
                   activebackground='#FFDD95',
                   command=verify_login,  # Use the verify_login function
                   font=font_login_button
                   )
    Login.pack(padx=10, pady=20)

    # Setting up the back button
    def feature_back(current_window, previous_window):
        current_window.withdraw()  # Hide the current window
        previous_window.deiconify()

    Back = Button(login_window,
                  text="Back",
                  foreground='#f7f7f7',
                  background='#D24545',
                  activeforeground='#D24545',
                  activebackground='#FFDD95',
                  command=lambda: feature_back(login_window, parent),
                  # command=back,
                  font=font_button
                  )
    Back.pack(padx=10, anchor='sw')

    return login_window


if __name__ == "__main__":
    # Initialize global variable for current employee
    current_employee = None

    window = Tk()
    create_login(window)
    window.mainloop()