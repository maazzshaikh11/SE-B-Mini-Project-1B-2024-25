# pages/login_page.py
import tkinter as tk
from tkinter import font, messagebox
from database import get_db_connection
import math

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Professional Color Scheme
        self.bg_color = "#ECF0F3"  # Soft background
        self.card_bg = "#FFFFFF"    # Card background
        self.primary_color = "#0A2463"  # Deep blue
        self.accent_color = "#3E92CC"   # Light blue
        self.text_color = "#1B1B1E"     # Near black
        self.error_color = "#D64045"    # Error red
        
        self.configure(bg=self.bg_color)
        
        # Create main container with neumorphic effect
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create and pack all elements
        self.create_title_section()
        self.create_login_card()
        self.create_footer()
        
        # Bind keyboard events
        self.bind_keyboard_events()

    def create_title_section(self):
        title_frame = tk.Frame(self.main_container, bg=self.bg_color)
        title_frame.pack(pady=(0, 30))

        # Create canvas for logo
        logo_size = 60
        canvas = tk.Canvas(
            title_frame, 
            width=logo_size, 
            height=logo_size, 
            bg=self.bg_color,
            highlightthickness=0
        )
        canvas.pack()

        # Draw stylized logo
        self.draw_logo(canvas, logo_size)

        # Title with gradient effect
        title_label = tk.Label(
            title_frame,
            text="HELP NEST",
            font=("Helvetica", 32, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title_label.pack(pady=(10, 5))

        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="Welcome back! Please sign in to continue",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.accent_color
        )
        subtitle_label.pack()

    def create_login_card(self):
        # Create outer frame for neumorphic effect
        outer_frame = tk.Frame(
            self.main_container,
            bg=self.bg_color,
            padx=3,
            pady=3
        )
        outer_frame.pack(padx=40, pady=20)

        # Create inner card
        self.login_card = tk.Frame(
            outer_frame,
            bg=self.card_bg,
            padx=40,
            pady=30
        )
        self.login_card.pack()
        
        # Add neumorphic effect
        self.add_neumorphic_effect(self.login_card)

        # Email Field
        self.create_input_field("Email", "email")

        # Password Field
        self.create_input_field("Password", "password", show="•")

        # Login Button with animated effect
        self.login_button = self.create_animated_button(
            self.login_card,
            "Sign In",
            self.login
        )
        self.login_button.pack(fill="x", pady=(25, 0))

    def create_footer(self):
        footer_frame = tk.Frame(self.main_container, bg=self.bg_color)
        footer_frame.pack(pady=20)

        register_button = tk.Button(
            footer_frame,
            text="New to Help Nest? Create Account",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg=self.accent_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=self.bg_color,
            activeforeground=self.primary_color,
            command=lambda: self.controller.show_frame("RegisterPage")
        )
        register_button.pack()

    def create_input_field(self, label_text, field_type, show=None):
        container = tk.Frame(self.login_card, bg=self.card_bg)
        container.pack(fill="x", pady=10)

        label = tk.Label(
            container,
            text=label_text,
            font=("Helvetica", 11, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        label.pack(anchor="w")

        entry_frame = tk.Frame(
            container,
            bg=self.bg_color,
            relief="flat",
            bd=1
        )
        entry_frame.pack(fill="x", pady=(5, 0))

        entry = tk.Entry(
            entry_frame,
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            show=show
        )
        entry.pack(fill="x", padx=10, pady=8)

        # Add focus events
        entry.bind("<FocusIn>", lambda e: self.on_focus_in(entry_frame))
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(entry_frame))

        # Store entry widget reference
        if field_type == "email":
            self.email_entry = entry
        else:
            self.password_entry = entry

    def create_animated_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            font=("Helvetica", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=command,
            activebackground=self.accent_color,
            activeforeground="white"
        )
        
        # Add hover animation
        button.bind("<Enter>", lambda e: self.button_hover(button, True))
        button.bind("<Leave>", lambda e: self.button_hover(button, False))
        
        return button

    def draw_logo(self, canvas, size):
        # Create a stylized 'HN' logo
        center_x = size // 2
        center_y = size // 2
        radius = size // 3

        # Draw circular background
        canvas.create_oval(
            5, 5, size-5, size-5,
            fill=self.primary_color,
            outline=self.accent_color,
            width=2
        )

        # Draw stylized 'HN'
        canvas.create_text(
            center_x,
            center_y,
            text="HN",
            font=("Helvetica", int(radius*1.2), "bold"),
            fill="white"
        )

    def add_neumorphic_effect(self, widget):
        widget.configure(
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )

    def button_hover(self, button, entering):
        if entering:
            button.configure(bg=self.accent_color)
        else:
            button.configure(bg=self.primary_color)

    def on_focus_in(self, frame):
        frame.configure(bg=self.accent_color)

    def on_focus_out(self, frame):
        frame.configure(bg=self.bg_color)

    def bind_keyboard_events(self):
        self.email_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Tab order
        self.email_entry.bind('<Tab>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Tab>', lambda e: self.login_button.focus())

    def show_loading(self):
        # Create loading overlay
        self.loading_frame = tk.Frame(
            self.login_card,
            bg=self.card_bg,
            width=self.login_card.winfo_width(),
            height=self.login_card.winfo_height()
        )
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Loading animation
        loading_label = tk.Label(
            self.loading_frame,
            text="Signing in...",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.accent_color
        )
        loading_label.pack(pady=10)
        
        # Update loading dots animation
        self.loading_dots = 0
        self.update_loading_animation(loading_label)

    def update_loading_animation(self, label):
        if hasattr(self, 'loading_frame'):
            dots = "." * (self.loading_dots % 4)
            label.config(text=f"Signing in{dots}")
            self.loading_dots += 1
            self.after(300, lambda: self.update_loading_animation(label))

    def hide_loading(self):
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()
            delattr(self, 'loading_frame')

    def show_message(self, message, is_error=False):
        # Remove any existing message
        if hasattr(self, 'message_label'):
            self.message_label.destroy()

        # Create new message
        self.message_label = tk.Label(
            self.login_card,
            text=message,
            font=("Helvetica", 10),
            bg=self.card_bg,
            fg=self.error_color if is_error else "#4CAF50",
            wraplength=250
        )
        self.message_label.pack(pady=(10, 0))
        
        # Auto-hide message after 3 seconds
        self.after(3000, self.hide_message)

    def hide_message(self):
        if hasattr(self, 'message_label'):
            self.message_label.destroy()
            delattr(self, 'message_label')

    def validate_input(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email:
            self.show_message("Please enter your email address", True)
            self.email_entry.focus()
            return False

        if not password:
            self.show_message("Please enter your password", True)
            self.password_entry.focus()
            return False

        # Basic email validation
        if '@' not in email or '.' not in email:
            self.show_message("Please enter a valid email address", True)
            self.email_entry.focus()
            return False

        return True

    def clear_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.email_entry.focus()

    def login(self):
        if not self.validate_input():
            return

        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        # Show loading animation
        self.show_loading()
        
        # Disable input fields and button during login
        self.email_entry.configure(state='disabled')
        self.password_entry.configure(state='disabled')
        self.login_button.configure(state='disabled')

        # Simulate network delay (remove in production)
        self.after(1000, lambda: self.perform_login(email, password))

    def perform_login(self, email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, role FROM users WHERE email=%s AND password=%s",
                (email, password)
            )
            user = cursor.fetchone()
            
            if user:
                user_id, name, role = user
                self.controller.user_id = user_id
                self.controller.role = role
                self.controller.username = name

                # Hide loading and clear fields
                self.hide_loading()
                self.clear_fields()

                # Enable input fields and button
                self.email_entry.configure(state='normal')
                self.password_entry.configure(state='normal')
                self.login_button.configure(state='normal')

                # Show success message before redirecting
                self.show_message(f"Welcome back, {name}!")
                
                # Navigate after short delay
                self.after(1000, lambda: self.navigate_to_dashboard(role))
            else:
                self.hide_loading()
                self.show_message("Invalid email or password", True)
                self.email_entry.configure(state='normal')
                self.password_entry.configure(state='normal')
                self.login_button.configure(state='normal')
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()

        except Exception as e:
            self.hide_loading()
            self.show_message(f"An error occurred: {str(e)}", True)
            self.email_entry.configure(state='normal')
            self.password_entry.configure(state='normal')
            self.login_button.configure(state='normal')
        finally:
            conn.close()

    def navigate_to_dashboard(self, role):
        if role == "Admin":
            self.controller.show_frame("AdminDashboardPage")
        elif role == "Junior":
            self.controller.show_frame("JuniorDashboardPage")
        elif role == "Senior":
            self.controller.show_frame("SeniorDashboardPage")
        else:
            self.show_message(f"Invalid role: {role}", True)