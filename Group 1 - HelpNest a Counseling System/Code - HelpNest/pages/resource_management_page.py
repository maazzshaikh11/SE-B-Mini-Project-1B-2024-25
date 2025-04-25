import tkinter as tk
from tkinter import font, messagebox, ttk
from database import get_db_connection

class ResourceManagementPage(tk.Frame):
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
        self.error_color = "#D64045"
        
        self.configure(bg=self.bg_color)
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create layout
        self.create_header()
        self.create_resource_frame()
        self.create_action_buttons()
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
            text="Resource Management",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Manage and approve learning resources",
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

    def create_resource_frame(self):
        resource_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        resource_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Filter dropdown
        filter_frame = tk.Frame(resource_frame, bg=self.card_bg, padx=20, pady=15)
        filter_frame.pack(fill="x")

        self.filter_var = tk.StringVar(value="Pending Resources")
        filters = ["Pending Resources", "Approved Resources", "Rejected Resources"]
        
        filter_menu = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=filters,
            state="readonly",
            font=("Helvetica", 11),
            width=20
        )
        filter_menu.pack(side="left")
        filter_menu.bind("<<ComboboxSelected>>", self.load_resources)

        # Resources Treeview
        columns = ("ID", "Title", "File Path", "Status")
        self.resources_tree = ttk.Treeview(
            resource_frame,
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
            self.resources_tree.heading(col, text=col, anchor="w")
            self.resources_tree.column(col, anchor="w", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            resource_frame,
            orient="vertical",
            command=self.resources_tree.yview
        )
        self.resources_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.resources_tree.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20), padx=(0, 20))

        # Load initial data
        self.load_resources()

    def create_action_buttons(self):
        buttons_frame = tk.Frame(self.main_container, bg=self.bg_color)
        buttons_frame.pack(fill="x", pady=(20, 0))

        # Approve button
        approve_btn = tk.Button(
            buttons_frame,
            text="Approve Resource",
            font=("Helvetica", 11),
            bg=self.success_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.approve_resource,
            padx=20,
            pady=8
        )
        approve_btn.pack(side="left", padx=5)

        # Reject button
        reject_btn = tk.Button(
            buttons_frame,
            text="Reject Resource",
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.reject_resource,
            padx=20,
            pady=8
        )
        reject_btn.pack(side="left", padx=5)

    def load_resources(self, *args):
        """Load resources into the treeview based on the selected filter."""
        # Clear existing items
        for item in self.resources_tree.get_children():
            self.resources_tree.delete(item)

        filter_type = self.filter_var.get()
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if filter_type == "Pending Resources":
                cursor.execute("SELECT id, title, file_path, 'Pending' as status FROM resources WHERE approved = 0")
            elif filter_type == "Approved Resources":
                cursor.execute("SELECT id, title, file_path, 'Approved' as status FROM resources WHERE approved = 1")
            elif filter_type == "Rejected Resources":
                cursor.execute("SELECT id, title, file_path, 'Rejected' as status FROM resources WHERE approved = -1")
            
            rows = cursor.fetchall()
            for row in rows:
                self.resources_tree.insert("", "end", values=row)

            if not rows:
                self.resources_tree.insert("", "end", values=("No resources found", "", "", ""))

        except Exception as e:
            self.show_error_message(f"An error occurred while loading resources: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def approve_resource(self):
        """Approve the selected resource."""
        selected_item = self.resources_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a resource to approve.")
            return

        resource_id = self.resources_tree.item(selected_item)['values'][0]
        
        # Show confirmation dialog
        if messagebox.askyesno("Confirm Approval", "Are you sure you want to approve this resource?"):
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Fix for the SQL parameterization - use %s instead of ? for MySQL
                cursor.execute("UPDATE resources SET approved = 1 WHERE id = %s", (resource_id,))
                
                # Get resource owner to notify them
                cursor.execute("""
                    SELECT r.user_id, r.title 
                    FROM resources r
                    WHERE r.id = %s
                """, (resource_id,))
                result = cursor.fetchone()
                
                if result:
                    user_id, title = result
                    # Create notification for the user
                    cursor.execute("""
                        INSERT INTO notifications (user_id, message, is_read) 
                        VALUES (%s, %s, FALSE)
                    """, (user_id, f"Your resource '{title}' has been approved."))
                
                conn.commit()
                self.show_success_message("Resource approved successfully!")
                self.load_resources()
                
            except Exception as e:
                if conn:
                    conn.rollback()
                self.show_error_message(f"An error occurred: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def reject_resource(self):
        """Reject the selected resource."""
        selected_item = self.resources_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a resource to reject.")
            return

        resource_id = self.resources_tree.item(selected_item)['values'][0]
        
        # Show confirmation dialog
        if messagebox.askyesno("Confirm Rejection", "Are you sure you want to reject this resource?"):
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Fix for the SQL parameterization - use %s instead of ? for MySQL
                cursor.execute("UPDATE resources SET approved = -1 WHERE id = %s", (resource_id,))
                
                # Get resource owner to notify them
                cursor.execute("""
                    SELECT r.user_id, r.title 
                    FROM resources r
                    WHERE r.id = %s
                """, (resource_id,))
                result = cursor.fetchone()
                
                if result:
                    user_id, title = result
                    # Create notification for the user
                    cursor.execute("""
                        INSERT INTO notifications (user_id, message, is_read) 
                        VALUES (%s, %s, FALSE)
                    """, (user_id, f"Your resource '{title}' has been rejected."))
                
                conn.commit()
                self.show_success_message("Resource rejected successfully!")
                self.load_resources()
                
            except Exception as e:
                if conn:
                    conn.rollback()
                self.show_error_message(f"An error occurred: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

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

    def on_resource_select(self, event):
        """Handle resource selection event"""
        selected_item = self.resources_tree.selection()
        if selected_item:
            resource_data = self.resources_tree.item(selected_item)['values']
            # You can add more functionality here, like showing details in a separate panel

    def refresh_resources(self):
        """Refresh the resources list"""
        self.load_resources()
        self.show_success_message("Resources refreshed successfully")

    def setup_bindings(self):
        """Setup bindings for the treeview"""
        self.resources_tree.bind("<<TreeviewSelect>>", self.on_resource_select)

    def create_refresh_button(self):
        """Create a refresh button for the resources"""
        refresh_btn = tk.Button(
            self.main_container,
            text="Refresh Resources",
            font=("Helvetica", 11),
            bg=self.accent_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.refresh_resources,
            padx=20,
            pady=8
        )
        refresh_btn.pack(pady=(0, 20))

    def on_close(self):
        """Method to be called when closing the page"""
        # Perform any cleanup or saving operations here
        pass
        
    def on_show_frame(self):
        """Called when this frame is shown"""
        self.load_resources()