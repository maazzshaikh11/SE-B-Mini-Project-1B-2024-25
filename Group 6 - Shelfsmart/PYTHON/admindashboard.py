import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import mysql.connector
from mysql.connector import Error

# Load products from home.py
from home import PRODUCTS

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")
        self.root.geometry("800x700")
        
        # Database connection
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Shubham@1905",
                database="inventory"
            )
            self.cursor = self.conn.cursor()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            self.root.destroy()
            return
        
        # Set modern color scheme
        self.root.config(bg="#f0f8ff")  # Light blue background
        
        # Create main container with padding
        self.main_frame = tk.Frame(root, bg="#f0f8ff", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section with modern styling
        header_frame = tk.Frame(self.main_frame, bg="#f0f8ff")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Back button
        back_btn = tk.Button(header_frame,
                           text="← Back to Login",
                           command=self.go_back_to_login,
                           font=("Segoe UI", 12, "bold"),
                           bg="#95a5a6",
                           fg="white",
                           activebackground="#7f8c8d",
                           relief="flat",
                           borderwidth=0,
                           cursor="hand2",
                           padx=15,
                           pady=5)
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Title with modern styling
        title_label = tk.Label(header_frame,
                             text="👨‍💼 Admin Dashboard",
                             font=("Segoe UI", 28, "bold"),
                             bg="#f0f8ff",
                             fg="#2c3e50")
        title_label.pack(expand=True)
        
        # Create two main sections
        sections_frame = tk.Frame(self.main_frame, bg="#f0f8ff")
        sections_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add Product Section
        add_frame = tk.LabelFrame(sections_frame,
                                text="➕ Add New Product",
                                font=("Segoe UI", 14, "bold"),
                                bg="white",
                                fg="#2c3e50",
                                relief="solid",
                                borderwidth=1)
        add_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Category selection for adding
        category_add_frame = tk.Frame(add_frame, bg="white")
        category_add_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(category_add_frame,
                text="Select Category:",
                font=("Segoe UI", 12),
                bg="white",
                fg="#2c3e50").pack(side=tk.LEFT, padx=5)
        
        self.category_add_var = tk.StringVar()
        self.category_add_combo = ttk.Combobox(category_add_frame,
                                             textvariable=self.category_add_var,
                                             values=list(PRODUCTS.keys()),
                                             font=("Segoe UI", 12),
                                             state="readonly",
                                             width=30)
        self.category_add_combo.pack(side=tk.LEFT, padx=5)
        
        # Product name entry
        name_frame = tk.Frame(add_frame, bg="white")
        name_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(name_frame,
                text="Product Name:",
                font=("Segoe UI", 12),
                bg="white",
                fg="#2c3e50").pack(side=tk.LEFT, padx=5)
        
        self.new_product_name = tk.Entry(name_frame,
                                       font=("Segoe UI", 12),
                                       relief="solid",
                                       borderwidth=1)
        self.new_product_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Price entry
        price_frame = tk.Frame(add_frame, bg="white")
        price_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(price_frame,
                text="Price:",
                font=("Segoe UI", 12),
                bg="white",
                fg="#2c3e50").pack(side=tk.LEFT, padx=5)
        
        self.new_product_price = tk.Entry(price_frame,
                                        font=("Segoe UI", 12),
                                        relief="solid",
                                        borderwidth=1)
        self.new_product_price.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Add product button
        add_btn = tk.Button(add_frame,
                          text="Add Product",
                          command=self.add_product,
                          font=("Segoe UI", 12, "bold"),
                          bg="#4169e1",
                          fg="white",
                          activebackground="#1e40af",
                          relief="flat",
                          borderwidth=0,
                          cursor="hand2")
        add_btn.pack(pady=10)
        
        # Delete Product Section
        delete_frame = tk.LabelFrame(sections_frame,
                                   text="❌ Delete Product",
                                   font=("Segoe UI", 14, "bold"),
                                   bg="white",
                                   fg="#2c3e50",
                                   relief="solid",
                                   borderwidth=1)
        delete_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Category selection for deleting
        category_delete_frame = tk.Frame(delete_frame, bg="white")
        category_delete_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(category_delete_frame,
                text="Select Category:",
                font=("Segoe UI", 12),
                bg="white",
                fg="#2c3e50").pack(side=tk.LEFT, padx=5)
        
        self.category_delete_var = tk.StringVar()
        self.category_delete_combo = ttk.Combobox(category_delete_frame,
                                                textvariable=self.category_delete_var,
                                                values=list(PRODUCTS.keys()),
                                                font=("Segoe UI", 12),
                                                state="readonly",
                                                width=30)
        self.category_delete_combo.pack(side=tk.LEFT, padx=5)
        self.category_delete_combo.bind('<<ComboboxSelected>>', self.update_product_combo)
        
        # Product selection for deleting
        product_delete_frame = tk.Frame(delete_frame, bg="white")
        product_delete_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(product_delete_frame,
                text="Select Product:",
                font=("Segoe UI", 12),
                bg="white",
                fg="#2c3e50").pack(side=tk.LEFT, padx=5)
        
        self.product_delete_var = tk.StringVar()
        self.product_delete_combo = ttk.Combobox(product_delete_frame,
                                               textvariable=self.product_delete_var,
                                               font=("Segoe UI", 12),
                                               state="readonly",
                                               width=30)
        self.product_delete_combo.pack(side=tk.LEFT, padx=5)
        
        # Delete product button
        delete_btn = tk.Button(delete_frame,
                             text="Delete Product",
                             command=self.delete_product,
                             font=("Segoe UI", 12, "bold"),
                             bg="#e74c3c",
                             fg="white",
                             activebackground="#c0392b",
                             relief="flat",
                             borderwidth=0,
                             cursor="hand2")
        delete_btn.pack(pady=10)
    
    def update_product_combo(self, event=None):
        """Update the product combobox when category is selected"""
        category = self.category_delete_var.get()
        if category in PRODUCTS:
            self.product_delete_combo['values'] = list(PRODUCTS[category].keys())
            self.product_delete_combo.set('')  # Clear current selection
    
    def add_product(self):
        category = self.category_add_var.get()
        if not category:
            messagebox.showerror("Error", "Please select a category first")
            return
            
        product_name = self.new_product_name.get()
        try:
            price = float(self.new_product_price.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
            return
            
        if not product_name:
            messagebox.showerror("Error", "Please enter a product name")
            return
            
        if product_name in PRODUCTS[category]:
            messagebox.showerror("Error", "Product already exists in this category")
            return
            
        try:
            # Add to in-memory dictionary
            PRODUCTS[category][product_name] = price
            
            # Add to database
            query = "INSERT INTO products (category, product_name, price) VALUES (%s, %s, %s)"
            values = (category, product_name, price)
            self.cursor.execute(query, values)
            self.conn.commit()
            
            # Show success message
            success_window = tk.Toplevel(self.root)
            success_window.title("Success")
            success_window.geometry("300x150")
            success_window.config(bg="#f0f8ff")
            
            # Center the success window
            screen_width = success_window.winfo_screenwidth()
            screen_height = success_window.winfo_screenheight()
            x = (screen_width - 300) // 2
            y = (screen_height - 150) // 2
            success_window.geometry(f"300x150+{x}+{y}")
            
            # Success message
            success_label = tk.Label(success_window,
                                   text="✅ Product added successfully!",
                                   font=("Segoe UI", 14, "bold"),
                                   bg="#f0f8ff",
                                   fg="#27ae60")
            success_label.pack(pady=20)
            
            # OK button
            ok_btn = tk.Button(success_window,
                             text="OK",
                             command=success_window.destroy,
                             font=("Segoe UI", 12, "bold"),
                             bg="#4169e1",
                             fg="white",
                             activebackground="#1e40af",
                             relief="flat",
                             borderwidth=0,
                             cursor="hand2",
                             width=10)
            ok_btn.pack(pady=10)
            
            # Clear inputs
            self.new_product_name.delete(0, tk.END)
            self.new_product_price.delete(0, tk.END)
            
            # Make the success window modal
            success_window.transient(self.root)
            success_window.grab_set()
            self.root.wait_window(success_window)
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add product to database: {str(e)}")
            # Remove from in-memory dictionary if database update failed
            del PRODUCTS[category][product_name]
    
    def delete_product(self):
        category = self.category_delete_var.get()
        if not category:
            messagebox.showerror("Error", "Please select a category first")
            return
            
        product_name = self.product_delete_var.get()
        if not product_name:
            messagebox.showerror("Error", "Please select a product to delete")
            return
            
        # Confirmation dialog
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("Confirm Delete")
        confirm_window.geometry("400x200")
        confirm_window.config(bg="#f0f8ff")
        
        # Center the confirmation window
        screen_width = confirm_window.winfo_screenwidth()
        screen_height = confirm_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 200) // 2
        confirm_window.geometry(f"400x200+{x}+{y}")
        
        # Warning message
        warning_label = tk.Label(confirm_window,
                               text="⚠️ Are you sure you want to delete this product?",
                               font=("Segoe UI", 14, "bold"),
                               bg="#f0f8ff",
                               fg="#2c3e50")
        warning_label.pack(pady=20)
        
        # Product details
        details_label = tk.Label(confirm_window,
                               text=f"Product: {product_name}\nCategory: {category}",
                               font=("Segoe UI", 12),
                               bg="#f0f8ff",
                               fg="#34495e")
        details_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(confirm_window, bg="#f0f8ff")
        button_frame.pack(pady=20)
        
        # Delete button
        delete_btn = tk.Button(button_frame,
                             text="Delete",
                             command=lambda: self.confirm_delete(category, product_name, confirm_window),
                             font=("Segoe UI", 12, "bold"),
                             bg="#e74c3c",
                             fg="white",
                             activebackground="#c0392b",
                             relief="flat",
                             borderwidth=0,
                             cursor="hand2",
                             width=10)
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             command=confirm_window.destroy,
                             font=("Segoe UI", 12, "bold"),
                             bg="#95a5a6",
                             fg="white",
                             activebackground="#7f8c8d",
                             relief="flat",
                             borderwidth=0,
                             cursor="hand2",
                             width=10)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Make the confirmation window modal
        confirm_window.transient(self.root)
        confirm_window.grab_set()
        self.root.wait_window(confirm_window)
    
    def confirm_delete(self, category, product_name, window):
        """Handle the actual deletion of the product"""
        try:
            # Delete from database first
            query = "DELETE FROM products WHERE category = %s AND product_name = %s"
            values = (category, product_name)
            self.cursor.execute(query, values)
            self.conn.commit()
            
            # If database deletion successful, delete from in-memory dictionary
            del PRODUCTS[category][product_name]
            window.destroy()
            
            # Show success message
            success_window = tk.Toplevel(self.root)
            success_window.title("Success")
            success_window.geometry("300x150")
            success_window.config(bg="#f0f8ff")
            
            # Center the success window
            screen_width = success_window.winfo_screenwidth()
            screen_height = success_window.winfo_screenheight()
            x = (screen_width - 300) // 2
            y = (screen_height - 150) // 2
            success_window.geometry(f"300x150+{x}+{y}")
            
            # Success message
            success_label = tk.Label(success_window,
                                   text="✅ Product deleted successfully!",
                                   font=("Segoe UI", 14, "bold"),
                                   bg="#f0f8ff",
                                   fg="#27ae60")
            success_label.pack(pady=20)
            
            # OK button
            ok_btn = tk.Button(success_window,
                             text="OK",
                             command=success_window.destroy,
                             font=("Segoe UI", 12, "bold"),
                             bg="#4169e1",
                             fg="white",
                             activebackground="#1e40af",
                             relief="flat",
                             borderwidth=0,
                             cursor="hand2",
                             width=10)
            ok_btn.pack(pady=10)
            
            # Update product combobox
            self.update_product_combo()
            
            # Make the success window modal
            success_window.transient(self.root)
            success_window.grab_set()
            self.root.wait_window(success_window)
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete product from database: {str(e)}")
    
    def go_back_to_login(self):
        """Return to login page"""
        try:
            self.root.destroy()
            from login import create_gui
            create_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to login page: {str(e)}")
    
    def __del__(self):
        """Clean up database connection when object is destroyed"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

def create_admin_dashboard():
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()

if __name__ == "__main__":  # Fixed incorrect __name__ check
    create_admin_dashboard()
