import tkinter as tk
from tkinter import ttk

# Create main application window
root = tk.Tk()
root.title("User Page")
root.geometry("800x450")
root.configure(bg="#223344")  # Background color similar to the image

# Title Label
title_label = tk.Label(root, text="WELCOME ADMIN !!!", font=("Arial", 14, "bold"), bg="#223344", fg="lightblue")
title_label.pack(anchor="w", padx=20, pady=5)

user_label = tk.Label(root, text="USER PAGE", font=("Arial", 20, "bold"), bg="#223344", fg="white")
user_label.pack(anchor="center", pady=10)

# Navigation Bar
nav_frame = tk.Frame(root, bg="#335577")
nav_frame.pack(fill="x", pady=5, padx=10)

nav_label = tk.Label(nav_frame, text="ORGANISATION CONNECT - USER / RESULTS", font=("Arial", 12), bg="#335577", fg="white")
nav_label.pack(side="left", padx=10)

upcoming_btn = tk.Button(nav_frame, text="UPCOMING", font=("Arial", 10, "bold"), bg="lightgray", width=10)
upcoming_btn.pack(side="right", padx=5)

back_btn = tk.Button(nav_frame, text="BACK", font=("Arial", 10, "bold"), bg="lightgray", width=10)
back_btn.pack(side="right", padx=5)

# Assignments & Tests Section
content_frame = tk.Frame(root, bg="#223344")
content_frame.pack(fill="both", expand=True, padx=20, pady=10)

item_label = tk.Label(content_frame, text="ASSIGNMENT / TEST", font=("Arial", 12, "bold"), bg="#223344", fg="white")
item_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

view_btn = tk.Button(content_frame, text="VIEW", font=("Arial", 10), bg="lightgray", width=10)
view_btn.grid(row=0, column=1, padx=10, pady=10)

# Notes Section
notes_frame = tk.Frame(root, bg="#445566")
notes_frame.place(relx=0.85, rely=0.3, width=100, height=200)  # Positioned similar to the image

notes_label = tk.Label(notes_frame, text="NOTES", font=("Arial", 12, "bold"), bg="#445566", fg="white")
notes_label.pack(pady=5)

# Sidebar Buttons
sidebar_frame = tk.Frame(root, bg="#223344")
sidebar_frame.place(relx=0.85, rely=0.05, width=120, height=60)

close_btn = tk.Button(sidebar_frame, text="CLOSE", font=("Arial", 10), bg="lightgray", width=10)
close_btn.pack(pady=5)

homepage_btn = tk.Button(sidebar_frame, text="HOMEPAGE", font=("Arial", 10), bg="lightgray", width=10)
homepage_btn.pack(pady=5)

# Run the application
root.mainloop()
