import tkinter as tk
from tkinter import font, messagebox, ttk
from PIL import Image, ImageTk
from database import get_db_connection

class LeaderboardPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Professional Color Scheme
        self.bg_color = "#ECF0F3"
        self.card_bg = "#FFFFFF"
        self.primary_color = "#0A2463"
        self.accent_color = "#3E92CC"
        self.text_color = "#1B1B1E"
        
        self.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create layout
        self.create_header()
        self.create_leaderboard_frame()
        self.create_refresh_button()
        self.setup_bindings()

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="Leaderboard",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Top performing mentors",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg=self.accent_color
        )
        subtitle.pack(anchor="w")

        # Back button
        back_btn = tk.Button(
            header_frame,
            text="← Back to Dashboard",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.go_back_to_dashboard
        )
        back_btn.pack(side="right", pady=10)

    def create_leaderboard_frame(self):
        leaderboard_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        leaderboard_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Leaderboard Treeview
        columns = ("Rank", "Name", "Questions Answered", "Average Rating")
        self.leaderboard_tree = ttk.Treeview(
            leaderboard_frame,
            columns=columns,
            show="headings",
            selectmode="none"
        )

        # Style the Treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=self.card_bg,
            foreground=self.text_color,
            fieldbackground=self.card_bg,
            rowheight=40
        )
        style.configure(
            "Treeview.Heading",
            background=self.bg_color,
            foreground=self.primary_color,
            relief="flat",
            font=("Helvetica", 12, "bold")
        )

        # Configure columns
        self.leaderboard_tree.heading("Rank", text="Rank", anchor="center")
        self.leaderboard_tree.column("Rank", anchor="center", width=50)
        
        for col in columns[1:]:
            self.leaderboard_tree.heading(col, text=col, anchor="w")
            self.leaderboard_tree.column(col, anchor="w", width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            leaderboard_frame,
            orient="vertical",
            command=self.leaderboard_tree.yview
        )
        self.leaderboard_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.leaderboard_tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20, padx=(0, 20))

        # Load initial data
        self.load_leaderboard()

    def load_leaderboard(self):
        """Load leaderboard data into the treeview from the database."""
        # Clear existing items
        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Improved query with proper HAVING clause to filter out users with no answers
            # Also adding role filter to only show Senior mentors
            cursor.execute("""
                SELECT 
                    u.id, 
                    u.name, 
                    COUNT(a.id) AS answers_count, 
                    COALESCE(AVG(a.rating), 0) AS avg_rating,
                    u.featured
                FROM 
                    users u
                LEFT JOIN 
                    answers a ON u.id = a.user_id
                WHERE 
                    u.role = 'Senior'
                GROUP BY 
                    u.id, u.name, u.featured
                HAVING 
                    answers_count > 0
                ORDER BY 
                    u.featured DESC,
                    avg_rating DESC, 
                    answers_count DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()

            if not rows:
                self.leaderboard_tree.insert("", "end", values=("--", "No data available", "", ""), tags=('empty',))
                self.leaderboard_tree.tag_configure('empty', foreground='gray')
                return

            for rank, row in enumerate(rows, start=1):
                user_id, name, answers_count, avg_rating, featured = row
                
                # Format the rating with 2 decimal places
                formatted_rating = f"{float(avg_rating):.2f}" if avg_rating is not None else "N/A"
                
                # Determine tag based on rank and featured status
                if featured:
                    tag = 'featured'
                elif rank % 2 == 0:
                    tag = 'even'
                else:
                    tag = 'odd'
                    
                self.leaderboard_tree.insert(
                    "",
                    "end",
                    values=(rank, name, answers_count, formatted_rating),
                    tags=(tag,)
                )

            # Configure tag colors
            self.leaderboard_tree.tag_configure('odd', background='#f0f0f0')
            self.leaderboard_tree.tag_configure('even', background=self.card_bg)
            self.leaderboard_tree.tag_configure('featured', background='#FFF9C4')  # Light yellow background for featured mentors

        except Exception as e:
            self.show_error_message(f"An error occurred while loading the leaderboard: {e}")
        finally:
            cursor.close()
            conn.close()

    def go_back_to_dashboard(self):
        """Navigate back to the appropriate dashboard based on the user's role."""
        if not hasattr(self.controller, "role") or not self.controller.role:
            self.show_error_message("User role is not set.")
            return

        dashboard_pages = {
            "Junior": "JuniorDashboardPage",
            "Senior": "SeniorDashboardPage",
            "Admin": "AdminDashboardPage"
        }

        if self.controller.role in dashboard_pages:
            self.controller.show_frame(dashboard_pages[self.controller.role])
        else:
            self.show_error_message(f"Invalid role: {self.controller.role}")

    def show_error_message(self, message):
        """Show error message with animation"""
        if hasattr(self, 'message_label'):
            self.message_label.destroy()

        self.message_label = tk.Label(
            self.main_container,
            text=message,
            font=("Helvetica", 11),
            bg="#D64045",
            fg="white",
            padx=20,
            pady=10
        )
        self.message_label.pack(fill="x", pady=(0, 10))
        
        # Auto-hide after 3 seconds
        self.after(3000, self.hide_message)

    def hide_message(self):
        """Hide message with animation"""
        if hasattr(self, 'message_label'):
            self.message_label.destroy()

    def refresh_leaderboard(self):
        """Refresh the leaderboard data"""
        self.load_leaderboard()
        self.show_success_message("Leaderboard refreshed successfully")

    def show_success_message(self, message):
        """Show success message with animation"""
        if hasattr(self, 'message_label'):
            self.message_label.destroy()

        self.message_label = tk.Label(
            self.main_container,
            text=message,
            font=("Helvetica", 11),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.message_label.pack(fill="x", pady=(0, 10))
        
        # Auto-hide after 3 seconds
        self.after(3000, self.hide_message)

    def on_enter(self, event):
        """Change cursor to hand when hovering over a row"""
        self.leaderboard_tree.config(cursor="hand2")

    def on_leave(self, event):
        """Change cursor back to default when leaving a row"""
        self.leaderboard_tree.config(cursor="")

    def show_mentor_details(self, event):
        """Show details of the selected mentor"""
        region = self.leaderboard_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.leaderboard_tree.identify_row(event.y)
            column = self.leaderboard_tree.identify_column(event.x)
            values = self.leaderboard_tree.item(item, "values")
            if values and values[0] != "--":  # Don't show details for the empty state
                mentor_name = values[1]
                messagebox.showinfo("Mentor Details", f"Details for {mentor_name}\n\nRank: {values[0]}\nQuestions Answered: {values[2]}\nAverage Rating: {values[3]}")

    def setup_bindings(self):
        """Setup bindings for the treeview"""
        self.leaderboard_tree.bind("<Motion>", self.on_enter)
        self.leaderboard_tree.bind("<Leave>", self.on_leave)
        self.leaderboard_tree.bind("<ButtonRelease-1>", self.show_mentor_details)

    def create_refresh_button(self):
        """Create a refresh button for the leaderboard"""
        refresh_btn = tk.Button(
            self.main_container,
            text="Refresh Leaderboard",
            font=("Helvetica", 11),
            bg=self.accent_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.refresh_leaderboard,
            padx=20,
            pady=8
        )
        refresh_btn.pack(pady=(0, 20))

    def on_close(self):
        """Method to be called when closing the page"""
        # Perform any cleanup or saving operations here
        pass