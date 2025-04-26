import tkinter as tk
from tkinter import messagebox

def create_feedback_window():
    feedback_window = tk.Toplevel()
    feedback_window.title("Feedback")
    feedback_window.geometry("600x700")
    feedback_window.configure(bg="#f0f8ff")  # Light blue background

    # Center the window
    screen_width = feedback_window.winfo_screenwidth()
    screen_height = feedback_window.winfo_screenheight()
    x = (screen_width // 2) - (600 // 2)
    y = (screen_height // 2) - (700 // 2)
    feedback_window.geometry(f"600x700+{x}+{y}")

    # Main container with padding
    main_frame = tk.Frame(feedback_window, bg="#f0f8ff", padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header section
    header_frame = tk.Frame(main_frame, bg="#f0f8ff")
    header_frame.pack(fill=tk.X, pady=(0, 20))

    # Title with modern styling
    tk.Label(header_frame,
             text="📝 Your Feedback",
             font=("Segoe UI", 28, "bold"),
             bg="#f0f8ff",
             fg="#2c3e50").pack()

    # Subtitle
    tk.Label(header_frame,
             text="We value your opinion! Please share your experience with us.",
             font=("Segoe UI", 12),
             bg="#f0f8ff",
             fg="#34495e").pack(pady=10)

    # Rating section with card-like appearance
    rating_card = tk.Frame(main_frame, bg="white", relief="solid", borderwidth=1)
    rating_card.pack(fill=tk.X, pady=10, padx=20)

    # Rating title
    tk.Label(rating_card,
             text="⭐ Rate your experience",
             font=("Segoe UI", 16, "bold"),
             bg="white",
             fg="#2c3e50").pack(pady=(20, 10))

    # Rating buttons frame
    rating_var = tk.IntVar()
    rating_buttons_frame = tk.Frame(rating_card, bg="white")
    rating_buttons_frame.pack(pady=20)

    # Create star rating buttons
    for i in range(1, 6):
        star_btn = tk.Radiobutton(rating_buttons_frame,
                                text="★",
                                variable=rating_var,
                                value=i,
                                font=("Segoe UI", 24),
                                bg="white",
                                fg="#f1c40f",  # Gold color for stars
                                selectcolor="#f1c40f",
                                activebackground="white",
                                activeforeground="#f1c40f",
                                indicatoron=0,
                                width=2,
                                padx=10)
        star_btn.pack(side=tk.LEFT, padx=5)

    # Feedback text section with card-like appearance
    feedback_card = tk.Frame(main_frame, bg="white", relief="solid", borderwidth=1)
    feedback_card.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

    # Feedback title
    tk.Label(feedback_card,
             text="💬 Your feedback",
             font=("Segoe UI", 16, "bold"),
             bg="white",
             fg="#2c3e50").pack(pady=(20, 10))

    # Feedback text area with modern styling
    feedback_text = tk.Text(feedback_card,
                          height=10,
                          width=50,
                          font=("Segoe UI", 12),
                          relief="solid",
                          borderwidth=1,
                          padx=10,
                          pady=10)
    feedback_text.pack(pady=10, padx=20)

    # Placeholder text
    feedback_text.insert("1.0", "Share your thoughts here...")
    feedback_text.config(fg="#95a5a6")  # Gray color for placeholder

    def on_focus_in(event):
        if feedback_text.get("1.0", "end-1c") == "Share your thoughts here...":
            feedback_text.delete("1.0", "end")
            feedback_text.config(fg="#2c3e50")

    def on_focus_out(event):
        if not feedback_text.get("1.0", "end-1c"):
            feedback_text.insert("1.0", "Share your thoughts here...")
            feedback_text.config(fg="#95a5a6")

    feedback_text.bind("<FocusIn>", on_focus_in)
    feedback_text.bind("<FocusOut>", on_focus_out)

    def submit_feedback():
        rating = rating_var.get()
        feedback = feedback_text.get("1.0", tk.END).strip()

        if rating == 0:
            messagebox.showwarning("Warning", "Please select a rating!")
            return

        if not feedback or feedback == "Share your thoughts here...":
            messagebox.showwarning("Warning", "Please provide some feedback!")
            return

        # Show success message with modern styling
        success_window = tk.Toplevel(feedback_window)
        success_window.title("Thank You")
        success_window.geometry("400x200")
        success_window.configure(bg="#f0f8ff")

        # Center the success window
        screen_width = success_window.winfo_screenwidth()
        screen_height = success_window.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2)
        y = (screen_height // 2) - (200 // 2)
        success_window.geometry(f"400x200+{x}+{y}")

        # Success message
        tk.Label(success_window,
                text="✅ Thank you for your feedback!",
                font=("Segoe UI", 16, "bold"),
                bg="#f0f8ff",
                fg="#27ae60").pack(pady=30)

        # OK button with modern styling
        ok_btn = tk.Button(success_window,
                         text="OK",
                         command=lambda: [success_window.destroy(), feedback_window.destroy()],
                         font=("Segoe UI", 12, "bold"),
                         bg="#4169e1",
                         fg="white",
                         activebackground="#1e40af",
                         relief="flat",
                         borderwidth=0,
                         cursor="hand2",
                         width=10)
        ok_btn.pack(pady=20)

        # Make the success window modal
        success_window.transient(feedback_window)
        success_window.grab_set()
        feedback_window.wait_window(success_window)

    # Submit button with modern styling
    submit_btn = tk.Button(main_frame,
                         text="Submit Feedback",
                         command=submit_feedback,
                         font=("Segoe UI", 14, "bold"),
                         bg="#4169e1",
                         fg="white",
                         activebackground="#1e40af",
                         relief="flat",
                         borderwidth=0,
                         cursor="hand2",
                         width=20,
                         height=2)
    submit_btn.pack(pady=20)