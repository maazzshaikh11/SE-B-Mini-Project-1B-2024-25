# pages/dashboard_senior.py
import tkinter as tk
from tkinter import font, messagebox, scrolledtext, ttk, filedialog
from PIL import Image, ImageTk
import os
from datetime import datetime, timedelta
from database import get_db_connection

class SeniorDashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        # Color scheme
        self.bg_color = "#ECF0F3"      # Soft background
        self.card_bg = "#FFFFFF"        # Card background
        self.primary_color = "#0A2463"  # Deep blue
        self.accent_color = "#3E92CC"   # Light blue
        self.text_color = "#1B1B1E"     # Near black
        self.error_color = "#D64045"    # Error red
        self.success_color = "#4CAF50"  # Green for success indicators

        tk.Frame.__init__(self, parent, bg=self.bg_color)
        self.controller = controller
        
        # Store question IDs for retrieval
        self.question_ids = []

        # Custom Fonts
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.heading_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=14, weight="bold")
        
        # Header with welcome message and availability toggle
        header_frame = tk.Frame(self, bg=self.primary_color, padx=20, pady=15)
        header_frame.pack(fill="x")
        
        header_left = tk.Frame(header_frame, bg=self.primary_color)
        header_left.pack(side="left", fill="y")
        
        self.welcome_label = tk.Label(
            header_left, 
            text="Welcome to Help Nest!", 
            font=self.title_font, 
            bg=self.primary_color, 
            fg="white"
        )
        self.welcome_label.pack(anchor="w")
        
        self.user_info_label = tk.Label(
            header_left,
            text="Senior Mentor Dashboard",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        )
        self.user_info_label.pack(anchor="w")
        
        # Availability toggle in header (right side)
        header_right = tk.Frame(header_frame, bg=self.primary_color)
        header_right.pack(side="right", fill="y")
        
        availability_frame = tk.Frame(header_right, bg=self.primary_color)
        availability_frame.pack(pady=(10, 0))
        
        tk.Label(
            availability_frame, 
            text="Status: ", 
            font=self.label_font, 
            bg=self.primary_color, 
            fg="white"
        ).pack(side=tk.LEFT)

        self.availability_var = tk.StringVar(value="Available")
        availability_toggle = ttk.Combobox(
            availability_frame,
            textvariable=self.availability_var,
            values=["Available", "Busy"],
            state="readonly",
            width=10,
            font=self.label_font
        )
        availability_toggle.pack(side=tk.LEFT, padx=(5, 0))
        availability_toggle.bind("<<ComboboxSelected>>", self.update_availability)
        
        # Style the combobox
        style = ttk.Style()
        style.configure("TCombobox", 
                        background=self.accent_color,
                        foreground=self.text_color,
                        fieldbackground=self.card_bg)
        
        # Main content area
        content_frame = tk.Frame(self, bg=self.bg_color, padx=40, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Create dashboard grid (2x2 grid of cards)
        # Row 1, Column 1: Answer Questions
        answer_card = self.create_dashboard_card(
            content_frame,
            "Answer Questions",
            "Help students with their career questions",
            "💬",
            self.show_answer_questions
        )
        answer_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Row 1, Column 2: My Answers
        my_answers_card = self.create_dashboard_card(
            content_frame,
            "My Answers",
            "View and manage your previous answers",
            "📝",
            self.show_my_answers
        )
        my_answers_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Row 2, Column 1: Manage Sessions
        sessions_card = self.create_dashboard_card(
            content_frame,
            "Mentoring Sessions",
            "View and manage one-on-one sessions",
            "📅",
            self.show_sessions
        )
        sessions_card.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        # Row 2, Column 2: Upload Resources
        resource_card = self.create_dashboard_card(
            content_frame,
            "Upload Resources",
            "Share learning materials with students",
            "📚",
            self.show_upload_resources
        )
        resource_card.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        
        # Configure grid to expand properly
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Stats bar showing key metrics
        stats_frame = tk.Frame(self, bg=self.card_bg, pady=10, padx=20)
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Create stats to display
        self.pending_questions_label = tk.Label(
            stats_frame,
            text="Pending Questions: 0",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.primary_color
        )
        self.pending_questions_label.pack(side="left", padx=(0, 15))
        
        self.answers_given_label = tk.Label(
            stats_frame,
            text="Answers Given: 0",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.primary_color
        )
        self.answers_given_label.pack(side="left", padx=(0, 15))
        
        self.average_rating_label = tk.Label(
            stats_frame,
            text="Average Rating: -",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.primary_color
        )
        self.average_rating_label.pack(side="left", padx=(0, 15))
        
        self.pending_sessions_label = tk.Label(
            stats_frame,
            text="Pending Sessions: 0",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.primary_color
        )
        self.pending_sessions_label.pack(side="left", padx=(0, 15))
        
        # Footer with logout button
        footer_frame = tk.Frame(self, bg=self.primary_color, padx=20, pady=10)
        footer_frame.pack(side="bottom", fill="x")
        
        logout_button = tk.Button(
            footer_frame,
            text="Logout",
            font=self.label_font,
            bg=self.error_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            activebackground="#b33333",
            command=self.logout
        )
        logout_button.pack(side="right")
        logout_button.bind("<Enter>", self.on_enter_logout)
        logout_button.bind("<Leave>", self.on_leave_logout)
        
        refresh_button = tk.Button(
            footer_frame,
            text="Refresh Dashboard",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            activebackground=self.primary_color,
            command=self.refresh
        )
        refresh_button.pack(side="left")
        refresh_button.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        refresh_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
        settings_button = tk.Button(
            footer_frame,
            text="Settings",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            activebackground=self.primary_color,
            command=lambda: controller.show_frame("SettingsPage")
        )
        settings_button.pack(side="left", padx=(10,0))
        settings_button.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        settings_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
    def create_dashboard_card(self, parent, title, description, icon, command):
        """Create a dashboard card with icon, title, description and action button."""
        card = tk.Frame(
            parent,
            bg=self.card_bg,
            relief="raised",
            bd=1,
            highlightbackground=self.accent_color,
            highlightthickness=1
        )
        
        # Icon and title at the top
        header = tk.Frame(card, bg=self.card_bg)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        icon_label = tk.Label(
            header,
            text=icon,
            font=font.Font(family="Helvetica", size=36),
            bg=self.card_bg,
            fg=self.primary_color
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        title_label = tk.Label(
            header,
            text=title,
            font=self.subtitle_font,
            bg=self.card_bg,
            fg=self.primary_color
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Description
        tk.Label(
            card,
            text=description,
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=250,
            justify="center"
        ).pack(fill="x", padx=20, pady=(0, 20))
        
        # Button
        action_button = tk.Button(
            card,
            text=f"Open {title}",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground=self.accent_color,
            activeforeground="white",
            command=command
        )
        action_button.pack(pady=(10, 30))
        
        # Hover effects
        action_button.bind("<Enter>", self.on_enter)
        action_button.bind("<Leave>", self.on_leave)
        
        # Make entire card clickable
        for widget in [card, icon_label, title_label]:
            widget.bind("<Button-1>", lambda e, cmd=command: cmd())
            widget.bind("<Enter>", lambda e, w=card: w.configure(bg="#f5f8fa", cursor="hand2"))
            widget.bind("<Leave>", lambda e, w=card: w.configure(bg=self.card_bg, cursor=""))
        
        return card
    
    def update_welcome_label(self):
        """Update welcome label with the current username."""
        if hasattr(self.controller, 'user_id') and self.controller.user_id:
            # Get the user's full name from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT name, department, expertise, availability
                    FROM users 
                    WHERE id = %s
                """, (self.controller.user_id,))
                user_data = cursor.fetchone()
                
                if user_data and user_data[0]:
                    self.welcome_label.config(text=f"Welcome, {user_data[0]}!")
                    
                    # Also update user info if available
                    info_parts = []
                    if user_data[1]:  # Department
                        info_parts.append(f"Department: {user_data[1]}")
                    if user_data[2]:  # Expertise
                        info_parts.append(f"Expertise: {user_data[2]}")
                        
                    if info_parts:
                        self.user_info_label.config(text=" | ".join(info_parts))
                    else:
                        self.user_info_label.config(text="Senior Mentor Dashboard")
                        
                    # Update availability toggle
                    if user_data[3]:
                        self.availability_var.set(user_data[3])
                    else:
                        self.availability_var.set("Available")
                else:
                    self.welcome_label.config(text=f"Welcome, Mentor!")
                    self.user_info_label.config(text="Senior Mentor Dashboard")
            except Exception as e:
                print(f"Error retrieving user data: {e}")
                self.welcome_label.config(text="Welcome to Help Nest!")
                self.user_info_label.config(text="Senior Mentor Dashboard")
            finally:
                conn.close()
        else:
            self.welcome_label.config(text="Welcome to Help Nest!")
            self.user_info_label.config(text="Senior Mentor Dashboard")
    
    def update_stats(self):
        """Update the statistics display."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Get count of pending questions (approved but not resolved)
            cursor.execute("""
                SELECT COUNT(*) FROM questions 
                WHERE approved = TRUE AND resolved = FALSE
            """)
            pending_count = cursor.fetchone()[0]
            self.pending_questions_label.config(text=f"Pending Questions: {pending_count}")
            
            # Get count of answers given by this mentor
            cursor.execute("""
                SELECT COUNT(*) FROM answers 
                WHERE user_id = %s
            """, (self.controller.user_id,))
            answers_given = cursor.fetchone()[0]
            self.answers_given_label.config(text=f"Answers Given: {answers_given}")
            
            # Get average rating
            cursor.execute("""
                SELECT AVG(rating) FROM answers 
                WHERE user_id = %s AND rating > 0
            """, (self.controller.user_id,))
            avg_rating = cursor.fetchone()[0]
            if avg_rating:
                self.average_rating_label.config(text=f"Average Rating: {avg_rating:.1f}/5")
            else:
                self.average_rating_label.config(text="Average Rating: -")
            
            # Get count of pending sessions
            cursor.execute("""
                SELECT COUNT(*) FROM sessions 
                WHERE senior_id = %s AND status = 'Pending'
            """, (self.controller.user_id,))
            pending_sessions = cursor.fetchone()[0]
            self.pending_sessions_label.config(text=f"Pending Sessions: {pending_sessions}")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
        finally:
            conn.close()
    
    def show_answer_questions(self):
        """Show dialog to answer questions."""
        dialog = tk.Toplevel(self)
        dialog.title("Answer Questions")
        dialog.geometry("900x1050")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        header_left = tk.Frame(header, bg=self.primary_color)
        header_left.pack(side="left")
        
        tk.Label(
            header_left,
            text="Questions Pending Your Expertise",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        tk.Label(
            header_left,
            text="Select a question and provide your guidance to help students",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        header_right = tk.Frame(header, bg=self.primary_color)
        header_right.pack(side="right")
        
        refresh_btn = tk.Button(
            header_right,
            text="Refresh Questions",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=10,
            pady=2,
            command=lambda: self.load_questions_to_tree(questions_tree, filter_var.get())
        )
        refresh_btn.pack()
        refresh_btn.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        refresh_btn.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
        # Filter section
        filter_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        filter_frame.pack(fill="x")
        
        tk.Label(
            filter_frame,
            text="Filter Questions:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        filter_var = tk.StringVar(value="All")
        filters = ["All", "Newest", "Oldest", "Unanswered"]
        filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=filter_var,
            values=filters,
            state="readonly",
            font=self.label_font,
            width=15
        )
        filter_dropdown.pack(side="left")
        filter_dropdown.bind("<<ComboboxSelected>>", 
                          lambda e: self.load_questions_to_tree(questions_tree, filter_var.get()))
        
        # Category filter
        category_frame = tk.Frame(filter_frame, bg=self.bg_color)
        category_frame.pack(side="right")
        
        tk.Label(
            category_frame,
            text="Category:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        category_var = tk.StringVar(value="All Categories")
        categories = ["All Categories", "Career", "Internships", "Higher Studies"]
        category_dropdown = ttk.Combobox(
            category_frame,
            textvariable=category_var,
            values=categories,
            state="readonly",
            font=self.label_font,
            width=15
        )
        category_dropdown.pack(side="left")
        category_dropdown.bind("<<ComboboxSelected>>", 
                             lambda e: self.load_questions_to_tree(questions_tree, filter_var.get(), category_var.get()))
        
        # Questions treeview
        tree_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("category", "question", "asker", "date", "status")
        questions_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )
        
        # Define headings
        questions_tree.heading("category", text="Category")
        questions_tree.heading("question", text="Question")
        questions_tree.heading("asker", text="Asked By")
        questions_tree.heading("date", text="Date Posted")
        questions_tree.heading("status", text="Status")
        
        # Define columns width
        questions_tree.column("category", width=100, minwidth=80)
        questions_tree.column("question", width=350, minwidth=200)
        questions_tree.column("asker", width=120, minwidth=100)
        questions_tree.column("date", width=120, minwidth=100)
        questions_tree.column("status", width=120, minwidth=100)
        
        # Configure scrollbar
        scrollbar.config(command=questions_tree.yview)
        questions_tree.configure(yscrollcommand=scrollbar.set)
        
        questions_tree.pack(fill="both", expand=True)
        
        # Load questions
        self.question_ids = []  # Clear question IDs
        self.load_questions_to_tree(questions_tree, "All")
        
        # Action buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        button_frame.pack(fill="x")
        
        answer_button = tk.Button(
            button_frame,
            text="Answer Selected Question",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.answer_selected_question(questions_tree, dialog)
        )
        answer_button.pack(side="left")
        answer_button.bind("<Enter>", self.on_enter)
        answer_button.bind("<Leave>", self.on_leave)
        
        view_button = tk.Button(
            button_frame,
            text="View Question Details",
            font=self.button_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.view_question_details(questions_tree)
        )
        view_button.pack(side="left", padx=10)
        view_button.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        view_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            font=self.button_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        close_button.pack(side="right")
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Double-click to view details
        questions_tree.bind("<Double-1>", lambda e: self.answer_selected_question(questions_tree, dialog))
        
    def load_questions_to_tree(self, tree, filter_type, category="All Categories"):
        """Load questions into the treeview based on filter and category."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.question_ids = []  # Reset question IDs
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Base query
            base_query = """
                SELECT q.id, q.question, q.category, q.timestamp, 
                       CASE WHEN q.anonymous = 1 THEN 'Anonymous' ELSE u.name END as asker,
                       q.approved, q.resolved,
                       (SELECT COUNT(*) FROM answers WHERE question_id = q.id) as answer_count
                FROM questions q
                LEFT JOIN users u ON q.user_id = u.id
                WHERE q.approved = TRUE
            """
            
            # Add category filter if specified
            if category != "All Categories":
                base_query += f" AND q.category = '{category}'"
            
            # Add order based on filter type
            if filter_type == "Newest":
                base_query += " ORDER BY q.timestamp DESC"
            elif filter_type == "Oldest":
                base_query += " ORDER BY q.timestamp ASC"
            elif filter_type == "Unanswered":
                base_query += " AND (SELECT COUNT(*) FROM answers WHERE question_id = q.id) = 0 ORDER BY q.timestamp DESC"
            else:  # All
                base_query += " ORDER BY q.timestamp DESC"
            
            cursor.execute(base_query)
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("", "No questions found", "", "", ""))
                return
                
            for row in rows:
                # Unpack row data
                question_id, question, category, timestamp, asker, approved, resolved, answer_count = row
                
                # Store the question ID
                self.question_ids.append(question_id)
                
                # Format data for display
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                truncated_question = question if len(question) < 50 else f"{question[:50]}..."
                
                # Determine status
                if resolved:
                    status = "Resolved"
                elif answer_count > 0:
                    status = f"{answer_count} Answers"
                else:
                    status = "Unanswered"
                
                # Insert into tree
                item_id = tree.insert(
                    "",
                    "end",
                    values=(category, truncated_question, asker, formatted_time, status)
                )
                
                # Apply tags for visual status
                if resolved:
                    tree.item(item_id, tags=("resolved",))
                elif answer_count > 0:
                    tree.item(item_id, tags=("answered",))
                else:
                    tree.item(item_id, tags=("unanswered",))
            
            # Configure tag colors
            tree.tag_configure("resolved", foreground=self.success_color)
            tree.tag_configure("answered", foreground=self.accent_color)
            tree.tag_configure("unanswered", foreground=self.error_color)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {e}")
        finally:
            conn.close()
    
    def answer_selected_question(self, tree, parent_dialog=None):
        """Open a dialog to answer the selected question."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Question", "Please select a question to answer.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.question_ids):
            return
            
        question_id = self.question_ids[item_index]
        
        # Fetch question details
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT q.question, q.category, q.timestamp, 
                       CASE WHEN q.anonymous = 1 THEN 'Anonymous' ELSE u.name END as asker,
                       q.resolved, u.department, u.year
                FROM questions q
                LEFT JOIN users u ON q.user_id = u.id
                WHERE q.id = %s
            """, (question_id,))
            
            question_data = cursor.fetchone()
            if not question_data:
                messagebox.showerror("Error", "Question not found!")
                return
                
            question_text, category, timestamp, asker, resolved, department, year = question_data
            
            # Check if already resolved
            if resolved:
                if messagebox.askyesno(
                    "Question Resolved", 
                    "This question is already marked as resolved. Do you still want to add an answer?"
                ):
                    pass
                else:
                    return
            
            # Create answer dialog
            answer_dialog = tk.Toplevel(self)
            answer_dialog.title("Answer Question")
            answer_dialog.geometry("900x900")
            answer_dialog.configure(bg=self.bg_color)
            answer_dialog.transient(self if parent_dialog is None else parent_dialog)
            answer_dialog.grab_set()
            
            # Header
            header = tk.Frame(answer_dialog, bg=self.primary_color, padx=20, pady=15)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text=f"Answer Question - {category}",
                font=self.subtitle_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            meta_info = []
            if asker != "Anonymous":
                meta_info.append(f"Asked by: {asker}")
            if department:
                meta_info.append(f"Department: {department}")
            if year:
                meta_info.append(f"Year: {year}")
                
            meta_text = " | ".join(meta_info) if meta_info else "Asked anonymously"
            meta_text += f" | Posted: {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            tk.Label(
                header,
                text=meta_text,
                font=self.label_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            # Question content
            question_frame = tk.Frame(answer_dialog, bg=self.card_bg, padx=20, pady=20)
            question_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(
                question_frame,
                text="Question:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            question_display = scrolledtext.ScrolledText(
                question_frame,
                height=6,
                font=self.label_font,
                wrap="word",
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1
            )
            question_display.pack(fill="x", pady=10)
            question_display.insert("1.0", question_text)
            question_display.config(state="disabled")
            
            # Answer section
            answer_frame = tk.Frame(answer_dialog, bg=self.card_bg, padx=20, pady=20)
            answer_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            tk.Label(
                answer_frame,
                text="Your Answer:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            answer_text = scrolledtext.ScrolledText(
                answer_frame,
                height=12,
                font=self.label_font,
                wrap="word",
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1
            )
            answer_text.pack(fill="both", expand=True, pady=10)
            
            # Focus on the answer text area
            answer_text.focus_set()
            
            # Option to mark as resolved
            resolve_var = tk.BooleanVar(value=True)
            resolve_check = tk.Checkbutton(
                answer_frame,
                text="Mark question as resolved after answering",
                variable=resolve_var,
                font=self.label_font,
                bg=self.card_bg,
                fg=self.text_color,
                selectcolor=self.card_bg,
                activebackground=self.card_bg
            )
            resolve_check.pack(anchor="w")
            
            # Buttons
            button_frame = tk.Frame(answer_dialog, bg=self.bg_color, padx=20, pady=15)
            button_frame.pack(fill="x")
            
            cancel_button = tk.Button(
                button_frame,
                text="Cancel",
                font=self.button_font,
                bg="#E0E0E0",
                fg=self.text_color,
                relief="flat",
                padx=15,
                pady=5,
                command=answer_dialog.destroy
            )
            cancel_button.pack(side="left")
            cancel_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
            cancel_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
            
            submit_button = tk.Button(
                button_frame,
                text="Submit Answer",
                font=self.button_font,
                bg=self.primary_color,
                fg="white",
                relief="flat",
                padx=15,
                pady=5,
                command=lambda: self.submit_answer(
                    question_id, 
                    answer_text.get("1.0", tk.END).strip(), 
                    resolve_var.get(),
                    answer_dialog
                )
            )
            submit_button.pack(side="right")
            submit_button.bind("<Enter>", self.on_enter)
            submit_button.bind("<Leave>", self.on_leave)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load question: {e}")
        finally:
            conn.close()
    
    def submit_answer(self, question_id, answer, resolve, dialog):
        """Submit an answer and optionally mark the question as resolved."""
        if not answer.strip():
            messagebox.showerror("Error", "Please provide an answer.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert the answer
            cursor.execute(
                "INSERT INTO answers (question_id, user_id, answer) VALUES (%s, %s, %s)",
                (question_id, self.controller.user_id, answer)
            )
            
            # Mark as resolved if checked
            if resolve:
                cursor.execute(
                    "UPDATE questions SET resolved = TRUE WHERE id = %s",
                    (question_id,)
                )
                
            # Get student ID to notify
            cursor.execute(
                "SELECT user_id FROM questions WHERE id = %s",
                (question_id,)
            )
            student_id = cursor.fetchone()[0]
            
            # Create a notification for the student
            if student_id:
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (student_id, f"Your question has been answered by {self.controller.username}.")
                )
                
            conn.commit()
            messagebox.showinfo("Success", "Your answer has been submitted successfully!")
            
            # Close dialog
            dialog.destroy()
            
            # Refresh stats
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not submit answer: {e}")
        finally:
            conn.close()
    
    def view_question_details(self, tree):
        """View full details of a question without answering it."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Question", "Please select a question to view.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.question_ids):
            return
            
        question_id = self.question_ids[item_index]
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Question Details")
        dialog.geometry("700x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Get question data
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Get question details
            cursor.execute("""
                SELECT q.question, q.category, q.timestamp, 
                       CASE WHEN q.anonymous = 1 THEN 'Anonymous' ELSE u.name END as asker,
                       q.resolved, q.approved, u.department, u.year
                FROM questions q
                LEFT JOIN users u ON q.user_id = u.id
                WHERE q.id = %s
            """, (question_id,))
            
            question_data = cursor.fetchone()
            if not question_data:
                messagebox.showerror("Error", "Question not found!")
                dialog.destroy()
                return
                
            question_text, category, timestamp, asker, resolved, approved, department, year = question_data
            
            # Question header
            header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text=f"Question Details - {category}",
                font=self.subtitle_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            meta_info = []
            if asker != "Anonymous":
                meta_info.append(f"Asked by: {asker}")
            if department:
                meta_info.append(f"Department: {department}")
            if year:
                meta_info.append(f"Year: {year}")
                
            meta_text = " | ".join(meta_info) if meta_info else "Asked anonymously"
            meta_text += f" | Posted: {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            tk.Label(
                header,
                text=meta_text,
                font=self.label_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            status_text = f"Status: {'Resolved' if resolved else 'Unresolved'} | {'Approved' if approved else 'Pending Approval'}"
            tk.Label(
                header,
                text=status_text,
                font=self.label_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            # Question content
            question_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            question_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(
                question_frame,
                text="Question:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            question_display = scrolledtext.ScrolledText(
                question_frame,
                height=6,
                font=self.label_font,
                wrap="word",
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1
            )
            question_display.pack(fill="x", pady=10)
            question_display.insert("1.0", question_text)
            question_display.config(state="disabled")
            
            # Answers section
            answers_label_frame = tk.Frame(dialog, bg=self.bg_color, padx=20)
            answers_label_frame.pack(fill="x")
            
            tk.Label(
                answers_label_frame,
                text="Existing Answers",
                font=self.heading_font,
                bg=self.bg_color,
                fg=self.primary_color
            ).pack(anchor="w", pady=(10, 5))
            
            # Get existing answers
            cursor.execute("""
                SELECT a.answer, u.name, a.timestamp, a.rating
                FROM answers a
                JOIN users u ON a.user_id = u.id
                WHERE a.question_id = %s
                ORDER BY a.timestamp DESC
            """, (question_id,))
            
            answers = cursor.fetchall()
            
            # Create scrollable frame for answers
            answers_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            answers_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            if not answers:
                tk.Label(
                    answers_frame,
                    text="No answers yet.",
                    font=("Helvetica", 12, "italic"),
                    bg=self.card_bg,
                    fg=self.text_color,
                    pady=30
                ).pack()
            else:
                # Create scrollable canvas
                canvas = tk.Canvas(answers_frame, bg=self.card_bg, highlightthickness=0)
                scrollbar = ttk.Scrollbar(answers_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg=self.card_bg)
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Function to adjust frame width when canvas is resized
                def on_canvas_configure(e):
                    canvas.itemconfig(
                        canvas.find_withtag("all")[0], 
                        width=e.width - 5
                    )
                
                canvas.bind("<Configure>", on_canvas_configure)
                
                # Add each answer
                for i, (answer_text, answerer, answer_time, rating) in enumerate(answers):
                    answer_container = tk.Frame(
                        scrollable_frame,
                        bg="#F5F5F5" if i % 2 == 0 else self.card_bg,
                        relief="solid",
                        borderwidth=1,
                        padx=15,
                        pady=15
                    )
                    answer_container.pack(fill="x", pady=5)
                    
                    # Answer header
                    header_frame = tk.Frame(answer_container, bg=answer_container["bg"])
                    header_frame.pack(fill="x", pady=(0, 10))
                    
                    # Answerer info
                    tk.Label(
                        header_frame,
                        text=f"Answered by: {answerer if answerer == self.controller.username else 'Another mentor'}",
                        font=("Helvetica", 11, "bold"),
                        bg=header_frame["bg"],
                        fg=self.primary_color
                    ).pack(side="left")
                    
                    # Time and rating
                    rating_text = f"Rating: {'★' * rating + '☆' * (5 - rating) if rating else 'Not rated yet'}"
                    meta_text = f"{answer_time.strftime('%Y-%m-%d %H:%M')} | {rating_text}"
                    
                    tk.Label(
                        header_frame,
                        text=meta_text,
                        font=("Helvetica", 10),
                        bg=header_frame["bg"],
                        fg=self.text_color
                    ).pack(side="right")
                    
                    # Answer content
                    answer_scroll = scrolledtext.ScrolledText(
                        answer_container,
                        height=4,
                        font=self.label_font,
                        wrap="word",
                        bg=answer_container["bg"],
                        fg=self.text_color,
                        relief="flat"
                    )
                    answer_scroll.pack(fill="x")
                    answer_scroll.insert("1.0", answer_text)
                    answer_scroll.config(state="disabled")
                    
            # Action buttons
            button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
            button_frame.pack(fill="x")
            
            # Add answer button
            if not resolved:
                answer_btn = tk.Button(
                    button_frame,
                    text="Add Answer",
                    font=self.button_font,
                    bg=self.primary_color,
                    fg="white",
                    relief="flat",
                    padx=15,
                    pady=5,
                    command=lambda: [dialog.destroy(), self.answer_selected_question(tree)]
                )
                answer_btn.pack(side="left")
                answer_btn.bind("<Enter>", self.on_enter)
                answer_btn.bind("<Leave>", self.on_leave)
            
            close_button = tk.Button(
                button_frame,
                text="Close",
                font=self.button_font,
                bg="#E0E0E0",
                fg=self.text_color,
                relief="flat",
                padx=15,
                pady=5,
                command=dialog.destroy
            )
            close_button.pack(side="right")
            close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
            close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load question details: {e}")
        finally:
            conn.close()
    
    def show_my_answers(self):
        """Show a dialog with all answers given by this mentor."""
        dialog = tk.Toplevel(self)
        dialog.title("My Answers")
        dialog.geometry("900x900")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="My Answers",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="View all the answers you've provided to student questions",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        # Filter section
        filter_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        filter_frame.pack(fill="x")
        
        tk.Label(
            filter_frame,
            text="Filter By:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        filter_var = tk.StringVar(value="All")
        filters = ["All", "Newest", "Oldest", "Highest Rated", "Unrated"]
        filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=filter_var,
            values=filters,
            state="readonly",
            font=self.label_font,
            width=15
        )
        filter_dropdown.pack(side="left")
        
        # Search box
        search_frame = tk.Frame(filter_frame, bg=self.bg_color)
        search_frame.pack(side="right")
        
        tk.Label(
            search_frame,
            text="Search:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side="left", padx=(0, 5))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=search_var,
            font=self.label_font,
            width=20,
            relief="solid",
            borderwidth=1
        )
        search_entry.pack(side="left", padx=(0, 5))
        
        search_button = tk.Button(
            search_frame,
            text="Search",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=10,
            pady=2,
            command=lambda: self.load_my_answers_to_tree(
                answers_tree, 
                filter_var.get(), 
                search_var.get()
            )
        )
        search_button.pack(side="left")
        search_button.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        search_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
        # Answers treeview
        tree_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("question", "answer_preview", "date", "rating")
        answers_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )
        
        # Define headings
        answers_tree.heading("question", text="Question")
        answers_tree.heading("answer_preview", text="Answer Preview")
        answers_tree.heading("date", text="Date Answered")
        answers_tree.heading("rating", text="Rating")
        
        # Define columns width
        answers_tree.column("question", width=300, minwidth=200)
        answers_tree.column("answer_preview", width=300, minwidth=200)
        answers_tree.column("date", width=120, minwidth=100)
        answers_tree.column("rating", width=80, minwidth=80)
        
        # Configure scrollbar
        scrollbar.config(command=answers_tree.yview)
        answers_tree.configure(yscrollcommand=scrollbar.set)
        
        answers_tree.pack(fill="both", expand=True)
        
        # Load answers
        self.answer_ids = []  # Clear answer IDs
        self.load_my_answers_to_tree(answers_tree, "All")
        
        # Apply filter when selected
        filter_dropdown.bind("<<ComboboxSelected>>", 
                           lambda e: self.load_my_answers_to_tree(
                               answers_tree, 
                               filter_var.get(), 
                               search_var.get()
                           ))
        
        # Action buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        button_frame.pack(fill="x")
        
        view_button = tk.Button(
            button_frame,
            text="View Full Answer",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.view_full_answer(answers_tree)
        )
        view_button.pack(side="left")
        view_button.bind("<Enter>", self.on_enter)
        view_button.bind("<Leave>", self.on_leave)
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            font=self.button_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        close_button.pack(side="right")
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Double-click to view full answer
        answers_tree.bind("<Double-1>", lambda e: self.view_full_answer(answers_tree))
    
    def load_my_answers_to_tree(self, tree, filter_type, search_term=""):
        """Load this mentor's answers into the treeview."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.answer_ids = []  # Reset answer IDs
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Base query
            base_query = """
                SELECT a.id, a.answer, a.timestamp, a.rating, 
                       q.question, q.category, q.resolved
                FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE a.user_id = %s
            """
            
            # Add search condition if provided
            if search_term:
                base_query += f" AND (a.answer LIKE '%{search_term}%' OR q.question LIKE '%{search_term}%')"
            
            # Add filter conditions
            if filter_type == "Newest":
                base_query += " ORDER BY a.timestamp DESC"
            elif filter_type == "Oldest":
                base_query += " ORDER BY a.timestamp ASC"
            elif filter_type == "Highest Rated":
                base_query += " ORDER BY a.rating DESC, a.timestamp DESC"
            elif filter_type == "Unrated":
                base_query += " AND (a.rating IS NULL OR a.rating = 0) ORDER BY a.timestamp DESC"
            else:  # All
                base_query += " ORDER BY a.timestamp DESC"
            
            cursor.execute(base_query, (self.controller.user_id,))
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No answers found", "", "", ""))
                return
                
            for row in rows:
                # Unpack row data
                answer_id, answer, timestamp, rating, question, category, resolved = row
                
                # Store the answer ID
                self.answer_ids.append(answer_id)
                
                # Format data for display
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                truncated_question = question if len(question) < 40 else f"{question[:40]}..."
                truncated_answer = answer if len(answer) < 40 else f"{answer[:40]}..."
                
                # Format rating
                rating_display = rating if rating else "-"
                if rating:
                    rating_display = f"{rating}/5"
                
                # Insert into tree
                item_id = tree.insert(
                    "",
                    "end",
                    values=(truncated_question, truncated_answer, formatted_time, rating_display)
                )
                
                # Apply tags for visual status
                if resolved:
                    tree.item(item_id, tags=("resolved",))
                if rating and rating >= 4:
                    tree.item(item_id, tags=("high_rating",))
                elif rating and rating < 3:
                    tree.item(item_id, tags=("low_rating",))
            
            # Configure tag colors
            tree.tag_configure("resolved", foreground=self.success_color)
            tree.tag_configure("high_rating", foreground="#FFD700")  # Gold color for high ratings
            tree.tag_configure("low_rating", foreground="#FFA500")   # Orange for low ratings
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load answers: {e}")
        finally:
            conn.close()
    
    def view_full_answer(self, tree):
        """View the full answer and related question."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select an Answer", "Please select an answer to view.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.answer_ids):
            return
            
        answer_id = self.answer_ids[item_index]
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Answer Details")
        dialog.geometry("700x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Get answer data
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Get answer details
            cursor.execute("""
                SELECT a.answer, a.timestamp, a.rating, 
                       q.question, q.category, q.resolved,
                       CASE WHEN q.anonymous = 1 THEN 'Anonymous' ELSE u.name END as asker
                FROM answers a
                JOIN questions q ON a.question_id = q.id
                LEFT JOIN users u ON q.user_id = u.id
                WHERE a.id = %s
            """, (answer_id,))
            
            answer_data = cursor.fetchone()
            if not answer_data:
                messagebox.showerror("Error", "Answer not found!")
                dialog.destroy()
                return
                
            answer_text, timestamp, rating, question_text, category, resolved, asker = answer_data
            
            # Answer header
            header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text=f"Answer Details - {category}",
                font=self.subtitle_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            status_text = f"Status: {'Resolved' if resolved else 'Open'}"
            if rating:
                status_text += f" | Rating: {rating}/5"
            else:
                status_text += " | Not rated yet"
                
            tk.Label(
                header,
                text=f"{status_text} | Answered on: {timestamp.strftime('%Y-%m-%d %H:%M')}",
                font=self.label_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            # Original question section
            question_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            question_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(
                question_frame,
                text=f"Question by {asker}:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            question_display = scrolledtext.ScrolledText(
                question_frame,
                height=5,
                font=self.label_font,
                wrap="word",
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1
            )
            question_display.pack(fill="x", pady=10)
            question_display.insert("1.0", question_text)
            question_display.config(state="disabled")
            
            # Your answer section
            answer_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            answer_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            tk.Label(
                answer_frame,
                text="Your Answer:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            answer_display = scrolledtext.ScrolledText(
                answer_frame,
                height=12,
                font=self.label_font,
                wrap="word",
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1
            )
            answer_display.pack(fill="both", expand=True, pady=10)
            answer_display.insert("1.0", answer_text)
            answer_display.config(state="disabled")
            
            # Rating display if rated
            if rating:
                rating_frame = tk.Frame(answer_frame, bg=self.card_bg)
                rating_frame.pack(fill="x", pady=(0, 10))
                
                stars = "★" * rating + "☆" * (5 - rating)
                tk.Label(
                    rating_frame,
                    text=f"Rating: {stars} ({rating}/5)",
                    font=self.label_font,
                    bg=self.card_bg,
                    fg="#FFD700"
                ).pack(side="right")
            
            # Close button
            button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
            button_frame.pack(fill="x")
            
            close_button = tk.Button(
                button_frame,
                text="Close",
                font=self.button_font,
                bg="#E0E0E0",
                fg=self.text_color,
                relief="flat",
                padx=15,
                pady=5,
                command=dialog.destroy
            )
            close_button.pack(side="right")
            close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
            close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load answer details: {e}")
        finally:
            conn.close()
    
    def show_sessions(self):
        """Show interface for managing mentoring sessions."""
        dialog = tk.Toplevel(self)
        dialog.title("Mentoring Sessions")
        dialog.geometry("900x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="Mentoring Sessions",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="Manage one-on-one mentoring sessions with students",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        # Notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Style the notebook
        style = ttk.Style()
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background=self.card_bg, foreground=self.text_color)
        style.map("TNotebook.Tab", 
                  background=[("selected", self.primary_color)],
                  foreground=[("selected", "white")])
        
        # Tab 1: Pending Sessions
        pending_frame = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(pending_frame, text="  Pending Requests  ")
        
        # Tab 2: Upcoming Sessions
        upcoming_frame = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(upcoming_frame, text="  Upcoming Sessions  ")
        
        # Tab 3: Past Sessions
        past_frame = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(past_frame, text="  Past Sessions  ")
        
        # Setup each tab
        self.setup_pending_sessions_tab(pending_frame)
        self.setup_upcoming_sessions_tab(upcoming_frame)
        self.setup_past_sessions_tab(past_frame)
        
        # Bottom buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        button_frame.pack(fill="x")
        
        refresh_button = tk.Button(
            button_frame,
            text="Refresh All",
            font=self.button_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.refresh_session_tabs(dialog)
        )
        refresh_button.pack(side="left")
        refresh_button.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        refresh_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            font=self.button_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        close_button.pack(side="right")
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
    
    def setup_pending_sessions_tab(self, parent_frame):
        """Setup the pending sessions tab."""
        # Treeview for pending sessions
        tree_frame = tk.Frame(parent_frame, bg=self.card_bg, padx=20, pady=20)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("student", "date", "time", "purpose")
        pending_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10
        )
        
        # Define headings
        pending_tree.heading("student", text="Student")
        pending_tree.heading("date", text="Date")
        pending_tree.heading("time", text="Time")
        pending_tree.heading("purpose", text="Purpose")
        
        # Define columns width
        pending_tree.column("student", width=150, minwidth=100)
        pending_tree.column("date", width=100, minwidth=80)
        pending_tree.column("time", width=80, minwidth=50)
        pending_tree.column("purpose", width=400, minwidth=200)
        
        # Configure scrollbar
        scrollbar.config(command=pending_tree.yview)
        pending_tree.configure(yscrollcommand=scrollbar.set)
        
        pending_tree.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = tk.Frame(parent_frame, bg=self.card_bg, padx=20, pady=10)
        button_frame.pack(fill="x")
        
        accept_button = tk.Button(
            button_frame,
            text="Accept Request",
            font=self.label_font,
            bg=self.success_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.accept_session_request(pending_tree)
        )
        accept_button.pack(side="left", padx=(0, 10))
        accept_button.bind("<Enter>", lambda e: e.widget.configure(bg="#3d8b40"))
        accept_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.success_color))
        
        decline_button = tk.Button(
            button_frame,
            text="Decline Request",
            font=self.label_font,
            bg=self.error_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.decline_session_request(pending_tree)
        )
        decline_button.pack(side="left")
        decline_button.bind("<Enter>", lambda e: e.widget.configure(bg="#b33333"))
        decline_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.error_color))
        
        # Load pending sessions
        self.pending_session_ids = []
        self.load_pending_sessions(pending_tree)
        
        # Store the tree for refreshing
        parent_frame.pending_tree = pending_tree
    
    def setup_upcoming_sessions_tab(self, parent_frame):
        """Setup the upcoming sessions tab."""
        # Treeview for upcoming sessions
        tree_frame = tk.Frame(parent_frame, bg=self.card_bg, padx=20, pady=20)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("student", "date", "time", "status", "purpose")
        upcoming_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10
        )
        
        # Define headings
        upcoming_tree.heading("student", text="Student")
        upcoming_tree.heading("date", text="Date")
        upcoming_tree.heading("time", text="Time")
        upcoming_tree.heading("status", text="Status")
        upcoming_tree.heading("purpose", text="Purpose")
        
        # Define columns width
        upcoming_tree.column("student", width=150, minwidth=100)
        upcoming_tree.column("date", width=100, minwidth=80)
        upcoming_tree.column("time", width=80, minwidth=50)
        upcoming_tree.column("status", width=100, minwidth=80)
        upcoming_tree.column("purpose", width=300, minwidth=200)
        
        # Configure scrollbar
        scrollbar.config(command=upcoming_tree.yview)
        upcoming_tree.configure(yscrollcommand=scrollbar.set)
        
        upcoming_tree.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = tk.Frame(parent_frame, bg=self.card_bg, padx=20, pady=10)
        button_frame.pack(fill="x")
        
        complete_button = tk.Button(
            button_frame,
            text="Mark as Completed",
            font=self.label_font,
            bg=self.success_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.complete_session(upcoming_tree)
        )
        complete_button.pack(side="left", padx=(0, 10))
        complete_button.bind("<Enter>", lambda e: e.widget.configure(bg="#3d8b40"))
        complete_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.success_color))
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel Session",
            font=self.label_font,
            bg=self.error_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.cancel_session(upcoming_tree)
        )
        cancel_button.pack(side="left")
        cancel_button.bind("<Enter>", lambda e: e.widget.configure(bg="#b33333"))
        cancel_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.error_color))
        
        # Load upcoming sessions
        self.upcoming_session_ids = []
        self.load_upcoming_sessions(upcoming_tree)
        
        # Store the tree for refreshing
        parent_frame.upcoming_tree = upcoming_tree
    
    def setup_past_sessions_tab(self, parent_frame):
        """Setup the past sessions tab."""
        # Treeview for past sessions
        tree_frame = tk.Frame(parent_frame, bg=self.card_bg, padx=20, pady=20)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("student", "date", "time", "status")
        past_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10
        )
        
        # Define headings
        past_tree.heading("student", text="Student")
        past_tree.heading("date", text="Date")
        past_tree.heading("time", text="Time")
        past_tree.heading("status", text="Status")
        
        # Define columns width
        past_tree.column("student", width=200, minwidth=150)
        past_tree.column("date", width=120, minwidth=100)
        past_tree.column("time", width=100, minwidth=80)
        past_tree.column("status", width=120, minwidth=100)
        
        # Configure scrollbar
        scrollbar.config(command=past_tree.yview)
        past_tree.configure(yscrollcommand=scrollbar.set)
        
        past_tree.pack(fill="both", expand=True)
        
        # Load past sessions
        self.past_session_ids = []
        self.load_past_sessions(past_tree)  # Make sure this line is correct
        
        # Store the tree for refreshing
        parent_frame.past_tree = past_tree
    
    def load_pending_sessions(self, tree):
        """Load pending session requests into the tree."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.pending_session_ids = []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Simplified query to avoid the CONCAT issue
            cursor.execute("""
                SELECT s.id, u.name, s.date, s.time, n.message
                FROM sessions s
                JOIN users u ON s.junior_id = u.id
                LEFT JOIN notifications n ON n.user_id = %s 
                    AND n.message LIKE CONCAT('%%', u.name, '%%', 'session request%%')
                WHERE s.senior_id = %s AND s.status = 'Pending'
                ORDER BY s.date, s.time
            """, (self.controller.user_id, self.controller.user_id))
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No pending requests", "", "", ""))
                return

                
            for row in rows:
                # Unpack row data
                session_id, student_name, session_date, session_time, notification = row
                
                # Store the session ID
                self.pending_session_ids.append(session_id)
                
                # Extract purpose from notification if available
                purpose = "No details provided"
                if notification:
                    # Extract purpose part from notification message
                    purpose_start = notification.find("Purpose:")
                    if purpose_start > 0:
                        purpose = notification[purpose_start + 8:].strip()
                
                # Format date and time
                formatted_date = session_date.strftime("%Y-%m-%d") if hasattr(session_date, 'strftime') else str(session_date)
                # Fix for timedelta object
                if isinstance(session_time, timedelta):
                    # Convert timedelta to string in HH:MM format
                    total_seconds = int(session_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_time = f"{hours:02d}:{minutes:02d}"
                else:
                    formatted_time = session_time.strftime("%H:%M") if hasattr(session_time, 'strftime') else str(session_time)
                
                # Insert into tree
                tree.insert(
                    "",
                    "end",
                    values=(student_name, formatted_date, formatted_time, purpose)
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pending sessions: {e}")
        finally:
            conn.close()
    
    def load_upcoming_sessions(self, tree):
        """Load upcoming accepted sessions into the tree."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.upcoming_session_ids = []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.id, u.name, s.date, s.time, s.status,
                    n.message
                FROM sessions s
                JOIN users u ON s.junior_id = u.id
                LEFT JOIN notifications n ON n.user_id = %s 
                    AND n.message LIKE CONCAT('%%', u.name, '%%', 'session request%%')
                WHERE s.senior_id = %s 
                AND s.status = 'Active'
                AND s.date >= CURDATE()
                ORDER BY s.date, s.time
            """, (self.controller.user_id, self.controller.user_id))
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No upcoming sessions", "", "", "", ""))
                return
                
            for row in rows:
                # Unpack row data
                session_id, student_name, session_date, session_time, status, notification = row
                
                # Store the session ID
                self.upcoming_session_ids.append(session_id)
                
                # Extract purpose from notification if available
                purpose = "No details provided"
                if notification:
                    # Extract purpose part from notification message
                    purpose_start = notification.find("Purpose:")
                    if purpose_start > 0:
                        purpose = notification[purpose_start + 8:].strip()
                
                # Format date and time
                formatted_date = session_date.strftime("%Y-%m-%d") if hasattr(session_date, 'strftime') else str(session_date)
                # Fix for timedelta object
                if isinstance(session_time, timedelta):
                    # Convert timedelta to string in HH:MM format
                    total_seconds = int(session_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_time = f"{hours:02d}:{minutes:02d}"
                else:
                    formatted_time = session_time.strftime("%H:%M") if hasattr(session_time, 'strftime') else str(session_time)
                
                # Insert into tree
                tree.insert(
                    "",
                    "end",
                    values=(student_name, formatted_date, formatted_time, status, purpose)
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load upcoming sessions: {e}")
        finally:
            conn.close()

    def load_past_sessions(self, tree):
        """Load past sessions into the tree."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.past_session_ids = []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.id, u.name, s.date, s.time, s.status
                FROM sessions s
                JOIN users u ON s.junior_id = u.id
                WHERE s.senior_id = %s 
                AND (s.status = 'Completed' 
                    OR (s.date < CURDATE() AND s.status = 'Active')
                    OR s.status = 'Reported')
                ORDER BY s.date DESC, s.time DESC
                LIMIT 50
            """, (self.controller.user_id,))
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No past sessions", "", "", ""))
                return
                
            for row in rows:
                # Unpack row data
                session_id, student_name, session_date, session_time, status = row
                
                # Store the session ID
                self.past_session_ids.append(session_id)
                
                # Format date and time
                formatted_date = session_date.strftime("%Y-%m-%d") if hasattr(session_date, 'strftime') else str(session_date)
                # Fix for timedelta object
                if isinstance(session_time, timedelta):
                    # Convert timedelta to string in HH:MM format
                    total_seconds = int(session_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_time = f"{hours:02d}:{minutes:02d}"
                else:
                    formatted_time = session_time.strftime("%H:%M") if hasattr(session_time, 'strftime') else str(session_time)
                
                # Update status for past sessions that weren't marked completed
                display_status = status
                if status == 'Active' and session_date < datetime.today().date():
                    display_status = "Incomplete"
                
                # Insert into tree
                item_id = tree.insert(
                    "",
                    "end",
                    values=(student_name, formatted_date, formatted_time, display_status)
                )
                
                # Apply color tags
                if display_status == "Completed":
                    tree.item(item_id, tags=("completed",))
                elif display_status == "Reported":
                    tree.item(item_id, tags=("reported",))
                elif display_status == "Incomplete":
                    tree.item(item_id, tags=("incomplete",))
            
            # Configure tag colors
            tree.tag_configure("completed", foreground=self.success_color)
            tree.tag_configure("reported", foreground=self.error_color)
            tree.tag_configure("incomplete", foreground="#FFA500")  # Orange for incomplete
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load past sessions: {e}")
        finally:
            conn.close()
        
    
    
    def accept_session_request(self, tree):
        """Accept a pending session request."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Request", "Please select a session request to accept.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.pending_session_ids):
            return
            
        session_id = self.pending_session_ids[item_index]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Update session status
            cursor.execute(
                "UPDATE sessions SET status = 'Active' WHERE id = %s",
                (session_id,)
            )
            
            # Get student ID to notify
            cursor.execute(
                "SELECT junior_id, date, time FROM sessions WHERE id = %s",
                (session_id,)
            )
            result = cursor.fetchone()
            
            if result:
                student_id, session_date, session_time = result
                
                # Format date and time for notification
                formatted_date = session_date.strftime("%Y-%m-%d") if hasattr(session_date, 'strftime') else str(session_date)
                # Fix for timedelta object
                if isinstance(session_time, timedelta):
                    total_seconds = int(session_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    formatted_time = f"{hours:02d}:{minutes:02d}"
                else:
                    formatted_time = session_time.strftime("%H:%M") if hasattr(session_time, 'strftime') else str(session_time)
                
                # Create a notification for the student
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (student_id, f"Your session request for {formatted_date} at {formatted_time} has been accepted by {self.controller.username}.")
                )
                    
            conn.commit()
            messagebox.showinfo("Success", "Session request accepted!")
            
            # Refresh the trees
            self.load_pending_sessions(tree)
            
            # Update stats
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not accept session request: {e}")
        finally:
            conn.close()
    
    def decline_session_request(self, tree):
        """Decline a pending session request."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Request", "Please select a session request to decline.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.pending_session_ids):
            return
            
        session_id = self.pending_session_ids[item_index]
        
        # Ask for reason
        reason_dialog = tk.Toplevel(self)
        reason_dialog.title("Decline Reason")
        reason_dialog.geometry("400x300")
        reason_dialog.configure(bg=self.bg_color)
        reason_dialog.transient(self)
        reason_dialog.grab_set()
        
        tk.Label(
            reason_dialog,
            text="Please provide a reason for declining:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 10), padx=20)
        
        reason_text = scrolledtext.ScrolledText(
            reason_dialog,
            height=6,
            font=self.label_font,
            wrap="word"
        )
        reason_text.pack(fill="x", padx=20, pady=(0, 20))
        
        button_frame = tk.Frame(reason_dialog, bg=self.bg_color)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=self.label_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=10,
            pady=5,
            command=reason_dialog.destroy
        )
        cancel_button.pack(side="left")
        
        submit_button = tk.Button(
            button_frame,
            text="Submit",
            font=self.label_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: self.process_decline(
                session_id, 
                reason_text.get("1.0", tk.END).strip(),
                reason_dialog, 
                tree
            )
        )
        submit_button.pack(side="right")
    
    def process_decline(self, session_id, reason, dialog, tree):
        """Process the session decline with the provided reason."""
        if not reason:
            messagebox.showerror("Error", "Please provide a reason for declining.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Delete the session
            cursor.execute(
                "DELETE FROM sessions WHERE id = %s",
                (session_id,)
            )
            
            # Get student ID to notify
            cursor.execute(
                "SELECT junior_id, date, time FROM sessions WHERE id = %s",
                (session_id,)
            )
            result = cursor.fetchone()
            
            if result:
                student_id, session_date, session_time = result
                
                # Create a notification for the student
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (student_id, f"Your session request for {session_date} at {session_time} has been declined by {self.controller.username}. Reason: {reason}")
                )
                
            conn.commit()
            messagebox.showinfo("Success", "Session request declined!")
            
            # Close dialog
            dialog.destroy()
            
            # Refresh the trees
            self.load_pending_sessions(tree)
            
            # Update stats
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not decline session request: {e}")
        finally:
            conn.close()
    
    def complete_session(self, tree):
        """Mark a session as completed."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Session", "Please select a session to mark as completed.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.upcoming_session_ids):
            return
            
        session_id = self.upcoming_session_ids[item_index]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Update session status
            cursor.execute(
                "UPDATE sessions SET status = 'Completed' WHERE id = %s",
                (session_id,)
            )
            
            # Get student ID to notify
            cursor.execute(
                "SELECT junior_id, date, time FROM sessions WHERE id = %s",
                (session_id,)
            )
            result = cursor.fetchone()
            
            if result:
                student_id, session_date, session_time = result
                
                # Create a notification for the student
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (student_id, f"Your session on {session_date} at {session_time} has been marked as completed by {self.controller.username}.")
                )
                
            conn.commit()
            messagebox.showinfo("Success", "Session marked as completed!")
            
            # Refresh the trees
            self.load_upcoming_sessions(tree)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not mark session as completed: {e}")
        finally:
            conn.close()
    
    def cancel_session(self, tree):
        """Cancel an upcoming session."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Session", "Please select a session to cancel.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.upcoming_session_ids):
            return
            
        session_id = self.upcoming_session_ids[item_index]
        
        if not messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this session? This action cannot be undone."):
            return
        
        # Ask for reason
        reason_dialog = tk.Toplevel(self)
        reason_dialog.title("Cancellation Reason")
        reason_dialog.geometry("400x300")
        reason_dialog.configure(bg=self.bg_color)
        reason_dialog.transient(self)
        reason_dialog.grab_set()
        
        tk.Label(
            reason_dialog,
            text="Please provide a reason for cancellation:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 10), padx=20)
        
        reason_text = scrolledtext.ScrolledText(
            reason_dialog,
            height=6,
            font=self.label_font,
            wrap="word"
        )
        reason_text.pack(fill="x", padx=20, pady=(0, 20))
        
        button_frame = tk.Frame(reason_dialog, bg=self.bg_color)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        cancel_button = tk.Button(
            button_frame,
            text="Go Back",
            font=self.label_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=10,
            pady=5,
            command=reason_dialog.destroy
        )
        cancel_button.pack(side="left")
        
        submit_button = tk.Button(
            button_frame,
            text="Submit",
            font=self.label_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: self.process_cancel(
                session_id, 
                reason_text.get("1.0", tk.END).strip(),
                reason_dialog, 
                tree
            )
        )
        submit_button.pack(side="right")
    
    def process_cancel(self, session_id, reason, dialog, tree):
        """Process the session cancellation with the provided reason."""
        if not reason:
            messagebox.showerror("Error", "Please provide a reason for cancellation.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Delete the session
            cursor.execute(
                "DELETE FROM sessions WHERE id = %s",
                (session_id,)
            )
            
            # Get student ID to notify
            cursor.execute(
                "SELECT junior_id, date, time FROM sessions WHERE id = %s",
                (session_id,)
            )
            result = cursor.fetchone()
            
            if result:
                student_id, session_date, session_time = result
                
                # Create a notification for the student
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (student_id, f"Your session scheduled for {session_date} at {session_time} has been cancelled by {self.controller.username}. Reason: {reason}")
                )
                
            conn.commit()
            messagebox.showinfo("Success", "Session has been cancelled!")
            
            # Close dialog
            dialog.destroy()
            
            # Refresh the trees
            self.load_upcoming_sessions(tree)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not cancel session: {e}")
        finally:
            conn.close()
    
    def refresh_session_tabs(self, dialog):
        """Refresh all session tabs in the dialog."""
        try:
            for tab_name, tree_attr in [
                ("pending_tree", "load_pending_sessions"), 
                ("upcoming_tree", "load_upcoming_sessions"), 
                ("past_tree", "load_past_sessions")
            ]:
                for child in dialog.winfo_children():
                    if hasattr(child, "winfo_children"):
                        for tab in child.winfo_children():
                            if hasattr(tab, tab_name):
                                tree = getattr(tab, tab_name)
                                refresh_method = getattr(self, tree_attr)
                                refresh_method(tree)
                                
            messagebox.showinfo("Refresh", "Session lists refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh sessions: {e}")
    
    def show_upload_resources(self):
        """Show interface for uploading resources."""
        dialog = tk.Toplevel(self)
        dialog.title("Upload Resources")
        dialog.geometry("700x950")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="Share Resources with Students",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="Upload study materials, guides, or any helpful resources",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        # Form section
        upload_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        upload_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(
            upload_frame,
            text="Upload New Resource",
            font=self.heading_font,
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        # Title field
        title_frame = tk.Frame(upload_frame, bg=self.card_bg)
        title_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            title_frame,
            text="Title:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side="left")
        
        title_var = tk.StringVar()
        title_entry = tk.Entry(
            title_frame,
            textvariable=title_var,
            font=self.label_font,
            width=40,
            relief="solid",
            borderwidth=1
        )
        title_entry.pack(side="left", padx=(10, 0))
        
        # Description field
        tk.Label(
            upload_frame,
            text="Description:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor="w", pady=(10, 5))
        
        description_entry = scrolledtext.ScrolledText(
            upload_frame,
            height=5,
            font=self.label_font,
            wrap="word",
            relief="solid",
            borderwidth=1
        )
        description_entry.pack(fill="x", pady=(0, 10))
        
        # File selection
        file_frame = tk.Frame(upload_frame, bg=self.card_bg)
        file_frame.pack(fill="x", pady=(10, 5))
        
        tk.Label(
            file_frame,
            text="Select File:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side="left")
        
        file_path_var = tk.StringVar()
        file_path_entry = tk.Entry(
            file_frame,
            textvariable=file_path_var,
            font=self.label_font,
            width=30,
            relief="solid",
            borderwidth=1,
            state="readonly"
        )
        file_path_entry.pack(side="left", padx=(10, 10))
        
        browse_button = tk.Button(
            file_frame,
            text="Browse",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=10,
            command=lambda: self.browse_file(file_path_var)
        )
        browse_button.pack(side="left")
        browse_button.bind("<Enter>", lambda e: e.widget.configure(bg=self.primary_color))
        browse_button.bind("<Leave>", lambda e: e.widget.configure(bg=self.accent_color))
        
        # Upload button
        upload_button = tk.Button(
            upload_frame,
            text="Upload Resource",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.upload_resource(
                title_var.get(),
                description_entry.get("1.0", tk.END).strip(),
                file_path_var.get()
            )
        )
        upload_button.pack(pady=(15, 0))
        upload_button.bind("<Enter>", self.on_enter)
        upload_button.bind("<Leave>", self.on_leave)
        
        # My uploads section
        uploads_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        uploads_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        tk.Label(
            uploads_frame,
            text="My Uploaded Resources",
            font=self.heading_font,
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        # Treeview for resources
        tree_frame = tk.Frame(uploads_frame, bg=self.card_bg)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("title", "date", "downloads", "status")
        resources_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=8
        )
        
        # Define headings
        resources_tree.heading("title", text="Title")
        resources_tree.heading("date", text="Upload Date")
        resources_tree.heading("downloads", text="Downloads")
        resources_tree.heading("status", text="Status")
        
        # Define columns width
        resources_tree.column("title", width=300, minwidth=200)
        resources_tree.column("date", width=120, minwidth=100)
        resources_tree.column("downloads", width=80, minwidth=80)
        resources_tree.column("status", width=100, minwidth=80)
        
        # Configure scrollbar
        scrollbar.config(command=resources_tree.yview)
        resources_tree.configure(yscrollcommand=scrollbar.set)
        
        resources_tree.pack(fill="both", expand=True)
        
        # Load resources
        self.resource_ids = []
        self.load_my_resources(resources_tree)
        
        # Close button
        close_button = tk.Button(
            dialog,
            text="Close",
            font=self.button_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        close_button.pack(side="right", padx=20, pady=(0, 20))
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Double-click to view resource details
        resources_tree.bind("<Double-1>", lambda e: self.view_resource_details(resources_tree))
    
    def browse_file(self, file_path_var):
        """Open file browser to select a resource."""
        file_types = [
            ("PDF Files", "*.pdf"),
            ("Document Files", "*.doc;*.docx"),
            ("Presentation Files", "*.ppt;*.pptx"),
            ("Spreadsheet Files", "*.xls;*.xlsx"),
            ("Image Files", "*.jpg;*.jpeg;*.png"),
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Resource File",
            filetypes=file_types
        )
        
        if file_path:
            file_path_var.set(file_path)
    
    def upload_resource(self, title, description, file_path):
        """Upload a resource to the system."""
        # Validate inputs
        if not title:
            messagebox.showerror("Error", "Please provide a title for the resource.")
            return
            
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload.")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "The selected file does not exist.")
            return
        
        # Handle file size (optional check)
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            messagebox.showerror("Error", "File size exceeds 50MB limit.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert resource into database
            cursor.execute(
                """INSERT INTO resources 
                   (user_id, title, file_path, description, downloads, approved) 
                   VALUES (%s, %s, %s, %s, 0, FALSE)""",
                (self.controller.user_id, title, file_path, description)
            )
            
            # Notify admin about new resource
            cursor.execute(
                """SELECT id FROM users WHERE role = 'Admin' LIMIT 1"""
            )
            admin_id = cursor.fetchone()
            
            if admin_id:
                cursor.execute(
                    """INSERT INTO notifications
                       (user_id, message, is_read)
                       VALUES (%s, %s, FALSE)""",
                    (admin_id[0], f"New resource '{title}' uploaded by {self.controller.username} pending approval.")
                )
            
            conn.commit()
            messagebox.showinfo(
                "Success", 
                "Resource uploaded successfully! It will be available to students once approved by an admin."
            )
            
            # Refresh resource list
            dialog = self.winfo_toplevel()
            for child in dialog.winfo_children():
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Treeview):
                            self.load_my_resources(grandchild)
                            break
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not upload resource: {e}")
        finally:
            conn.close()
    
    def load_my_resources(self, tree):
        """Load this mentor's uploaded resources into the tree."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.resource_ids = []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, title, timestamp, downloads, approved
                FROM resources
                WHERE user_id = %s
                ORDER BY timestamp DESC
            """, (self.controller.user_id,))
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No resources uploaded yet", "", "", ""))
                return
                
            for row in rows:
                # Unpack row data
                resource_id, title, timestamp, downloads, approved = row
                
                # Store the resource ID
                self.resource_ids.append(resource_id)
                
                # Format date
                formatted_date = timestamp.strftime("%Y-%m-%d")
                
                # Status text
                status = "Approved" if approved else "Pending"
                
                # Insert into tree
                item_id = tree.insert(
                    "",
                    "end",
                    values=(title, formatted_date, downloads, status)
                )
                # Apply tag for status color
                if approved:
                    tree.item(item_id, tags=("approved",))
                else:
                    tree.item(item_id, tags=("pending",))
            
            # Configure tag colors
            tree.tag_configure("approved", foreground=self.success_color)
            tree.tag_configure("pending", foreground=self.accent_color)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load resources: {e}")
        finally:
            conn.close()
    
    def view_resource_details(self, tree):
        """View details of a selected resource."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Resource", "Please select a resource to view details.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.resource_ids):
            return
            
        resource_id = self.resource_ids[item_index]
        
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Resource Details")
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Get resource data
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT title, description, file_path, timestamp, downloads, approved
                FROM resources
                WHERE id = %s
            """, (resource_id,))
            
            resource_data = cursor.fetchone()
            if not resource_data:
                messagebox.showerror("Error", "Resource not found!")
                dialog.destroy()
                return
                
            title, description, file_path, timestamp, downloads, approved = resource_data
            
            # Resource header
            header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text="Resource Details",
                font=self.subtitle_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            # Status banner
            status_text = "Approved" if approved else "Pending Approval"
            status_color = self.success_color if approved else self.accent_color
            
            status_frame = tk.Frame(dialog, bg=status_color, padx=20, pady=5)
            status_frame.pack(fill="x")
            
            tk.Label(
                status_frame,
                text=f"Status: {status_text}",
                font=self.label_font,
                bg=status_color,
                fg="white"
            ).pack(side="left")
            
            tk.Label(
                status_frame,
                text=f"Downloads: {downloads}",
                font=self.label_font,
                bg=status_color,
                fg="white"
            ).pack(side="right")
            
            # Main content
            content_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            tk.Label(
                content_frame,
                text="Title:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            tk.Label(
                content_frame,
                text=title,
                font=self.label_font,
                bg=self.card_bg,
                fg=self.text_color,
                wraplength=550,
                justify="left"
            ).pack(anchor="w", pady=(0, 15))
            
            # Upload date
            tk.Label(
                content_frame,
                text="Uploaded:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            tk.Label(
                content_frame,
                text=timestamp.strftime("%Y-%m-%d %H:%M"),
                font=self.label_font,
                bg=self.card_bg,
                fg=self.text_color
            ).pack(anchor="w", pady=(0, 15))
            
            # Description
            tk.Label(
                content_frame,
                text="Description:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            description_text = scrolledtext.ScrolledText(
                content_frame,
                height=8,
                font=self.label_font,
                wrap="word",
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1
            )
            description_text.pack(fill="both", expand=True, pady=(0, 15))
            description_text.insert("1.0", description or "No description provided.")
            description_text.config(state="disabled")
            
            # File path
            tk.Label(
                content_frame,
                text="File Path:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w")
            
            tk.Label(
                content_frame,
                text=file_path,
                font=self.label_font,
                bg=self.card_bg,
                fg=self.accent_color,
                wraplength=550,
                justify="left"
            ).pack(anchor="w", pady=(0, 15))
            
            # Close button
            button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
            button_frame.pack(fill="x")
            
            close_button = tk.Button(
                button_frame,
                text="Close",
                font=self.button_font,
                bg="#E0E0E0",
                fg=self.text_color,
                relief="flat",
                padx=15,
                pady=5,
                command=dialog.destroy
            )
            close_button.pack(side="right")
            close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
            close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load resource details: {e}")
        finally:
            conn.close()
    
    def on_enter(self, e):
        """Hover effect for primary buttons."""
        e.widget.configure(bg=self.accent_color)

    def on_leave(self, e):
        """Remove hover effect for primary buttons."""
        e.widget.configure(bg=self.primary_color)
    
    def on_enter_logout(self, e):
        """Hover effect for logout button."""
        e.widget.configure(bg="#b33333")

    def on_leave_logout(self, e):
        """Remove hover effect for logout button."""
        e.widget.configure(bg=self.error_color)
    
    def update_availability(self, *args):
        """Update the senior's availability in the database."""
        availability = self.availability_var.get()
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET availability = %s WHERE id = %s",
                (availability, self.controller.user_id)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Status updated to {availability}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()
    
    def logout(self):
        """Handle logout functionality."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.controller.username = None
            self.controller.user_id = None
            self.controller.show_frame("LoginPage")

    def refresh(self):
        """Refresh the questions list."""
        self.update_welcome_label()
        self.update_stats()
    
    def on_show_frame(self):
        """Called when this frame is shown."""
        self.update_welcome_label()
        self.update_stats()
                