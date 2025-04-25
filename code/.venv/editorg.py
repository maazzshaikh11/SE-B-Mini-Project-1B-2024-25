import tkinter as tk
from tkinter import messagebox
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'usermanagement',
    'port': 3306
}


def open_edit_org_page(org_name):
    root = tk.Tk()
    root.title(f"Edit Organization - {org_name}")
    root.geometry("600x350")

    # Center window
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    center_window(root, 600, 350)
    root.configure(bg="#223344")

    # Fetch existing organization details
    org_details = {}

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT email, contact, org_password FROM organizations WHERE org_name = %s", (org_name,))
        result = cursor.fetchone()
        if result:
            org_details = {'email': result[0], 'contact': result[1], 'org_password': result[2]}
        else:
            messagebox.showerror("Error", "Organization not found!")
            root.destroy()
            return
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        root.destroy()
        return
    finally:
        cursor.close()
        conn.close()

    # Page title
    title_label = tk.Label(root, text=f"Edit Organization - {org_name}", font=("Arial", 18, "bold"), bg="#223344", fg="lightblue")
    title_label.pack(pady=20)

    form_frame = tk.Frame(root, bg="#223344")
    form_frame.pack(pady=10)

    labels = ["Mail Id", "Contact", "Org Password"]
    entries = {}

    for i, text in enumerate(labels):
        label = tk.Label(form_frame, text=text, font=("Arial", 12), bg="#223344", fg="white")
        label.grid(row=i, column=0, padx=20, pady=5, sticky="w")

        entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        entry.grid(row=i, column=1, pady=5)
        entries[text] = entry

    # Populate current data
    entries["Mail Id"].insert(0, org_details['email'])
    entries["Contact"].insert(0, org_details['contact'])
    entries["Org Password"].insert(0, org_details['org_password'])

    def update_organization():
        email = entries["Mail Id"].get()
        contact = entries["Contact"].get()
        password = entries["Org Password"].get()

        if not email or not contact or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            update_org_query = """
            UPDATE organizations
            SET email = %s, contact = %s, org_password = %s
            WHERE org_name = %s
            """
            cursor.execute(update_org_query, (email, contact, password, org_name))
            conn.commit()
            messagebox.showinfo("Success", "Organization updated successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
            root.destroy()

    btn_frame = tk.Frame(root, bg="#223344")
    btn_frame.pack(pady=10)

    update_btn = tk.Button(btn_frame, text="Update", font=("Arial", 12), bg="lightgray", width=10, command=update_organization)
    update_btn.pack(side="left", padx=10)

    cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), bg="lightgray", width=10, command=root.destroy)
    cancel_btn.pack(side="left", padx=10)

    root.mainloop()
