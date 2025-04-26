# pages/resource_sharing_page.py
import tkinter as tk
from tkinter import font, filedialog, messagebox
from PIL import Image, ImageTk  # For adding images (requires Pillow library)
from database import get_db_connection

class ResourceSharingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#f0f0f0")  # Set background color
        self.controller = controller

        # Custom Fonts
        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        label_font = font.Font(family="Helvetica", size=12)
        button_font = font.Font(family="Helvetica", size=12, weight="bold")

        # Title Label
        tk.Label(self, text="Share Resources", font=title_font, bg="#f0f0f0", fg="#333333").pack(pady=(30, 10))

        # Frame for Resource Sharing
        resource_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, bd=2, relief="groove")
        resource_frame.pack(pady=20, fill="both", expand=True)

        # Upload Section
        tk.Label(resource_frame, text="Upload a File", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333").grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        tk.Label(resource_frame, text="File Path", font=label_font, bg="#ffffff", fg="#333333").grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )
        self.file_path_entry = tk.Entry(resource_frame, font=label_font, relief="solid", borderwidth=1, state="readonly")
        self.file_path_entry.grid(row=2, column=0, pady=(0, 10), sticky="ew")

        browse_button = tk.Button(
            resource_frame,
            text="Browse",
            font=button_font,
            bg="#0078d4",
            fg="#ffffff",
            relief="flat",
            activebackground="#005bb5",
            command=self.browse_file
        )
        browse_button.grid(row=2, column=1, pady=(0, 10), padx=(10, 0), sticky="ew")

        # Share Button
        share_button = tk.Button(
            resource_frame,
            text="Share Resource",
            font=button_font,
            bg="#0078d4",
            fg="#ffffff",
            relief="flat",
            activebackground="#005bb5",
            command=self.share_resource
        )
        share_button.grid(row=3, column=0, columnspan=2, pady=(10, 0), ipadx=10, ipady=5, sticky="ew")

        # Back to Dashboard Button
        back_button = tk.Button(
            self,
            text="Back to Dashboard",
            font=button_font,
            bg="#ff4d4d",
            fg="#ffffff",
            relief="flat",
            activebackground="#e60000",
            command=lambda: controller.show_frame("JuniorDashboardPage" if self.controller.role == "Junior" else "SeniorDashboardPage")
        )
        back_button.pack(pady=(10, 20), ipadx=10, ipady=5)

    def browse_file(self):
        """Open a file dialog to select a file."""
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_entry.config(state="normal")
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.file_path_entry.config(state="readonly")

    def share_resource(self):
        """Share the selected resource."""
        file_path = self.file_path_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file to share.")
            return

        # Save the file path to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO resources (user_id, title, file_path, description, approved) VALUES (%s, %s, %s, %s, %s)",
                (self.controller.user_id, "Untitled", file_path, "No description provided", 0)  # Default values for title and description
            )
            conn.commit()
            messagebox.showinfo("Success", "Resource shared successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()