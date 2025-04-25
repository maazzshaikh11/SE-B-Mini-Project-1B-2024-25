import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'UserManagement',
    'port': 3306
}

def open_create_org_page(admin_username=None):
    print(f"[DEBUG] Opening Create Organisation Page with admin_username: {admin_username}")  # Debugging line

    # Use Toplevel instead of Tk
    root = tk.Toplevel()  # Create a new top-level window
    root.title("Create Organisation")
    root.geometry("600x400")

    # Center window
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    center_window(root, 600, 400)
    root.configure(bg="#223344")

    # Page title
    title_label = tk.Label(root, text="Create Organisation", font=("Arial", 18, "bold"), bg="#223344", fg="lightblue")
    title_label.pack(pady=20)

    form_frame = tk.Frame(root, bg="#223344")
    form_frame.pack(pady=10)

    labels = ["Org Name", "Mail Id", "Contact", "Org Password"]
    entries = {}

    for i, text in enumerate(labels):
        label = tk.Label(form_frame, text=text, font=("Arial", 12), bg="#223344", fg="white")
        label.grid(row=i, column=0, padx=20, pady=5, sticky="w")

        entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        entry.grid(row=i, column=1, pady=5)
        entries[text] = entry

    # Add the dropdown for "Sector"
    sector_label = tk.Label(form_frame, text="Sector", font=("Arial", 12), bg="#223344", fg="white")
    sector_label.grid(row=len(labels), column=0, padx=20, pady=5, sticky="w")

    sector_options = [
        "Not Specified",
        "Education and Research",
        "Industry and Manufacturing",
        "Corporate and Financial Services",
        "Health and Social Services",
        "Tourism Media and Entertainment",
        "Real Estate and Infrastructure",
        "Technology and Innovation"
    ]

    # Create the StringVar and Combobox after the form is initialized
    sector_var = tk.StringVar(value="Not Specified")  # Set default value right here

    sector_dropdown = ttk.Combobox(form_frame, textvariable=sector_var, values=sector_options, state="readonly",
                                    width=28)
    sector_dropdown.grid(row=len(labels), column=1, pady=5)

    # Ensure the dropdown has a default value set explicitly
    sector_var.set("Not Specified")

    def create_organization():
        org_name = entries["Org Name"].get().strip()
        email = entries["Mail Id"].get().strip()
        contact = entries["Contact"].get().strip()
        password = entries["Org Password"].get().strip()

        # Debugging: Check what sector value is right before submission
        sector = sector_var.get()
        print(f"[DEBUG] Selected Sector Before Insertion: '{sector}'")  # Debugging line

        if not org_name or not email or not contact or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        # Handle empty sector case (not mandatory)
        if sector == "Not Specified":
            sector = "Not Specified"

        print(f"[DEBUG] Value to be inserted in DB - Sector: '{sector}'")  # Debugging line

        try:
            with mysql.connector.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    # Check for duplicate organization
                    cursor.execute("SELECT COUNT(*) FROM organizations WHERE org_name = %s", (org_name,))
                    result = cursor.fetchone()

                    if result[0] > 0:
                        messagebox.showerror("Error", f"Organization '{org_name}' already exists.")
                        return

                    # Create a specific table for the organization with backticks
                    table_name = f"{org_name.lower().replace(' ', '_')}_members"
                    create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS `{table_name}` (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user VARCHAR(255) NOT NULL
                    )
                    """
                    cursor.execute(create_table_query)

                    # Insert into the organizations table, including the sector
                    insert_org_query = """
                    INSERT INTO organizations (org_name, email, contact, org_password, admin, sector)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_org_query, (org_name, email, contact, password, admin_username or None, sector))

                    conn.commit()
                    messagebox.showinfo("Success", "Organization created successfully!")

                    # Reset form fields BEFORE closing the window
                    for entry in entries.values():
                        entry.delete(0, tk.END)

                    # Reset the dropdown by reinitializing the StringVar
                    sector_var.set("Not Specified")

                    # Close the window after resetting the fields
                    root.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    btn_frame = tk.Frame(root, bg="#223344")
    btn_frame.pack(pady=10)

    create_btn = tk.Button(btn_frame, text="Create", font=("Arial", 12), bg="lightgray", width=10,
                           command=create_organization)
    create_btn.pack(side="left", padx=10)

    cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), bg="lightgray", width=10, command=root.destroy)
    cancel_btn.pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__":
    open_create_org_page(admin_username="admin_user")  # Replace with actual username when running from homepage
