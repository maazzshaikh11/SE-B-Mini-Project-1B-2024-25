# pages/register_page.py
import tkinter as tk
from tkinter import messagebox, font, ttk
from database import get_db_connection

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Professional Color Scheme (matching login page)
        self.bg_color = "#ECF0F3"
        self.card_bg = "#FFFFFF"
        self.primary_color = "#0A2463"
        self.accent_color = "#3E92CC"
        self.text_color = "#1B1B1E"
        self.error_color = "#D64045"
        
        self.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create and pack all elements
        self.create_title_section()
        self.create_register_card()
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

        # Title
        title_label = tk.Label(
            title_frame,
            text="CREATE ACCOUNT",
            font=("Helvetica", 28, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title_label.pack(pady=(10, 5))

        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="Join Help Nest and start your journey",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.accent_color
        )
        subtitle_label.pack()

    def create_register_card(self):
        # Create outer frame for neumorphic effect
        outer_frame = tk.Frame(
            self.main_container,
            bg=self.bg_color,
            padx=3,
            pady=3
        )
        outer_frame.pack(padx=40, pady=20)

        # Create inner card
        self.register_card = tk.Frame(
            outer_frame,
            bg=self.card_bg,
            padx=40,
            pady=30
        )
        self.register_card.pack()
        
        # Add neumorphic effect
        self.add_neumorphic_effect(self.register_card)

        # Create input fields
        self.create_input_field("Full Name", "name")
        self.create_input_field("Email Address", "email")
        self.create_input_field("Password", "password", show="•")
        
        # Create new fields for department and year
        self.create_input_field("Department", "department")
        self.create_year_dropdown()
        
        self.create_role_dropdown()

        # Register Button
        self.register_button = self.create_animated_button(
            self.register_card,
            "Create Account",
            self.register
        )
        self.register_button.pack(fill="x", pady=(25, 0))

    def create_input_field(self, label_text, field_type, show=None):
        container = tk.Frame(self.register_card, bg=self.card_bg)
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
        if field_type == "name":
            self.name_entry = entry
        elif field_type == "email":
            self.email_entry = entry
        elif field_type == "password":
            self.password_entry = entry
        elif field_type == "department":
            self.department_entry = entry

    def create_year_dropdown(self):
        container = tk.Frame(self.register_card, bg=self.card_bg)
        container.pack(fill="x", pady=10)

        label = tk.Label(
            container,
            text="Year",
            font=("Helvetica", 11, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        label.pack(anchor="w")

        self.year_var = tk.StringVar(value="Select your year")
        years = ["First Year", "Second Year", "Third Year", "Fourth Year", "Graduate", "Faculty"]

        dropdown_frame = tk.Frame(
            container,
            bg=self.bg_color,
            relief="flat",
            bd=1
        )
        dropdown_frame.pack(fill="x", pady=(5, 0))

        year_menu = tk.OptionMenu(
            dropdown_frame,
            self.year_var,
            *years
        )
        year_menu.configure(
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            highlightthickness=0,
            activebackground=self.accent_color,
            activeforeground="white"
        )
        year_menu["menu"].configure(
            bg=self.card_bg,
            fg=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white"
        )
        year_menu.pack(fill="x", padx=5, pady=3)

    def create_role_dropdown(self):
        container = tk.Frame(self.register_card, bg=self.card_bg)
        container.pack(fill="x", pady=10)

        label = tk.Label(
            container,
            text="Select Role",
            font=("Helvetica", 11, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        label.pack(anchor="w")

        self.role_var = tk.StringVar(value="Select your role")
        roles = ["Junior", "Senior", "Admin"]

        dropdown_frame = tk.Frame(
            container,
            bg=self.bg_color,
            relief="flat",
            bd=1
        )
        dropdown_frame.pack(fill="x", pady=(5, 0))

        role_menu = tk.OptionMenu(
            dropdown_frame,
            self.role_var,
            *roles
        )
        role_menu.configure(
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            highlightthickness=0,
            activebackground=self.accent_color,
            activeforeground="white"
        )
        role_menu["menu"].configure(
            bg=self.card_bg,
            fg=self.text_color,
            activebackground=self.accent_color,
            activeforeground="white"
        )
        role_menu.pack(fill="x", padx=5, pady=3)

    def create_footer(self):
        footer_frame = tk.Frame(self.main_container, bg=self.bg_color)
        footer_frame.pack(pady=20)

        login_button = tk.Button(
            footer_frame,
            text="Already have an account? Sign In",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg=self.accent_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=self.bg_color,
            activeforeground=self.primary_color,
            command=lambda: self.controller.show_frame("LoginPage")
        )
        login_button.pack()

    def draw_logo(self, canvas, size):
        center_x = size // 2
        center_y = size // 2
        radius = size // 3

        canvas.create_oval(
            5, 5, size-5, size-5,
            fill=self.primary_color,
            outline=self.accent_color,
            width=2
        )

        canvas.create_text(
            center_x,
            center_y,
            text="HN",
            font=("Helvetica", int(radius*1.2), "bold"),
            fill="white"
        )

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
        self.name_entry.bind('<Return>', lambda e: self.email_entry.focus())
        self.email_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.department_entry.focus())
        self.department_entry.bind('<Return>', lambda e: self.register())

    def show_loading(self):
        self.loading_frame = tk.Frame(
            self.register_card,
            bg=self.card_bg,
            width=self.register_card.winfo_width(),
            height=self.register_card.winfo_height()
        )
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        loading_label = tk.Label(
            self.loading_frame,
            text="Creating account...",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.accent_color
        )
        loading_label.pack(pady=10)
        
        self.loading_dots = 0
        self.update_loading_animation(loading_label)

    def update_loading_animation(self, label):
        if hasattr(self, 'loading_frame'):
            dots = "." * (self.loading_dots % 4)
            label.config(text=f"Creating account{dots}")
            self.loading_dots += 1
            self.after(300, lambda: self.update_loading_animation(label))

    def hide_loading(self):
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()
            delattr(self, 'loading_frame')

    def show_message(self, message, is_error=False):
        if hasattr(self, 'message_label'):
            self.message_label.destroy()

        self.message_label = tk.Label(
            self.register_card,
            text=message,
            font=("Helvetica", 10),
            bg=self.card_bg,
            fg=self.error_color if is_error else "#4CAF50",
            wraplength=250
        )
        self.message_label.pack(pady=(10, 0))
        
        self.after(3000, self.hide_message)

    def hide_message(self):
        if hasattr(self, 'message_label'):
            self.message_label.destroy()
            delattr(self, 'message_label')

    def validate_input(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        department = self.department_entry.get().strip()
        year = self.year_var.get()
        role = self.role_var.get()

        if not name:
            self.show_message("Please enter your name", True)
            self.name_entry.focus()
            return False

        if not email:
            self.show_message("Please enter your email address", True)
            self.email_entry.focus()
            return False

        if '@' not in email or '.' not in email:
            self.show_message("Please enter a valid email address", True)
            self.email_entry.focus()
            return False

        if not password:
            self.show_message("Please enter a password", True)
            self.password_entry.focus()
            return False

        if len(password) < 6:
            self.show_message("Password must be at least 6 characters", True)
            self.password_entry.focus()
            return False
            
        if not department:
            self.show_message("Please enter your department", True)
            self.department_entry.focus()
            return False
            
        if year == "Select your year":
            self.show_message("Please select your year", True)
            return False

        if role == "Select your role":
            self.show_message("Please select your role", True)
            return False

        return True

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.department_entry.delete(0, tk.END)
        self.year_var.set("Select your year")
        self.role_var.set("Select your role")
        self.name_entry.focus()

    def register(self):
        if not self.validate_input():
            return

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        department = self.department_entry.get().strip()
        year = self.year_var.get()
        role = self.role_var.get()

        # Show loading animation
        self.show_loading()
        
        # Disable all inputs during registration
        self.name_entry.configure(state='disabled')
        self.email_entry.configure(state='disabled')
        self.password_entry.configure(state='disabled')
        self.department_entry.configure(state='disabled')
        self.register_button.configure(state='disabled')

        # Simulate network delay (remove in production)
        self.after(1000, lambda: self.perform_registration(name, email, password, department, year, role))

    def perform_registration(self, name, email, password, department, year, role):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role, department, year) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, password, role, department, year)
            )
            conn.commit()
            
            # Hide loading and show success message
            self.hide_loading()
            self.show_message("Registration successful!")
            
            # Clear fields and enable inputs
            self.clear_fields()
            self.name_entry.configure(state='normal')
            self.email_entry.configure(state='normal')
            self.password_entry.configure(state='normal')
            self.department_entry.configure(state='normal')
            self.register_button.configure(state='normal')
            
            # Redirect to login page after short delay
            self.after(1500, lambda: self.controller.show_frame("LoginPage"))
            
        except Exception as e:
            self.hide_loading()
            self.show_message(f"An error occurred: {str(e)}", True)
            self.name_entry.configure(state='normal')
            self.email_entry.configure(state='normal')
            self.password_entry.configure(state='normal')
            self.department_entry.configure(state='normal')
            self.register_button.configure(state='normal')
        finally:
            conn.close()