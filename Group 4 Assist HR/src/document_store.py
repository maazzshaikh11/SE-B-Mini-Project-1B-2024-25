from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import mysql.connector
from PIL import Image, ImageTk
import datetime
import uuid
import PyPDF2
from io import BytesIO


# Database connection function
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="CHIR2502004|",
            database="hrassistance"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None


# Create the necessary table in the database
def setup_document_table():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            # Create table if not exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(36) PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                category VARCHAR(100) NOT NULL,
                upload_date DATETIME NOT NULL,
                description TEXT,
                file_size INT NOT NULL
            )
            """)
            conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to setup database: {err}")
        finally:
            cursor.close()
            conn.close()


def document_storage(parent):
    # Create document storage directory if it doesn't exist
    doc_storage_path = os.path.join(os.getcwd(), "document_storage")
    if not os.path.exists(doc_storage_path):
        os.makedirs(doc_storage_path)

    # Ensure database table exists
    setup_document_table()

    dashboard_window = Toplevel(parent)
    dashboard_window.title("Document Store")
    dashboard_window.configure(background="#FFDD95")
    dashboard_window.state('zoomed')

    # Positioning the application
    window_width = 1000
    window_height = 600
    screen_width = dashboard_window.winfo_screenwidth()
    screen_height = dashboard_window.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    dashboard_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Setting up fonts
    font_info1 = ('Arial', 30, 'italic')
    font_info2 = ('Arial', 15, 'italic')
    font_button = ('Arial', 15, 'bold')
    font_normal = ('Arial', 12)

    # Labels
    info1_label = Label(dashboard_window, text="Document Store", fg='#3468C0', bg='#FFDD95', font=font_info1)
    info1_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    info2_label = Label(dashboard_window, text="Upload your company's documents here", fg='#3468C0', bg='#FFDD95',
                        font=font_info2)
    info2_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='n')

    # Create frame for document upload section
    upload_frame = Frame(dashboard_window, bg="#FFDD95", bd=2, relief=RIDGE)
    upload_frame.grid(row=2, column=0, padx=20, pady=10, sticky='nsew')

    # Upload section
    upload_title = Label(upload_frame, text="Upload Document", fg='#3468C0', bg='#FFDD95', font=('Arial', 16, 'bold'))
    upload_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')

    # Category selection
    category_label = Label(upload_frame, text="Document Category:", fg='#3468C0', bg='#FFDD95', font=font_normal)
    category_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    categories = ["HR Policies", "Employee Handbooks", "Training Materials", "Legal Documents", "Forms", "Other"]
    category_var = StringVar()
    category_var.set(categories[0])

    category_menu = ttk.Combobox(upload_frame, textvariable=category_var, values=categories, font=font_normal, width=20)
    category_menu.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    # Description field
    desc_label = Label(upload_frame, text="Description:", fg='#3468C0', bg='#FFDD95', font=font_normal)
    desc_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

    desc_text = Text(upload_frame, height=4, width=30, font=font_normal)
    desc_text.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    # Selected file display
    file_label = Label(upload_frame, text="Selected File:", fg='#3468C0', bg='#FFDD95', font=font_normal)
    file_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

    selected_file_var = StringVar()
    selected_file_var.set("No file selected")
    selected_file_display = Label(upload_frame, textvariable=selected_file_var, fg='#666666', bg='#FFDD95',
                                  font=font_normal)
    selected_file_display.grid(row=3, column=1, padx=10, pady=5, sticky='w')

    # Store the file path
    selected_file_path = {"path": None}

    # File browser function
    def browse_file():
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Document Files", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt"),
                ("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            file_name = os.path.basename(file_path)
            selected_file_var.set(file_name)
            selected_file_path["path"] = file_path

            # Show file preview if it's an image
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                try:
                    preview_image = Image.open(file_path)
                    preview_image = preview_image.resize((150, 150), Image.LANCZOS)
                    preview_photo = ImageTk.PhotoImage(preview_image)
                    preview_label.config(image=preview_photo)
                    preview_label.image = preview_photo
                except Exception as e:
                    messagebox.showerror("Preview Error", f"Could not preview image: {e}")
            # Show PDF preview (first page)
            elif file_ext == '.pdf':
                try:
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        if len(pdf_reader.pages) > 0:
                            # Display PDF info instead of preview
                            preview_label.config(image='')
                            preview_info = f"PDF Document\nPages: {len(pdf_reader.pages)}"
                            preview_label.config(text=preview_info)
                        else:
                            preview_label.config(text="Empty PDF")
                except Exception as e:
                    messagebox.showerror("Preview Error", f"Could not preview PDF: {e}")
            else:
                # For other file types just show file type
                preview_label.config(image='')
                preview_label.config(text=f"File Type: {file_ext[1:].upper()}\nNo preview available")

    # Browse button
    browse_button = Button(upload_frame, text="Browse Files", fg='#f7f7f7', bg='#3468C0',
                           activeforeground='#3468C0', activebackground='#FFDD95',
                           command=browse_file, font=font_button)
    browse_button.grid(row=4, column=0, padx=10, pady=10, sticky='w')

    # Preview area
    preview_frame = Frame(upload_frame, bg="#FFFFFF", width=200, height=200, bd=1, relief=SUNKEN)
    preview_frame.grid(row=1, column=2, rowspan=4, padx=20, pady=10, sticky='nsew')

    preview_label = Label(preview_frame, text="File Preview\nWill appear here", bg="#FFFFFF")
    preview_label.pack(expand=True, fill=BOTH)

    # Upload function
    def upload_document():
        if not selected_file_path["path"]:
            messagebox.showwarning("No File Selected", "Please select a file to upload.")
            return

        file_path = selected_file_path["path"]
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        category = category_var.get()
        description = desc_text.get("1.0", END).strip()
        file_size = os.path.getsize(file_path)

        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Create destination directory
        category_dir = os.path.join(os.getcwd(), "document_storage", category.replace(" ", "_"))
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        # Destination path
        dest_path = os.path.join(category_dir, f"{file_id}_{file_name}")

        # Copy file to destination
        try:
            shutil.copy2(file_path, dest_path)

            # Save to database
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                    INSERT INTO documents (id, filename, file_path, file_type, category, upload_date, description, file_size) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        file_id,
                        file_name,
                        dest_path,
                        file_ext[1:],
                        category,
                        datetime.datetime.now(),
                        description,
                        file_size
                    ))
                    conn.commit()
                    messagebox.showinfo("Success", "Document uploaded successfully!")

                    # Refresh document list
                    load_documents()

                    # Clear form
                    selected_file_var.set("No file selected")
                    selected_file_path["path"] = None
                    desc_text.delete("1.0", END)
                    preview_label.config(image='')
                    preview_label.config(text="File Preview\nWill appear here")

                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error saving document: {err}")
                finally:
                    cursor.close()
                    conn.close()
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload document: {e}")

    # Upload button
    upload_button = Button(upload_frame, text="Upload Document", fg='#f7f7f7', bg='#3468C0',
                           activeforeground='#3468C0', activebackground='#FFDD95',
                           command=upload_document, font=font_button)
    upload_button.grid(row=4, column=1, padx=10, pady=10, sticky='w')

    # Document list frame
    list_frame = Frame(dashboard_window, bg="#FFDD95", bd=2, relief=RIDGE)
    list_frame.grid(row=2, column=1, columnspan=2, padx=20, pady=10, sticky='nsew')

    list_title = Label(list_frame, text="Document Library", fg='#3468C0', bg='#FFDD95', font=('Arial', 16, 'bold'))
    list_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')

    # Create treeview for document list
    columns = ("Filename", "Category", "Type", "Size", "Upload Date")
    doc_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

    # Configure columns
    doc_tree.heading("Filename", text="Filename")
    doc_tree.heading("Category", text="Category")
    doc_tree.heading("Type", text="Type")
    doc_tree.heading("Size", text="Size")
    doc_tree.heading("Upload Date", text="Upload Date")

    doc_tree.column("Filename", width=200)
    doc_tree.column("Category", width=150)
    doc_tree.column("Type", width=80)
    doc_tree.column("Size", width=80)
    doc_tree.column("Upload Date", width=150)

    doc_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')

    # Add scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=doc_tree.yview)
    scrollbar.grid(row=1, column=2, padx=0, pady=5, sticky='ns')
    doc_tree.configure(yscrollcommand=scrollbar.set)

    # Store document IDs for use in operations
    doc_ids = {}

    # Function to load documents from database
    def load_documents():
        # Clear existing items
        for item in doc_tree.get_children():
            doc_tree.delete(item)

        doc_ids.clear()

        # Get documents from database
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT id, filename, category, file_type, file_size, upload_date FROM documents ORDER BY upload_date DESC")
                for row in cursor.fetchall():
                    doc_id, filename, category, file_type, file_size, upload_date = row

                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    # Format date
                    date_str = upload_date.strftime("%Y-%m-%d %H:%M")

                    # Insert into treeview
                    item_id = doc_tree.insert("", "end",
                                              values=(filename, category, file_type.upper(), size_str, date_str))
                    doc_ids[item_id] = doc_id

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error loading documents: {err}")
            finally:
                cursor.close()
                conn.close()

    # Load initial documents
    load_documents()

    # Search function
    def search_documents():
        search_term = search_var.get().lower()

        # Clear existing items
        for item in doc_tree.get_children():
            doc_tree.delete(item)

        doc_ids.clear()

        # Get filtered documents from database
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                SELECT id, filename, category, file_type, file_size, upload_date FROM documents 
                WHERE LOWER(filename) LIKE %s OR LOWER(category) LIKE %s OR LOWER(description) LIKE %s
                ORDER BY upload_date DESC
                """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))

                for row in cursor.fetchall():
                    doc_id, filename, category, file_type, file_size, upload_date = row

                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    # Format date
                    date_str = upload_date.strftime("%Y-%m-%d %H:%M")

                    # Insert into treeview
                    item_id = doc_tree.insert("", "end",
                                              values=(filename, category, file_type.upper(), size_str, date_str))
                    doc_ids[item_id] = doc_id

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error searching documents: {err}")
            finally:
                cursor.close()
                conn.close()

    # Search bar
    search_frame = Frame(list_frame, bg="#FFDD95")
    search_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='w')

    search_label = Label(search_frame, text="Search:", fg='#3468C0', bg='#FFDD95', font=font_normal)
    search_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    search_var = StringVar()
    search_entry = Entry(search_frame, textvariable=search_var, font=font_normal, width=30)
    search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    search_button = Button(search_frame, text="Search", fg='#f7f7f7', bg='#3468C0',
                           activeforeground='#3468C0', activebackground='#FFDD95',
                           command=search_documents, font=font_normal)
    search_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    clear_button = Button(search_frame, text="Clear", fg='#f7f7f7', bg='#666666',
                          activeforeground='#666666', activebackground='#FFDD95',
                          command=lambda: [search_var.set(""), load_documents()], font=font_normal)
    clear_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    # Function to open the selected document
    def open_document():
        selected_items = doc_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a document to open.")
            return

        selected_item = selected_items[0]
        doc_id = doc_ids.get(selected_item)

        if doc_id:
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT file_path FROM documents WHERE id = %s", (doc_id,))
                    result = cursor.fetchone()

                    if result and result[0]:
                        file_path = result[0]

                        # Check if file exists
                        if os.path.exists(file_path):
                            # Open file with default application
                            os.startfile(file_path) if os.name == 'nt' else os.system(f"xdg-open {file_path}")
                        else:
                            messagebox.showerror("File Not Found", "The file could not be found in the system.")

                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error opening document: {err}")
                finally:
                    cursor.close()
                    conn.close()

    # Function to delete the selected document
    def delete_document():
        selected_items = doc_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a document to delete.")
            return

        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this document?"):
            return

        selected_item = selected_items[0]
        doc_id = doc_ids.get(selected_item)

        if doc_id:
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    # Get file path before deletion
                    cursor.execute("SELECT file_path FROM documents WHERE id = %s", (doc_id,))
                    result = cursor.fetchone()

                    if result and result[0]:
                        file_path = result[0]

                        # Delete from database
                        cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
                        conn.commit()

                        # Delete file from filesystem
                        if os.path.exists(file_path):
                            os.remove(file_path)

                        # Refresh document list
                        load_documents()
                        messagebox.showinfo("Success", "Document deleted successfully!")

                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error deleting document: {err}")
                finally:
                    cursor.close()
                    conn.close()

    # Action buttons
    button_frame = Frame(list_frame, bg="#FFDD95")
    button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='w')

    open_button = Button(button_frame, text="Open Document", fg='#f7f7f7', bg='#3468C0',
                         activeforeground='#3468C0', activebackground='#FFDD95',
                         command=open_document, font=font_normal)
    open_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    delete_button = Button(button_frame, text="Delete Document", fg='#f7f7f7', bg='#D24545',
                           activeforeground='#D24545', activebackground='#A94438',
                           command=delete_document, font=font_normal)
    delete_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    refresh_button = Button(button_frame, text="Refresh List", fg='#f7f7f7', bg='#3468C0',
                            activeforeground='#3468C0', activebackground='#FFDD95',
                            command=load_documents, font=font_normal)
    refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    # Back button function
    def feature_back(current_window, previous_window):
        current_window.withdraw()
        previous_window.deiconify()

    back_button = Button(dashboard_window, text="Back", fg='#f7f7f7', bg='#D24545', activeforeground='#D24545',
                         activebackground='#A94438', command=lambda: feature_back(dashboard_window, parent),
                         font=font_button)
    back_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='w')

    # Configure column and row sizes
    dashboard_window.grid_columnconfigure(0, weight=1)
    dashboard_window.grid_columnconfigure(1, weight=1)
    dashboard_window.grid_columnconfigure(2, weight=1)
    dashboard_window.grid_rowconfigure(2, weight=1)


if __name__ == "__main__":
    window = Tk()
    document_storage(window)
    window.mainloop()