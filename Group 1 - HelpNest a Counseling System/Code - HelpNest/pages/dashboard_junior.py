# pages/dashboard_junior.py
import tkinter as tk
from tkinter import font, messagebox, scrolledtext, ttk, filedialog
from PIL import Image, ImageTk
import textwrap
import os
from datetime import datetime, timedelta
from database import get_db_connection

class JuniorDashboardPage(tk.Frame):
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
        
        # Header with welcome message and settings button
        header_frame = tk.Frame(self, bg=self.primary_color, padx=20, pady=15)
        header_frame.pack(fill="x")
        
        # Left side: Welcome message
        welcome_frame = tk.Frame(header_frame, bg=self.primary_color)
        welcome_frame.pack(side="left", fill="y")
        
        self.welcome_label = tk.Label(
            welcome_frame, 
            text="Welcome to Help Nest!", 
            font=self.title_font, 
            bg=self.primary_color, 
            fg="white"
        )
        self.welcome_label.pack(anchor="w")
        
        self.user_info_label = tk.Label(
            welcome_frame,
            text="Junior Dashboard",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        )
        self.user_info_label.pack(anchor="w")
        
        # Right side: Settings button
        settings_button = tk.Button(
            header_frame,
            text="⚙️ Settings",
            font=self.label_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
            activebackground=self.accent_color,
            cursor="hand2",
            command=self.go_to_settings
        )
        settings_button.pack(side="right", padx=10)

        # Main content area - will contain either dashboard or ban message
        self.main_content = tk.Frame(self, bg=self.bg_color)
        self.main_content.pack(fill="both", expand=True)
        
        # Create the ban message UI (initially hidden)
        self.create_ban_message_ui()

        # Create the dashboard content
        self.create_dashboard_content()
        
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
        
        # Bind event to check ban status when frame is shown
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def create_ban_message_ui(self):
        """Create the UI for displaying a ban message"""
        self.ban_frame = tk.Frame(self.main_content, bg=self.bg_color)
        
        # Warning card with ban information
        ban_card = tk.Frame(
            self.ban_frame, 
            bg=self.card_bg,
            relief="solid",
            borderwidth=2,
            highlightbackground=self.error_color,
            highlightthickness=2,
            padx=40,
            pady=40
        )
        ban_card.pack(expand=True, fill="both", padx=100, pady=100)
        
        # Warning icon (text emoji)
        tk.Label(
            ban_card,
            text="⚠️",
            font=("Helvetica", 72),
            bg=self.card_bg,
            fg=self.error_color
        ).pack(pady=(20, 30))
        
        # Ban title
        tk.Label(
            ban_card,
            text="Your Account Has Been Suspended",
            font=self.title_font,
            bg=self.card_bg,
            fg=self.error_color
        ).pack(pady=(0, 30))
        
        # Ban reason label
        tk.Label(
            ban_card,
            text="Reason for suspension:",
            font=self.heading_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor="w", padx=50)
        
        # Ban reason text (will be populated when needed)
        self.ban_reason_text = tk.Label(
            ban_card,
            text="",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color,
            justify="left",
            wraplength=500
        )
        self.ban_reason_text.pack(anchor="w", padx=50, pady=(5, 30))
        
        # Info text
        tk.Label(
            ban_card,
            text="If you believe this is in error, please contact the administrators.",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=500,
            justify="center"
        ).pack(pady=(0, 30))

    def create_dashboard_content(self):
        """Create the main dashboard UI elements"""
        self.dashboard_frame = tk.Frame(self.main_content, bg=self.bg_color, padx=40, pady=40)
        
        # Create dashboard grid (2x2 grid of cards)
        # Row 1, Column 1: Ask Questions
        ask_card = self.create_dashboard_card(
            self.dashboard_frame,
            "Ask a Question",
            "Get help from experienced mentors",
            "✏️",
            self.show_ask_question_dialog
        )
        ask_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Row 1, Column 2: View My Questions
        view_card = self.create_dashboard_card(
            self.dashboard_frame,
            "My Questions",
            "View and manage your questions",
            "📋",
            self.show_my_questions
        )
        view_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Row 2, Column 1: Browse Resources
        resource_card = self.create_dashboard_card(
            self.dashboard_frame,
            "View Resources",
            "Access study materials shared by mentors",
            "📚",
            self.show_resources
        )
        resource_card.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        # Row 2, Column 2: Book a Session
        session_card = self.create_dashboard_card(
            self.dashboard_frame,
            "Book a Session",
            "Schedule one-on-one mentoring",
            "📅",
            self.show_book_session
        )
        session_card.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        
        # Configure grid to expand properly
        self.dashboard_frame.columnconfigure(0, weight=1)
        self.dashboard_frame.columnconfigure(1, weight=1)
        self.dashboard_frame.rowconfigure(0, weight=1)
        self.dashboard_frame.rowconfigure(1, weight=1)
        
        # By default, show the dashboard frame
        self.dashboard_frame.pack(fill="both", expand=True)

    def check_ban_status(self):
        """Check if user is banned and show appropriate content"""
        if not hasattr(self.controller, 'user_id') or not self.controller.user_id:
            return False
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT banned, ban_reason FROM users WHERE id = %s",
                (self.controller.user_id,)
            )
            result = cursor.fetchone()
            
            if result and result[0]:  # If banned is True
                # Update ban reason text
                ban_reason = result[1] if result[1] else "Violation of community guidelines"
                self.ban_reason_text.config(text=ban_reason)
                
                # Show ban content, hide dashboard content
                self.dashboard_frame.pack_forget()
                self.ban_frame.pack(fill="both", expand=True)
                return True
            else:
                # Show dashboard content, hide ban content
                self.ban_frame.pack_forget()
                self.dashboard_frame.pack(fill="both", expand=True)
                return False
        except Exception as e:
            print(f"Error checking ban status: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def go_to_settings(self):
        """Navigate to the settings page."""
        # Check ban status first
        if self.check_ban_status():
            messagebox.showerror("Access Denied", "Your account is suspended. You cannot access settings.")
            return
            
        # If not banned, go to settings page
        self.controller.show_frame("SettingsPage")

    def on_show_frame(self, event=None):
        """Called when frame is shown. Checks ban status and updates UI."""
        # Check if user is banned
        is_banned = self.check_ban_status()
        
        if not is_banned:
            # Only update dashboard if user is not banned
            self.update_welcome_label()
    
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
                    SELECT name, department, year 
                    FROM users 
                    WHERE id = %s
                """, (self.controller.user_id,))
                user_data = cursor.fetchone()

                if user_data and user_data[0]:
                    self.welcome_label.config(text=f"Welcome, {user_data[0]}!")

                    # Also update user info if available
                    dept_info = f"Department: {user_data[1]}" if user_data[1] else ""
                    year_info = f"Year: {user_data[2]}" if user_data[2] else ""
                    
                    if dept_info and year_info:
                        self.user_info_label.config(text=f"{dept_info} | {year_info}")
                    elif dept_info:
                        self.user_info_label.config(text=dept_info)
                    elif year_info:
                        self.user_info_label.config(text=year_info)
                else:
                    self.welcome_label.config(text="Welcome, Student!")
                    self.user_info_label.config(text="Junior Dashboard")
            except Exception as e:
                print(f"Error retrieving user data: {e}")
                self.welcome_label.config(text="Welcome to Help Nest!")
                self.user_info_label.config(text="Junior Dashboard")
            finally:
                conn.close()
        else:
            self.welcome_label.config(text="Welcome to Help Nest!")
            self.user_info_label.config(text="Junior Dashboard")


    def show_ask_question_dialog(self):
        """Show dialog to ask a new question."""
        # Check ban status first
        if self.check_ban_status():
            messagebox.showerror("Access Denied", "Your account is suspended. You cannot post questions.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Ask a Question")
        dialog.geometry("800x600")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)  # Set to be on top of the main window
        dialog.grab_set()  # Make it modal
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="Ask a Question",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="Get guidance from experienced mentors",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        # Form
        form_frame = tk.Frame(dialog, bg=self.card_bg, padx=30, pady=30)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Question field
        tk.Label(
            form_frame,
            text="Your Question:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor="w", pady=(0, 5))
        
        question_entry = scrolledtext.ScrolledText(
            form_frame,
            height=8,
            font=self.label_font,
            wrap="word"
        )
        question_entry.pack(fill="x", pady=(0, 20))
        
        # Category selection
        option_frame = tk.Frame(form_frame, bg=self.card_bg)
        option_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            option_frame,
            text="Category:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        category_var = tk.StringVar(value="Select a category")
        categories = ["Career", "Internships", "Higher Studies"]
        
        category_menu = ttk.Combobox(
            option_frame,
            textvariable=category_var,
            values=categories,
            state="readonly",
            font=self.label_font,
            width=20
        )
        category_menu.pack(side="left")
        
        # Anonymous option
        anonymous_var = tk.BooleanVar(value=False)
        anonymous_frame = tk.Frame(form_frame, bg=self.card_bg)
        anonymous_frame.pack(fill="x", pady=(0, 20))
        
        anonymous_check = tk.Checkbutton(
            anonymous_frame,
            text="Post Anonymously",
            variable=anonymous_var,
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color,
            selectcolor=self.card_bg
        )
        anonymous_check.pack(side="left")
        
        # Info icon and help text
        tk.Label(
            anonymous_frame,
            text="ℹ️",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.accent_color
        ).pack(side="left", padx=(5, 5))
        
        tk.Label(
            anonymous_frame,
            text="Your name will be hidden from other students",
            font=("Helvetica", 10, "italic"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side="left")
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=self.button_font,
            bg="#E0E0E0",
            fg=self.text_color,
            relief="flat",
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        submit_button = tk.Button(
            button_frame,
            text="Submit Question",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.submit_question(
                question_entry.get("1.0", tk.END).strip(),
                category_var.get(),
                anonymous_var.get(),
                dialog
            )
        )
        submit_button.pack(side="right")
        
        # Button hover effects
        submit_button.bind("<Enter>", self.on_enter)
        submit_button.bind("<Leave>", self.on_leave)
        cancel_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        cancel_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Set focus to the question entry
        question_entry.focus_set()
        
    def submit_question(self, question, category, anonymous, dialog):
        """Submit a new question from the dialog."""
        # Validate inputs
        if not question:
            messagebox.showerror("Error", "Please enter your question.")
            return
            
        if category == "Select a category":
            messagebox.showerror("Error", "Please select a category.")
            return

        # Add question to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO questions 
                (user_id, question, category, anonymous, resolved, reported, approved) 
                VALUES (%s, %s, %s, %s, FALSE, FALSE, FALSE)""",
                (self.controller.user_id, question, category, anonymous)
            )
            conn.commit()
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                "Your question has been submitted and is pending approval."
            )
            
            # Close the dialog
            dialog.destroy()
            
            # Refresh the questions list
            self.refresh()
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"An error occurred: {e}"
            )
        finally:
            conn.close()

    def show_my_questions(self):
        """Show a dialog with all questions asked by the user."""
        # Check ban status first
        if self.check_ban_status():
            messagebox.showerror("Access Denied", "Your account is suspended. You cannot view your questions.")
            return
            
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("My Questions")
        dialog.geometry("900x900")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="My Questions",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(side="left")
        
        refresh_btn = tk.Button(
            header,
            text="Refresh",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            command=lambda: self.load_questions_to_tree(questions_tree)
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Main content
        content = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create Treeview
        tree_frame = tk.Frame(content, bg=self.card_bg)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview columns
        columns = ("date", "category", "question", "status")
        questions_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )
        
        # Define column headings
        questions_tree.heading("date", text="Date Posted")
        questions_tree.heading("category", text="Category")
        questions_tree.heading("question", text="Question")
        questions_tree.heading("status", text="Status")
        
        # Column widths
        questions_tree.column("date", width=120, anchor="w")
        questions_tree.column("category", width=100, anchor="w")
        questions_tree.column("question", width=350, anchor="w")
        questions_tree.column("status", width=180, anchor="w")
        
        # Attach scrollbar
        scrollbar.config(command=questions_tree.yview)
        questions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree
        questions_tree.pack(fill="both", expand=True)
        
        # Load questions
        self.load_questions_to_tree(questions_tree)
        
        # Action buttons at bottom
        button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        button_frame.pack(fill="x")
        
        view_button = tk.Button(
            button_frame,
            text="View Selected Question",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.view_selected_question(questions_tree)
        )
        view_button.pack(side="left", pady=10)
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
        close_button.pack(side="right", pady=10)
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Double click to view details
        questions_tree.bind("<Double-1>", lambda e: self.view_selected_question(questions_tree))

    def show_resources(self):
        """Show resources shared by mentors."""
        # Check ban status first
        if self.check_ban_status():
            messagebox.showerror("Access Denied", "Your account is suspended. You cannot access resources.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Learning Resources")
        dialog.geometry("800x1000")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="Learning Resources",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(side="left")
        
        refresh_btn = tk.Button(
            header,
            text="Refresh",
            font=self.label_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            command=lambda: self.load_resources(resources_tree)
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Search frame
        search_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        search_frame.pack(fill="x")
        
        tk.Label(
            search_frame,
            text="Search:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, 
            textvariable=search_var,
            font=self.label_font,
            width=30
        )
        search_entry.pack(side="left")
        
        search_button = tk.Button(
            search_frame,
            text="Search",
            font=self.label_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=10,
            command=lambda: self.search_resources(resources_tree, search_var.get())
        )
        search_button.pack(side="left", padx=10)
        
        # Content frame
        content = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create Treeview for resources
        tree_frame = tk.Frame(content, bg=self.card_bg)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview columns
        columns = ("title", "uploaded_by", "date", "downloads")
        resources_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )
        
        # Define column headings
        resources_tree.heading("title", text="Resource Title")
        resources_tree.heading("uploaded_by", text="Uploaded By")
        resources_tree.heading("date", text="Date Added")
        resources_tree.heading("downloads", text="Downloads")
        
        # Column widths
        resources_tree.column("title", width=300, anchor="w")
        resources_tree.column("uploaded_by", width=150, anchor="w")
        resources_tree.column("date", width=120, anchor="w")
        resources_tree.column("downloads", width=80, anchor="center")
        
        # Attach scrollbar
        scrollbar.config(command=resources_tree.yview)
        resources_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree
        resources_tree.pack(fill="both", expand=True)
        
        # Load resources
        self.resource_ids = []  # Store resource IDs
        self.load_resources(resources_tree)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
        button_frame.pack(fill="x")
        
        download_button = tk.Button(
            button_frame,
            text="Download Selected Resource",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.download_resource(resources_tree)
        )
        download_button.pack(side="left", pady=10)
        download_button.bind("<Enter>", self.on_enter)
        download_button.bind("<Leave>", self.on_leave)
        
        view_button = tk.Button(
            button_frame,
            text="View Details",
            font=self.button_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=lambda: self.view_resource_details(resources_tree)
        )
        view_button.pack(side="left", padx=10, pady=10)
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
        close_button.pack(side="right", pady=10)
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Double click to view details
        resources_tree.bind("<Double-1>", lambda e: self.view_resource_details(resources_tree))

    def show_book_session(self):
        """Show interface for booking a session with a mentor."""
        # Check ban status first
        if self.check_ban_status():
            messagebox.showerror("Access Denied", "Your account is suspended. You cannot book sessions.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Book a Mentoring Session")
        dialog.geometry("800x900")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="Book a Mentoring Session",
            font=self.subtitle_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="Schedule one-on-one time with a mentor for personalized guidance",
            font=self.label_font,
            bg=self.primary_color,
            fg="white"
        ).pack(anchor="w")
        
        # Split into two panels
        panel_frame = tk.Frame(dialog, bg=self.bg_color)
        panel_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel: Mentor Selection
        left_panel = tk.Frame(panel_frame, bg=self.card_bg, padx=20, pady=20, relief="solid", borderwidth=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(
            left_panel,
            text="Select a Mentor",
            font=self.heading_font,
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        # Mentor list frame
        mentor_frame = tk.Frame(left_panel, bg=self.card_bg)
        mentor_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(mentor_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview columns
        columns = ("name", "expertise", "availability")
        mentors_tree = ttk.Treeview(
            mentor_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )
        
        # Define column headings
        mentors_tree.heading("name", text="Mentor Name")
        mentors_tree.heading("expertise", text="Expertise")
        mentors_tree.heading("availability", text="Status")
        
        # Column widths
        mentors_tree.column("name", width=150, anchor="w")
        mentors_tree.column("expertise", width=150, anchor="w")
        mentors_tree.column("availability", width=100, anchor="center")
        
        # Attach scrollbar
        scrollbar.config(command=mentors_tree.yview)
        mentors_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree
        mentors_tree.pack(fill="both", expand=True)
        
        # Load mentors
        self.mentor_ids = []  # Store mentor IDs
        self.load_mentors(mentors_tree)
        
        # Right panel: Session Booking Form
        right_panel = tk.Frame(panel_frame, bg=self.card_bg, padx=20, pady=20, relief="solid", borderwidth=1)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(
            right_panel,
            text="Session Details",
            font=self.heading_font,
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        # Selected mentor info
        selected_mentor_frame = tk.Frame(right_panel, bg=self.card_bg, padx=10, pady=10)
        selected_mentor_frame.pack(fill="x")
        
        selected_mentor_label = tk.Label(
            selected_mentor_frame,
            text="Select a mentor from the list",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        )
        selected_mentor_label.pack(anchor="w")
        
        # Date selection
        date_frame = tk.Frame(right_panel, bg=self.card_bg, padx=10, pady=10)
        date_frame.pack(fill="x")
        
        tk.Label(
            date_frame,
            text="Select Date:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor="w", pady=(0, 5))
        
        # Create a list of next 7 days
        date_options = []
        for i in range(7):
            future_date = datetime.now() + timedelta(days=i+1)
            date_options.append(future_date.strftime("%Y-%m-%d"))
        
        date_var = tk.StringVar()
        date_dropdown = ttk.Combobox(
            date_frame,
            textvariable=date_var,
            values=date_options,
            state="readonly",
            font=self.label_font,
            width=15
        )
        date_dropdown.pack(anchor="w")
        if date_options:
            date_var.set(date_options[0])
        
        # Time selection
        time_frame = tk.Frame(right_panel, bg=self.card_bg, padx=10, pady=10)
        time_frame.pack(fill="x")
        
        tk.Label(
            time_frame,
            text="Select Time:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor="w", pady=(0, 5))
        
        times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        time_var = tk.StringVar()
        time_dropdown = ttk.Combobox(
            time_frame,
            textvariable=time_var,
            values=times,
            state="readonly",
            font=self.label_font,
            width=15
        )
        time_dropdown.pack(anchor="w")
        time_var.set(times[0])
        
        # Purpose of session
        purpose_frame = tk.Frame(right_panel, bg=self.card_bg, padx=10, pady=10)
        purpose_frame.pack(fill="x")
        
        tk.Label(
            purpose_frame,
            text="Purpose of Session:",
            font=self.label_font,
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor="w", pady=(0, 5))
        
        purpose_entry = scrolledtext.ScrolledText(
            purpose_frame,
            height=4,
            font=self.label_font,
            wrap="word"
        )
        purpose_entry.pack(fill="x")
        
        # Book session button
        button_frame = tk.Frame(right_panel, bg=self.card_bg, padx=10, pady=20)
        button_frame.pack(fill="x")
        
        book_button = tk.Button(
            button_frame,
            text="Request Session",
            font=self.button_font,
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            state="disabled",  # Disabled until mentor is selected
            command=lambda: self.book_session(
                selected_mentor_id,
                date_var.get(),
                time_var.get(),
                purpose_entry.get("1.0", tk.END).strip(),
                dialog
            )
        )
        book_button.pack(side="right")
        book_button.bind("<Enter>", self.on_enter)
        book_button.bind("<Leave>", self.on_leave)
        
        # My sessions section
        sessions_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
        sessions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(
            sessions_frame,
            text="My Upcoming Sessions",
            font=self.heading_font,
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", pady=(0, 10))
        
        # Create listbox for sessions
        sessions_list = tk.Listbox(
            sessions_frame,
            font=self.label_font,
            height=3,
            relief="solid",
            borderwidth=1
        )
        sessions_list.pack(fill="x")
        
        # Load existing sessions
        self.load_sessions(sessions_list)
        
        # Bottom close button
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
        close_button.pack(pady=10)
        close_button.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
        close_button.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
        
        # Variable to store selected mentor ID
        selected_mentor_id = None
        
        # Function to update selected mentor
        def on_mentor_select(event):
            nonlocal selected_mentor_id
            selection = mentors_tree.selection()
            if not selection:
                return
                
            item_id = selection[0]
            item_index = mentors_tree.index(item_id)
            
            if item_index >= len(self.mentor_ids):
                return
                
            mentor_id = self.mentor_ids[item_index]
            selected_mentor_id = mentor_id
            
            # Get mentor details
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT name, expertise, department 
                    FROM users 
                    WHERE id = %s
                """, (mentor_id,))
                
                mentor_data = cursor.fetchone()
                if mentor_data:
                    name, expertise, department = mentor_data
                    info_text = f"Selected: {name}"
                    if expertise:
                        info_text += f"\nExpertise: {expertise}"
                    if department:
                        info_text += f"\nDepartment: {department}"
                    
                    selected_mentor_label.config(text=info_text)
                    book_button.config(state="normal")  # Enable booking button
            except Exception as e:
                print(f"Error getting mentor details: {e}")
            finally:
                conn.close()
        
        # Bind selection event
        mentors_tree.bind("<<TreeviewSelect>>", on_mentor_select)

    def load_questions_to_tree(self, tree):
        """Load questions from database into the provided treeview."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.question_ids = []  # Reset question IDs
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, question, category, anonymous, timestamp, resolved, approved,
                    (SELECT COUNT(*) FROM answers WHERE answers.question_id = questions.id) as answer_count
                FROM questions 
                WHERE user_id = %s 
                ORDER BY timestamp DESC
            """, (self.controller.user_id,))
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("N/A", "N/A", "No questions found", "N/A"))
                return
                
            for row in rows:
                # Unpack data
                question_id = row[0]
                question_text = row[1]
                category = row[2]
                is_anonymous = row[3]
                timestamp = row[4]
                is_resolved = row[5]
                is_approved = row[6]
                answer_count = row[7]
                
                # Store question ID
                self.question_ids.append(question_id)
                
                # Format timestamp
                formatted_date = timestamp.strftime("%b %d, %Y")
                
                # Truncate question if too long
                display_question = question_text if len(question_text) < 40 else f"{question_text[:40]}..."
                
                # Create status text
                status_parts = []
                if is_approved:
                    status_parts.append("Approved")
                else:
                    status_parts.append("Pending")
                
                if is_resolved:
                    status_parts.append("Resolved")
                
                status_parts.append(f"{answer_count} Answers")
                status_text = " | ".join(status_parts)
                
                # Insert into tree
                item_id = tree.insert(
                    "",
                    "end",
                    values=(formatted_date, category, display_question, status_text)
                )
                
                # Color coding based on status
                if is_resolved:
                    tree.item(item_id, tags=("resolved",))
                elif is_approved and answer_count > 0:
                    tree.item(item_id, tags=("answered",))
                elif not is_approved:
                    tree.item(item_id, tags=("pending",))
            
            # Configure tag colors
            tree.tag_configure("resolved", foreground=self.success_color)
            tree.tag_configure("answered", foreground=self.accent_color)
            tree.tag_configure("pending", foreground="#888888")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load questions: {e}")
        finally:
            conn.close()

    def view_selected_question(self, tree):
        """View details of the selected question."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Question", "Please select a question to view.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.question_ids):
            return
            
        question_id = self.question_ids[item_index]
        self.show_question_details(question_id)
        
    def show_question_details(self, question_id):
        """Show a dialog with question details and answers."""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Question Details")
        dialog.geometry("700x900")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self)
        dialog.grab_set()
        
        # Get question data
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Get question details
            cursor.execute("""
                SELECT question, category, timestamp, resolved, approved
                FROM questions
                WHERE id = %s
            """, (question_id,))
            
            question_data = cursor.fetchone()
            if not question_data:
                messagebox.showerror("Error", "Question not found!")
                dialog.destroy()
                return
                
            question_text, category, timestamp, resolved, approved = question_data
            
            # Question header
            header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text=f"Question: {category}",
                font=self.subtitle_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            status_text = f"Status: {'Approved' if approved else 'Pending Approval'} | {'Resolved' if resolved else 'Open'}"
            tk.Label(
                header,
                text=f"{status_text} | Posted: {timestamp.strftime('%b %d, %Y %H:%M')}",
                font=self.label_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            # Question content
            question_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            question_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(
                question_frame,
                text="Your Question:",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w", pady=(0, 10))
            
            question_display = tk.Text(
                question_frame,
                height=5,
                wrap="word",
                font=self.label_font,
                bg=self.card_bg,
                fg=self.text_color,
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=10
            )
            question_display.pack(fill="x")
            question_display.insert("1.0", question_text)
            question_display.config(state="disabled")
            
            # Answers section
            answers_label_frame = tk.Frame(dialog, bg=self.bg_color, padx=20)
            answers_label_frame.pack(fill="x")
            
            tk.Label(
                answers_label_frame,
                text="Mentor Responses",
                font=self.heading_font,
                bg=self.bg_color,
                fg=self.primary_color
            ).pack(anchor="w", pady=(10, 5))
            
            answers_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=15)
            answers_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Get answers
            cursor.execute("""
                SELECT answers.id, answers.answer, users.name, answers.rating, answers.timestamp,
                    users.expertise, users.department
                FROM answers
                JOIN users ON answers.user_id = users.id
                WHERE answers.question_id = %s
                ORDER BY answers.timestamp DESC
            """, (question_id,))
            
            answers = cursor.fetchall()
            
            if not answers:
                no_answers = tk.Label(
                    answers_frame,
                    text="No responses yet. Mentors will answer your question soon.",
                    font=("Helvetica", 12, "italic"),
                    bg=self.card_bg,
                    fg=self.text_color,
                    pady=30
                )
                no_answers.pack()
            else:
                # Create scrollable canvas for answers
                canvas = tk.Canvas(answers_frame, bg=self.card_bg, highlightthickness=0)
                scrollbar = ttk.Scrollbar(answers_frame, orient="vertical", command=canvas.yview)
                scrollable_inner = tk.Frame(canvas, bg=self.card_bg)
                
                scrollable_inner.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_inner, anchor="nw", width=canvas.winfo_width())
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Bind canvas resize event to update inner frame width
                def on_canvas_configure(e):
                    canvas.itemconfig(
                        canvas.find_withtag("all")[0], 
                        width=e.width - 5
                    )
                
                canvas.bind("<Configure>", on_canvas_configure)
                
                # Add answers
                for i, (answer_id, answer, mentor_name, rating, answer_time, expertise, department) in enumerate(answers):
                    answer_container = tk.Frame(
                        scrollable_inner,
                        bg="#F5F5F5" if i % 2 == 0 else self.card_bg,
                        relief="solid",
                        borderwidth=1,
                        padx=15,
                        pady=15
                    )
                    answer_container.pack(fill="x", pady=5)
                    
                    # Mentor info and timestamp
                    info_frame = tk.Frame(answer_container, bg=answer_container["bg"])
                    info_frame.pack(fill="x", pady=(0, 10))
                    
                    mentor_info = tk.Label(
                        info_frame,
                        text=f"From: {mentor_name}",
                        font=("Helvetica", 12, "bold"),
                        bg=answer_container["bg"],
                        fg=self.primary_color
                    )
                    mentor_info.pack(side="left")
                    
                    timestamp_info = tk.Label(
                        info_frame,
                        text=answer_time.strftime("%b %d, %Y %H:%M"),
                        font=self.label_font,
                        bg=answer_container["bg"],
                        fg=self.text_color
                    )
                    timestamp_info.pack(side="right")
                    
                    # Mentor expertise if available
                    if expertise or department:
                        expertise_frame = tk.Frame(answer_container, bg=answer_container["bg"])
                        expertise_frame.pack(fill="x", pady=(0, 10))
                        
                        expertise_text = []
                        if expertise:
                            expertise_text.append(f"Expertise: {expertise}")
                        if department:
                            expertise_text.append(f"Department: {department}")
                            
                        tk.Label(
                            expertise_frame,
                            text=" | ".join(expertise_text),
                            font=("Helvetica", 10, "italic"),
                            bg=answer_container["bg"],
                            fg=self.accent_color
                        ).pack(side="left")
                    
                    # Answer content
                    answer_text = tk.Text(
                        answer_container,
                        wrap="word",
                        height=4,
                        font=self.label_font,
                        bg=answer_container["bg"],
                        fg=self.text_color,
                        relief="flat",
                        padx=5,
                        pady=5
                    )
                    answer_text.pack(fill="x", pady=(0, 10))
                    answer_text.insert("1.0", answer)
                    answer_text.config(state="disabled")
                    
                    # Display rating or rating buttons
                    rating_frame = tk.Frame(answer_container, bg=answer_container["bg"])
                    rating_frame.pack(fill="x")
                    
                    if rating:
                        # Show the existing rating
                        rating_stars = "★" * rating + "☆" * (5 - rating)
                        tk.Label(
                            rating_frame,
                            text=f"Your Rating: {rating_stars}",
                            font=self.label_font,
                            bg=answer_container["bg"],
                            fg=self.accent_color
                        ).pack(side="left")
                    else:
                        # Show rating buttons
                        tk.Label(
                            rating_frame,
                            text="Rate this answer: ",
                            font=self.label_font,
                            bg=answer_container["bg"],
                            fg=self.text_color
                        ).pack(side="left")
                        
                        for star in range(1, 6):
                            star_btn = tk.Button(
                                rating_frame,
                                text="★",
                                font=("Helvetica", 14),
                                bg=answer_container["bg"],
                                fg="#FFD700",  # Gold color for stars
                                relief="flat",
                                command=lambda a=answer_id, s=star: self.rate_answer(a, s, dialog, question_id)
                            )
                            star_btn.pack(side="left", padx=2)
            
            # Bottom action buttons
            button_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=15)
            button_frame.pack(fill="x")
            
            # Add option to mark as resolved only if approved and not already resolved
            if approved and not resolved:
                resolve_btn = tk.Button(
                    button_frame,
                    text="Mark as Resolved",
                    font=self.button_font,
                    bg=self.success_color,
                    fg="white",
                    relief="flat",
                    padx=15,
                    pady=5,
                    command=lambda: self.mark_resolved(question_id, dialog)
                )
                resolve_btn.pack(side="left", padx=(0, 10))
                resolve_btn.bind("<Enter>", lambda e: e.widget.configure(bg="#3d8b40"))
                resolve_btn.bind("<Leave>", lambda e: e.widget.configure(bg=self.success_color))
                
            close_btn = tk.Button(
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
            close_btn.pack(side="right")
            close_btn.bind("<Enter>", lambda e: e.widget.configure(bg="#CCCCCC"))
            close_btn.bind("<Leave>", lambda e: e.widget.configure(bg="#E0E0E0"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load question details: {e}")
        finally:
            conn.close()
            
    def load_resources(self, tree):
        """Load resources from database into the provided treeview."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.resource_ids = []  # Reset resource IDs
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Query only approved resources
            cursor.execute("""
                SELECT resources.id, resources.title, users.name, resources.timestamp, 
                    resources.downloads, resources.description
                FROM resources
                JOIN users ON resources.user_id = users.id
                WHERE resources.approved = TRUE
                ORDER BY resources.timestamp DESC
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No resources available", "", "", ""))
                return
                
            for row in rows:
                # Unpack data
                resource_id, title, uploaded_by, timestamp, downloads, description = row
                
                # Store resource ID
                self.resource_ids.append(resource_id)
                
                # Format timestamp
                formatted_date = timestamp.strftime("%b %d, %Y")
                
                # Insert into tree
                tree.insert(
                    "",
                    "end",
                    values=(title, uploaded_by, formatted_date, downloads)
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load resources: {e}")
        finally:
            conn.close()
            
    def load_mentors(self, tree):
        """Load available mentors into the treeview."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.mentor_ids = []  # Reset mentor IDs
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, name, expertise, availability 
                FROM users 
                WHERE role = 'Senior' AND banned = FALSE
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=("No mentors available", "", ""))
                return
                
            for row in rows:
                # Unpack data
                mentor_id, name, expertise, availability = row
                
                # Store mentor ID
                self.mentor_ids.append(mentor_id)
                
                # Format expertise
                expertise_display = expertise if expertise else "General"
                
                # Format availability status
                availability_display = availability if availability else "Available"
                
                # Insert into tree
                item_id = tree.insert(
                    "",
                    "end",
                    values=(name, expertise_display, availability_display)
                )
                
                # Color code availability status
                if availability == "Busy":
                    tree.item(item_id, tags=("busy",))
                else:
                    tree.item(item_id, tags=("available",))
            
            # Configure tag colors
            tree.tag_configure("busy", foreground="#888888")
            tree.tag_configure("available", foreground=self.success_color)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load mentors: {e}")
        finally:
            conn.close()

    def load_sessions(self, listbox):
        """Load user's upcoming sessions into the listbox."""
        # Clear existing items
        listbox.delete(0, tk.END)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT sessions.date, sessions.time, sessions.status, users.name
                FROM sessions
                JOIN users ON sessions.senior_id = users.id
                WHERE sessions.junior_id = %s
                AND sessions.date >= CURDATE()
                ORDER BY sessions.date, sessions.time
            """, (self.controller.user_id,))
            
            rows = cursor.fetchall()
            
            if not rows:
                listbox.insert(tk.END, "You have no upcoming sessions.")
                return
                
            for row in rows:
                # Unpack data
                session_date, session_time, status, mentor_name = row
                
                # Format display string
                display_text = f"{session_date.strftime('%b %d, %Y')} at {session_time} - with {mentor_name} - Status: {status}"
                listbox.insert(tk.END, display_text)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load sessions: {e}")
        finally:
            conn.close()

    def search_resources(self, tree, search_term):
        """Search resources by title or description."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        self.resource_ids = []  # Reset resource IDs
        
        if not search_term:
            self.load_resources(tree)
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Query resources matching search term
            cursor.execute("""
                SELECT resources.id, resources.title, users.name, resources.timestamp, 
                    resources.downloads, resources.description
                FROM resources
                JOIN users ON resources.user_id = users.id
                WHERE resources.approved = TRUE
                AND (resources.title LIKE %s OR resources.description LIKE %s)
                ORDER BY resources.timestamp DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            rows = cursor.fetchall()
            
            if not rows:
                tree.insert("", "end", values=(f"No resources matching '{search_term}'", "", "", ""))
                return
                
            for row in rows:
                # Unpack data
                resource_id, title, uploaded_by, timestamp, downloads, description = row
                
                # Store resource ID
                self.resource_ids.append(resource_id)
                
                # Format timestamp
                formatted_date = timestamp.strftime("%b %d, %Y")
                
                # Insert into tree
                tree.insert(
                    "",
                    "end",
                    values=(title, uploaded_by, formatted_date, downloads)
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not search resources: {e}")
        finally:
            conn.close()

    def view_resource_details(self, tree):
        """View details of the selected resource."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Resource", "Please select a resource to view.")
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
                SELECT resources.title, resources.description, users.name, 
                    resources.file_path, resources.timestamp, resources.downloads,
                    users.expertise, users.department
                FROM resources
                JOIN users ON resources.user_id = users.id
                WHERE resources.id = %s
            """, (resource_id,))
            
            resource_data = cursor.fetchone()
            if not resource_data:
                messagebox.showerror("Error", "Resource not found!")
                dialog.destroy()
                return
                
            title, description, uploaded_by, file_path, timestamp, downloads, expertise, department = resource_data
            
            # Resource header
            header = tk.Frame(dialog, bg=self.primary_color, padx=20, pady=15)
            header.pack(fill="x")
            
            tk.Label(
                header,
                text=title,
                font=self.subtitle_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            tk.Label(
                header,
                text=f"Uploaded by: {uploaded_by} | Downloads: {downloads}",
                font=self.label_font,
                bg=self.primary_color,
                fg="white"
            ).pack(anchor="w")
            
            # Resource details
            details_frame = tk.Frame(dialog, bg=self.card_bg, padx=20, pady=20)
            details_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Upload details
            info_frame = tk.Frame(details_frame, bg=self.card_bg)
            info_frame.pack(fill="x", pady=(0, 15))
            
            tk.Label(
                info_frame,
                text=f"Uploaded: {timestamp.strftime('%B %d, %Y at %H:%M')}",
                font=self.label_font,
                bg=self.card_bg,
                fg=self.text_color
            ).pack(side="left")
            
            # Mentor info if available
            if expertise or department:
                mentor_frame = tk.Frame(details_frame, bg=self.card_bg)
                mentor_frame.pack(fill="x", pady=(0, 15))
                
                mentor_info = []
                if expertise:
                    mentor_info.append(f"Expertise: {expertise}")
                if department:
                    mentor_info.append(f"Department: {department}")
                    
                tk.Label(
                    mentor_frame,
                    text="Mentor Information",
                    font=("Helvetica", 12, "bold"),
                    bg=self.card_bg,
                    fg=self.primary_color
                ).pack(anchor="w")
                
                tk.Label(
                    mentor_frame,
                    text=" | ".join(mentor_info),
                    font=self.label_font,
                    bg=self.card_bg,
                    fg=self.text_color
                ).pack(anchor="w")
            
            # Description section
            tk.Label(
                details_frame,
                text="Description",
                font=("Helvetica", 12, "bold"),
                bg=self.card_bg,
                fg=self.primary_color
            ).pack(anchor="w", pady=(0, 5))
            
            description_text = scrolledtext.ScrolledText(
                details_frame,
                height=8,
                wrap="word",
                font=self.label_font,
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=10
            )
            description_text.pack(fill="both", expand=True, pady=(0, 15))
            description_text.insert("1.0", description or "No description provided.")
            description_text.config(state="disabled")
            
            # File info
            file_frame = tk.Frame(details_frame, bg=self.card_bg)
            file_frame.pack(fill="x", pady=(0, 15))
            
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1]
            
            file_icon = "📄"
            if file_extension.lower() in ['.pdf']:
                file_icon = "📕"
            elif file_extension.lower() in ['.doc', '.docx']:
                file_icon = "📘"
            elif file_extension.lower() in ['.ppt', '.pptx']:
                file_icon = "📙"
            elif file_extension.lower() in ['.xls', '.xlsx']:
                file_icon = "📗"
                
            tk.Label(
                file_frame,
                text=f"{file_icon} {file_name}",
                font=self.label_font,
                bg=self.card_bg,
                fg=self.accent_color
            ).pack(anchor="w")
            
            # Buttons
            button_frame = tk.Frame(details_frame, bg=self.card_bg)
            button_frame.pack(fill="x", pady=(15, 0))
            
            download_button = tk.Button(
                button_frame,
                text="Download Resource",
                font=self.button_font,
                bg=self.primary_color,
                fg="white",
                relief="flat",
                padx=15,
                pady=5,
                command=lambda: self.download_specific_resource(resource_id, file_path)
            )
            download_button.pack(side="left")
            download_button.bind("<Enter>", self.on_enter)
            download_button.bind("<Leave>", self.on_leave)
            
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

    def download_resource(self, tree):
        """Download the selected resource."""
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Select a Resource", "Please select a resource to download.")
            return
            
        item_id = selection[0]
        item_index = tree.index(item_id)
        
        if item_index >= len(self.resource_ids):
            return
            
        resource_id = self.resource_ids[item_index]
        
        # Get resource file path
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT file_path FROM resources WHERE id = %s",
                (resource_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Error", "Resource not found!")
                return
                
            file_path = result[0]
            self.download_specific_resource(resource_id, file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not download resource: {e}")
        finally:
            conn.close()

    def download_specific_resource(self, resource_id, file_path):
        """Download a specific resource and update download count."""
        # Check if file exists
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "The file does not exist or cannot be accessed!")
            return
            
        # Ask user where to save the file
        file_name = os.path.basename(file_path)
        save_path = filedialog.asksaveasfilename(
            defaultextension=os.path.splitext(file_name)[1],
            filetypes=[("All Files", "*.*")],
            initialfile=file_name
        )
        
        if not save_path:
            return  # User canceled
            
        try:
            # Copy the file to the destination
            with open(file_path, 'rb') as source_file:
                with open(save_path, 'wb') as dest_file:
                    dest_file.write(source_file.read())
                    
            # Update download count
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE resources SET downloads = downloads + 1 WHERE id = %s",
                    (resource_id,)
                )
                conn.commit()
            finally:
                conn.close()
                
            messagebox.showinfo("Success", "Resource downloaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download resource: {e}")

    def book_session(self, mentor_id, date, time, purpose, dialog):
        """Book a session with a mentor."""
        # Validate inputs
        if not mentor_id:
            messagebox.showerror("Error", "Please select a mentor.")
            return
            
        if not date or not time:
            messagebox.showerror("Error", "Please select date and time for the session.")
            return
            
        if not purpose:
            messagebox.showerror("Error", "Please specify the purpose of the session.")
            return
        
        # Check if mentor is available at that time
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if mentor already has a session at that time
            cursor.execute("""
                SELECT id FROM sessions 
                WHERE senior_id = %s AND date = %s AND time = %s
                AND status IN ('Pending', 'Active')
            """, (mentor_id, date, time))
            
            existing_session = cursor.fetchone()
            if existing_session:
                messagebox.showerror(
                    "Time Slot Unavailable", 
                    "The mentor already has a session scheduled at this time. Please select another time."
                )
                return
                
            # Check if student already has a session at that time
            cursor.execute("""
                SELECT id FROM sessions 
                WHERE junior_id = %s AND date = %s AND time = %s
                AND status IN ('Pending', 'Active')
            """, (self.controller.user_id, date, time))
            
            student_session = cursor.fetchone()
            if student_session:
                messagebox.showerror(
                    "Time Slot Unavailable", 
                    "You already have a session scheduled at this time. Please select another time."
                )
                return
            
            # Insert the session request
            cursor.execute("""
                INSERT INTO sessions 
                (junior_id, senior_id, date, time, status) 
                VALUES (%s, %s, %s, %s, 'Pending')
            """, (self.controller.user_id, mentor_id, date, time))
            
            # Get the session ID
            session_id = cursor.lastrowid
            
            # Add purpose as notification to mentor
            cursor.execute("""
                INSERT INTO notifications
                (user_id, message, is_read)
                VALUES (%s, %s, FALSE)
            """, (mentor_id, f"New session request from {self.controller.username} on {date} at {time}. Purpose: {purpose}"))
            
            conn.commit()
            messagebox.showinfo("Success", "Session request sent successfully! The mentor will be notified.")
            
            # Close dialog
            dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not book session: {e}")
        finally:
            conn.close()

    def mark_resolved(self, question_id, dialog=None):
            """Mark a question as resolved."""
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE questions SET resolved = TRUE WHERE id = %s AND user_id = %s",
                    (question_id, self.controller.user_id)
                )
                conn.commit()
                
                messagebox.showinfo("Success", "Question marked as resolved!")
                
                # Close dialog if provided
                if dialog:
                    dialog.destroy()
                    
                # Refresh dashboard
                self.refresh()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not mark question as resolved: {e}")
            finally:
                conn.close()
        
    def rate_answer(self, answer_id, rating, dialog, question_id):
        """Rate an answer and refresh the dialog."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE answers SET rating = %s WHERE id = %s",
                (rating, answer_id)
            )
            conn.commit()

            messagebox.showinfo("Rating Submitted", f"You rated this answer {rating} out of 5 stars.")

            # Close and reopen the dialog to refresh
            if dialog:
                dialog.destroy()
                self.show_question_details(question_id)

        except Exception as e:
            messagebox.showerror("Error", f"Could not submit rating: {e}")
        
        finally:
            conn.close()

        
    def logout(self):
            """Log out the current user."""
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.controller.username = None
                self.controller.user_id = None
                self.controller.show_frame("LoginPage")
        
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
        
    def refresh(self):
            """Refresh the dashboard."""
            # First check if user is banned
            is_banned = self.check_ban_status()
            
            if not is_banned:
                # Only update dashboard if user is not banned
                self.update_welcome_label()