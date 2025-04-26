from tkinter import *
import tkinter as tk
from corporate_register import create_register
from employee_singnin import create_login
from hr_signin import create_hr_login

# Setting Up the app
window = Tk()
window.title("HR Assistance Portal")
window.configure(background="#FFDD95")
window.state('zoomed')
# window_width = 900
# window_height = 630

# # Center window on screen
# screen_width = window.winfo_screenwidth()
# screen_height = window.winfo_screenheight()
# x_position = int((screen_width - window_width) / 2)
# y_position = int((screen_height - window_height) / 2)
# window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Add window icon support (commented out until file is available)
# window.iconphoto(True, PhotoImage(file='logo.png'))

# Define consistent fonts
font_title = ('Arial', 36, 'bold')
font_heading = ("Arial", 28, "bold")
font_subheading = ("Arial", 22, "bold")
font_normal = ("Arial", 16)
font_button = ("Arial", 16, "bold")

# Create a frame for better layout control
main_frame = Frame(window, bg="#FFDD95", padx=40, pady=30)
main_frame.pack(fill=BOTH, expand=True)

# Add logo placeholder (commented out until file is available)
# logo = PhotoImage(file='logo2.png')
# logo_label = Label(main_frame, image=logo, bg='#FFDD95')
# logo_label.pack(pady=(0, 15))

# Main title with subtle shadow effect
title_frame = Frame(main_frame, bg="#FFDD95")
title_frame.pack(pady=(0, 30))

title_shadow = Label(title_frame, text="HR ASSISTANCE", font=font_title, fg='#2A569F', bg='#FFDD95')
title_shadow.grid(row=0, column=0, padx=2, pady=2)

title_label = Label(title_frame, text="HR ASSISTANCE", font=font_title, fg='#3468C0', bg='#FFDD95')
title_label.grid(row=0, column=0)

# Welcome message
welcome_label = Label(main_frame, text="Welcome to Your HR Portal", font=font_heading, fg='#3468C0', bg='#FFDD95')
welcome_label.pack(pady=(0, 15))

# Descriptive text in a frame
info_frame = Frame(main_frame, bg="#FFDD95", pady=15)
info_frame.pack(fill=X)

description1 = Label(info_frame,
                    text="Your comprehensive solution for HR management and employee services",
                    fg='#3468C0', bg='#FFDD95', font=font_subheading)
description1.pack()

description2 = Label(info_frame,
                    text="Streamline your HR processes with our intuitive platform",
                    fg='#3468C0', bg='#FFDD95', font=font_normal)
description2.pack(pady=(10, 0))

# Separator line
separator = Frame(main_frame, height=2, width=700, bg="#3468C0")
separator.pack(pady=25)

# Action section title
action_label = Label(main_frame, text="Select Your Access Point", fg='#3468C0', bg='#FFDD95', font=font_subheading)
action_label.pack(pady=(0, 20))

# Create button frames for better organization
button_frame = Frame(main_frame, bg="#FFDD95")
button_frame.pack(pady=10)

# HR button section
hr_frame = Frame(button_frame, bg="#FFDD95", padx=20)
hr_frame.grid(row=0, column=0, padx=15)

hr_label = Label(hr_frame, text="HR Personnel", fg='#3468C0', bg='#FFDD95', font=font_normal)
hr_label.pack(pady=(0, 10))

def open_hr_signin():
    window.withdraw()
    hr_signin = create_hr_login(window)
    hr_signin.protocol("WM_DELETE_WINDOW", lambda: close_windows(window, hr_signin))

hr_button = Button(hr_frame,
                text="HR Sign In",
                foreground='white',
                background='#D24545',
                activeforeground='white',
                activebackground='#B73E3E',
                padx=20, pady=10,
                relief=RAISED, bd=2,
                cursor="hand2",
                command=open_hr_signin,
                font=font_button)
hr_button.pack()

# Employee button section
employee_frame = Frame(button_frame, bg="#FFDD95", padx=20)
employee_frame.grid(row=0, column=1, padx=15)

employee_label = Label(employee_frame, text="Employees", fg='#3468C0', bg='#FFDD95', font=font_normal)
employee_label.pack(pady=(0, 10))

def open_employee_signin():
    window.withdraw()
    employee_signin = create_login(window)
    employee_signin.protocol("WM_DELETE_WINDOW", lambda: close_windows(window, employee_signin))

employee_button = Button(employee_frame,
                      text="Employee Sign In",
                      foreground='white',
                      background='#D24545',
                      activeforeground='white',
                      activebackground='#B73E3E',
                      padx=20, pady=10,
                      relief=RAISED, bd=2,
                      cursor="hand2",
                      command=open_employee_signin,
                      font=font_button)
employee_button.pack()

# Registration section
register_frame = Frame(main_frame, bg="#FFDD95", pady=25)
register_frame.pack()

register_label = Label(register_frame, text="New Organization?", fg='#3468C0', bg='#FFDD95', font=font_normal)
register_label.pack(pady=(10, 10))

def open_corporate_register():
    window.withdraw()
    corporate_register_window = create_register(window)
    corporate_register_window.protocol("WM_DELETE_WINDOW", lambda: close_windows(window, corporate_register_window))

register_button = Button(register_frame,
                      text="Register Company",
                      foreground='white',
                      background='#D24545',
                      activeforeground='white',
                      activebackground='#B73E3E',
                      padx=20, pady=10,
                      relief=RAISED, bd=2,
                      cursor="hand2",
                      command=open_corporate_register,
                      font=font_button)
register_button.pack()

# Footer text
footer_label = Label(main_frame,
                    text="© 2025 HR Assistance Portal - Simplifying Human Resources",
                    fg='#3468C0', bg='#FFDD95', font=("Arial", 10))
footer_label.pack(side=BOTTOM, pady=10)

def close_windows(main_window, popup_window):
    popup_window.destroy()
    main_window.destroy()

window.mainloop()