# pages/settings_page.py
import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk  # For adding images (requires Pillow library)
from database import get_db_connection
import hashlib

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Professional Color Scheme
        self.bg_color = "#ECF0F3"
        self.card_bg = "#FFFFFF"
        self.primary_color = "#0A2463"
        self.accent_color = "#3E92CC"
        self.text_color = "#1B1B1E"
        self.error_color = "#D64045"
        
        self.configure(bg=self.bg_color)
        
        # Custom Fonts
        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        label_font = font.Font(family="Helvetica", size=12)
        button_font = font.Font(family="Helvetica", size=12, weight="bold")

        # Title Label
        tk.Label(
            self, 
            text="Settings", 
            font=title_font, 
            bg=self.bg_color, 
            fg=self.primary_color
        ).pack(pady=(30, 10))

        # Frame for Settings Options
        settings_frame = tk.Frame(
            self, 
            bg=self.card_bg, 
            padx=20, 
            pady=20, 
            highlightbackground=self.accent_color,
            highlightthickness=1
        )
        settings_frame.pack(pady=20, fill="both", expand=True, padx=50)

        # Update Profile Section
        tk.Label(
            settings_frame, 
            text="Update Profile", 
            font=("Helvetica", 16, "bold"), 
            bg=self.card_bg, 
            fg=self.primary_color
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Name Field
        tk.Label(
            settings_frame, 
            text="Name:", 
            font=label_font, 
            bg=self.card_bg, 
            fg=self.text_color
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.name_entry = tk.Entry(
            settings_frame, 
            font=label_font, 
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            highlightbackground="#D1D9E6",
            highlightthickness=1
        )
        self.name_entry.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky="ew", ipady=5, ipadx=5)

        # Email Field
        tk.Label(
            settings_frame, 
            text="Email:", 
            font=label_font, 
            bg=self.card_bg, 
            fg=self.text_color
        ).grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        self.email_entry = tk.Entry(
            settings_frame, 
            font=label_font, 
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            highlightbackground="#D1D9E6",
            highlightthickness=1
        )
        self.email_entry.grid(row=4, column=0, columnspan=2, pady=(0, 15), sticky="ew", ipady=5, ipadx=5)

        # Password Field
        tk.Label(
            settings_frame, 
            text="New Password (leave blank to keep current):", 
            font=label_font, 
            bg=self.card_bg, 
            fg=self.text_color
        ).grid(row=5, column=0, sticky="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(
            settings_frame, 
            font=label_font, 
            show="*", 
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            highlightbackground="#D1D9E6",
            highlightthickness=1
        )
        self.password_entry.grid(row=6, column=0, columnspan=2, pady=(0, 15), sticky="ew", ipady=5, ipadx=5)

        # Confirm Password Field
        tk.Label(
            settings_frame, 
            text="Confirm New Password:", 
            font=label_font, 
            bg=self.card_bg, 
            fg=self.text_color
        ).grid(row=7, column=0, sticky="w", pady=(0, 5))
        
        self.confirm_password_entry = tk.Entry(
            settings_frame, 
            font=label_font, 
            show="*", 
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            highlightbackground="#D1D9E6",
            highlightthickness=1
        )
        self.confirm_password_entry.grid(row=8, column=0, columnspan=2, pady=(0, 15), sticky="ew", ipady=5, ipadx=5)

        # For Junior users, show the Anonymous Questions option
        self.anonymous_var = tk.BooleanVar(value=False)
        self.anonymous_check = tk.Checkbutton(
            settings_frame,
            text="Post Questions Anonymously by Default",
            variable=self.anonymous_var,
            font=label_font,
            bg=self.card_bg,
            fg=self.text_color,
            activebackground=self.card_bg,
            selectcolor=self.card_bg
        )
        
        # We'll decide whether to show this when loading user data

        # Buttons Frame
        button_frame = tk.Frame(settings_frame, bg=self.card_bg)
        button_frame.grid(row=10, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Save Changes Button
        save_button = tk.Button(
            button_frame,
            text="Save Changes",
            font=button_font,
            bg=self.accent_color,
            fg="white",
            relief="flat",
            activebackground=self.primary_color,
            cursor="hand2",
            command=self.save_changes,
            padx=15
        )
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew", ipady=8)

        # Reset Button
        reset_button = tk.Button(
            button_frame,
            text="Reset Fields",
            font=button_font,
            bg="#808080",
            fg="white",
            relief="flat",
            activebackground="#606060",
            cursor="hand2",
            command=self.reset_fields,
            padx=15
        )
        reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew", ipady=8)

        # Back button container
        back_button_frame = tk.Frame(self, bg=self.bg_color)
        back_button_frame.pack(fill="x", pady=(10, 30), padx=50)

        # Back to Dashboard Button
        back_button = tk.Button(
            back_button_frame,
            text="← Back to Dashboard",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            activebackground="#E6E6E6",
            cursor="hand2",
            command=self.go_back
        )
        back_button.pack(side="left")

        # Error/Success message label
        self.message_label = tk.Label(
            self, 
            text="", 
            font=label_font, 
            bg=self.bg_color,
            fg="white",
            padx=15,
            pady=10
        )
        
        # Load user data when page is shown
        self.bind("<<ShowFrame>>", self.load_user_data)

    def load_user_data(self, event=None):
        """Load user data from database when the page is shown."""
        if hasattr(self.controller, 'user_id'):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT name, email, role FROM users WHERE id = %s",
                    (self.controller.user_id,)
                )
                user_data = cursor.fetchone()
                
                if user_data:
                    # Clear existing entries
                    self.name_entry.delete(0, tk.END)
                    self.email_entry.delete(0, tk.END)
                    self.password_entry.delete(0, tk.END)
                    self.confirm_password_entry.delete(0, tk.END)
                    
                    # Fill with user data
                    self.name_entry.insert(0, user_data[0])
                    self.email_entry.insert(0, user_data[1])
                    
                    # Only show the anonymous option for Junior role
                    if user_data[2] == "Junior":
                        self.anonymous_check.grid(row=9, column=0, columnspan=2, pady=(0, 20), sticky="w")
                    else:
                        self.anonymous_check.grid_forget()
                        
            except Exception as e:
                self.show_message(f"Error loading user data: {str(e)}", "error")
            finally:
                cursor.close()
                conn.close()

    def save_changes(self):
        """Save user settings to the database with proper validation."""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate inputs
        if not name:
            self.show_message("Name is required", "error")
            return
            
        if not email:
            self.show_message("Email is required", "error")
            return
            
        # Email format validation
        if "@" not in email or "." not in email:
            self.show_message("Please enter a valid email address", "error")
            return
            
        # Password validation
        if password and password != confirm_password:
            self.show_message("Passwords do not match", "error")
            return

        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("START TRANSACTION")
            
            # Check if email is already taken by another user
            cursor.execute(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (email, self.controller.user_id)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.execute("ROLLBACK")
                self.show_message("Email is already in use by another account", "error")
                return
                
            # Build the update query based on whether password was provided
            if password:
                # Hash the password (in a real app, use a secure hashing library)
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                cursor.execute(
                    """
                    UPDATE users 
                    SET name = %s, email = %s, password = %s
                    WHERE id = %s
                    """,
                    (name, email, hashed_password, self.controller.user_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE users 
                    SET name = %s, email = %s
                    WHERE id = %s
                    """,
                    (name, email, self.controller.user_id)
                )
                
            conn.commit()
            self.show_message("Profile updated successfully!", "success")
            
            # Clear password fields
            self.password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            self.show_message(f"Error updating profile: {str(e)}", "error")
        finally:
            cursor.close()
            conn.close()

    def reset_fields(self):
        """Reset all fields to current user data."""
        self.load_user_data()

    def show_message(self, message, message_type="info"):
        """Show a message to the user."""
        # Hide any existing message
        self.message_label.pack_forget()
        
        # Set message color based on type
        if message_type == "error":
            self.message_label.config(bg=self.error_color, text=message)
        elif message_type == "success":
            self.message_label.config(bg="#4CAF50", text=message)
        else:
            self.message_label.config(bg=self.accent_color, text=message)
            
        # Show the message
        self.message_label.pack(fill="x", padx=50, pady=(0, 10))
        
        # Auto-hide after 3 seconds
        self.after(3000, self.hide_message)
    
    def hide_message(self):
        """Hide the message label."""
        self.message_label.pack_forget()

    def go_back(self):
        """Return to the appropriate dashboard based on user role."""
        if hasattr(self.controller, 'role'):
            if self.controller.role == "Junior":
                self.controller.show_frame("JuniorDashboardPage")
            elif self.controller.role == "Senior":
                self.controller.show_frame("SeniorDashboardPage")
            else:
                self.controller.show_frame("AdminDashboardPage")
        else:
            # Fallback to a default page
            self.controller.show_frame("LoginPage")