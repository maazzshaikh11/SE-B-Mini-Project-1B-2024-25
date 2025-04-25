import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import get_db_connection

class AdminDashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Professional Color Scheme (matching login page)
        self.bg_color = "#ECF0F3" # Mystic White
        self.card_bg = "#FFFFFF" # White
        self.primary_color = "#0A2463" # Navy Blue (Madison)
        self.accent_color = "#3E92CC" # Sky Blue (Shakespear)
        self.text_color = "#1B1B1E" # Black kind of 
        self.error_color = "#D64045" # Littish Red
        
        self.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create layout
        self.create_header()
        self.create_dashboard_content()
        self.create_navigation()

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        # Left side - Title and Welcome message
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="Admin Dashboard",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        # Get admin name from database if available
        admin_name = "Admin"
        if hasattr(self.controller, 'user_id') and self.controller.user_id:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM users WHERE id = %s", (self.controller.user_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    admin_name = result[0]
            except Exception:
                pass  # Use default name if error occurs
            finally:
                conn.close()

        welcome_msg = tk.Label(
            title_frame,
            text=f"Welcome back, {admin_name}",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg=self.accent_color
        )
        welcome_msg.pack(anchor="w")

        # Right side buttons frame
        buttons_frame = tk.Frame(header_frame, bg=self.bg_color)
        buttons_frame.pack(side="right")
        
        # Refresh button
        refresh_btn = tk.Button(
            buttons_frame,
            text="Refresh Dashboard",
            font=("Helvetica", 11),
            bg=self.accent_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.refresh_dashboard,
            padx=10,
            pady=5
        )
        refresh_btn.pack(side="left", padx=(0, 10), pady=10)

        # Logout button
        self.create_logout_button(buttons_frame)

    def create_dashboard_content(self):
        # Main content area with neumorphic effect
        content_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        content_frame.pack(fill="both", expand=True, pady=20)

        # Analytics section
        analytics_title = tk.Label(
            content_frame,
            text="Platform Analytics",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.primary_color
        )
        analytics_title.pack(pady=(20, 10), padx=20, anchor="w")

        # Create analytics cards container
        cards_frame = tk.Frame(content_frame, bg=self.card_bg)
        cards_frame.pack(fill="x", padx=20, pady=10)

        # Fetch actual data from database
        stats = self.get_platform_statistics()
        
        # Analytics cards with actual data
        self.create_analytics_card(cards_frame, "Total Users", str(stats['total_users']))
        self.create_analytics_card(cards_frame, "Active Sessions", str(stats['active_sessions']))
        self.create_analytics_card(cards_frame, "Questions", str(stats['total_questions']))
        self.create_analytics_card(cards_frame, "Resources", str(stats['total_resources']))

        # User distribution chart
        chart_frame = tk.Frame(content_frame, bg=self.card_bg)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.plot_user_distribution(chart_frame)
    
    def get_platform_statistics(self):
        """Fetch actual statistics from the database"""
        stats = {
            'total_users': 0,
            'active_sessions': 0,
            'total_questions': 0,
            'total_resources': 0
        }
        
        conn = None
        cursor = None
        
        try:
            conn = get_db_connection()  # Get fresh connection
            cursor = conn.cursor()
            
            # Get total users
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()
            stats['total_users'] = result[0] if result else 0
            
            # Get active sessions
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'Active'")
            result = cursor.fetchone()
            stats['active_sessions'] = result[0] if result else 0
            
            # Get total questions
            cursor.execute("SELECT COUNT(*) FROM questions")
            result = cursor.fetchone()
            stats['total_questions'] = result[0] if result else 0
            
            # Get total resources
            cursor.execute("SELECT COUNT(*) FROM resources")
            result = cursor.fetchone()
            stats['total_resources'] = result[0] if result else 0
            
        except Exception as e:
            self.show_error_message(f"Error fetching statistics: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
        return stats

    def create_navigation(self):
        nav_frame = tk.Frame(self.main_container, bg=self.bg_color)
        nav_frame.pack(fill="x", pady=(20, 0))

        buttons = [
            ("Manage Users", "UserManagementPage"),
            ("Moderate Questions", "QuestionModerationPage"),
            ("Monitor Sessions", "SessionMonitoringPage"),
            ("Manage Leaderboard", "LeaderboardPage"),
            ("Manage Resources", "ResourceManagementPage")
        ]

        for text, page in buttons:
            self.create_nav_button(nav_frame, text, lambda p=page: self.controller.show_frame(p))

    def create_analytics_card(self, parent, title, value):
        card = tk.Frame(
            parent,
            bg=self.card_bg,
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        card.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(
            card,
            text=title,
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(pady=(15, 5))

        tk.Label(
            card,
            text=value,
            font=("Helvetica", 24, "bold"),
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(pady=(0, 15))

    def create_nav_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=command,
            padx=15,
            pady=10
        )
        button.pack(side="left", padx=5)

        # Hover effects
        button.bind("<Enter>", lambda e: button.configure(
            bg=self.accent_color,
            fg="white"
        ))
        button.bind("<Leave>", lambda e: button.configure(
            bg=self.card_bg,
            fg=self.text_color
        ))

    def create_logout_button(self, parent):
        logout_btn = tk.Button(
            parent,
            text="Logout",
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.logout,  # Call our proper logout method
            padx=20,
            pady=8
        )
        logout_btn.pack(side="right")
    
    def on_show_frame(self):
        """Called when this frame is shown"""
        self.refresh_dashboard()
        
    def logout(self):
        """Handle logout with proper cleanup"""
        if messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?"):
            # Clear any stored user information
            if hasattr(self.controller, 'user_id'):
                self.controller.user_id = None
            if hasattr(self.controller, 'username'): 
                self.controller.username = None
            
            # Redirect to login page
            self.controller.show_frame("LoginPage")

    def plot_user_distribution(self, parent_frame):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            rows = cursor.fetchall()
            
            if not rows:
                # Handle the case when no data is returned
                empty_frame = tk.Frame(parent_frame, bg=self.card_bg)
                empty_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                tk.Label(
                    empty_frame,
                    text="No user data available",
                    font=("Helvetica", 12, "italic"),
                    bg=self.card_bg,
                    fg=self.text_color
                ).pack(pady=50)
                return
            
            roles, counts = zip(*rows)

            # Create figure with transparent background
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')

            # Custom colors matching the theme
            colors = [self.primary_color, self.accent_color, '#4CAF50']
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                counts,
                labels=roles,
                autopct=lambda pct: f'{int(pct * sum(counts) / 100)}\n({pct:.1f}%)',
                startangle=90,
                colors=colors[:len(roles)],  # Only use as many colors as we have roles
                wedgeprops={
                    'width': 0.7,
                    'edgecolor': 'white',
                    'linewidth': 2,
                    'antialiased': True
                }
            )

            # Customize text appearance
            plt.setp(autotexts, size=9, weight="bold", color="white")
            plt.setp(texts, size=10, color=self.text_color)

            # Add title with custom styling
            ax.set_title(
                "User Distribution by Role",
                pad=20,
                fontsize=14,
                color=self.text_color,
                fontweight='bold'
            )

            # Create legend with custom styling
            legend = ax.legend(
                wedges,
                roles,
                title="Roles",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1)
            )
            plt.setp(legend.get_title(), color=self.text_color)
            
            # Create canvas and embed in frame
            chart_frame = tk.Frame(parent_frame, bg=self.card_bg)
            chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            self.show_error_message(f"Error loading analytics: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def show_error_message(self, message):
        error_frame = tk.Frame(self.main_container, bg=self.error_color)
        error_frame.pack(fill="x", padx=20, pady=10)
        
        error_label = tk.Label(
            error_frame,
            text=message,
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            padx=10,
            pady=5
        )
        error_label.pack()
        
        # Auto-hide error message after 3 seconds
        self.after(3000, error_frame.destroy)

    def refresh_dashboard(self):
        """Method to refresh dashboard data"""
        # Clear existing content
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Recreate dashboard content
        self.create_header()
        self.create_dashboard_content()
        self.create_navigation()

    def create_stat_card(self, parent, title, value, icon=None):
        """Create a statistical card with icon"""
        card = tk.Frame(
            parent,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        card.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Add hover effect
        card.bind("<Enter>", lambda e: self.card_hover(card, True))
        card.bind("<Leave>", lambda e: self.card_hover(card, False))

        # Icon (if provided)
        if icon:
            icon_label = tk.Label(
                card,
                image=icon,
                bg=self.card_bg
            )
            icon_label.image = icon
            icon_label.pack(pady=(15, 5))

        # Title
        tk.Label(
            card,
            text=title,
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(pady=(15, 5))

        # Value
        tk.Label(
            card,
            text=value,
            font=("Helvetica", 24, "bold"),
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(pady=(0, 15))

    def card_hover(self, card, entering):
        """Handle card hover effect"""
        if entering:
            card.configure(
                highlightbackground=self.accent_color,
                highlightthickness=2
            )
        else:
            card.configure(
                highlightbackground="#D1D9E6",
                highlightthickness=1
            )

    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = tk.Frame(parent, bg=self.card_bg)
        actions_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=("Helvetica", 14, "bold"),
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", pady=(0, 10))

        actions = [
            ("Add New User", "UserManagementPage"),
            ("Review Questions", "QuestionModerationPage"),
            ("View Reports", "ReportsPage")
        ]

        for text, page in actions:
            self.create_quick_action_button(actions_frame, text, lambda p=page: self.controller.show_frame(p))

    def create_quick_action_button(self, parent, text, command):
        """Create styled quick action button"""
        button = tk.Button(
            parent,
            text=text,
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=command,
            padx=15,
            pady=8
        )
        button.pack(side="left", padx=5)

        # Hover effects
        button.bind("<Enter>", lambda e: button.configure(
            bg=self.accent_color,
            fg="white"
        ))
        button.bind("<Leave>", lambda e: button.configure(
            bg=self.bg_color,
            fg=self.text_color
        ))