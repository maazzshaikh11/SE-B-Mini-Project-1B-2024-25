import tkinter as tk
from tkinter import font, messagebox, ttk
from database import get_db_connection

class SessionMonitoringPage(tk.Frame):
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
        self.success_color = "#4CAF50"
        
        self.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create layout
        self.create_header()
        self.create_session_frame()
        self.create_action_buttons()
        
        # Store session IDs for reference
        self.session_ids = []

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="Session Monitoring",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Monitor and manage active and reported sessions",
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

    def create_session_frame(self):
        session_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        session_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Filter dropdown
        filter_frame = tk.Frame(session_frame, bg=self.card_bg, padx=20, pady=15)
        filter_frame.pack(fill="x")

        self.filter_var = tk.StringVar(value="Active Sessions")
        filters = ["Active Sessions", "Reported Sessions", "All Sessions"]
        
        filter_menu = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=filters,
            state="readonly",
            font=("Helvetica", 11),
            width=20
        )
        filter_menu.pack(side="left")
        filter_menu.bind("<<ComboboxSelected>>", self.load_sessions)
        
        # Refresh button
        refresh_btn = tk.Button(
            filter_frame,
            text="Refresh",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.load_sessions,
            padx=10,
            pady=2
        )
        refresh_btn.pack(side="right", padx=5)

        # Sessions listbox with frame for better control
        session_list_frame = tk.Frame(session_frame, bg=self.card_bg, padx=20)
        session_list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create scrollbar first
        scrollbar = ttk.Scrollbar(session_list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Create listbox
        self.sessions_listbox = tk.Listbox(
            session_list_frame,
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color,
            selectbackground=self.accent_color,
            selectforeground="white",
            relief="solid",
            bd=1,
            height=15,
            yscrollcommand=scrollbar.set
        )
        self.sessions_listbox.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbar to work with listbox
        scrollbar.config(command=self.sessions_listbox.yview)

        # Load initial data
        self.load_sessions()

    def create_action_buttons(self):
        buttons_frame = tk.Frame(self.main_container, bg=self.bg_color)
        buttons_frame.pack(fill="x", pady=(20, 0))

        # View details button
        view_btn = tk.Button(
            buttons_frame,
            text="View Details",
            font=("Helvetica", 11),
            bg=self.primary_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.view_session_details,
            padx=20,
            pady=8
        )
        view_btn.pack(side="left", padx=5)
        
        # Resolve button
        resolve_btn = tk.Button(
            buttons_frame,
            text="Resolve Issue",
            font=("Helvetica", 11),
            bg=self.success_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.resolve_session_issue,
            padx=20,
            pady=8
        )
        resolve_btn.pack(side="left", padx=5)

        # Cancel button
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel Session",
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.cancel_session,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side="left", padx=5)

    def load_sessions(self, *args):
        """Load sessions into the listbox based on the selected filter."""
        self.sessions_listbox.delete(0, tk.END)
        self.session_ids = []  # Clear stored session IDs
        
        filter_type = self.filter_var.get()
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Base query with joins to get user names
            base_query = """
                SELECT s.id, s.date, s.time, s.status,
                       j.name as junior_name, s.junior_id,
                       sen.name as senior_name, s.senior_id
                FROM sessions s
                JOIN users j ON s.junior_id = j.id
                JOIN users sen ON s.senior_id = sen.id
            """
            
            where_clause = ""
            if filter_type == "Active Sessions":
                where_clause = " WHERE s.status = 'Active'"
            elif filter_type == "Reported Sessions":
                where_clause = " WHERE s.status = 'Reported'"
            
            order_clause = " ORDER BY s.date DESC, s.time DESC"
            
            # Complete query
            query = base_query + where_clause + order_clause
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                session_id = row[0]
                date = row[1]
                time = row[2]
                status = row[3]
                junior_name = row[4]
                junior_id = row[5]
                senior_name = row[6]
                senior_id = row[7]
                
                # Store the session ID for reference
                self.session_ids.append(session_id)
                
                # Format display string
                display_text = f"Date: {date} | Time: {time} | Status: {status}"
                display_text += f"\nJunior: {junior_name} (ID: {junior_id}) | Senior: {senior_name} (ID: {senior_id})"
                
                # Insert into listbox
                self.sessions_listbox.insert(tk.END, display_text)
                
                # Add color coding based on status
                index = len(self.session_ids) - 1
                if status == "Reported":
                    self.sessions_listbox.itemconfig(index, {'fg': self.error_color})
                elif status == "Active":
                    self.sessions_listbox.itemconfig(index, {'fg': self.success_color})
            
            if not rows:
                self.sessions_listbox.insert(tk.END, "No sessions found")
                self.sessions_listbox.itemconfig(0, {'fg': 'gray'})

        except Exception as e:
            self.show_error_message(f"An error occurred while loading sessions: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def view_session_details(self):
        """View detailed information about the selected session."""
        # Get selected session
        selection_index = self.sessions_listbox.curselection()
        if not selection_index:
            self.show_error_message("Please select a session to view.")
            return
            
        index = selection_index[0]
        if index >= len(self.session_ids) or self.sessions_listbox.get(index) == "No sessions found":
            return
        
        session_id = self.session_ids[index]
        
        # Create details window
        details_window = tk.Toplevel(self)
        details_window.title("Session Details")
        details_window.geometry("600x400")
        details_window.configure(bg=self.bg_color)
        details_window.grab_set()  # Make window modal
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get session details with user information
            cursor.execute("""
                SELECT s.id, s.date, s.time, s.status,
                       j.name as junior_name, j.email as junior_email, j.department as junior_dept, j.year as junior_year,
                       sen.name as senior_name, sen.email as senior_email, sen.expertise as senior_expertise
                FROM sessions s
                JOIN users j ON s.junior_id = j.id
                JOIN users sen ON s.senior_id = sen.id
                WHERE s.id = %s
            """, (session_id,))
            
            session_data = cursor.fetchone()
            
            if session_data:
                # Unpack data
                session_id, date, time, status = session_data[0:4]
                junior_name, junior_email, junior_dept, junior_year = session_data[4:8]
                senior_name, senior_email, senior_expertise = session_data[8:11]
                
                # Create details UI
                # Header
                header = tk.Frame(details_window, bg=self.primary_color, padx=20, pady=10)
                header.pack(fill="x")
                
                tk.Label(
                    header,
                    text=f"Session Details - {date} at {time}",
                    font=("Helvetica", 16, "bold"),
                    bg=self.primary_color,
                    fg="white"
                ).pack(anchor="w")
                
                tk.Label(
                    header,
                    text=f"Status: {status}",
                    font=("Helvetica", 12),
                    bg=self.primary_color,
                    fg="white"
                ).pack(anchor="w")
                
                # Content frame
                content = tk.Frame(details_window, bg=self.card_bg, padx=20, pady=20)
                content.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Junior details
                tk.Label(
                    content,
                    text="Junior Details",
                    font=("Helvetica", 14, "bold"),
                    bg=self.card_bg,
                    fg=self.primary_color
                ).pack(anchor="w", pady=(0, 5))
                
                junior_info = f"Name: {junior_name}\nEmail: {junior_email}"
                if junior_dept:
                    junior_info += f"\nDepartment: {junior_dept}"
                if junior_year:
                    junior_info += f"\nYear: {junior_year}"
                
                tk.Label(
                    content,
                    text=junior_info,
                    font=("Helvetica", 12),
                    bg=self.card_bg,
                    fg=self.text_color,
                    justify="left"
                ).pack(anchor="w", pady=(0, 15))
                
                # Senior details
                tk.Label(
                    content,
                    text="Senior Details",
                    font=("Helvetica", 14, "bold"),
                    bg=self.card_bg,
                    fg=self.primary_color
                ).pack(anchor="w", pady=(0, 5))
                
                senior_info = f"Name: {senior_name}\nEmail: {senior_email}"
                if senior_expertise:
                    senior_info += f"\nExpertise: {senior_expertise}"
                
                tk.Label(
                    content,
                    text=senior_info,
                    font=("Helvetica", 12),
                    bg=self.card_bg,
                    fg=self.text_color,
                    justify="left"
                ).pack(anchor="w")
                
                # Button frame
                button_frame = tk.Frame(details_window, bg=self.bg_color, padx=20, pady=10)
                button_frame.pack(fill="x")
                
                if status == "Reported":
                    resolve_btn = tk.Button(
                        button_frame,
                        text="Resolve Issue",
                        font=("Helvetica", 11),
                        bg=self.success_color,
                        fg="white",
                        relief="flat",
                        bd=0,
                        cursor="hand2",
                        command=lambda: self.resolve_from_details(session_id, details_window)
                    )
                    resolve_btn.pack(side="left", padx=5)
                
                cancel_btn = tk.Button(
                    button_frame,
                    text="Cancel Session",
                    font=("Helvetica", 11),
                    bg=self.error_color,
                    fg="white",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda: self.cancel_from_details(session_id, details_window)
                )
                cancel_btn.pack(side="left", padx=5)
                
                close_btn = tk.Button(
                    button_frame,
                    text="Close",
                    font=("Helvetica", 11),
                    bg=self.card_bg,
                    fg=self.text_color,
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=details_window.destroy
                )
                close_btn.pack(side="right")
            else:
                tk.Label(
                    details_window,
                    text="Session details not found.",
                    font=("Helvetica", 14),
                    bg=self.bg_color,
                    fg=self.error_color,
                    pady=50
                ).pack()
                
        except Exception as e:
            tk.Label(
                details_window,
                text=f"Error loading session details: {e}",
                font=("Helvetica", 12),
                bg=self.bg_color,
                fg=self.error_color,
                pady=50
            ).pack()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def resolve_from_details(self, session_id, details_window):
        """Resolve a session issue from the details window."""
        if self.resolve_session_issue_by_id(session_id):
            details_window.destroy()
    
    def cancel_from_details(self, session_id, details_window):
        """Cancel a session from the details window."""
        if self.cancel_session_by_id(session_id):
            details_window.destroy()

    def resolve_session_issue(self):
        """Resolve a reported session issue."""
        selection = self.sessions_listbox.curselection()
        if not selection:
            self.show_error_message("Please select a session to resolve.")
            return
            
        index = selection[0]
        if index >= len(self.session_ids) or self.sessions_listbox.get(index) == "No sessions found":
            return
        
        session_id = self.session_ids[index]
        self.resolve_session_issue_by_id(session_id)
    
    def resolve_session_issue_by_id(self, session_id):
        """Resolve a session issue by session ID."""
        if messagebox.askyesno("Confirm Resolution", "Are you sure you want to resolve this issue?"):
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # First, get the session details to notify users
                cursor.execute("""
                    SELECT junior_id, senior_id, date, time 
                    FROM sessions 
                    WHERE id = %s
                """, (session_id,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    self.show_error_message("Session not found.")
                    return False
                
                junior_id, senior_id, date, time = session_data
                
                # Update the session status
                cursor.execute(
                    "UPDATE sessions SET status = 'Completed' WHERE id = %s", 
                    (session_id,)
                )
                
                # Create notification for both junior and senior
                message = f"Your reported session on {date} at {time} has been resolved by an admin."
                
                # Notification for junior
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (junior_id, message)
                )
                
                # Notification for senior
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (senior_id, message)
                )
                
                conn.commit()
                self.show_success_message("Session issue resolved successfully!")
                self.load_sessions()
                return True
                
            except Exception as e:
                if conn:
                    conn.rollback()
                self.show_error_message(f"An error occurred: {e}")
                return False
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        return False

    def cancel_session(self):
        """Cancel a session."""
        selection = self.sessions_listbox.curselection()
        if not selection:
            self.show_error_message("Please select a session to cancel.")
            return
            
        index = selection[0]
        if index >= len(self.session_ids) or self.sessions_listbox.get(index) == "No sessions found":
            return
        
        session_id = self.session_ids[index]
        self.cancel_session_by_id(session_id)
    
    def cancel_session_by_id(self, session_id):
        """Cancel a session by session ID."""
        # Show confirmation dialog
        if messagebox.askyesno(
            "Confirm Cancellation",
            "Are you sure you want to cancel this session? This action cannot be undone."
        ):
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # First, get the session details to notify users
                cursor.execute("""
                    SELECT junior_id, senior_id, date, time 
                    FROM sessions 
                    WHERE id = %s
                """, (session_id,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    self.show_error_message("Session not found.")
                    return False
                
                junior_id, senior_id, date, time = session_data
                
                # Create notification for both junior and senior before deleting
                message = f"Your session scheduled for {date} at {time} has been cancelled by an admin."
                
                # Notification for junior
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (junior_id, message)
                )
                
                # Notification for senior
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, FALSE)",
                    (senior_id, message)
                )
                
                # Now delete the session
                cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
                
                conn.commit()
                self.show_success_message("Session canceled successfully!")
                self.load_sessions()
                return True
                
            except Exception as e:
                if conn:
                    conn.rollback()
                self.show_error_message(f"An error occurred: {e}")
                return False
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        return False

    def show_error_message(self, message):
        """Show error message with animation"""
        if hasattr(self, 'message_label') and self.message_label.winfo_exists():
            self.message_label.destroy()

        self.message_label = tk.Label(
            self.main_container,
            text=message,
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            padx=20,
            pady=10
        )
        self.message_label.pack(fill="x", pady=(0, 10))
        
        # Auto-hide after 3 seconds
        self.after(3000, self.hide_message)

    def show_success_message(self, message):
        """Show success message with animation"""
        if hasattr(self, 'message_label') and self.message_label.winfo_exists():
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
        if hasattr(self, 'message_label') and self.message_label.winfo_exists():
            self.message_label.destroy()
    
    def on_show_frame(self):
        """Called when this frame is shown"""
        self.load_sessions()