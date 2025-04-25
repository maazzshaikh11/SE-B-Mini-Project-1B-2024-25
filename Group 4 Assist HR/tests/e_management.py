from tkinter import *
from tkinter import ttk
import tkinter as tk


def employee_management(parent):
    dashboard_window = Toplevel(parent)
    dashboard_window.title("Employee Management")
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

    info1_label = Label(dashboard_window, text="Employee Management", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Manage your organization's employees here", fg='#3468C0', bg='#FFDD95',
                        font=font_info2)
    info2_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    Back = Button(dashboard_window, text="Back", fg='#f7f7f7', bg='#D24545', activeforeground='#D24545',
                  activebackground='#A94438', command=lambda: feature_back(dashboard_window, parent), font=font_button)
    Back.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='w')

    search_label = Label(dashboard_window, text="Search:", fg='#3468C0', bg='#FFDD95', font=font_info2)
    search_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

    search_entry = Entry(dashboard_window, font=('Arial', 12))
    search_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    columns = ("Name", "DOB", "Department", "Role", "Education", "Marks", "Experience", "Salary", "Location")
    tree = ttk.Treeview(dashboard_window, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree_scroll_y = Scrollbar(dashboard_window, orient="vertical", command=tree.yview)
    tree_scroll_x = Scrollbar(dashboard_window, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=tree_scroll_y.set, xscroll=tree_scroll_x.set)

    tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    tree_scroll_y.grid(row=3, column=3, sticky='ns')
    tree_scroll_x.grid(row=4, column=0, columnspan=3, sticky='ew')

    fake_data = [
        ("Krishna Kaul", "1990-05-14", "HR", "Manager", "MBA", "85%", "10 years", "$80,000", "New York"),
        ("Dilin Nair", "1985-08-23", "IT", "Developer", "B.Tech", "90%", "8 years", "$95,000", "San Francisco"),
        ("Vivek Arora", "1992-12-05", "Marketing", "Executive", "BBA", "88%", "6 years", "$70,000", "Los Angeles"),
        ("Vivian Divine", "1988-07-19", "Finance", "Analyst", "M.Com", "92%", "9 years", "$85,000", "Chicago"),
        ("Marshal Mathers", "1995-04-30", "Sales", "Representative", "BA", "80%", "4 years", "$60,000", "Miami")
    ]

    for employee in fake_data:
        tree.insert("", "end", values=employee)

    button_frame = Frame(dashboard_window, bg="#FFDD95")
    button_frame.grid(row=5, column=0, columnspan=3, pady=10)

    save_button = Button(button_frame, text="Save", bg='#28A745', fg='white', font=font_button)
    save_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Delete", bg='#DC3545', fg='white', font=font_button)
    delete_button.grid(row=0, column=1, padx=10)

    update_button = Button(button_frame, text="Update", bg='#007BFF', fg='white', font=font_button)
    update_button.grid(row=0, column=2, padx=10)

    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)


if __name__ == "__main__":
    window = Tk()
    employee_management(window)
    window.mainloop()