import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import customtkinter as ctk  # New modern UI library
from database import DatabaseConnection
import logging
import hashlib
import os
from PIL import Image, ImageTk
import shutil
from datetime import datetime

# Set appearance mode and default theme
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

logging.basicConfig(level=logging.INFO, filename='forum.log', 
                  format='%(asctime)s - %(levelname)s - %(message)s')

class ForumApp:
    def __init__(self):
        """Initialize the application"""
        # Create main window first
        self.root = ctk.CTk()
        self.root.title("Forum Application")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set color scheme
        self.colors = {
            'primary': "#1f538d",       # Deep blue
            'secondary': "#14a098",     # Teal
            'accent': "#f1e3d3",        # Light cream
            'text_light': "#f5f5f5",    # Off-white text for dark backgrounds
            'text_dark': "#333333",     # Dark gray text for light backgrounds
            'bg_light': "#ffffff",      # Pure white background
            'bg_dark': "#1a1a1a",       # Very dark gray background
            'success': "#28a745",       # Green
            'warning': "#ffc107",       # Yellow
            'danger': "#dc3545",        # Red
            'info': "#17a2b8"           # Light blue
        }
        
        try:
            # Initialize database connection
            self.db = DatabaseConnection()
            self.db.connect()  # Ensure connection is established
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            self.root.destroy()
            return
            
        self.current_user = None
        self.current_user_id = None
        
        # Create images directory if it doesn't exist
        self.images_dir = "post_images"
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        self.create_main_frame()
        self.show_start_page()

    def on_closing(self):
        """Handle application closing"""
        try:
            if hasattr(self, 'db') and self.db is not None:
                if hasattr(self.db, 'cursor') and self.db.cursor is not None:
                    self.db.cursor.close()
                if hasattr(self.db, 'connection') and self.db.connection is not None:
                    self.db.connection.close()
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
        finally:
            self.root.destroy()

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error running application: {str(e)}")
            self.on_closing()

    def create_main_frame(self):
        # Create a main frame that fills the window
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def show_start_page(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a center frame with rounded corners
        center_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.8, relheight=0.8)
        
        # App logo/title
        title_label = ctk.CTkLabel(center_frame, 
                                text="FORUM APP", 
                                font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
                                text_color=self.colors['primary'])
        title_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        
        # Welcome text
        welcome_text = ctk.CTkLabel(center_frame,
                               text="Welcome to Discussion Forum",
                               font=ctk.CTkFont(family="Segoe UI", size=18),
                               text_color=self.colors['text_dark'])
        welcome_text.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        # Continue button with hover effect
        continue_btn = ctk.CTkButton(center_frame,
                                text="Continue",
                                command=self.show_login_frame,
                                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                fg_color=self.colors['primary'],
                                hover_color=self.colors['secondary'],
                                corner_radius=10,
                                width=200,
                                height=40)
        continue_btn.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        # Animate elements with fade-in effect
        self.animate_widget(title_label, 0.3)
        self.animate_widget(welcome_text, 0.4, delay=300)
        self.animate_widget(continue_btn, 0.6, delay=600)

    def animate_widget(self, widget, target_rely, delay=0, duration=500):
        """Animate a widget from below to its target position"""
        if isinstance(widget, ctk.CTkButton) or isinstance(widget, ctk.CTkLabel):
            # Get current info
            info = widget.place_info()
            relx = float(info.get('relx', 0.5))
            
            # Start from below
            widget.place(relx=relx, rely=1.2, anchor=tk.CENTER)
            
            # Animate to target position
            def move_step(current_rely, step=0):
                if step >= duration:
                    widget.place(relx=relx, rely=target_rely, anchor=tk.CENTER)
                    return
                
                # Calculate new position
                new_rely = current_rely - (current_rely - target_rely) * (step / duration)
                widget.place(relx=relx, rely=new_rely, anchor=tk.CENTER)
                
                # Schedule next step
                self.root.after(10, lambda: move_step(new_rely, step + 10))
            
            # Start animation after delay
            self.root.after(delay, lambda: move_step(1.2))

    def login(self):
        """Handle user login with secure password verification"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Input validation
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required!")
            return
            
        try:
            # Get user from database
            user = self.db.execute_query(
                "SELECT id, username, password FROM users WHERE username = %s",
                (username,)
            )
            
            if not user:
                messagebox.showerror("Error", "Invalid username or password!")
                return
                
            # Verify password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password != user[0]['password']:
                messagebox.showerror("Error", "Invalid username or password!")
                logging.warning(f"Failed login attempt for user: {username}")
                return
                
            # Set current user
            self.current_user = user[0]['username']
            self.current_user_id = user[0]['id']
            
            logging.info(f"User logged in: {username}")
            self.show_forum_frame()
            
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            messagebox.showerror("Error", "An error occurred during login!")
    
    def register(self):
        """Handle user registration with secure password hashing"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm_password = self.reg_confirm_password_entry.get().strip()
        
        # Input validation
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters long!")
            return
            
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long!")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
            
        try:
            # Check if username exists
            existing_user = self.db.execute_query(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            
            if existing_user:
                messagebox.showerror("Error", "Username already exists!")
                return
                
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert new user
            self.db.execute_query(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            logging.info(f"New user registered: {username}")
            self.show_login_frame()
            
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            messagebox.showerror("Error", "An error occurred during registration!")
    
    def logout(self):
        """Handle user logout"""
        try:
            self.current_user = None
            self.current_user_id = None
            logging.info("User logged out")
            self.show_login_frame()
        except Exception as e:
            logging.error(f"Logout error: {str(e)}")
            messagebox.showerror("Error", "An error occurred during logout!")
    
    def show_login_frame(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a card-like frame with shadow effect
        login_card = ctk.CTkFrame(self.main_frame, corner_radius=15)
        login_card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.6, relheight=0.7)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(login_card, 
                                  text="Welcome Back", 
                                  font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                                  text_color=self.colors['primary'])
        welcome_label.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
        
        subtitle_label = ctk.CTkLabel(login_card, 
                                   text="Sign in to continue", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   text_color=self.colors['text_dark'])
        subtitle_label.place(relx=0.5, rely=0.22, anchor=tk.CENTER)
        
        # Username field
        username_label = ctk.CTkLabel(login_card, 
                                   text="Username", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   text_color=self.colors['text_dark'])
        username_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        self.username_entry = ctk.CTkEntry(login_card, 
                                        width=300, 
                                        height=40,
                                        placeholder_text="Enter your username",
                                        corner_radius=8,
                                        border_width=1)
        self.username_entry.place(relx=0.5, rely=0.42, anchor=tk.CENTER)
        
        # Password field
        password_label = ctk.CTkLabel(login_card, 
                                   text="Password", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   text_color=self.colors['text_dark'])
        password_label.place(relx=0.5, rely=0.52, anchor=tk.CENTER)
        
        self.password_entry = ctk.CTkEntry(login_card, 
                                        width=300, 
                                        height=40,
                                        placeholder_text="Enter your password",
                                        show="•",
                                        corner_radius=8,
                                        border_width=1)
        self.password_entry.place(relx=0.5, rely=0.59, anchor=tk.CENTER)
        
        # Login button
        login_btn = ctk.CTkButton(login_card, 
                               text="Sign In", 
                               command=self.login,
                               font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                               fg_color=self.colors['primary'],
                               hover_color=self.colors['secondary'],
                               corner_radius=10,
                               width=300,
                               height=40)
        login_btn.place(relx=0.5, rely=0.72, anchor=tk.CENTER)
        
        # Register link
        register_btn = ctk.CTkButton(login_card, 
                                  text="Create Account", 
                                  command=self.show_register_frame,
                                  font=ctk.CTkFont(family="Segoe UI", size=12),
                                  fg_color="transparent",
                                  text_color=self.colors['primary'],
                                  hover_color=self.colors['bg_light'],
                                  corner_radius=8)
        register_btn.place(relx=0.5, rely=0.82, anchor=tk.CENTER)
        
        # Animate elements
        self.animate_widget(welcome_label, 0.15)
        self.animate_widget(subtitle_label, 0.22, delay=100)
        self.animate_widget(username_label, 0.35, delay=200)
        self.animate_widget(self.username_entry, 0.42, delay=250)
        self.animate_widget(password_label, 0.52, delay=300)
        self.animate_widget(self.password_entry, 0.59, delay=350)
        self.animate_widget(login_btn, 0.72, delay=400)
        self.animate_widget(register_btn, 0.82, delay=450)

    def show_register_frame(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a card-like frame with shadow effect
        register_card = ctk.CTkFrame(self.main_frame, corner_radius=15)
        register_card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.6, relheight=0.7)
        
        # Title
        title_label = ctk.CTkLabel(register_card, 
                                text="Create Account", 
                                font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                                text_color=self.colors['primary'])
        title_label.place(relx=0.5, rely=0.12, anchor=tk.CENTER)
        
        subtitle_label = ctk.CTkLabel(register_card, 
                                   text="Join our community today", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   text_color=self.colors['text_dark'])
        subtitle_label.place(relx=0.5, rely=0.18, anchor=tk.CENTER)
        
        # Username field
        username_label = ctk.CTkLabel(register_card, 
                                   text="Username", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   text_color=self.colors['text_dark'])
        username_label.place(relx=0.5, rely=0.28, anchor=tk.CENTER)
        
        self.reg_username_entry = ctk.CTkEntry(register_card, 
                                            width=300, 
                                            height=40,
                                            placeholder_text="Choose a username",
                                            corner_radius=8,
                                            border_width=1)
        self.reg_username_entry.place(relx=0.5, rely=0.34, anchor=tk.CENTER)
        
        # Password field
        password_label = ctk.CTkLabel(register_card, 
                                   text="Password", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   text_color=self.colors['text_dark'])
        password_label.place(relx=0.5, rely=0.44, anchor=tk.CENTER)
        
        self.reg_password_entry = ctk.CTkEntry(register_card, 
                                            width=300, 
                                            height=40,
                                            placeholder_text="Create a password",
                                            show="•",
                                            corner_radius=8,
                                            border_width=1)
        self.reg_password_entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Confirm Password field
        confirm_label = ctk.CTkLabel(register_card, 
                                  text="Confirm Password", 
                                  font=ctk.CTkFont(family="Segoe UI", size=14),
                                  text_color=self.colors['text_dark'])
        confirm_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        self.reg_confirm_password_entry = ctk.CTkEntry(register_card, 
                                                    width=300, 
                                                    height=40,
                                                    placeholder_text="Confirm your password",
                                                    show="•",
                                                    corner_radius=8,
                                                    border_width=1)
        self.reg_confirm_password_entry.place(relx=0.5, rely=0.66, anchor=tk.CENTER)
        
        # Register button
        register_btn = ctk.CTkButton(register_card, 
                                  text="Create Account", 
                                  command=self.register,
                                  font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                  fg_color=self.colors['primary'],
                                  hover_color=self.colors['secondary'],
                                  corner_radius=10,
                                  width=300,
                                  height=40)
        register_btn.place(relx=0.5, rely=0.78, anchor=tk.CENTER)
        
        # Back to login link
        back_btn = ctk.CTkButton(register_card, 
                              text="Back to Login", 
                              command=self.show_login_frame,
                              font=ctk.CTkFont(family="Segoe UI", size=12),
                              fg_color="transparent",
                              text_color=self.colors['primary'],
                              hover_color=self.colors['bg_light'],
                              corner_radius=8)
        back_btn.place(relx=0.5, rely=0.88, anchor=tk.CENTER)
        
        # Animate elements
        self.animate_widget(title_label, 0.12)
        self.animate_widget(subtitle_label, 0.18, delay=100)
        self.animate_widget(username_label, 0.28, delay=200)
        self.animate_widget(self.reg_username_entry, 0.34, delay=250)
        self.animate_widget(password_label, 0.44, delay=300)
        self.animate_widget(self.reg_password_entry, 0.5, delay=350)
        self.animate_widget(confirm_label, 0.6, delay=400)
        self.animate_widget(self.reg_confirm_password_entry, 0.66, delay=450)
        self.animate_widget(register_btn, 0.78, delay=500)
        self.animate_widget(back_btn, 0.88, delay=550)

    def show_forum_frame(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a sidebar for navigation
        sidebar = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color=self.colors['bg_dark'])
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # User profile section
        profile_frame = ctk.CTkFrame(sidebar, corner_radius=10, fg_color=self.colors['primary'])
        profile_frame.pack(padx=10, pady=20, fill=tk.X)
        
        # User avatar (placeholder)
        avatar_label = ctk.CTkLabel(profile_frame, 
                                 text="👤", 
                                 font=ctk.CTkFont(size=36),
                                 text_color=self.colors['text_light'])
        avatar_label.pack(pady=(10, 5))
        
        # Username
        username_label = ctk.CTkLabel(profile_frame, 
                                   text=f"Welcome, {self.current_user}", 
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   text_color=self.colors['text_light'])
        username_label.pack(pady=(0, 10))
        
        # Navigation buttons
        nav_buttons_data = [
            {"text": "All Posts", "icon": "🏠", "command": self.show_all_posts},
            {"text": "My Posts", "icon": "📝", "command": self.show_my_posts},
            {"text": "Travel Buddy", "icon": "✈️", "command": self.show_travel_buddy_frame},
            {"text": "Notifications", "icon": "🔔", "command": self.view_notifications},
            {"text": "New Post", "icon": "➕", "command": self.show_new_post_frame},
            {"text": "Logout", "icon": "🚪", "command": self.logout}
        ]
        
        for btn_data in nav_buttons_data:
            btn = ctk.CTkButton(sidebar, 
                             text=f"{btn_data['icon']} {btn_data['text']}", 
                             command=btn_data['command'],
                             font=ctk.CTkFont(size=14),
                             fg_color="transparent",
                             text_color=self.colors['text_light'],
                             hover_color=self.colors['primary'],
                             anchor="w",
                             height=40,
                             width=180)
            btn.pack(padx=10, pady=5, fill=tk.X)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header with search and filter
        header_frame = ctk.CTkFrame(content_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Category filter
        filter_label = ctk.CTkLabel(header_frame, 
                                 text="FILTER BY:", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.category_var = tk.StringVar(value="All Categories")
        self.categories = self.load_categories()
        category_dropdown = ctk.CTkOptionMenu(header_frame,
                                           values=["All Categories"] + self.categories,
                                           variable=self.category_var,
                                           width=200,
                                           dynamic_resizing=False,
                                           command=self.filter_posts)
        category_dropdown.pack(side=tk.LEFT)
        
        # Posts container with scrollbar
        posts_container = ctk.CTkFrame(content_frame)
        posts_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create canvas and scrollbar for posts
        posts_canvas = ctk.CTkCanvas(posts_container, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(posts_container, orientation="vertical", command=posts_canvas.yview)
        
        # Configure canvas
        posts_canvas.configure(yscrollcommand=scrollbar.set)
        posts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create frame for posts inside canvas
        self.posts_frame = ctk.CTkFrame(posts_canvas, fg_color=self.colors['bg_light'])
        posts_canvas_window = posts_canvas.create_window((0, 0), window=self.posts_frame, anchor="nw", width=posts_canvas.winfo_width())
        
        # Update canvas scroll region when posts frame size changes
        def configure_posts_frame(event):
            posts_canvas.configure(scrollregion=posts_canvas.bbox("all"))
            posts_canvas.itemconfig(posts_canvas_window, width=posts_canvas.winfo_width())
        
        self.posts_frame.bind("<Configure>", configure_posts_frame)
        
        # Set view_my_posts attribute to False by default
        self.view_my_posts = False
        
        # Load posts
        self.load_posts()

    def load_categories(self):
        """Load categories from database"""
        try:
            categories = self.db.execute_query("SELECT name FROM categories ORDER BY name")
            return [category['name'] for category in categories]
        except Exception as e:
            logging.error(f"Error loading categories: {str(e)}")
            return []

    def filter_posts(self, _=None):
        """Filter posts by category"""
        selected_category = self.category_var.get()
        self.load_posts(selected_category)

    def load_posts(self, category=None):
        """Load posts from database with optional category filter"""
        try:
            # Clear existing posts
            for widget in self.posts_frame.winfo_children():
                widget.destroy()

            # Build query based on filters
            conditions = []
            params = []
            
            if category and category != "All Categories":
                conditions.append("c.name = %s")
                params.append(category)
            
            if getattr(self, 'view_my_posts', False):
                conditions.append("p.user_id = %s")
                params.append(self.current_user_id)
            
            where_clause = " AND ".join(conditions)
            if where_clause:
                where_clause = "WHERE " + where_clause

            query = f"""
                SELECT p.*, u.username, c.name as category_name
                FROM posts p 
                JOIN users u ON p.user_id = u.id 
                JOIN categories c ON p.category_id = c.id
                {where_clause}
                ORDER BY p.created_at DESC
            """

            posts = self.db.execute_query(query, tuple(params) if params else None)
            
            if posts:
                for post in posts:
                    self.create_post_card(post)
            else:
                # No posts message
                no_posts_label = ctk.CTkLabel(
                    self.posts_frame,
                    text="No posts found. Be the first to create a post!",
                    font=ctk.CTkFont(size=16),
                    text_color=self.colors['text_dark']
                )
                no_posts_label.pack(pady=50)
                
        except Exception as e:
            logging.error(f"Error loading posts: {str(e)}")
            messagebox.showerror("Error", "Failed to load posts!")

    def create_post_card(self, post):
        """Create a card widget for a post"""
        # Create post card frame
        card = ctk.CTkFrame(self.posts_frame, corner_radius=10)
        card.pack(fill=tk.X, padx=10, pady=5)

        # Post header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Category badge
        category_badge = ctk.CTkLabel(
            header_frame,
            text=post['category_name'],
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_light'],
            fg_color=self.colors['secondary'],
            corner_radius=5
        )
        category_badge.pack(side=tk.LEFT)

        # Post title
        title_label = ctk.CTkLabel(
            card,
            text=post['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_dark']
        )
        title_label.pack(fill=tk.X, padx=10, pady=5)

        # Post content preview
        content_preview = post['content'][:200] + "..." if len(post['content']) > 200 else post['content']
        content_label = ctk.CTkLabel(
            card,
            text=content_preview,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_dark'],
            wraplength=400
        )
        content_label.pack(fill=tk.X, padx=10, pady=5)

        # Post footer
        footer_frame = ctk.CTkFrame(card, fg_color="transparent")
        footer_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Author and date
        author_label = ctk.CTkLabel(
            footer_frame,
            text=f"Posted by {post['username']} on {post['created_at'].strftime('%Y-%m-%d %H:%M')}",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_dark']
        )
        author_label.pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        buttons_frame.pack(side=tk.RIGHT)

        # View post button
        view_btn = ctk.CTkButton(
            buttons_frame,
            text="View Post",
            command=lambda p=post: self.view_post(p['id']),
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            width=100,
            height=28
        )
        view_btn.pack(side=tk.RIGHT, padx=5)

        # Delete post button (only for post owner)
        if post['user_id'] == self.current_user_id:
            delete_btn = ctk.CTkButton(
                buttons_frame,
                text="Delete Post",
                command=lambda p=post: self.delete_post(p['id']),
                font=ctk.CTkFont(size=12),
                fg_color=self.colors['danger'],
                hover_color="#b52d3a",
                width=100,
                height=28
            )
            delete_btn.pack(side=tk.RIGHT, padx=5)

    def show_all_posts(self):
        """Show all posts"""
        self.view_my_posts = False
        self.load_posts()

    def show_my_posts(self):
        """Show only user's posts"""
        self.view_my_posts = True
        self.load_posts()

    def view_post(self, post_id):
        """View full post details"""
        try:
            # Get post details
            post = self.db.execute_query("""
                SELECT p.*, u.username, c.name as category_name 
                FROM posts p 
                JOIN users u ON p.user_id = u.id 
                JOIN categories c ON p.category_id = c.id 
                WHERE p.id = %s
            """, (post_id,))

            if not post:
                messagebox.showerror("Error", "Post not found!")
                return

            # Create post view window
            post_window = ctk.CTkToplevel(self.root)
            post_window.title(post[0]['title'])
            post_window.geometry("600x800")

            # Post content
            content_frame = ctk.CTkFrame(post_window)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Title
            title_label = ctk.CTkLabel(
                content_frame,
                text=post[0]['title'],
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=self.colors['text_dark']
            )
            title_label.pack(pady=(0, 10))

            # Category
            category_label = ctk.CTkLabel(
                content_frame,
                text=post[0]['category_name'],
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_light'],
                fg_color=self.colors['secondary'],
                corner_radius=5
            )
            category_label.pack(pady=(0, 20))

            # Content
            content_text = scrolledtext.ScrolledText(
                content_frame,
                wrap=tk.WORD,
                font=("Segoe UI", 12),
                height=20
            )
            content_text.insert(tk.END, post[0]['content'])
            content_text.configure(state='disabled')
            content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

            # Author and date
            info_label = ctk.CTkLabel(
                content_frame,
                text=f"Posted by {post[0]['username']} on {post[0]['created_at'].strftime('%Y-%m-%d %H:%M')}",
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_dark']
            )
            info_label.pack(pady=(0, 20))

            # Close button
            close_btn = ctk.CTkButton(
                content_frame,
                text="Close",
                command=post_window.destroy,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors['primary'],
                hover_color=self.colors['secondary']
            )
            close_btn.pack(pady=(0, 10))

        except Exception as e:
            logging.error(f"Error viewing post: {str(e)}")
            messagebox.showerror("Error", "Failed to load post details!")

    def show_new_post_frame(self):
        """Show new post creation form"""
        # Create new post window
        post_window = ctk.CTkToplevel(self.root)
        post_window.title("Create New Post")
        post_window.geometry("600x800")

        # Create form
        form_frame = ctk.CTkFrame(post_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            form_frame,
            text="Title",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_dark']
        )
        title_label.pack(pady=(0, 5))

        title_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter post title",
            width=400,
            height=35
        )
        title_entry.pack(pady=(0, 20))

        # Category
        category_label = ctk.CTkLabel(
            form_frame,
            text="Category",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_dark']
        )
        category_label.pack(pady=(0, 5))

        category_var = tk.StringVar(value=self.categories[0])
        category_dropdown = ctk.CTkOptionMenu(
            form_frame,
            values=self.categories,
            variable=category_var,
            width=200
        )
        category_dropdown.pack(pady=(0, 20))

        # Content
        content_label = ctk.CTkLabel(
            form_frame,
            text="Content",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_dark']
        )
        content_label.pack(pady=(0, 5))

        content_text = scrolledtext.ScrolledText(
            form_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            height=15
        )
        content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Image upload section
        image_frame = ctk.CTkFrame(form_frame)
        image_frame.pack(fill=tk.X, pady=(0, 10))

        self.selected_image_path = None
        self.image_preview_label = None

        def select_image():
            file_types = [("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            image_path = filedialog.askopenfilename(filetypes=file_types)
            
            if image_path:
                try:
                    # Create a preview
                    with Image.open(image_path) as img:
                        # Convert to RGB if needed
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        # Create thumbnail
                        img.thumbnail((200, 200))
                        photo = ImageTk.PhotoImage(img)
                        
                        # Update or create preview label
                        if self.image_preview_label:
                            self.image_preview_label.configure(image=photo)
                            self.image_preview_label.image = photo
                        else:
                            self.image_preview_label = ctk.CTkLabel(image_frame, image=photo, text="")
                            self.image_preview_label.pack(pady=5)
                            
                        self.selected_image_path = image_path
                except Exception as e:
                    logging.error(f"Error loading image preview: {str(e)}")
                    messagebox.showerror("Error", "Failed to load image preview!")

        # Image upload button
        upload_btn = ctk.CTkButton(
            image_frame,
            text="Upload Image",
            command=select_image,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['info'],
            hover_color=self.colors['primary'],
            width=150
        )
        upload_btn.pack(pady=5)

        # Submit button
        def submit_post():
            try:
                # Get category ID
                category_id = self.db.execute_query(
                    "SELECT id FROM categories WHERE name = %s",
                    (category_var.get(),)
                )[0]['id']

                # Handle image if selected
                image_path = None
                if self.selected_image_path:
                    # Generate unique filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"post_image_{timestamp}{os.path.splitext(self.selected_image_path)[1]}"
                    destination = os.path.join(self.images_dir, filename)
                    
                    # Copy image to posts directory
                    shutil.copy2(self.selected_image_path, destination)
                    image_path = os.path.join("post_images", filename)

                # Insert post
                self.db.execute_query("""
                    INSERT INTO posts (user_id, category_id, title, content, image_path)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.current_user_id, category_id, title_entry.get(), 
                       content_text.get("1.0", tk.END), image_path))

                messagebox.showinfo("Success", "Post created successfully!")
                post_window.destroy()
                self.load_posts()

            except Exception as e:
                logging.error(f"Error creating post: {str(e)}")
                messagebox.showerror("Error", "Failed to create post!")

        submit_btn = ctk.CTkButton(
            form_frame,
            text="Create Post",
            command=submit_post,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        submit_btn.pack(pady=(0, 10))

    def show_travel_buddy_frame(self):
        """Show travel buddy feature"""
        messagebox.showinfo("Coming Soon", "Travel Buddy feature is coming soon!")

    def view_notifications(self):
        """Display user notifications in a new window"""
        try:
            # Create a new window for notifications
            notification_window = ctk.CTkToplevel(self.root)
            notification_window.title("Notifications")
            notification_window.geometry("600x400")
            
            # Create a scrollable frame for notifications
            notifications_frame = ctk.CTkScrollableFrame(notification_window)
            notifications_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Get user's notifications
            notifications = self.db.get_notifications(self.current_user_id)
            
            if not notifications:
                no_notif_label = ctk.CTkLabel(notifications_frame,
                                           text="No notifications",
                                           font=ctk.CTkFont(size=16),
                                           text_color=self.colors['primary'])
                no_notif_label.pack(pady=20)
                return
            
            # Display each notification
            for notif in notifications:
                # Create a frame for each notification
                notif_frame = ctk.CTkFrame(notifications_frame)
                notif_frame.pack(fill="x", padx=5, pady=5)
                
                # Notification message
                message_label = ctk.CTkLabel(notif_frame,
                                         text=notif['message'],
                                         font=ctk.CTkFont(size=14),
                                         text_color=self.colors['primary'],
                                         wraplength=400)
                message_label.pack(side="left", padx=10, pady=10)
                
                # If notification is about travel interest and is unread, show action buttons
                if notif['notification_type'] == 'travel_interest' and not notif['is_read']:
                    buttons_frame = ctk.CTkFrame(notif_frame, fg_color="transparent")
                    buttons_frame.pack(side="right", padx=10)
                    
                    # Accept button
                    accept_btn = ctk.CTkButton(buttons_frame,
                                           text="Accept",
                                           command=lambda n=notif: self.handle_interest_notification('accepted', n),
                                           fg_color=self.colors['success'],
                                           hover_color="#1e8535",
                                           width=80,
                                           height=25)
                    accept_btn.pack(side="left", padx=5)
                    
                    # Reject button
                    reject_btn = ctk.CTkButton(buttons_frame,
                                           text="Reject",
                                           command=lambda n=notif: self.handle_interest_notification('rejected', n),
                                           fg_color=self.colors['danger'],
                                           hover_color="#bb2d3b",
                                           width=80,
                                           height=25)
                    reject_btn.pack(side="left", padx=5)
                
                # Show notification time
                time_label = ctk.CTkLabel(notif_frame,
                                      text=notif['created_at'].strftime("%Y-%m-%d %H:%M"),
                                      font=ctk.CTkFont(size=12),
                                      text_color=self.colors['secondary'])
                time_label.pack(side="right", padx=10)
                
                # Mark notification as read
                if not notif['is_read']:
                    self.db.mark_notification_read(notif['id'])
        
        except Exception as e:
            logging.error(f"Error viewing notifications: {str(e)}")
            messagebox.showerror("Error", "Failed to load notifications!")

    def handle_interest_notification(self, action, notification):
        """Handle accepting or rejecting travel interest from notification"""
        try:
            # Get the plan and user details
            plan_id = notification['related_post_id']
            interested_user_id = notification['related_user_id']
            
            # Show confirmation dialog
            if not messagebox.askyesno("Confirm Action", 
                                     f"Are you sure you want to {action} this travel interest request?"):
                return
            
            # Update the interest status in database
            success = self.db.handle_travel_interest(plan_id, interested_user_id, action)
            
            if success:
                messagebox.showinfo("Success", f"Interest request {action} successfully!")
                # Refresh notifications
                self.view_notifications()
                # Refresh travel plans to update the display
                self.load_my_travel_plans()
            else:
                messagebox.showerror("Error", f"Failed to {action} interest request!")
                
        except Exception as e:
            logging.error(f"Error handling interest notification: {str(e)}")
            messagebox.showerror("Error", "Failed to process the request!")

    def express_interest_in_trip(self, plan):
        """Express interest in joining a travel plan"""
        try:
            # Show dialog for optional message
            dialog = ctk.CTkInputDialog(
                text="Add a message (optional):",
                title="Express Interest"
            )
            message = dialog.get_input()
            
            # If user cancelled the dialog, return
            if message is None:
                return
            
            # Express interest in the plan
            success, response = self.db.express_interest_in_plan(plan['id'], self.current_user_id, message or "")
            
            if success:
                messagebox.showinfo("Success", "Interest expressed successfully! The plan creator will be notified.")
                # Refresh the travel plans display
                self.load_travel_plans()
            else:
                messagebox.showerror("Error", response)
                
        except Exception as e:
            logging.error(f"Error expressing interest: {str(e)}")
            messagebox.showerror("Error", "Failed to express interest in the plan!")

    # Keep all other methods the same but update their UI components to use CustomTkinter
    # For example, the load_posts method would create CTkFrame instead of ttk.Frame
    
    def load_posts(self, category=None):
        try:
            # Clear existing posts
            for widget in self.posts_frame.winfo_children():
                widget.destroy()

            # Build query based on category filter and view toggle
            conditions = []
            params = []
            
            if category and category != "All Categories":
                conditions.append("c.name = %s")
                params.append(category)
            
            if getattr(self, 'view_my_posts', False):
                conditions.append("p.user_id = %s")
                params.append(self.current_user_id)
            
            where_clause = " AND ".join(conditions)
            if where_clause:
                where_clause = "WHERE " + where_clause

            query = f"""
                SELECT p.*, u.username, c.name as category_name
                FROM posts p 
                JOIN users u ON p.user_id = u.id 
                JOIN categories c ON p.category_id = c.id
                {where_clause}
                ORDER BY p.created_at DESC
            """

            posts = self.db.execute_query(query, tuple(params) if params else None)
            
            if posts:
                for post in posts:
                    # Create a modern card for each post
                    post_card = ctk.CTkFrame(self.posts_frame, corner_radius=10)
                    post_card.pack(fill=tk.X, padx=10, pady=10, ipadx=10, ipady=10)
                    
                    # Header with title and category
                    header_frame = ctk.CTkFrame(post_card, fg_color="transparent")
                    header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
                    
                    # Title with larger font
                    title_label = ctk.CTkLabel(header_frame, 
                                            text=post['title'],
                                            font=ctk.CTkFont(size=18, weight="bold"),
                                            text_color=self.colors['primary'])
                    title_label.pack(side=tk.LEFT)
                    
                    # Category badge
                    category_badge = ctk.CTkLabel(header_frame,
                                               text=post['category_name'],
                                               font=ctk.CTkFont(size=12),
                                               fg_color=self.colors['secondary'],
                                               corner_radius=5,
                                               text_color=self.colors['text_light'],
                                               padx=8, pady=2)
                    category_badge.pack(side=tk.RIGHT)
                    
                    # Author and date info
                    info_frame = ctk.CTkFrame(post_card, fg_color="transparent")
                    info_frame.pack(fill=tk.X, padx=10, pady=0)
                    
                    # Format date nicely
                    post_date = post['created_at'].strftime("%B %d, %Y at %I:%M %p")
                    
                    author_label = ctk.CTkLabel(info_frame,
                                             text=f"Posted by {post['username']} • {post_date}",
                                             font=ctk.CTkFont(size=12),
                                             text_color=self.colors['text_dark'])
                    author_label.pack(anchor="w")
                    
                    # Post content
                    content_frame = ctk.CTkFrame(post_card, fg_color=self.colors['bg_light'], corner_radius=5)
                    content_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    content_text = ctk.CTkTextbox(content_frame, height=80, wrap="word", activate_scrollbars=False)
                    content_text.pack(fill=tk.X, padx=5, pady=5)
                    content_text.insert("1.0", post['content'])
                    content_text.configure(state="disabled")
                    
                    # Display image if present
                    if post['image_path']:
                        try:
                            # Convert database path to full path
                            full_path = os.path.abspath(post['image_path'])
                            logging.info(f"Loading image from: {full_path}")
                            
                            if os.path.exists(full_path):
                                with Image.open(full_path) as img:
                                    # Convert to RGB if needed
                                    if img.mode in ('RGBA', 'P'):
                                        img = img.convert('RGB')
                                    # Create thumbnail
                                    img.thumbnail((300, 300))
                                    photo = ImageTk.PhotoImage(img)
                                    
                                    # Create clickable image label
                                    img_label = ctk.CTkLabel(post_card, image=photo, text="", cursor="hand2")
                                    img_label.image = photo  # Keep a reference
                                    img_label.pack(pady=5)
                                    
                                    # Bind click event to show full image
                                    def show_full_image(event, image_path=full_path):
                                        # Create modal window
                                        modal = ctk.CTkToplevel(self.root)
                                        modal.title("")
                                        modal.attributes('-topmost', True)
                                        
                                        # Get screen dimensions
                                        screen_width = modal.winfo_screenwidth()
                                        screen_height = modal.winfo_screenheight()
                                        
                                        # Set modal size to screen size
                                        modal.geometry(f"{screen_width}x{screen_height}+0+0")
                                        
                                        # Set semi-transparent dark background
                                        modal.configure(fg_color='#000000')
                                        
                                        # Load and display full image
                                        with Image.open(image_path) as full_img:
                                            # Convert to RGB if needed
                                            if full_img.mode in ('RGBA', 'P'):
                                                full_img = full_img.convert('RGB')
                                            
                                            # Calculate aspect ratio
                                            img_ratio = full_img.width / full_img.height
                                            
                                            # Calculate max dimensions while maintaining aspect ratio
                                            max_width = screen_width * 0.9
                                            max_height = screen_height * 0.9
                                            
                                            if img_ratio > max_width / max_height:
                                                # Width limited
                                                new_width = int(max_width)
                                                new_height = int(max_width / img_ratio)
                                            else:
                                                # Height limited
                                                new_height = int(max_height)
                                                new_width = int(max_height * img_ratio)
                                            
                                            # Resize image
                                            full_img = full_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                            photo_full = ImageTk.PhotoImage(full_img)
                                            
                                            # Create and display image label
                                            full_img_label = ctk.CTkLabel(modal, image=photo_full, text="")
                                            full_img_label.image = photo_full
                                            full_img_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                                        
                                        # Bind click event to close modal
                                        def close_modal(event):
                                            modal.destroy()
                                        
                                        modal.bind('<Button-1>', close_modal)
                                        full_img_label.bind('<Button-1>', close_modal)
                                    
                                    # Bind click event to the image label
                                    img_label.bind('<Button-1>', show_full_image)
                            else:
                                logging.error(f"Image file not found: {full_path}")
                        except Exception as e:
                            logging.error(f"Error loading image: {str(e)}")
                    
                    # Action buttons
                    action_frame = ctk.CTkFrame(post_card, fg_color="transparent")
                    action_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    # Reply button
                    reply_button = ctk.CTkButton(action_frame, 
                                              text="Reply", 
                                              command=lambda p=post: self.show_reply_frame(p['id']),
                                              fg_color=self.colors['primary'],
                                              hover_color=self.colors['secondary'],
                                              corner_radius=8,
                                              width=100,
                                              height=30)
                    reply_button.pack(side=tk.RIGHT, padx=5)
                    
                    # Delete button if user owns the post
                    if post['user_id'] == self.current_user_id:
                        delete_btn = ctk.CTkButton(action_frame,
                                                text="Delete",
                                                command=lambda p=post: self.delete_post(p['id']),
                                                fg_color=self.colors['danger'],
                                                hover_color="#b52d3a",  # Darker red
                                                corner_radius=8,
                                                width=100,
                                                height=30)
                        delete_btn.pack(side=tk.RIGHT, padx=5)
                    
                    # Load replies
                    self.load_replies(post['id'], post_card)
            else:
                # No posts message
                no_posts_label = ctk.CTkLabel(self.posts_frame,
                                           text="No posts found. Be the first to create a post!",
                                           font=ctk.CTkFont(size=16),
                                           text_color=self.colors['text_dark'])
                no_posts_label.pack(pady=50)
                
        except Exception as e:
            logging.error(f"Error loading posts: {str(e)}")
            messagebox.showerror("Error", "Failed to load posts!")

    def load_replies(self, post_id, post_frame):
        """Load replies for a post with chat lock indicators"""
        try:
            # Get post info and replies
            post_info = self.db.execute_query("""
                SELECT p.user_id as post_creator_id,
                       u.username as creator_username,
                       (SELECT user_id FROM replies 
                        WHERE post_id = p.id 
                        ORDER BY created_at ASC LIMIT 1) as first_replier_id,
                       (SELECT username FROM replies r
                        JOIN users u ON r.user_id = u.id
                        WHERE r.post_id = p.id 
                        ORDER BY r.created_at ASC LIMIT 1) as first_replier_username
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s
            """, (post_id,))

            replies = self.db.execute_query("""
                SELECT r.*, u.username
                FROM replies r 
                JOIN users u ON r.user_id = u.id 
                WHERE r.post_id = %s 
                ORDER BY r.created_at
            """, (post_id,))
            
            if replies:
                # Create a modern replies section with rounded corners
                replies_frame = ctk.CTkFrame(post_frame, fg_color=self.colors['bg_light'], corner_radius=8)
                replies_frame.pack(fill="x", padx=10, pady=5)
                
                # Header for replies section with chat lock info
                replies_header = ctk.CTkFrame(replies_frame, fg_color="transparent")
                replies_header.pack(fill="x", padx=5, pady=5)
                
                replies_count = ctk.CTkLabel(replies_header,
                                          text=f"Replies ({len(replies)})",
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          text_color=self.colors['primary'])
                replies_count.pack(side='left', padx=5)

                # Show chat lock status if there are replies
                if post_info and replies:
                    post_info = post_info[0]
                    if post_info['first_replier_id']:
                        chat_lock_label = ctk.CTkLabel(replies_header,
                            text=f"🔒 Chat locked between {post_info['creator_username']} and {post_info['first_replier_username']}",
                            font=ctk.CTkFont(size=12),
                            text_color=self.colors['warning'])
                        chat_lock_label.pack(side='right', padx=5)
                
                # Display each reply
                for reply in replies:
                    # Format date nicely
                    reply_date = reply['created_at'].strftime("%b %d, %Y at %I:%M %p")
                    
                    # Create a card for each reply
                    reply_card = ctk.CTkFrame(replies_frame, fg_color=self.colors['accent'], corner_radius=5)
                    reply_card.pack(fill="x", padx=10, pady=3)
                    
                    # Reply header with username and date
                    header_frame = ctk.CTkFrame(reply_card, fg_color="transparent")
                    header_frame.pack(fill="x", padx=5, pady=(5,0))
                    
                    # Username with role indicator
                    author_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                    author_frame.pack(side='left')
                    
                    # Add role indicator (Post Creator or First Replier)
                    role_text = ""
                    if post_info and reply['user_id'] == post_info['post_creator_id']:
                        role_text = " (Post Creator)"
                    elif post_info and reply['user_id'] == post_info['first_replier_id']:
                        role_text = " (First Replier)"
                    
                    author_label = ctk.CTkLabel(author_frame, 
                                             text=f"{reply['username']}{role_text}",
                                             font=ctk.CTkFont(size=12, weight="bold"),
                                             text_color=self.colors['text_dark'])
                    author_label.pack(side='left')
                    
                    date_label = ctk.CTkLabel(header_frame,
                                           text=reply_date,
                                           font=ctk.CTkFont(size=10),
                                           text_color=self.colors['text_dark'])
                    date_label.pack(side='right')
                    
                    # Reply content
                    content_frame = ctk.CTkFrame(reply_card, fg_color="transparent")
                    content_frame.pack(fill="x", padx=5, pady=5)
                    
                    content_text = ctk.CTkTextbox(content_frame, height=60, wrap="word", activate_scrollbars=False)
                    content_text.pack(fill="x", padx=5, pady=5)
                    content_text.insert("1.0", reply['content'])
                    content_text.configure(state="disabled")
                    
                    # Delete button if user owns the reply
                    if reply['user_id'] == self.current_user_id:
                        delete_btn = ctk.CTkButton(reply_card,
                                           text="Delete",
                                           command=lambda r=reply: self.delete_reply(r['id']),
                                           fg_color=self.colors['danger'],
                                           hover_color="#b52d3a",
                                           corner_radius=5,
                                           width=80,
                                           height=25,
                                           font=ctk.CTkFont(size=11))
                        delete_btn.pack(side='right', padx=5, pady=5)
                
        except Exception as e:
            logging.error(f"Error loading replies: {str(e)}")
            messagebox.showerror("Error", "Failed to load replies!")

    def delete_reply(self, reply_id):
        """Delete a single reply"""
        try:
            # Check if user owns the reply or is the post owner
            reply_info = self.db.execute_query("""
                SELECT r.user_id as reply_user_id, 
                       p.user_id as post_user_id,
                       (SELECT MIN(created_at) FROM replies WHERE post_id = r.post_id) as first_reply_time,
                       r.created_at as reply_time
                FROM replies r
                JOIN posts p ON r.post_id = p.id
                WHERE r.id = %s
            """, (reply_id,))
            
            if not reply_info:
                messagebox.showerror("Error", "Reply not found!")
                return
            
            reply_info = reply_info[0]
            
            # Check if user has permission to delete
            is_reply_owner = reply_info['reply_user_id'] == self.current_user_id
            is_post_owner = reply_info['post_user_id'] == self.current_user_id
            is_first_reply = reply_info['first_reply_time'] == reply_info['reply_time']
            
            if not (is_reply_owner or is_post_owner):
                messagebox.showerror("Error", "You can only delete your own replies or replies to your posts!")
                return
            
            # Special warning if it's the first reply (will unlock the chat)
            message = "Are you sure you want to delete this reply?"
            if is_first_reply:
                message = "This is the first reply. Deleting it will unlock the chat. Are you sure?"
            
            if messagebox.askyesno("Confirm Delete", message):
                self.db.execute_query(
                    "DELETE FROM replies WHERE id = %s",
                    (reply_id,)
                )
                
                messagebox.showinfo("Success", "Reply deleted successfully!")
                self.load_posts(self.category_var.get())  # Refresh the posts
        except Exception as e:
            logging.error(f"Error deleting reply: {str(e)}")
            messagebox.showerror("Error", "Failed to delete reply!")

    def delete_post(self, post_id):
        """Delete a post and all its replies"""
        try:
            # Check if user owns the post
            post_check = self.db.execute_query(
                "SELECT user_id FROM posts WHERE id = %s",
                (post_id,)
            )
            
            if not post_check or post_check[0]['user_id'] != self.current_user_id:
                messagebox.showerror("Error", "You can only delete your own posts!")
                return
                
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this post? This will also delete all replies."):
                # Delete all replies first (due to foreign key constraints)
                self.db.execute_query(
                    "DELETE FROM replies WHERE post_id = %s",
                    (post_id,)
                )
                
                # Then delete the post
                self.db.execute_query(
                    "DELETE FROM posts WHERE id = %s AND user_id = %s",
                    (post_id, self.current_user_id)
                )
                
                messagebox.showinfo("Success", "Post and all replies deleted successfully!")
                self.load_posts(self.category_var.get())  # Refresh the posts
        except Exception as e:
            logging.error(f"Error deleting post: {str(e)}")
            messagebox.showerror("Error", "Failed to delete post!")

    def show_travel_buddy_frame(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a header frame
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors['primary'], corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Title with icon
        title_label = ctk.CTkLabel(header_frame, 
                                text="✈️ Travel Buddy", 
                                font=ctk.CTkFont(size=24, weight="bold"),
                                text_color=self.colors['text_light'])
        title_label.pack(side="left", padx=20, pady=15)
        
        # Back button
        back_btn = ctk.CTkButton(header_frame,
                              text="Back to Forum",
                              command=self.show_forum_frame,
                              fg_color=self.colors['secondary'],
                              hover_color=self.colors['info'],
                              corner_radius=8,
                              height=35,
                              width=120)
        back_btn.pack(side="right", padx=20, pady=15)
        
        # Main content area with tabs
        content_frame = ctk.CTkTabview(self.main_frame, corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        tab_find = content_frame.add("Find Travel Buddies")
        tab_create = content_frame.add("Create Travel Plan")
        tab_my = content_frame.add("My Travel Plans")
        
        # Style the tabs
        content_frame._segmented_button.configure(
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=self.colors['bg_light'],
            selected_color=self.colors['primary'],
            selected_hover_color=self.colors['secondary'],
            unselected_color=self.colors['bg_light'],
            unselected_hover_color=self.colors['accent']
        )
        
        # === Find Travel Buddies Tab ===
        # Search and filter section
        search_frame = ctk.CTkFrame(tab_find, corner_radius=10)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        # Destination filter
        dest_label = ctk.CTkLabel(search_frame, 
                               text="Destination:", 
                               font=ctk.CTkFont(size=14))
        dest_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.destination_var = tk.StringVar(value="All Destinations")
        destinations = self.load_destinations()
        dest_dropdown = ctk.CTkOptionMenu(search_frame,
                                       values=["All Destinations"] + destinations,
                                       variable=self.destination_var,
                                       width=200,
                                       dynamic_resizing=False,
                                       command=self.filter_travel_plans)
        dest_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Date range filter
        date_label = ctk.CTkLabel(search_frame, 
                               text="Date Range:", 
                               font=ctk.CTkFont(size=14))
        date_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        self.date_range_var = tk.StringVar(value="All Dates")
        date_ranges = ["All Dates", "Next 7 Days", "Next 30 Days", "Next 3 Months", "Next 6 Months"]
        date_dropdown = ctk.CTkOptionMenu(search_frame,
                                       values=date_ranges,
                                       variable=self.date_range_var,
                                       width=200,
                                       dynamic_resizing=False,
                                       command=self.filter_travel_plans)
        date_dropdown.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Search button
        search_btn = ctk.CTkButton(search_frame,
                                text="Search",
                                command=self.filter_travel_plans,
                                fg_color=self.colors['primary'],
                                hover_color=self.colors['secondary'],
                                corner_radius=8,
                                width=100,
                                height=35)
        search_btn.grid(row=0, column=4, padx=20, pady=10)
        
        # Configure grid
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_columnconfigure(3, weight=1)
        
        # Travel plans list with scrollbar
        plans_container = ctk.CTkFrame(tab_find)
        plans_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for plans
        plans_canvas = ctk.CTkCanvas(plans_container, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(plans_container, orientation="vertical", command=plans_canvas.yview)
        
        # Configure canvas
        plans_canvas.configure(yscrollcommand=scrollbar.set)
        plans_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create frame for plans inside canvas
        self.travel_plans_frame = ctk.CTkFrame(plans_canvas, fg_color=self.colors['bg_light'])
        plans_canvas_window = plans_canvas.create_window((0, 0), window=self.travel_plans_frame, anchor="nw", width=plans_canvas.winfo_width())
        
        # Update canvas scroll region when plans frame size changes
        def configure_plans_frame(event):
            plans_canvas.configure(scrollregion=plans_canvas.bbox("all"))
            plans_canvas.itemconfig(plans_canvas_window, width=plans_canvas.winfo_width())
        
        self.travel_plans_frame.bind("<Configure>", configure_plans_frame)
        
        # === Create Travel Plan Tab ===
        create_form = ctk.CTkFrame(tab_create, corner_radius=10)
        create_form.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form title
        form_title = ctk.CTkLabel(create_form, 
                               text="Create a New Travel Plan", 
                               font=ctk.CTkFont(size=20, weight="bold"),
                               text_color=self.colors['primary'])
        form_title.pack(pady=(20, 30))
        
        # Form fields
        fields_frame = ctk.CTkFrame(create_form, fg_color="transparent")
        fields_frame.pack(fill="x", padx=40, pady=10)
        
        # Destination field
        dest_label = ctk.CTkLabel(fields_frame, 
                               text="Destination:", 
                               font=ctk.CTkFont(size=14),
                               anchor="e",
                               width=120)
        dest_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.new_destination_entry = ctk.CTkEntry(fields_frame, 
                                               width=300, 
                                               height=35,
                                               placeholder_text="Enter destination city/country")
        self.new_destination_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Start date field
        start_label = ctk.CTkLabel(fields_frame, 
                                text="Start Date:", 
                                font=ctk.CTkFont(size=14),
                                anchor="e",
                                width=120)
        start_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self.start_date_entry = ctk.CTkEntry(fields_frame, 
                                          width=300, 
                                          height=35,
                                          placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # End date field
        end_label = ctk.CTkLabel(fields_frame, 
                              text="End Date:", 
                              font=ctk.CTkFont(size=14),
                              anchor="e",
                              width=120)
        end_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.end_date_entry = ctk.CTkEntry(fields_frame, 
                                        width=300, 
                                        height=35,
                                        placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Description field
        desc_label = ctk.CTkLabel(fields_frame, 
                               text="Description:", 
                               font=ctk.CTkFont(size=14),
                               anchor="e",
                               width=120)
        desc_label.grid(row=3, column=0, padx=10, pady=10, sticky="ne")
        
        self.description_text = ctk.CTkTextbox(fields_frame, 
                                            width=300, 
                                            height=100)
        self.description_text.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Max travelers field
        max_label = ctk.CTkLabel(fields_frame, 
                              text="Max Travelers:", 
                              font=ctk.CTkFont(size=14),
                              anchor="e",
                              width=120)
        max_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        
        self.max_travelers_var = tk.StringVar(value="2")
        max_travelers_values = [str(i) for i in range(1, 11)]
        max_travelers_dropdown = ctk.CTkOptionMenu(fields_frame,
                                                values=max_travelers_values,
                                                variable=self.max_travelers_var,
                                                width=300,
                                                height=35,
                                                dynamic_resizing=False)
        max_travelers_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Submit button
        submit_btn = ctk.CTkButton(create_form,
                                text="Create Travel Plan",
                                command=self.create_travel_plan,
                                fg_color=self.colors['primary'],
                                hover_color=self.colors['secondary'],
                                corner_radius=8,
                                width=200,
                                height=40,
                                font=ctk.CTkFont(size=14, weight="bold"))
        submit_btn.pack(pady=30)
        
        # === My Travel Plans Tab ===
        my_plans_container = ctk.CTkFrame(tab_my)
        my_plans_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for my plans
        my_plans_canvas = ctk.CTkCanvas(my_plans_container, bg=self.colors['bg_light'], highlightthickness=0)
        my_scrollbar = ctk.CTkScrollbar(my_plans_container, orientation="vertical", command=my_plans_canvas.yview)
        
        # Configure canvas
        my_plans_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_plans_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create frame for my plans inside canvas
        self.my_travel_plans_frame = ctk.CTkFrame(my_plans_canvas, fg_color=self.colors['bg_light'])
        my_plans_canvas_window = my_plans_canvas.create_window((0, 0), window=self.my_travel_plans_frame, anchor="nw", width=my_plans_canvas.winfo_width())
        
        # Update canvas scroll region when my plans frame size changes
        def configure_my_plans_frame(event):
            my_plans_canvas.configure(scrollregion=my_plans_canvas.bbox("all"))
            my_plans_canvas.itemconfig(my_plans_canvas_window, width=my_plans_canvas.winfo_width())
        
        self.my_travel_plans_frame.bind("<Configure>", configure_my_plans_frame)
        
        # Load travel plans
        self.load_travel_plans()
        self.load_my_travel_plans()

    def load_destinations(self):
        try:
            # Get unique destinations from travel_plans table
            result = self.db.execute_query(
                "SELECT DISTINCT destination FROM travel_plans ORDER BY destination"
            )
            return [row['destination'] for row in result] if result else []
        except Exception as e:
            logging.error(f"Error loading destinations: {str(e)}")
            return []

    def filter_travel_plans(self, event=None):
        try:
            # Get selected filters
            destination = self.destination_var.get()
            date_range = self.date_range_var.get()
            
            # Validate filters
            if not destination or not date_range:
                messagebox.showerror("Error", "Please select both destination and date range filters.")
                return
            
            # Load travel plans with filters
            self.load_travel_plans()
            
        except Exception as e:
            logging.error(f"Error filtering travel plans: {str(e)}")
            messagebox.showerror("Error", "Failed to filter travel plans!")

    def load_travel_plans(self):
        try:
            # Clear existing travel plans
            for widget in self.travel_plans_frame.winfo_children():
                widget.destroy()
                
            # Add refresh button at the top
            refresh_frame = ctk.CTkFrame(self.travel_plans_frame, fg_color="transparent")
            refresh_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            refresh_btn = ctk.CTkButton(refresh_frame,
                                    text="🔄 Refresh",
                                    command=self.load_travel_plans,
                                    fg_color=self.colors['secondary'],
                                    hover_color=self.colors['info'],
                                    corner_radius=8,
                                    width=120,
                                    height=35)
            refresh_btn.pack(side="right")
            
            # Get travel plans excluding user's own plans
            query = """
                SELECT 
                    tp.*,
                    u.username,
                    (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = tp.id AND status = 'accepted') as current_buddies,
                    (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = tp.id) as interest_count,
                    CONCAT(tp.start_date, ' to ', tp.end_date) as travel_dates
                FROM travel_plans tp
                JOIN users u ON tp.user_id = u.id
                WHERE tp.start_date >= CURDATE() AND tp.user_id != %s
                ORDER BY tp.start_date ASC
            """
            
            plans = self.db.execute_query(query, (self.current_user_id,))
            
            if not plans:
                no_plans_label = ctk.CTkLabel(self.travel_plans_frame,
                                           text="No travel plans found",
                                           font=ctk.CTkFont(size=14),
                                           text_color=self.colors['text_dark'])
                no_plans_label.pack(pady=20)
                return
            
            for plan in plans:
                # Create a card for each travel plan
                plan_card = ctk.CTkFrame(self.travel_plans_frame, corner_radius=10)
                plan_card.pack(fill="x", padx=10, pady=10)
                
                # Header with destination and dates
                header_frame = ctk.CTkFrame(plan_card, fg_color=self.colors['primary'], corner_radius=10)
                header_frame.pack(fill="x", padx=0, pady=0)
                
                # Destination with icon
                dest_label = ctk.CTkLabel(header_frame,
                                       text=f"✈️ {plan['destination']}",
                                       font=ctk.CTkFont(size=18, weight="bold"),
                                       text_color=self.colors['text_light'])
                dest_label.pack(side="left", padx=15, pady=10)
                
                # Get dates from travel_dates string
                travel_dates = plan['travel_dates'].split(" to ")
                start_date = travel_dates[0]
                end_date = travel_dates[1] if len(travel_dates) > 1 else start_date
                
                date_label = ctk.CTkLabel(header_frame,
                                       text=f"{start_date} - {end_date}",
                                       font=ctk.CTkFont(size=14),
                                       text_color=self.colors['text_light'])
                date_label.pack(side="right", padx=15, pady=10)
                
                # Content area
                content_frame = ctk.CTkFrame(plan_card, fg_color="transparent")
                content_frame.pack(fill="x", padx=15, pady=15)
                
                # Organizer info
                organizer_label = ctk.CTkLabel(content_frame,
                                            text=f"Organized by: {plan['username']}",
                                            font=ctk.CTkFont(size=12, weight="bold"),
                                            text_color=self.colors['text_dark'])
                organizer_label.pack(anchor="w", pady=(0, 5))
                
                # Description
                if plan.get('description'):
                    desc_label = ctk.CTkLabel(content_frame,
                                           text=plan['description'],
                                           font=ctk.CTkFont(size=12),
                                           text_color=self.colors['text_dark'],
                                           wraplength=400)
                    desc_label.pack(anchor="w", pady=5)
                
                # Interest count
                interest_label = ctk.CTkLabel(content_frame,
                                           text=f"👥 {plan['interest_count']} interested",
                                           font=ctk.CTkFont(size=12),
                                           text_color=self.colors['text_dark'])
                interest_label.pack(anchor="w", pady=5)
                
                # Express interest button
                # Check if user has already expressed interest
                interest_check = self.db.execute_query(
                    "SELECT id, status FROM travel_buddies WHERE plan_id = %s AND user_id = %s",
                    (plan['id'], self.current_user_id)
                )
                
                if interest_check:
                    status = interest_check[0]['status']
                    if status == 'pending':
                        interest_btn = ctk.CTkButton(content_frame,
                                                  text="Interest Pending",
                                                  state="disabled",
                                                  fg_color=self.colors['warning'],
                                                  corner_radius=8,
                                                  width=150,
                                                  height=35)
                    elif status == 'accepted':
                        interest_btn = ctk.CTkButton(content_frame,
                                                  text="Interest Accepted",
                                                  state="disabled",
                                                  fg_color=self.colors['success'],
                                                  corner_radius=8,
                                                  width=150,
                                                  height=35)
                    else:  # rejected
                        interest_btn = ctk.CTkButton(content_frame,
                                                  text="Interest Rejected",
                                                  state="disabled",
                                                  fg_color=self.colors['danger'],
                                                  corner_radius=8,
                                                  width=150,
                                                  height=35)
                else:
                    interest_btn = ctk.CTkButton(content_frame,
                                              text="Express Interest",
                                              command=lambda p=plan: self.express_interest_in_trip(p),
                                              fg_color=self.colors['secondary'],
                                              hover_color=self.colors['info'],
                                              corner_radius=8,
                                              width=150,
                                              height=35)
                interest_btn.pack(anchor="w", pady=10)
                    
                # Description
                if plan.get('description'):
                    desc_text = ctk.CTkTextbox(content_frame, height=80, wrap="word", activate_scrollbars=False)
                    desc_text.pack(fill="x", pady=5)
                    desc_text.insert("1.0", plan['description'])
                    desc_text.configure(state="disabled")
                    
                # Travelers count
                travelers_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                travelers_frame.pack(fill="x", pady=5)
                
                travelers_label = ctk.CTkLabel(travelers_frame,
                                            text=f"Travelers: {plan['current_buddies']}/{plan['max_travelers']}",
                                            font=ctk.CTkFont(size=12),
                                            text_color=self.colors['text_dark'])
                travelers_label.pack(side="left")
                
                # Join button - disabled if full
                is_full = plan['current_buddies'] >= plan['max_travelers']
                
                # Check if user already joined
                joined_check = self.db.execute_query(
                    "SELECT id FROM travel_buddies WHERE plan_id = %s AND user_id = %s AND status = 'accepted'",
                    (plan['id'], self.current_user_id)
                )
                already_joined = bool(joined_check)
                
                if already_joined:
                    join_btn = ctk.CTkButton(travelers_frame,
                                          text="Already Joined",
                                          state="disabled",
                                          fg_color=self.colors['info'],
                                          corner_radius=8,
                                          width=120,
                                          height=30)
                elif is_full:
                    join_btn = ctk.CTkButton(travelers_frame,
                                          text="Full",
                                          state="disabled",
                                          fg_color=self.colors['warning'],
                                          corner_radius=8,
                                          width=120,
                                          height=30)
                else:
                    join_btn = ctk.CTkButton(travelers_frame,
                                          text="Join Trip",
                                          command=lambda p=plan: self.join_travel_plan(p['id']),
                                          fg_color=self.colors['success'],
                                          hover_color="#1e8535",  # Darker green
                                          corner_radius=8,
                                          width=120,
                                          height=30)
                
                join_btn.pack(side="right")
            
        except Exception as e:
            logging.error(f"Error loading travel plans: {str(e)}")
            # Display error message in the frame
            error_label = ctk.CTkLabel(self.travel_plans_frame,
                                   text="No travel plans found matching your criteria.",
                                   font=ctk.CTkFont(size=16),
                                   text_color=self.colors['text_dark'])
            error_label.pack(pady=50)

    def express_interest(self, plan):
        try:
            # Check if user is trying to express interest in their own plan
            if plan['user_id'] == self.current_user_id:
                messagebox.showerror("Error", "You cannot express interest in your own travel plan!")
                return

            # Add interest to travel_buddies table
            self.db.execute_query(
                "INSERT INTO travel_buddies (plan_id, user_id, status, message) VALUES (%s, %s, 'pending', %s)",
                (plan['id'], self.current_user_id, "I'm interested in joining your travel plan!")
            )

            # Create notification for plan owner
            notification_message = f"{self.current_user} has expressed interest in your travel plan to {plan['destination']}"
            self.db.execute_query(
                """INSERT INTO notifications 
                   (user_id, message, notification_type, related_post_id, related_user_id, is_read)
                   VALUES (%s, %s, 'travel_interest', %s, %s, 0)""",
                (plan['user_id'], notification_message, plan['id'], self.current_user_id)
            )

            messagebox.showinfo("Success", "Interest expressed successfully! The plan owner will be notified.")
            
            # Refresh the travel plans display
            self.load_travel_plans()
            
        except Exception as e:
            logging.error(f"Error expressing interest: {str(e)}")
            messagebox.showerror("Error", "Failed to express interest in travel plan!")

    def handle_interest_request(self, interest_id, action):
        try:
            # Update the interest status
            self.db.execute_query(
                "UPDATE travel_buddies SET status = %s WHERE id = %s",
                (action, interest_id)
            )

            # Get interest details for notification
            interest_details = self.db.execute_query(
                """SELECT tb.user_id, tp.destination, u.username 
                   FROM travel_buddies tb 
                   JOIN travel_plans tp ON tb.plan_id = tp.id 
                   JOIN users u ON tb.user_id = u.id 
                   WHERE tb.id = %s""",
                (interest_id,)
            )[0]

            # Create notification for the interested user
            notification_message = f"Your interest in the travel plan to {interest_details['destination']} has been {action}"
            self.db.execute_query(
                """INSERT INTO notifications 
                   (user_id, message, notification_type, is_read)
                   VALUES (%s, %s, 'interest_response', 0)""",
                (interest_details['user_id'], notification_message)
            )

            messagebox.showinfo("Success", f"Interest request {action} successfully!")
            self.load_my_travel_plans()
            
        except Exception as e:
            logging.error(f"Error handling interest request: {str(e)}")
            messagebox.showerror("Error", "Failed to handle interest request!")

    def load_my_travel_plans(self):
        try:
            # Clear existing travel plans
            for widget in self.my_travel_plans_frame.winfo_children():
                widget.destroy()

            # Add refresh button at the top
            refresh_frame = ctk.CTkFrame(self.my_travel_plans_frame, fg_color="transparent")
            refresh_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            refresh_btn = ctk.CTkButton(refresh_frame,
                                    text="🔄 Refresh",
                                    command=self.load_my_travel_plans,
                                    fg_color=self.colors['secondary'],
                                    hover_color=self.colors['info'],
                                    corner_radius=8,
                                    width=120,
                                    height=35)
            refresh_btn.pack(side="right")
            
            # Get all my travel plans (created, joined, and pending)
            my_plans = self.db.get_my_travel_plans(self.current_user_id)
            
            if not my_plans:
                no_plans_label = ctk.CTkLabel(self.my_travel_plans_frame,
                                           text="You haven't created or joined any travel plans yet.",
                                           font=ctk.CTkFont(size=16),
                                           text_color=self.colors['text_dark'])
                no_plans_label.pack(pady=50)
                return

            # Organize plans by type
            created_plans = [p for p in my_plans if p['relationship_type'] == 'created']
            joined_plans = [p for p in my_plans if p['relationship_type'] == 'joined']
            pending_plans = [p for p in my_plans if p['relationship_type'] == 'pending']
            
            # Display created plans section
            if created_plans:
                created_section = ctk.CTkFrame(self.my_travel_plans_frame, fg_color="transparent")
                created_section.pack(fill="x", padx=10, pady=10)
                
                created_header = ctk.CTkLabel(created_section,
                                           text="Plans I Created",
                                           font=ctk.CTkFont(size=18, weight="bold"),
                                           text_color=self.colors['primary'])
                created_header.pack(anchor="w", padx=10, pady=10)
                
                for plan in created_plans:
                    self.create_travel_plan_card(created_section, plan, 'created')
            
            # Display joined plans section
            if joined_plans:
                joined_section = ctk.CTkFrame(self.my_travel_plans_frame, fg_color="transparent")
                joined_section.pack(fill="x", padx=10, pady=10)
                
                joined_header = ctk.CTkLabel(joined_section,
                                          text="Plans I Joined",
                                          font=ctk.CTkFont(size=18, weight="bold"),
                                          text_color=self.colors['primary'])
                joined_header.pack(anchor="w", padx=10, pady=10)
                
                for plan in joined_plans:
                    self.create_travel_plan_card(joined_section, plan, 'joined')
            
            # Display pending plans section
            if pending_plans:
                pending_section = ctk.CTkFrame(self.my_travel_plans_frame, fg_color="transparent")
                pending_section.pack(fill="x", padx=10, pady=10)
                
                pending_header = ctk.CTkLabel(pending_section,
                                          text="Pending Requests",
                                          font=ctk.CTkFont(size=18, weight="bold"),
                                          text_color=self.colors['primary'])
                pending_header.pack(anchor="w", padx=10, pady=10)
                
                for plan in pending_plans:
                    self.create_travel_plan_card(pending_section, plan, 'pending')
                
        except Exception as e:
            logging.error(f"Error loading my travel plans: {str(e)}")
            messagebox.showerror("Error", "Failed to load your travel plans!")

    def create_travel_plan_card(self, parent_frame, plan, plan_type):
        """Create a card for a travel plan"""
        # Create a card frame
        card = ctk.CTkFrame(parent_frame, corner_radius=10)
        card.pack(fill="x", padx=10, pady=5)
        
        # Header with destination and dates
        header_frame = ctk.CTkFrame(card, fg_color=self.colors['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Destination with icon
        dest_label = ctk.CTkLabel(header_frame,
                               text=f"✈️ {plan['destination']}",
                               font=ctk.CTkFont(size=18, weight="bold"),
                               text_color=self.colors['text_light'])
        dest_label.pack(side="left", padx=15, pady=10)
        
        # Dates
        date_label = ctk.CTkLabel(header_frame,
                               text=f"{plan['formatted_start_date']} - {plan['formatted_end_date']}",
                               font=ctk.CTkFont(size=14),
                               text_color=self.colors['text_light'])
        date_label.pack(side="right", padx=15, pady=10)
        
        # Content area
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=15)
        
        # Status/Info section
        if plan_type == 'created':
            status_text = f"👥 {plan['current_buddies']}/{plan['max_travelers']} travelers joined"
            status_color = self.colors['success']
        elif plan_type == 'joined':
            status_text = "You are part of this trip"
            status_color = self.colors['info']
        else:  # pending
            status_text = "Your request is pending"
            status_color = self.colors['warning']
            
        status_label = ctk.CTkLabel(content_frame,
                                 text=status_text,
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 text_color=status_color)
        status_label.pack(anchor="w", pady=5)
        
        # Description
        if plan.get('description'):
            desc_text = ctk.CTkTextbox(content_frame, height=60, wrap="word", activate_scrollbars=False)
            desc_text.pack(fill="x", pady=5)
            desc_text.insert("1.0", plan['description'])
            desc_text.configure(state="disabled")
        
        # Action buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        if plan_type == 'created':
            # View Interests button
            view_interests_btn = ctk.CTkButton(buttons_frame,
                                           text="View Interests",
                                           command=lambda p=plan: self.view_plan_interests(p['id']),
                                           fg_color=self.colors['secondary'],
                                           hover_color=self.colors['info'],
                                           corner_radius=8,
                                           width=120,
                                           height=30)
            view_interests_btn.pack(side="left", padx=5)
            
            # Delete button
            delete_btn = ctk.CTkButton(buttons_frame,
                                   text="Delete Plan",
                                   command=lambda p=plan: self.delete_travel_plan(p['id']),
                                   fg_color=self.colors['danger'],
                                   hover_color="#bb2d3b",
                                   corner_radius=8,
                                   width=120,
                                   height=30)
            delete_btn.pack(side="right", padx=5)
        elif plan_type == 'joined':
            # Leave button
            leave_btn = ctk.CTkButton(buttons_frame,
                                  text="Leave Trip",
                                  command=lambda p=plan: self.leave_travel_plan(p['id']),
                                  fg_color=self.colors['danger'],
                                  hover_color="#bb2d3b",
                                  corner_radius=8,
                                  width=120,
                                  height=30)
            leave_btn.pack(side="right", padx=5)
        elif plan_type == 'pending':
            # Cancel Request button
            cancel_btn = ctk.CTkButton(buttons_frame,
                                   text="Cancel Request",
                                   command=lambda p=plan: self.cancel_interest_request(p['id']),
                                   fg_color=self.colors['warning'],
                                   hover_color="#d6a106",
                                   corner_radius=8,
                                   width=120,
                                   height=30)
            cancel_btn.pack(side="right", padx=5)

    def display_travel_plan(self, travel_frame, plan):
        # Create a frame for each travel plan
        plan_frame = ctk.CTkFrame(travel_frame, corner_radius=10)
        plan_frame.pack(fill="x", padx=10, pady=5)
        
        # Destination header
        destination_label = ctk.CTkLabel(
            plan_frame,
            text=plan['destination'],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        destination_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Travel dates
        dates_label = ctk.CTkLabel(
            plan_frame,
            text=f"Dates: {plan['start_date']} - {plan['end_date']}"
        )
        dates_label.pack(anchor="w", padx=10, pady=2)
        
        # Description
        desc_label = ctk.CTkLabel(
            plan_frame,
            text=plan['description'],
            wraplength=400
        )
        desc_label.pack(anchor="w", padx=10, pady=2)
        
        # Travelers info
        travelers_label = ctk.CTkLabel(
            plan_frame,
            text=f"Travelers: {plan['current_buddies']}/{plan['max_travelers']}"
        )
        travelers_label.pack(anchor="w", padx=10, pady=2)
        
        # Express Interest button
        if plan['user_id'] != self.current_user_id:
            # Check if user has already expressed interest
            interest_check = self.db.execute_query(
                "SELECT id, status FROM travel_buddies WHERE plan_id = %s AND user_id = %s",
                (plan['id'], self.current_user_id)
            )
            
            if interest_check:
                status = interest_check[0]['status']
                if status == 'pending':
                    interest_btn = ctk.CTkButton(
                        plan_frame,
                        text="Interest Pending",
                        state="disabled",
                        fg_color=self.colors['warning'],
                        corner_radius=8,
                        width=120,
                        height=32
                    )
                elif status == 'accepted':
                    interest_btn = ctk.CTkButton(
                        plan_frame,
                        text="Interest Accepted",
                        state="disabled",
                        fg_color=self.colors['success'],
                        corner_radius=8,
                        width=120,
                        height=32
                    )
                else:
                    interest_btn = ctk.CTkButton(
                        plan_frame,
                        text="Interest Rejected",
                        state="disabled",
                        fg_color=self.colors['danger'],
                        corner_radius=8,
                        width=120,
                        height=32
                    )
            else:
                interest_btn = ctk.CTkButton(
                    plan_frame,
                    text="Express Interest",
                    command=lambda p=plan: self.express_interest(p),
                    fg_color=self.colors['secondary'],
                    hover_color=self.colors['info'],
                    corner_radius=8,
                    width=120,
                    height=32
                )
            interest_btn.pack(anchor="w", padx=10, pady=(5, 10))

    def mark_notification_read(self, notification_id):
        """
        Mark a notification as read
        """
        try:
            self.db.execute_query(
                "UPDATE notifications SET is_read = 1 WHERE id = %s",
                (notification_id,)
            )
            return True
        except Exception as e:
            logging.error(f"Error marking notification as read: {str(e)}")
            return False

    def create_travel_plan(self):
        try:
             # Get form data
            destination = self.new_destination_entry.get().strip()
            start_date = self.start_date_entry.get().strip()
            end_date = self.end_date_entry.get().strip()
            description = self.description_text.get("1.0", tk.END).strip()
            max_travelers = int(self.max_travelers_var.get())
            
            # Validate inputs
            if not destination or not start_date or not end_date or not description:
                messagebox.showerror("Error", "All fields are required!")
                return
                
            # Validate dates
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                
                if start_date_obj > end_date_obj:
                    messagebox.showerror("Error", "End date must be after start date!")
                    return
                    
                if start_date_obj < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    messagebox.showerror("Error", "Start date must be in the future!")
                    return
                    
                # Insert the travel plan
                self.db.execute_query(
                    """INSERT INTO travel_plans 
                       (user_id, destination, start_date, end_date, description, max_travelers) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (self.current_user_id, destination, start_date, end_date, description, max_travelers)
                )
                
                # Clear form fields
                self.new_destination_entry.delete(0, tk.END)
                self.start_date_entry.delete(0, tk.END)
                self.end_date_entry.delete(0, tk.END)
                self.description_text.delete("1.0", tk.END)
                self.max_travelers_var.set("2")
                
                messagebox.showinfo("Success", "Travel plan created successfully!")
                
                # Refresh travel plans
                self.load_my_travel_plans()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
                
        except Exception as e:
            logging.error(f"Error creating travel plan: {str(e)}")
            messagebox.showerror("Error", "An error occurred while creating the travel plan!")


    def join_travel_plan(self, plan_id):
        try:
            # Check if already joined
            check_query = "SELECT id FROM travel_buddies WHERE plan_id = %s AND user_id = %s"
            existing = self.db.execute_query(check_query, (plan_id, self.current_user_id))
            
            if existing:
                messagebox.showinfo("Info", "You have already joined this travel plan.")
                return
                
            # Check if plan is full
            plan_info = self.db.execute_query(
                """SELECT p.*, 
                          (SELECT COUNT(*) FROM travel_buddies WHERE plan_id = p.id AND status = 'accepted') as current_buddies,
                          u.username as organizer_name
                   FROM travel_plans p
                   JOIN users u ON p.user_id = u.id
                   WHERE p.id = %s""", 
                (plan_id,)
            )
            
            if not plan_info:
                messagebox.showerror("Error", "Travel plan not found!")
                return
                
            plan = plan_info[0]
            
            if plan['current_buddies'] >= plan['max_travelers']:
                messagebox.showerror("Error", "This travel plan is already full!")
                return
                
            # Add user to travel buddies
            self.db.execute_query(
                "INSERT INTO travel_buddies (plan_id, user_id) VALUES (%s, %s)",
                (plan_id, self.current_user_id)
            )
            
            # Create notification for plan owner
            notification_message = f"{self.current_user} has joined your trip to {plan['destination']}"
            self.db.execute_query(
                """INSERT INTO notifications 
                   (user_id, message, notification_type, related_post_id, related_user_id)
                   VALUES (%s, %s, %s, %s, %s)""",
                (plan['user_id'], notification_message, 'travel_buddy', plan_id, self.current_user_id)
            )
            
            messagebox.showinfo("Success", f"You have joined the trip to {plan['destination']}!")
            self.load_travel_plans()  # Refresh the view
            
        except Exception as e:
            logging.error(f"Error joining travel plan: {str(e)}")
            messagebox.showerror("Error", "Failed to join travel plan!")
            
    def express_interest_in_trip(self, plan):
        try:
            # Check if already expressed interest
            existing_interest = self.db.execute_query(
                "SELECT status FROM travel_buddies WHERE trip_id = %s AND user_id = %s",
                (plan['id'], self.current_user_id)
            )
            
            if existing_interest:
                messagebox.showinfo("Info", "You have already expressed interest in this trip!")
                return
            
            # Add interest record
            self.db.execute_query(
                "INSERT INTO travel_buddies (trip_id, user_id, status) VALUES (%s, %s, 'pending')",
                (plan['id'], self.current_user_id)
            )
            
            # Create notification for trip owner
            self.db.execute_query(
                "INSERT INTO notifications (user_id, message, type, related_id) VALUES (%s, %s, 'trip_interest', %s)",
                (plan['user_id'], f"User {self.current_user} is interested in your trip to {plan['destination']}", plan['id'])
            )
            
            messagebox.showinfo("Success", "Interest expressed successfully! The trip owner will be notified.")
            
        except Exception as e:
            logging.error(f"Error expressing interest: {str(e)}")
            messagebox.showerror("Error", "Failed to express interest in trip!")

    def can_reply_to_post(self, post_id):
        """
        Check if the current user can reply to a post based on chat lock rules:
        1. Post creator can always reply
        2. First replier can always reply
        3. Others cannot reply once the chat is locked (after first reply)
        """
        try:
            # Get post info and first replier
            post_info = self.db.execute_query("""
                SELECT p.user_id as post_creator_id,
                       (SELECT user_id FROM replies 
                        WHERE post_id = p.id 
                        ORDER BY created_at ASC LIMIT 1) as first_replier_id
                FROM posts p
                WHERE p.id = %s
            """, (post_id,))

            if not post_info:
                return False

            post_info = post_info[0]
            
            # Post creator can always reply
            if post_info['post_creator_id'] == self.current_user_id:
                return True
                
            # If there's no first replier yet, anyone can reply
            if post_info['first_replier_id'] is None:
                return True
                
            # If there is a first replier, only they can reply (besides the creator)
            return post_info['first_replier_id'] == self.current_user_id

        except Exception as e:
            logging.error(f"Error checking reply permission: {str(e)}")
            return False

    def reply_to_post(self, post_id):
        """
        Create a reply to a post with chat lock enforcement
        """
        reply_content = self.reply_text.get("1.0", tk.END).strip()
        
        if not reply_content:
            messagebox.showerror("Error", "Reply content cannot be empty!")
            return

        if not self.can_reply_to_post(post_id):
            messagebox.showerror("Error", "This chat is locked. Only the post creator and first replier can continue the conversation.")
            return

        try:
            # Insert the reply
            self.db.execute_query(
                "INSERT INTO replies (post_id, user_id, content) VALUES (%s, %s, %s)",
                (post_id, self.current_user_id, reply_content)
            )

            messagebox.showinfo("Success", "Reply submitted successfully!")
            self.reply_text.delete("1.0", tk.END)
            self.load_posts(self.category_var.get())  # Refresh the posts

        except Exception as e:
            logging.error(f"Error replying to post: {str(e)}")
            messagebox.showerror("Error", "Failed to submit reply!")

    def show_reply_frame(self, post_id):
        """Show reply dialog for a post with chat lock check"""
        if not self.can_reply_to_post(post_id):
            messagebox.showinfo("Info", "This chat is locked. Only the post creator and first replier can continue the conversation.")
            return

        # Create reply window
        reply_window = ctk.CTkToplevel(self.root)
        reply_window.title("Reply to Post")
        reply_window.geometry("600x400")
        reply_window.transient(self.root)
        reply_window.grab_set()

        # Create main frame
        main_frame = ctk.CTkFrame(reply_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Reply text area
        self.reply_text = ctk.CTkTextbox(
            main_frame,
            height=200,
            wrap="word",
            font=ctk.CTkFont(size=14)
        )
        self.reply_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 20))

        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=reply_window.destroy,
            fg_color=self.colors['danger'],
            hover_color="#b52d3a",
            width=100
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Submit button
        submit_btn = ctk.CTkButton(
            button_frame,
            text="Submit Reply",
            command=lambda: self.submit_reply(post_id, reply_window),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            width=100
        )
        submit_btn.pack(side=tk.RIGHT, padx=5)

    def submit_reply(self, post_id, reply_window):
        """Submit a reply and close the reply window - simplified version"""
        try:
            self.reply_to_post(post_id)
            reply_window.destroy()
        except Exception as e:
            logging.error(f"Error submitting reply: {str(e)}")
            messagebox.showerror("Error", "Failed to submit reply!")

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error running application: {str(e)}")
            self.on_closing()

    def view_plan_interests(self, plan_id):
        """Display all interests for a travel plan"""
        try:
            # Create a new window for interests
            interests_window = ctk.CTkToplevel(self.root)
            interests_window.title("Travel Plan Interests")
            interests_window.geometry("600x400")
            
            # Create a scrollable frame for interests
            interests_frame = ctk.CTkScrollableFrame(interests_window)
            interests_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Get all interests for this plan
            interests = self.db.execute_query("""
                SELECT tb.*, u.username, 
                       DATE_FORMAT(tb.created_at, '%Y-%m-%d %H:%i') as formatted_date
                FROM travel_buddies tb
                JOIN users u ON tb.user_id = u.id
                WHERE tb.plan_id = %s
                ORDER BY tb.created_at DESC
            """, (plan_id,))
            
            if not interests:
                no_interests_label = ctk.CTkLabel(interests_frame,
                                              text="No interests yet",
                                              font=ctk.CTkFont(size=16),
                                              text_color=self.colors['primary'])
                no_interests_label.pack(pady=20)
                return
            
            # Group interests by status
            pending_interests = [i for i in interests if i['status'] == 'pending']
            accepted_interests = [i for i in interests if i['status'] == 'accepted']
            rejected_interests = [i for i in interests if i['status'] == 'rejected']
            
            # Display pending interests
            if pending_interests:
                pending_header = ctk.CTkLabel(interests_frame,
                                         text="Pending Requests",
                                         font=ctk.CTkFont(size=18, weight="bold"),
                                         text_color=self.colors['warning'])
                pending_header.pack(anchor="w", padx=5, pady=(10, 5))
                
                for interest in pending_interests:
                    self.create_interest_card(interests_frame, interest, 'pending')
            
            # Display accepted interests
            if accepted_interests:
                accepted_header = ctk.CTkLabel(interests_frame,
                                          text="Accepted Travelers",
                                          font=ctk.CTkFont(size=18, weight="bold"),
                                          text_color=self.colors['success'])
                accepted_header.pack(anchor="w", padx=5, pady=(10, 5))
                
                for interest in accepted_interests:
                    self.create_interest_card(interests_frame, interest, 'accepted')
            
            # Display rejected interests
            if rejected_interests:
                rejected_header = ctk.CTkLabel(interests_frame,
                                          text="Rejected Requests",
                                          font=ctk.CTkFont(size=18, weight="bold"),
                                          text_color=self.colors['danger'])
                rejected_header.pack(anchor="w", padx=5, pady=(10, 5))
                
                for interest in rejected_interests:
                    self.create_interest_card(interests_frame, interest, 'rejected')
                    
        except Exception as e:
            logging.error(f"Error viewing plan interests: {str(e)}")
            messagebox.showerror("Error", "Failed to load travel plan interests!")

    def create_interest_card(self, parent_frame, interest, status):
        """Create a card for an interest request"""
        # Create card frame
        card = ctk.CTkFrame(parent_frame, corner_radius=10)
        card.pack(fill="x", padx=5, pady=5)
        
        # Content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=10)
        
        # User info
        user_label = ctk.CTkLabel(content,
                               text=f"👤 {interest['username']}",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color=self.colors['primary'])
        user_label.pack(anchor="w")
        
        # Date info
        date_label = ctk.CTkLabel(content,
                               text=f"📅 Requested on: {interest['formatted_date']}",
                               font=ctk.CTkFont(size=14),
                               text_color=self.colors['secondary'])
        date_label.pack(anchor="w", pady=(5, 0))
        
        # Message if any
        if interest.get('message'):
            message_label = ctk.CTkLabel(content,
                                     text=f"💬 Message: {interest['message']}",
                                     font=ctk.CTkFont(size=14),
                                     text_color=self.colors['primary'],
                                     wraplength=400)
            message_label.pack(anchor="w", pady=(5, 0))
        
        # Status-specific UI
        if status == 'pending':
            buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
            buttons_frame.pack(fill="x", pady=(10, 0))
            
            # Accept button
            accept_btn = ctk.CTkButton(buttons_frame,
                                   text="Accept",
                                   command=lambda: self.handle_interest_request(interest['id'], 'accepted'),
                                   fg_color=self.colors['success'],
                                   hover_color="#1e8535",
                                   width=100,
                                   height=30)
            accept_btn.pack(side="left", padx=5)
            
            # Reject button
            reject_btn = ctk.CTkButton(buttons_frame,
                                   text="Reject",
                                   command=lambda: self.handle_interest_request(interest['id'], 'rejected'),
                                   fg_color=self.colors['danger'],
                                   hover_color="#bb2d3b",
                                   width=100,
                                   height=30)
            reject_btn.pack(side="left", padx=5)
        else:
            # Status indicator for accepted/rejected
            status_color = self.colors['success'] if status == 'accepted' else self.colors['danger']
            status_label = ctk.CTkLabel(content,
                                    text=f"Status: {status.title()}",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color=status_color)
            status_label.pack(anchor="w", pady=(5, 0))

if __name__ == "__main__":
    try:
        app = ForumApp()
        app.run()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        if hasattr(app, 'on_closing'):
            app.on_closing()