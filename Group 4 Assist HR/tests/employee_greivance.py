from tkinter import *
from tkinter import ttk
import tkinter as tk


def employee_greviance(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Employee Grievance")
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

    info1_label = Label(dashboard_window, text="Employee Grievance", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Submit your grievances here", fg='#3468C0', bg='#FFDD95',
                        font=font_info2)
    info2_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    # Name Entry
    name_label = Label(dashboard_window, text="Enter Your Name:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    name_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

    name_entry = Entry(dashboard_window, width=40, font=font_info2)
    name_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

    # Grievance Text Area
    grievance_label = Label(dashboard_window, text="Describe Your Grievance:", fg='#3468C0', bg='#FFDD95',
                            font=font_info2)
    grievance_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    grievance_text = Text(dashboard_window, width=60, height=10, font=font_info2)
    grievance_text.grid(row=3, column=1, padx=10, pady=10, sticky='w')

    # Submit Button
    def submit_grievance():
        name = name_entry.get()
        grievance = grievance_text.get("1.0", END).strip()

        if not name or not grievance:
            error_label.config(text="Error: Name and grievance cannot be empty!", fg="red")
            return

        error_label.config(text="Grievance Submitted Successfully!", fg="green")
        name_entry.delete(0, END)
        grievance_text.delete("1.0", END)

    submit_button = Button(dashboard_window, text="Submit", fg='#f7f7f7', bg='#4CAF50', activeforeground='#4CAF50',
                           activebackground='#388E3C', command=submit_grievance, font=font_button)
    submit_button.grid(row=4, column=1, padx=10, pady=10, sticky='w')

    # Error/Success Message Label
    error_label = Label(dashboard_window, text="", fg="red", bg='#FFDD95', font=font_info2)
    error_label.grid(row=5, column=1, padx=10, pady=5, sticky='w')

    # Back Button
    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    back_button = Button(dashboard_window, text="Back", fg='#f7f7f7', bg='#D24545', activeforeground='#D24545',
                         activebackground='#A94438', command=lambda: feature_back(dashboard_window, parent),
                         font=font_button)
    back_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='w')

    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)


if __name__ == "__main__":
    window = Tk()
    employee_greviance(window)
    window.mainloop()
