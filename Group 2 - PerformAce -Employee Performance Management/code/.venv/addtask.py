import tkinter as tk

# Create main window
root = tk.Tk()
root.title("Add Selection Page")
root.geometry("500x350")
root.configure(bg="#223344")  # Background color similar to the image

# Title Label
title_label = tk.Label(root, text="SELECT WHAT TO BE ADDED", font=("Arial", 14, "bold"), bg="#223344", fg="white")
title_label.pack(pady=20)

# Buttons Frame
button_frame = tk.Frame(root, bg="#223344")
button_frame.pack(pady=20)

# Buttons
notes_btn = tk.Button(button_frame, text="NOTES", font=("Arial", 12, "bold"), bg="lightgray", width=12)
notes_btn.grid(row=0, column=0, padx=10, pady=10)

assignment_btn = tk.Button(button_frame, text="ASSIGNMENT", font=("Arial", 12, "bold"), bg="lightgray", width=12)
assignment_btn.grid(row=0, column=1, padx=10, pady=10)

test_btn = tk.Button(button_frame, text="TEST", font=("Arial", 12, "bold"), bg="lightgray", width=12)
test_btn.grid(row=0, column=2, padx=10, pady=10)

# Back Button
back_btn = tk.Button(root, text="BACK", font=("Arial", 12, "bold"), bg="lightgray", width=12)
back_btn.pack(pady=20)

# Run the application
root.mainloop()
