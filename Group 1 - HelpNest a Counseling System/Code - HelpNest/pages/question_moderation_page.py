import tkinter as tk
from tkinter import font, messagebox, ttk
from database import get_db_connection

class QuestionModerationPage(tk.Frame):
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
        self.create_filter_section()
        self.create_questions_table()
        self.create_action_buttons()

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="Question Moderation",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            text="Review and moderate community questions",
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

    def create_filter_section(self):
        filter_frame = tk.Frame(
            self.main_container,
            bg=self.card_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#D1D9E6",
            highlightcolor=self.accent_color
        )
        filter_frame.pack(fill="x", pady=(0, 20))

        # Filter container
        filter_container = tk.Frame(filter_frame, bg=self.card_bg, padx=20, pady=15)
        filter_container.pack(fill="x")

        # Stats labels
        self.pending_count = tk.Label(
            filter_container,
            text="Pending: 0",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.pending_count.pack(side="left", padx=10)

        self.reported_count = tk.Label(
            filter_container,
            text="Reported: 0",
            font=("Helvetica", 11),
            bg=self.card_bg,
            fg=self.error_color
        )
        self.reported_count.pack(side="left", padx=10)

        # Filter dropdown
        self.filter_var = tk.StringVar(value="Pending Questions")
        filters = ["Pending Questions", "Reported Questions"]
        
        filter_menu = ttk.Combobox(
            filter_container,
            textvariable=self.filter_var,
            values=filters,
            state="readonly",
            font=("Helvetica", 11),
            width=20
        )
        filter_menu.pack(side="right")
        filter_menu.bind("<<ComboboxSelected>>", self.load_questions)
        
        # Add refresh button
        refresh_btn = tk.Button(
            filter_container,
            text="Refresh",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.refresh_data,
            padx=10,
            pady=2
        )
        refresh_btn.pack(side="right", padx=5)

    def create_questions_table(self):
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
        columns = ("ID", "Question", "Category", "Status", "Date")
        self.questions_tree = ttk.Treeview(
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
            rowheight=40
        )
        style.configure(
            "Treeview.Heading",
            background=self.bg_color,
            foreground=self.primary_color,
            relief="flat"
        )

        # Configure columns
        self.questions_tree.heading("ID", text="ID", anchor="w")
        self.questions_tree.heading("Question", text="Question", anchor="w")
        self.questions_tree.heading("Category", text="Category", anchor="w")
        self.questions_tree.heading("Status", text="Status", anchor="w")
        self.questions_tree.heading("Date", text="Date", anchor="w")

        self.questions_tree.column("ID", width=50)
        self.questions_tree.column("Question", width=400)
        self.questions_tree.column("Category", width=100)
        self.questions_tree.column("Status", width=100)
        self.questions_tree.column("Date", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.questions_tree.yview
        )
        self.questions_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.questions_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Bind double-click event to show question details
        self.questions_tree.bind("<Double-1>", self.show_question_details)

        # Load initial data
        self.load_questions()

    def create_action_buttons(self):
        buttons_frame = tk.Frame(self.main_container, bg=self.bg_color)
        buttons_frame.pack(fill="x", pady=(20, 0))

        # Approve button
        approve_btn = tk.Button(
            buttons_frame,
            text="✓ Approve",
            font=("Helvetica", 11),
            bg=self.success_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.approve_question,
            padx=20,
            pady=8
        )
        approve_btn.pack(side="left", padx=5)

        # Reject button
        reject_btn = tk.Button(
            buttons_frame,
            text="✕ Reject",
            font=("Helvetica", 11),
            bg=self.error_color,
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.reject_question,
            padx=20,
            pady=8
        )
        reject_btn.pack(side="left", padx=5)

    def load_questions(self, *args):
        """Load questions into the treeview based on the selected filter."""
        # Clear existing items
        for item in self.questions_tree.get_children():
            self.questions_tree.delete(item)

        filter_type = self.filter_var.get()
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Update counters
            cursor.execute("SELECT COUNT(*) FROM questions WHERE approved=0")
            pending_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM questions WHERE reported=1")
            reported_count = cursor.fetchone()[0]

            self.pending_count.configure(text=f"Pending: {pending_count}")
            self.reported_count.configure(text=f"Reported: {reported_count}")

            if filter_type == "Pending Questions":
                cursor.execute("""
                    SELECT q.id, q.question, q.category, q.approved, q.timestamp, u.name 
                    FROM questions q 
                    LEFT JOIN users u ON q.user_id = u.id 
                    WHERE q.approved=0 
                    ORDER BY q.timestamp DESC
                """)
            else:  # Reported Questions
                cursor.execute("""
                    SELECT q.id, q.question, q.category, q.approved, q.timestamp, u.name 
                    FROM questions q 
                    LEFT JOIN users u ON q.user_id = u.id 
                    WHERE q.reported=1 
                    ORDER BY q.timestamp DESC
                """)

            rows = cursor.fetchall()
            
            if not rows:
                self.show_empty_state()
                return

            for row in rows:
                question_id, question, category, approved, timestamp, username = row
                status = "Pending" if not approved else "Reported"
                
                # Truncate long questions
                truncated_question = question[:100] + "..." if len(question) > 100 else question
                
                # Format date
                formatted_date = timestamp.strftime("%Y-%m-%d")
                
                tags = ('reported',) if status == "Reported" else ('pending',)
                
                self.questions_tree.insert(
                    "",
                    "end",
                    values=(question_id, truncated_question, category, status, formatted_date),
                    tags=tags
                )

            # Configure tag colors
            self.questions_tree.tag_configure('reported', foreground=self.error_color)
            self.questions_tree.tag_configure('pending', foreground=self.text_color)

        except Exception as e:
            self.show_error_message(f"Error loading questions: {str(e)}")
        finally:
            conn.close()

    def show_empty_state(self):
        """Show empty state message in the treeview"""
        self.questions_tree.insert(
            "",
            "end",
            values=("", "No questions found", "", "", ""),
            tags=('empty',)
        )
        self.questions_tree.tag_configure('empty', foreground="gray")

    def show_question_details(self, event):
        """Show detailed question information in a popup window"""
        selected_item = self.questions_tree.selection()
        if not selected_item:
            return

        item = self.questions_tree.item(selected_item)
        question_id = item['values'][0]

        # Create popup window
        popup = tk.Toplevel(self)
        popup.title("Question Details")
        popup.configure(bg=self.card_bg)
        popup.geometry("600x400")

        # Center the popup
        popup.geometry("+%d+%d" % (
            self.winfo_rootx() + 50,
            self.winfo_rooty() + 50
        ))

        # Fetch question details
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT q.question, q.category, q.timestamp, u.name, q.approved, q.reported
                FROM questions q
                LEFT JOIN users u ON q.user_id = u.id
                WHERE q.id = %s
            """, (question_id,))
            
            question_data = cursor.fetchone()
            if question_data:
                question, category, timestamp, username, approved, reported = question_data
                
                # Create details view
                details_frame = tk.Frame(popup, bg=self.card_bg, padx=20, pady=20)
                details_frame.pack(fill="both", expand=True)

                # Question header
                header_frame = tk.Frame(details_frame, bg=self.card_bg)
                header_frame.pack(fill="x", pady=(0, 15))

                tk.Label(
                    header_frame,
                    text=f"Question #{question_id}",
                    font=("Helvetica", 16, "bold"),
                    bg=self.card_bg,
                    fg=self.primary_color
                ).pack(side="left")

                status_color = self.error_color if reported else (
                    self.success_color if approved else "orange"
                )
                status_text = "Reported" if reported else (
                    "Approved" if approved else "Pending"
                )

                tk.Label(
                    header_frame,
                    text=status_text,
                    font=("Helvetica", 12),
                    bg=status_color,
                    fg="white",
                    padx=10,
                    pady=2
                ).pack(side="right")

                # Question content
                content_frame = tk.Frame(details_frame, bg=self.card_bg)
                content_frame.pack(fill="both", expand=True)

                # Question text
                tk.Label(
                    content_frame,
                    text="Question:",
                    font=("Helvetica", 11, "bold"),
                    bg=self.card_bg,
                    fg=self.text_color
                ).pack(anchor="w")
                
                question_text = tk.Text(
                    content_frame,
                    wrap=tk.WORD,
                    height=6,
                    font=("Helvetica", 11),
                    bg=self.bg_color,
                    fg=self.text_color,
                    relief="flat",
                    padx=10,
                    pady=10
                )
                question_text.insert("1.0", question)
                question_text.configure(state="disabled")
                question_text.pack(fill="x", pady=(5, 15))

                # Metadata
                meta_frame = tk.Frame(content_frame, bg=self.card_bg)
                meta_frame.pack(fill="x")

                # Left column
                left_meta = tk.Frame(meta_frame, bg=self.card_bg)
                left_meta.pack(side="left")

                tk.Label(
                    left_meta,
                    text=f"Category: {category}",
                    font=("Helvetica", 10),
                    bg=self.card_bg,
                    fg=self.text_color
                ).pack(anchor="w")

                tk.Label(
                    left_meta,
                    text=f"Posted by: {username}",
                    font=("Helvetica", 10),
                    bg=self.card_bg,
                    fg=self.text_color
                ).pack(anchor="w")

                # Right column
                right_meta = tk.Frame(meta_frame, bg=self.card_bg)
                right_meta.pack(side="right")

                tk.Label(
                    right_meta,
                    text=f"Date: {timestamp.strftime('%Y-%m-%d %H:%M')}",
                    font=("Helvetica", 10),
                    bg=self.card_bg,
                    fg=self.text_color
                ).pack(anchor="e")

                # Action buttons
                button_frame = tk.Frame(details_frame, bg=self.card_bg)
                button_frame.pack(fill="x", pady=(20, 0))

                approve_btn = tk.Button(
                    button_frame,
                    text="✓ Approve Question",
                    font=("Helvetica", 11),
                    bg=self.success_color,
                    fg="white",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda: self.approve_from_popup(question_id, popup),
                    padx=20,
                    pady=8
                )
                approve_btn.pack(side="left", padx=5)

                reject_btn = tk.Button(
                    button_frame,
                    text="✕ Reject Question",
                    font=("Helvetica", 11),
                    bg=self.error_color,
                    fg="white",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda: self.reject_from_popup(question_id, popup),
                    padx=20,
                    pady=8
                )
                reject_btn.pack(side="left", padx=5)

        except Exception as e:
            self.show_error_message(f"Error loading question details: {str(e)}")
        finally:
            conn.close()

    def approve_from_popup(self, question_id, popup):
        """Approve question from the detail popup"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE questions SET approved=1, reported=0 WHERE id=%s", (question_id,))
            conn.commit()
            self.show_success_message("Question approved successfully!")
            popup.destroy()
            self.load_questions()
        except Exception as e:
            self.show_error_message(f"Error approving question: {str(e)}")
        finally:
            conn.close()

    def reject_from_popup(self, question_id, popup):
        """Reject question from the detail popup"""
        if messagebox.askyesno("Confirm Rejection", "Are you sure you want to reject this question? This action cannot be undone."):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM questions WHERE id=%s", (question_id,))
                conn.commit()
                self.show_success_message("Question rejected successfully!")
                popup.destroy()
                self.load_questions()
            except Exception as e:
                self.show_error_message(f"Error rejecting question: {str(e)}")
            finally:
                conn.close()

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

    def show_error_message(self, message):
        """Show error message with animation"""
        if hasattr(self, 'message_label'):
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

    def hide_message(self):
        """Hide message with fade effect"""
        if hasattr(self, 'message_label'):
            self.message_label.destroy()
            delattr(self, 'message_label')

    def approve_question(self):
        """Approve the selected question from main view"""
        selected_item = self.questions_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a question to approve")
            return

        question_data = self.questions_tree.item(selected_item)['values']
        question_id = question_data[0]

        if messagebox.askyesno("Confirm Approval", "Are you sure you want to approve this question?"):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE questions SET approved=1, reported=0 WHERE id=%s",
                    (question_id,)
                )
                conn.commit()
                self.show_success_message("Question approved successfully!")
                self.load_questions()
            except Exception as e:
                self.show_error_message(f"Error approving question: {str(e)}")
            finally:
                conn.close()

    def reject_question(self):
        """Reject the selected question from main view"""
        selected_item = self.questions_tree.selection()
        if not selected_item:
            self.show_error_message("Please select a question to reject")
            return

        question_data = self.questions_tree.item(selected_item)['values']
        question_id = question_data[0]

        if messagebox.askyesno("Confirm Rejection", 
                              "Are you sure you want to reject this question?\nThis action cannot be undone."):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM questions WHERE id=%s", (question_id,))
                conn.commit()
                self.show_success_message("Question rejected successfully!")
                self.load_questions()
            except Exception as e:
                self.show_error_message(f"Error rejecting question: {str(e)}")
            finally:
                conn.close()

    def refresh_data(self):
        """Refresh the questions list"""
        self.load_questions()
        self.show_success_message("Data refreshed successfully!")

    def on_closing_popup(self, popup):
        """Handle popup window closing"""
        popup.destroy()
        self.load_questions()  # Refresh main view

    def apply_hover_effect(self, widget, enter_color, leave_color):
        """Apply hover effect to buttons"""
        widget.bind("<Enter>", lambda e: widget.configure(bg=enter_color))
        widget.bind("<Leave>", lambda e: widget.configure(bg=leave_color))

    def create_tooltip(self, widget, text):
        """Create tooltip for widgets"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                justify='left',
                background="#ffffff",
                relief='solid',
                borderwidth=1,
                font=("Helvetica", "10")
            )
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())

        widget.bind('<Enter>', show_tooltip)