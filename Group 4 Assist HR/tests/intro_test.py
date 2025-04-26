from tkinter import *
import tkinter as tk

# Setting Up the App
window = Tk()
window.title("HR Assistance")
window_width = 900
window_height = 600

# Centering the Window
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Custom Colors
bg_color = "#f4f4f4"  # Light grey background
primary_color = "#3468C0"  # Deep blue
accent_color = "#ff8c42"  # Warm orange for contrast
button_bg = "#2E86C1"  # Button default color
button_hover = "#1B4F72"  # Button hover color

window.configure(bg=bg_color)

# Fonts
font_title = ("Segoe UI", 35, "bold")
font_subtitle = ("Segoe UI", 24, "bold")
font_info = ("Segoe UI", 18, "normal")
font_button = ("Segoe UI", 14, "bold")

# Title Label
title_label = Label(window, text="HR ASSISTANCE", font=font_title, fg=primary_color, bg=bg_color)
title_label.pack(pady=(40, 10))

# Welcome Label
welcome_label = Label(window, text="Welcome,", font=font_subtitle, fg=primary_color, bg=bg_color)
welcome_label.pack()

# Info Labels
info_texts = [
    "Your go-to tool for HR-related tasks.",
    "Make your process more efficient and reliable with us.",
    "Get started now!"
]
for text in info_texts:
    label = Label(window, text=text, font=font_info, fg="#333", bg=bg_color)
    label.pack(pady=5)

# Button Hover Effects
def on_enter(e):
    e.widget.config(bg=button_hover)

def on_leave(e):
    e.widget.config(bg=button_bg)

# Button Factory Function
def create_button(text):
    btn = Button(window, text=text, font=font_button, fg="white", bg=button_bg,
                 activebackground=accent_color, activeforeground="white",
                 padx=15, pady=10, bd=0, relief=FLAT, cursor="hand2")
    btn.pack(pady=10, ipadx=10, ipady=3, fill=X, padx=100)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# Creating Buttons
hr_signin_btn = create_button("HR Sign-In")
corporate_register_btn = create_button("New Corporate Register")
employee_signin_btn = create_button("Employee Sign-In")

window.mainloop()
