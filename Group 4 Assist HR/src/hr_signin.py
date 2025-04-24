from tkinter import *
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from dashboard import create_dashboard

# Global session dictionary to track logged-in user
session = {}


def create_hr_login(parent):
    login_window = Toplevel(parent)
    login_window.title("HR Assistance Portal")
    login_window.configure(background="#FFDD95")

    # Positioning the application
    window_width = 500
    window_height = 540
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    login_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    login_window.resizable(False, False)  # Prevent window resizing

    # Setting up the fonts
    font_title = ('Arial', 32, 'bold')
    font_subtitle = ('Arial', 12, 'italic')
    font_label = ('Arial', 13, 'bold')
    font_button = ('Arial', 12, 'bold')

    # Create a main frame
    main_frame = Frame(login_window, bg="#FFDD95", padx=30, pady=20)
    main_frame.pack(fill=BOTH, expand=True)

    # Company logo placeholder (you can replace with an actual logo)
    logo_frame = Frame(main_frame, bg="#FFDD95")
    logo_frame.pack(pady=(10, 20))

    # You can add a logo image here if available
    # logo_img = PhotoImage(file="logo.png")
    # logo_label = Label(logo_frame, image=logo_img, bg="#FFDD95")
    # logo_label.image = logo_img
    # logo_label.pack()

    # Header section
    header_frame = Frame(main_frame, bg="#FFDD95")
    header_frame.pack(pady=(0, 25))

    title_label = Label(header_frame, text="HR PORTAL", fg='#3468C0', bg='#FFDD95', font=font_title)
    title_label.pack()

    subtitle_label = Label(header_frame, text="Sign in to access your dashboard", fg='#3468C0', bg='#FFDD95',
                           font=font_subtitle)
    subtitle_label.pack(pady=(5, 0))

    # Create a card-like frame for login
    login_card = Frame(main_frame, bg="#FFFFFF", highlightbackground="#3468C0", highlightthickness=1, bd=0)
    login_card.pack(fill=X, padx=20, pady=10)

    # Login form
    form_frame = Frame(login_card, bg="#FFFFFF", padx=20, pady=20)
    form_frame.pack(fill=X)

    # Username Label and Entry
    username_frame = Frame(form_frame, bg="#FFFFFF")
    username_frame.pack(fill=X, pady=(0, 15))

    username_label = Label(username_frame, text="Organization Email:", fg='#3468C0', bg='#FFFFFF', font=font_label,
                           anchor="w")
    username_label.pack(anchor="w")

    username_field = Entry(username_frame, width=45, font=('Arial', 12), bd=2, relief=GROOVE)
    username_field.pack(fill=X, pady=(5, 0))

    # Password Label and Entry
    password_frame = Frame(form_frame, bg="#FFFFFF")
    password_frame.pack(fill=X, pady=(0, 25))

    password_label = Label(password_frame, text="Password:", fg='#3468C0', bg='#FFFFFF', font=font_label, anchor="w")
    password_label.pack(anchor="w")

    password_field = Entry(password_frame, width=45, font=('Arial', 12), show="•", bd=2, relief=GROOVE)
    password_field.pack(fill=X, pady=(5, 0))

    # **MySQL Login Functionality**
    def verify_login():
        email = username_field.get()
        password = password_field.get()

        if not email or not password:
            messagebox.showerror("Login Failed", "Please enter both email and password.")
            return

        try:
            # Connect to MySQL Database
            conn = mysql.connector.connect(host="localhost", user="root", password="CHIR2502004|",
                                           database="hrassistance")
            cursor = conn.cursor()

            # Verify credentials
            query = "SELECT company_id, name_of_the_organization FROM corporate_register WHERE email_of_the_organization = %s AND password = %s"
            cursor.execute(query, (email, password))
            result = cursor.fetchone()

            if result:
                company_id, company_name = result  # Get the company_id and name
                session["email"] = email  # Store session for filtering
                session["company_id"] = company_id  # Store company_id in session
                session["company_name"] = company_name  # Store company name in session

                messagebox.showinfo("Login Successful", f"Welcome, {company_name}!")
                login_window.withdraw()  # Hide login window

                # Open dashboard with the company_id
                dashboard_window = create_dashboard(login_window, company_id)

                if dashboard_window:
                    dashboard_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(login_window, dashboard_window))

            else:
                messagebox.showerror("Login Failed", "Invalid Email or Password")

            conn.close()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    # Button frame
    button_frame = Frame(form_frame, bg="#FFFFFF")
    button_frame.pack(fill=X, pady=10)

    # Style for the login button
    login_button = Button(
        button_frame,
        text="Sign In",
        width=20,
        height=2,
        foreground='#FFFFFF',
        background='#3468C0',
        activeforeground='#FFFFFF',
        activebackground='#4F7FE3',
        font=font_button,
        bd=0,
        cursor="hand2",
        command=verify_login
    )
    login_button.pack(pady=5)

    # Function to close both windows
    def close_windows(main_window, popup_window):
        popup_window.destroy()
        main_window.destroy()

    # Back button function
    def feature_back(current_window, previous_window):
        current_window.withdraw()  # Hide the current window
        previous_window.deiconify()

    # Footer frame
    footer_frame = Frame(main_frame, bg="#FFDD95")
    footer_frame.pack(fill=X, side=BOTTOM, pady=20)

    # Setting up the back button with improved styling
    back_button = Button(
        footer_frame,
        text="← Back",
        foreground='#FFFFFF',
        background='#D24545',
        activeforeground='#FFFFFF',
        activebackground='#E35858',
        font=('Arial', 11, 'bold'),
        bd=0,
        padx=15,
        pady=5,
        cursor="hand2",
        command=lambda: feature_back(login_window, parent)
    )
    back_button.pack(side=LEFT, padx=25)

    # Add a help or forgot password link
    help_label = Label(
        footer_frame,
        text="Forgot Password?",
        fg='#3468C0',
        bg='#FFDD95',
        font=('Arial', 11, 'underline'),
        cursor="hand2"
    )
    help_label.pack(side=RIGHT, padx=25)

    return login_window


if __name__ == "__main__":
    window = Tk()
    create_hr_login(window)
    window.mainloop()