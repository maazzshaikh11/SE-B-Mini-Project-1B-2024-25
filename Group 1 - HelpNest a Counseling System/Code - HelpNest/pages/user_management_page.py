import tkinter as tk
from tkinter import font, messagebox, ttk
from database import get_db_connection

class UserManagementPage(tk.Frame):
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
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create layout
        self.create_header()
        self.create_search_section()
        self.create_users_table()
        self.create_action_buttons()

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="User Management",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Manage and monitor user accounts",
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

    def create_search_section(self):
        search_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        search_frame.pack(fill="x", pady=(0, 20))

        # Search container
        search_container = tk.Frame(search_frame, bg=self.card_bg, padx=20, pady=15)
        search_container.pack(fill="x")

        # Search entry
        search_entry_frame = tk.Frame(search_container, bg=self.card_bg)
        search_entry_frame.pack(side="left", fill="x", expand=True)

        self.search_entry = tk.Entry(
            search_entry_frame,
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            bd=0
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.insert(0, "Search users...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)

        # Search border
        tk.Frame(
            search_entry_frame,
            height=2,
            bg=self.accent_color
        ).pack(fill="x", pady=(2, 0))

        # Filter dropdown
        self.filter_var = tk.StringVar(value="All Users")
        filters = ["All Users", "Active", "Banned", "Top Mentors"]
        
        filter_menu = ttk.Combobox(
            search_container,
            textvariable=self.filter_var,
            values=filters,
            state="readonly",
            font=("Helvetica", 11),
            width=15
        )
        filter_menu.pack(side="right", padx=(20, 0))
        filter_menu.bind("<<ComboboxSelected>>", self.load_users)
        
        # Refresh button
        refresh_btn = tk.Button(
            search_container,
            text="Refresh",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.load_users,
            padx=10,
            pady=2
        )
        refresh_btn.pack(side="right", padx=5)

    def create_users_table(self):
        # Create table frame
        table_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        table_frame.pack(fill="both", expand=True)

        # Create Treeview
        columns = ("ID", "Name", "Email", "Role", "Status")
        self.users_tree = ttk.Treeview(
            table_frame,
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
            self.users_tree.heading(col, text=col, anchor="w")
            self.users_tree.column(col, anchor="w", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.users_tree.yview
        )
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.users_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Load initial data
        self.load_users()

    def create_action_buttons(self):
        buttons_frame = tk.Frame(self.main_container, bg=self.bg_color)
        buttons_frame.pack(fill="x", pady=(20, 0))

        # Ban button
        ban_btn = tk.Button(
            buttons_frame,
            text="Ban User",
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.ban_user,
            padx=20,
            pady=8
        )
        ban_btn.pack(side="left", padx=5)

        # Unban button
        unban_btn = tk.Button(
            buttons_frame,
            text="Unban User",
            font=("Helvetica", 11),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.unban_user,
            padx=20,
            pady=8
        )
        unban_btn.pack(side="left", padx=5)

    def on_search_focus_in(self, event):
        if self.search_entry.get() == "Search users...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.text_color)

    def on_search_focus_out(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search users...")
            self.search_entry.config(fg="gray")

    def load_users(self, *args):
        """Load users into the treeview based on the selected filter."""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        filter_type = self.filter_var.get()
        search_text = self.search_entry.get()
        if search_text == "Search users...":
            search_text = ""

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            params = [f"%{search_text}%", f"%{search_text}%"]
            
            if filter_type == "All Users":
                query = """
                    SELECT id, name, email, role, banned 
                    FROM users 
                    WHERE (name LIKE %s OR email LIKE %s)
                """
            elif filter_type == "Active":
                query = """
                    SELECT id, name, email, role, banned 
                    FROM users 
                    WHERE (name LIKE %s OR email LIKE %s) AND banned = 0
                """
            elif filter_type == "Banned":
                query = """
                    SELECT id, name, email, role, banned 
                    FROM users 
                    WHERE (name LIKE %s OR email LIKE %s) AND banned = 1
                """
            elif filter_type == "Top Mentors":
                query = """
                    SELECT u.id, u.name, u.email, u.role, u.banned
                    FROM users u
                    LEFT JOIN (
                        SELECT user_id, COUNT(*) as answer_count 
                        FROM answers 
                        GROUP BY user_id
                    ) a ON u.id = a.user_id
                    WHERE u.role = 'Senior' AND (u.name LIKE %s OR u.email LIKE %s)
                    ORDER BY a.answer_count DESC NULLS LAST
                    LIMIT 10
                """

            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                # Show empty state
                self.show_empty_state()
                return

            # Populate treeview
            for row in rows:
                user_id, name, email, role, banned = row
                status = "Banned" if banned else "Active"
                
                # Alternate row colors
                tags = ('banned',) if banned else ('active',)
                
                self.users_tree.insert(
                    "",
                    "end",
                    values=(user_id, name, email, role, status),
                    tags=tags
                )

            # Configure tag colors
            self.users_tree.tag_configure('banned', foreground=self.error_color)
            self.users_tree.tag_configure('active', foreground=self.text_color)

        except Exception as e:
            self.show_error_message(f"Error loading users: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def show_empty_state(self):
        """Show empty state message in the treeview"""
        self.users_tree.insert(
            "",
            "end",
            values=("No users found", "", "", "", ""),
            tags=('empty',)
        )
        self.users_tree.tag_configure('empty', foreground="gray")

    def show_error_message(self, message):
        """Show error message with animation"""
        if hasattr(self, 'error_label'):
            self.error_label.destroy()

        self.error_label = tk.Label(
            self.main_container,
            text=message,
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            padx=20,
            pady=10
        )
        self.error_label.pack(fill="x", pady=(0, 10))
        
        # Auto-hide after 3 seconds
        self.after(3000, self.hide_error_message)

    def hide_error_message(self):
        """Hide error message with animation"""
        if hasattr(self, 'error_label'):
            self.error_label.destroy()

    def ban_user(self):
        """Ban selected user with confirmation"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a user to ban")
            return

        user_data = self.users_tree.item(selected_item)['values']
        if user_data[4] == "Banned":
            self.show_error_message("User is already banned")
            return

        # Show confirmation dialog
        if messagebox.askyesno(
            "Confirm Ban",
            f"Are you sure you want to ban {user_data[1]}?"
        ):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("START TRANSACTION")
                cursor.execute(
                    "UPDATE users SET banned=1, ban_reason=%s WHERE id=%s",
                    ("Banned by administrator", user_data[0])
                )
                conn.commit()
                self.show_success_message(f"Successfully banned {user_data[1]}")
                self.load_users()
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.show_error_message(f"Error banning user: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def unban_user(self):
        """Unban selected user with confirmation"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a user to unban")
            return

        user_data = self.users_tree.item(selected_item)['values']
        if user_data[4] == "Active":
            self.show_error_message("User is not banned")
            return

        # Show confirmation dialog
        if messagebox.askyesno(
            "Confirm Unban",
            f"Are you sure you want to unban {user_data[1]}?"
        ):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("START TRANSACTION")
                cursor.execute(
                    "UPDATE users SET banned=0, ban_reason=NULL WHERE id=%s",
                    (user_data[0],)
                )
                conn.commit()
                self.show_success_message(f"Successfully unbanned {user_data[1]}")
                self.load_users()
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.show_error_message(f"Error unbanning user: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def show_success_message(self, message):
        """Show success message with animation"""
        if hasattr(self, 'success_label'):
            self.success_label.destroy()

        self.success_label = tk.Label(
            self.main_container,
            text=message,
            font=("Helvetica", 11),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.success_label.pack(fill="x", pady=(0, 10))
        
        # Auto-hide after 3 seconds
        self.after(3000, self.hide_success_message)

    def hide_success_message(self):
        """Hide success message with animation"""
        if hasattr(self, 'success_label'):
            self.success_label.destroy()