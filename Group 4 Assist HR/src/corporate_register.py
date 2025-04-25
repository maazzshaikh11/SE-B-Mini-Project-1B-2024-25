from tkinter import *
from tkinter import messagebox, ttk
import mysql.connector
from dashboard import create_dashboard


def create_register(parent):
    register_window = Toplevel(parent)
    register_window.title("Register Your Organization")
    register_window.configure(background="#FFDD95")

    # Smaller window dimensions
    window_width = 460
    window_height = 440
    screen_width = register_window.winfo_screenwidth()
    screen_height = register_window.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    register_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    register_window.resizable(True, True)  # Allow resizing if needed

    # Define fonts - slightly smaller
    font_title = ('Arial', 26, 'bold')
    font_subtitle = ('Arial', 10, 'italic')
    font_label = ('Arial', 12, 'bold')
    font_button = ("Arial", 11, "bold")

    # Create a main frame with reduced padding
    main_frame = Frame(register_window, bg="#FFDD95", padx=15, pady=10)
    main_frame.pack(fill=BOTH, expand=True)

    # Title and subtitle with reduced spacing
    title_frame = Frame(main_frame, bg="#FFDD95")
    title_frame.pack(fill=X, pady=(0, 10))

    Label(title_frame, text="REGISTER", fg='#3468C0', bg='#FFDD95', font=font_title).pack()
    Label(title_frame, text="Fill the details below", fg='#3468C0', bg='#FFDD95', font=font_subtitle).pack(pady=(2, 0))

    # Create a style for entry fields
    register_style = ttk.Style()
    register_style.configure("Register.TEntry", padding=(5, 3))

    # Form fields container
    form_frame = Frame(main_frame, bg="#FFDD95")
    form_frame.pack(fill=X, pady=5)

    # Create form fields with consistent styling but reduced spacing
    def create_field(parent, label_text, show=None):
        field_frame = Frame(parent, bg="#FFDD95")
        field_frame.pack(fill=X, pady=5)

        Label(field_frame, text=label_text, fg='#3468C0', bg='#FFDD95',
              font=font_label, anchor="w").pack(fill=X, pady=(0, 2))

        entry = ttk.Entry(field_frame, width=48, style="Register.TEntry", font=('Arial', 11))
        if show:
            entry.configure(show=show)
        entry.pack(fill=X, ipady=2)

        return entry

    # Create form fields
    name_field = create_field(form_frame, "Name of the organization:")
    email_field = create_field(form_frame, "Email of the organization:")
    key_field = create_field(form_frame, "A UNIQUE KEY FOR ORGANIZATION:")
    password_field = create_field(form_frame, "Password:", show="*")

    # Buttons container with reduced spacing
    button_frame = Frame(main_frame, bg="#FFDD95")
    button_frame.pack(fill=X, pady=(10, 5))

    # Register button with improved appearance but smaller
    register_btn = Button(
        button_frame,
        text="REGISTER",
        fg='white',
        bg='#3468C0',
        activeforeground='white',
        activebackground='#1E4C9A',
        font=font_button,
        cursor="hand2",
        relief=RAISED,
        borderwidth=2,
        padx=15,
        pady=5
    )
    register_btn.pack(pady=8)

    # Back button positioned at bottom left
    back_frame = Frame(main_frame, bg="#FFDD95")
    back_frame.pack(fill=X, side=BOTTOM, pady=5)

    back_btn = Button(
        back_frame,
        text="Back",
        fg='white',
        bg='#D24545',
        activeforeground='white',
        activebackground='#A94438',
        font=('Arial', 10, 'bold'),
        cursor="hand2",
        padx=8,
        pady=3
    )
    back_btn.pack(side=LEFT)

    def register_corporation():
        company_id = key_field.get().strip()
        name = name_field.get().strip()
        email = email_field.get().strip()
        password = password_field.get().strip()

        if not company_id or not name or not email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="CHIR2502004|",
                                           database="hrassistance")
            cursor = conn.cursor()

            # Check if the email already exists
            cursor.execute(
                "SELECT email_of_the_organization FROM corporate_register WHERE email_of_the_organization = %s",
                (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Email already registered!")
                return

            # Check if the company_id already exists
            cursor.execute(
                "SELECT company_id FROM corporate_register WHERE company_id = %s",
                (company_id,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Company ID already in use! Please use a different unique key.")
                return

            # Insert data along with the timestamp
            cursor.execute(
                "INSERT INTO corporate_register (company_id, name_of_the_organization, email_of_the_organization, password, registration_time) "
                "VALUES (%s, %s, %s, %s, NOW())",
                (company_id, name, email, password))
            conn.commit()
            messagebox.showinfo("Success", f"Registration successful for {name}!")

            # Store company details in a session-like variable
            register_window.company_data = {
                "company_id": company_id,
                "company_name": name,
                "email": email
            }

            # Open dashboard with company_id
            feature_dashboard(company_id)

            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def feature_dashboard(company_id=None):
        register_window.withdraw()
        dashboard_window = create_dashboard(register_window, company_id)
        if dashboard_window:
            dashboard_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(register_window, dashboard_window))

    def close_windows(main_window, popup_window):
        popup_window.destroy()
        main_window.destroy()

    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    # Connect commands to buttons
    register_btn.config(command=register_corporation)
    back_btn.config(command=lambda: feature_back(register_window, parent))

    return register_window


if __name__ == "__main__":
    window = Tk()
    create_register(window)
    window.mainloop()