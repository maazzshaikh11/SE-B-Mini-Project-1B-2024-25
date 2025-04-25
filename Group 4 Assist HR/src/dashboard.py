from tkinter import *
import tkinter as tk
import mysql.connector
from employee_managment import employee_management
from payroll_managment import payroll_management
from recruitment import recruitment_management
from performane_management import performance_management
from upskilling import upskilling_management
from greviance_check import grievance_check
from document_store import document_storage


def create_dashboard(parent, company_id=None):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("HR ASSISTANCE Dashboard")
    dashboard_window.configure(background="#FFDD95")

    # Store company_id as a global variable in the dashboard_window
    dashboard_window.company_id = company_id

    # Get company details from database
    company_name = get_company_details(company_id) if company_id else "Organization"

    # Positioning the application
    window_width = 1000
    window_height = 700  # Increased height to accommodate new buttons

    screen_width = dashboard_window.winfo_screenwidth()
    screen_height = dashboard_window.winfo_screenheight()

    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)

    dashboard_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    dashboard_window.resizable(False, False)  # Fixed size window for better layout control

    # Setting up the font
    font_title = ('Arial', 30, 'bold')
    font_subtitle = ('Arial', 16, 'italic')
    font_welcome = ('Arial', 18, 'bold')
    font_section = ('Arial', 14, 'italic')
    font_button = ('Arial', 14, 'bold')

    # Create a header frame
    header_frame = Frame(dashboard_window, bg="#FFDD95")
    header_frame.pack(fill=X, padx=20, pady=10)

    # Add Back button to header
    def feature_back(current_window, previous_window):
        current_window.withdraw()  # Hide the current window
        previous_window.deiconify()

    Back = Button(header_frame,
                  text="Back",
                  foreground='#FFFFFF',
                  background='#D24545',
                  activeforeground='#D24545',
                  activebackground='#A94438',
                  command=lambda: feature_back(dashboard_window, parent),
                  font=font_button,
                  width=8,
                  padx=5,
                  pady=2,
                  relief=RAISED,
                  bd=2
                  )
    Back.pack(side=LEFT, anchor=NW)

    # Add title to header
    title_frame = Frame(header_frame, bg="#FFDD95")
    title_frame.pack(side=TOP, fill=X)

    info1_label = Label(title_frame,
                        text="HR ASSISTANCE",
                        fg='#3468C0',
                        bg='#FFDD95',
                        font=font_title)
    info1_label.pack(side=TOP)

    org_name_label = Label(title_frame,
                           text=f"Welcome, {company_name}",
                           fg='#3468C0',
                           bg='#FFDD95',
                           font=font_welcome)
    org_name_label.pack(side=TOP, pady=5)

    info2_label = Label(title_frame,
                        text="Make your HR Operations more efficient by starting here",
                        fg='#3468C0',
                        bg='#FFDD95',
                        font=font_subtitle)
    info2_label.pack(side=TOP, pady=5)

    # Create main content frame
    main_frame = Frame(dashboard_window, bg="#FFDD95")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Create left and right columns
    left_column = Frame(main_frame, bg="#FFDD95")
    left_column.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

    right_column = Frame(main_frame, bg="#FFDD95")
    right_column.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

    # Helper function to create module sections
    def create_module_section(parent, title_text, button_text, command=None):
        section_frame = Frame(parent, bg="#FFDD95", bd=2, relief=RIDGE)
        section_frame.pack(fill=X, pady=10, padx=5, ipady=5)

        title_label = Label(section_frame,
                            text=title_text,
                            foreground='#3468C0',
                            background='#FFDD95',
                            font=font_section
                            )
        title_label.pack(pady=(10, 5))

        if command is None:
            # Placeholder function for future features
            command = lambda: tk.messagebox.showinfo("Future Feature",
                                                     f"{button_text} will be implemented in a future update.")

        button = Button(section_frame,
                        text=button_text,
                        foreground='#FFFFFF',
                        background='#D24545',
                        activeforeground='#E43A19',
                        activebackground='#111F4D',
                        command=command,
                        font=font_button,
                        width=20,
                        height=1,
                        relief=RAISED,
                        bd=3
                        )
        button.pack(pady=(5, 10))

        return section_frame

    # Define window closing functions
    def close_windows(main_window, popup_window):
        popup_window.destroy()
        main_window.destroy()

    # Employee Management Module
    def feature_employee_management():
        dashboard_window.withdraw()
        employee_window = employee_management(dashboard_window)
        if employee_window:
            employee_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, employee_window))

    create_module_section(
        left_column,
        "Efficient way to manage your employee data",
        "Employee Management",
        feature_employee_management
    )

    # Payroll Management Module
    def feature_payroll_management():
        dashboard_window.withdraw()
        payroll_window = payroll_management(dashboard_window)
        if payroll_window:
            payroll_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, payroll_window))

    create_module_section(
        left_column,
        "Manage your organization's payroll here",
        "Payroll Management",
        feature_payroll_management
    )

    # Grievance Tracking Module
    def feature_greviance_management():
        dashboard_window.withdraw()
        greviance_window = grievance_check(dashboard_window)
        if greviance_window:
            greviance_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, greviance_window))

    create_module_section(
        right_column,
        "Solve your employee's grievances here",
        "Grievance Tracking",
        feature_greviance_management
    )

    # Recruitment Module
    def feature_recruitment_management():
        dashboard_window.withdraw()
        recruitment_window = recruitment_management(dashboard_window)
        if recruitment_window:
            recruitment_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, recruitment_window))

    create_module_section(
        left_column,
        "Check your organization's recruitment status",
        "Recruitment",
        feature_recruitment_management
    )

    # Performance Management Module
    def feature_performance_management():
        dashboard_window.withdraw()
        performance_window = performance_management(dashboard_window)
        if performance_window:
            performance_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, performance_window))

    create_module_section(
        right_column,
        "Check your employee's performance here",
        "Performance Management",
        feature_performance_management
    )

    # Skillup Tracking Module
    def feature_skillup_management():
        dashboard_window.withdraw()
        skillup_window = upskilling_management(dashboard_window)
        if skillup_window:
            skillup_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, skillup_window))

    create_module_section(
        right_column,
        "Check your employee's skillup status",
        "Skillup Tracking",
        feature_skillup_management
    )

    def feature_document_management():
        dashboard_window.withdraw()
        document_window = document_storage(dashboard_window)
        if document_window:
            document_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(dashboard_window, document_window))

    # Future Feature 1 - Placeholder
    create_module_section(
        left_column,
        "Store your organizations document here",
        "Document Storage",
        feature_document_management
    )

    # # Future Feature 2 - Placeholder
    # create_module_section(
    #     right_column,
    #     "Additional HR capabilities coming soon",
    #     "Future Feature 2"
    # )

    return dashboard_window


def get_company_details(company_id):
    """Fetch company details from the database using company_id"""
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",  # Replace with your database host
            user="root",  # Replace with your database username
            password="CHIR2502004|",  # Replace with your database password
            database="hrassistance"  # Replace with your database name
        )

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to fetch company details
        query = "SELECT name_of_the_organization FROM corporate_register WHERE company_id = %s"
        cursor.execute(query, (company_id,))

        # Fetch result
        result = cursor.fetchone()

        # Close cursor and connection
        cursor.close()
        connection.close()

        if result:
            return result[0]  # Return company name
        else:
            return "Unknown Organization"

    except mysql.connector.Error as error:
        print(f"Database error: {error}")
        return "Organization"


if __name__ == "__main__":
    window = Tk()
    # For testing purposes, you can pass a dummy company_id
    # In actual usage, this would be passed from the login page
    create_dashboard(window, company_id=1)
    window.mainloop()