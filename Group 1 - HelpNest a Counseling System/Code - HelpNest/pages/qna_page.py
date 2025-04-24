# pages/qna_page.py
import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk  # For adding images (requires Pillow library)
from database import get_db_connection

class QnAPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#f0f0f0")  # Set background color
        self.controller = controller

        # Custom Fonts
        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        label_font = font.Font(family="Helvetica", size=12)
        button_font = font.Font(family="Helvetica", size=12, weight="bold")

        # Title Label
        tk.Label(self, text="Q&A", font=title_font, bg="#f0f0f0", fg="#333333").pack(pady=(30, 10))

        # Frame for Asking a Question
        ask_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, bd=2, relief="groove")
        ask_frame.pack(pady=20, fill="x")

        # Ask a Question Label
        tk.Label(ask_frame, text="Ask a Question", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Question Entry
        tk.Label(ask_frame, text="Question", font=label_font, bg="#ffffff", fg="#333333").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.question_entry = tk.Text(ask_frame, height=5, width=50, font=label_font, relief="solid", borderwidth=1)
        self.question_entry.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        # Category Dropdown
        tk.Label(ask_frame, text="Category", font=label_font, bg="#ffffff", fg="#333333").grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.category_var = tk.StringVar(value="Select a category")
        categories = ["Career", "Internships", "Personal Development"]
        category_dropdown = tk.OptionMenu(ask_frame, self.category_var, *categories)
        category_dropdown.config(font=label_font, relief="solid", borderwidth=1, bg="#ffffff", fg="#333333")
        category_dropdown.grid(row=4, column=0, pady=(0, 10), sticky="ew")

        # Anonymous Toggle
        self.anonymous_var = tk.BooleanVar(value=False)
        anonymous_check = tk.Checkbutton(
            ask_frame,
            text="Post Anonymously",
            variable=self.anonymous_var,
            font=label_font,
            bg="#ffffff",
            fg="#333333",
            activebackground="#ffffff"
        )
        anonymous_check.grid(row=4, column=1, pady=(0, 10), sticky="w")

        # Submit Button
        submit_button = tk.Button(
            ask_frame,
            text="Submit Question",
            font=button_font,
            bg="#0078d4",
            fg="#ffffff",
            relief="flat",
            activebackground="#005bb5",
            command=self.submit_question
        )
        submit_button.grid(row=5, column=0, columnspan=2, pady=(10, 0), ipadx=10, ipady=5, sticky="ew")

        # Frame for Viewing Questions
        view_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, bd=2, relief="groove")
        view_frame.pack(pady=20, fill="both", expand=True)

        # Search Bar
        tk.Label(view_frame, text="Search Questions", font=label_font, bg="#ffffff", fg="#333333").pack(anchor="w", pady=(0, 5))
        self.search_entry = tk.Entry(view_frame, font=label_font, relief="solid", borderwidth=1)
        self.search_entry.pack(fill="x", pady=(0, 10))

        # Filter Dropdown
        self.filter_var = tk.StringVar(value="All Categories")
        filters = ["All Categories", "Career", "Internships", "Personal Development"]
        filter_dropdown = tk.OptionMenu(view_frame, self.filter_var, *filters)
        filter_dropdown.config(font=label_font, relief="solid", borderwidth=1, bg="#ffffff", fg="#333333")
        filter_dropdown.pack(fill="x", pady=(0, 10))

        # List of Questions
        self.questions_listbox = tk.Listbox(
            view_frame,
            font=label_font,
            bg="#ffffff",
            fg="#333333",
            selectbackground="#0078d4",
            selectforeground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.questions_listbox.pack(fill="both", expand=True, pady=(0, 10))

        # Load Questions from Database
        self.load_questions()

        # Back to Dashboard Button
        back_button = tk.Button(
            self,
            text="Back to Dashboard",
            font=button_font,
            bg="#ff4d4d",
            fg="#ffffff",
            relief="flat",
            activebackground="#e60000",
            command=lambda: controller.show_frame("JuniorDashboardPage" if self.controller.role == "Junior" else "SeniorDashboardPage")
        )
        back_button.pack(pady=(10, 20), ipadx=10, ipady=5)

    def load_questions(self):
        """Load questions into the listbox from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT question FROM questions WHERE resolved=0")
            rows = cursor.fetchall()
            self.questions_listbox.delete(0, tk.END)
            for row in rows:
                self.questions_listbox.insert(tk.END, row[0])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading questions: {e}")
        finally:
            conn.close()

    def submit_question(self):
        """Submit a new question."""
        question = self.question_entry.get("1.0", tk.END).strip()
        category = self.category_var.get()
        anonymous = self.anonymous_var.get()

        # Validate inputs
        if not question or category == "Select a category":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Add question to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO questions (user_id, question, category, anonymous) VALUES (%s, %s, %s, %s)",
                (self.controller.user_id, question, category, int(anonymous))
            )
            conn.commit()
            messagebox.showinfo("Success", "Question submitted successfully!")
            self.question_entry.delete("1.0", tk.END)
            self.category_var.set("Select a category")
            self.anonymous_var.set(False)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

        # Reload questions
        self.questions_listbox.delete(0, tk.END)
        self.load_questions()