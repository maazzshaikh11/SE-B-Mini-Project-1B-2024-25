import tkinter as tk
from tkinter import font, messagebox, ttk
from database import get_db_connection

class LeaderboardManagementPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Professional Color Scheme
        self.bg_color = "#ECF0F3"
        self.card_bg = "#FFFFFF"
        self.primary_color = "#0A2463"
        self.accent_color = "#3E92CC"
        self.text_color = "#1B1B1E"
        self.success_color = "#4CAF50"
        
        self.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create layout
        self.create_header()
        self.create_leaderboard_frame()
        self.create_action_buttons()

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="Leaderboard Management",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Highlight top mentors and manage the leaderboard",
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
            command=lambda: self.controller.show_frame("AdminDashboardPage")
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

        # Top Mentors Label
        tk.Label(
            leaderboard_frame,
            text="Top Mentors",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.primary_color
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Top Mentors Treeview
        columns = ("ID", "Name", "Answers", "Rating")
        self.top_mentors_tree = ttk.Treeview(
            leaderboard_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Style the Treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=self.card_bg,
            foreground=self.text_color,
            fieldbackground=self.card_bg,
            rowheight=30
        )
        style.configure(
            "Treeview.Heading",
            background=self.bg_color,
            foreground=self.primary_color,
            relief="flat"
        )

        # Configure columns
        for col in columns:
            self.top_mentors_tree.heading(col, text=col, anchor="w")
            self.top_mentors_tree.column(col, anchor="w", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            leaderboard_frame,
            orient="vertical",
            command=self.top_mentors_tree.yview
        )
        self.top_mentors_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.top_mentors_tree.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20), padx=(0, 20))

        # Load initial data
        self.load_top_mentors()

    def create_action_buttons(self):
        buttons_frame = tk.Frame(self.main_container, bg=self.bg_color)
        buttons_frame.pack(fill="x", pady=(20, 0))

        # Highlight Mentor button
        highlight_btn = tk.Button(
            buttons_frame,
            text="Highlight Mentor",
            font=("Helvetica", 11),
            bg=self.success_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.highlight_mentor,
            padx=20,
            pady=8
        )
        highlight_btn.pack(side="left", padx=5)

    def load_top_mentors(self):
        """Load top mentors into the treeview."""
        # Clear existing items
        for item in self.top_mentors_tree.get_children():
            self.top_mentors_tree.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Fixed SQL query to handle NULL ratings and ensure proper grouping
            cursor.execute("""
                SELECT 
                    u.id, 
                    u.name, 
                    COUNT(a.id) AS answers_count, 
                    COALESCE(AVG(a.rating), 0) AS avg_rating
                FROM 
                    users u
                LEFT JOIN 
                    answers a ON u.id = a.user_id
                WHERE 
                    u.role = 'Senior'
                GROUP BY 
                    u.id, u.name
                ORDER BY 
                    avg_rating DESC, answers_count DESC
                LIMIT 10
            """)
            rows = cursor.fetchall()
            
            if not rows:
                self.top_mentors_tree.insert("", "end", values=("No top mentors found", "", "", ""))
                return
                
            for row in rows:
                user_id, name, answers_count, avg_rating = row
                # Format rating to show 1 decimal place
                formatted_rating = f"{float(avg_rating):.1f}" if avg_rating is not None else "N/A"
                self.top_mentors_tree.insert(
                    "",
                    "end",
                    values=(user_id, name, answers_count, formatted_rating)
                )

        except Exception as e:
            self.show_error_message(f"An error occurred while loading top mentors: {e}")
        finally:
            cursor.close()
            conn.close()

    def highlight_mentor(self):
        """Highlight a mentor on the leaderboard."""
        selected_item = self.top_mentors_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a mentor to highlight.")
            return

        user_data = self.top_mentors_tree.item(selected_item)['values']
        if user_data[0] == "No top mentors found":
            self.show_error_message("No valid mentor selected.")
            return
            
        user_id = user_data[0]

        # Show confirmation dialog
        if messagebox.askyesno(
            "Confirm Highlight",
            f"Are you sure you want to highlight mentor {user_data[1]}?"
        ):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Start transaction
                cursor.execute("START TRANSACTION")
                
                # First, reset featured status for all users
                cursor.execute("UPDATE users SET featured = 0")
                
                # Then, set featured for the selected mentor
                cursor.execute("UPDATE users SET featured = 1 WHERE id = %s", (user_id,))
                
                # Commit the transaction
                conn.commit()
                
                self.show_success_message(f"Successfully highlighted mentor {user_data[1]}")
                self.load_top_mentors()  # Refresh the list
            except Exception as e:
                # Rollback in case of error
                cursor.execute("ROLLBACK")
                self.show_error_message(f"An error occurred: {e}")
            finally:
                cursor.close()
                conn.close()

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

    def show_success_message(self, message):
        """Show success message with animation"""
        if hasattr(self, 'message_label'):
            self.message_label.destroy()

        self.message_label = tk.Label(
            self.main_container,
            text=message,
            font=("Helvetica", 11),
            bg=self.success_color,
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
        self.load_top_mentors()
        self.show_success_message("Leaderboard refreshed successfully")

    def on_close(self):
        """Method to be called when closing the page"""
        # Perform any cleanup or saving operations here
        pass