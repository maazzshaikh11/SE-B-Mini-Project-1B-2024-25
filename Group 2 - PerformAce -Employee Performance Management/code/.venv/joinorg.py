import tkinter as tk
from tkinter import messagebox
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'UserManagement',
    'port': 3306
}

def open_join_org_page(username=None):
    root = tk.Tk()
    root.title("Join Organisation")
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

    # Page title
    title_label = tk.Label(root, text="Join Organisation", font=("Arial", 18, "bold"), bg="#223344", fg="lightblue")
    title_label.pack(pady=20)

    form_frame = tk.Frame(root, bg="#223344")
    form_frame.pack(pady=10)

    labels = ["Org Name", "Org Password"]
    entries = {}

    for i, text in enumerate(labels):
        label = tk.Label(form_frame, text=text, font=("Arial", 12), bg="#223344", fg="white")
        label.grid(row=i, column=0, padx=20, pady=5, sticky="w")

        entry = tk.Entry(form_frame, font=("Arial", 12), width=30, show='*' if text == "Org Password" else None)
        entry.grid(row=i, column=1, pady=5)
        entries[text] = entry

    def join_organization():
        org_name = entries["Org Name"].get().strip()
        org_password = entries["Org Password"].get().strip()

        if not org_name or not org_password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Validate organization credentials
            cursor.execute("SELECT org_password FROM organizations WHERE org_name = %s", (org_name,))
            result = cursor.fetchone()

            if not result:
                messagebox.showerror("Error", f"Organization '{org_name}' does not exist.")
                return

            if result[0] != org_password:
                messagebox.showerror("Error", "Invalid organization password.")
                return

            # Insert username into the specific organization member table
            table_name = f"{org_name.lower().replace(' ', '_')}_members"
            insert_member_query = f"""
            INSERT INTO `{table_name}` (user) VALUES (%s)
            """
            cursor.execute(insert_member_query, (username,))
            conn.commit()

            messagebox.showinfo("Success", "Successfully joined the organization!")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
            root.destroy()

    btn_frame = tk.Frame(root, bg="#223344")
    btn_frame.pack(pady=10)

    join_btn = tk.Button(btn_frame, text="Join", font=("Arial", 12), bg="lightgray", width=10, command=join_organization)
    join_btn.pack(side="left", padx=10)

    cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), bg="lightgray", width=10, command=root.destroy)
    cancel_btn.pack(side="left", padx=10)

    root.mainloop()
