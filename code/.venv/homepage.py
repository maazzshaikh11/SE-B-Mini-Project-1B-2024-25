import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar
import datetime
from time import strftime
import login
from createorg import open_create_org_page
from joinorg import open_join_org_page
from editorg import open_edit_org_page
import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'UserManagement'
}


def open_homepage(username=None):
    root = tk.Tk()
    root.title("Homepage")
    root.geometry("1600x750")

    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    center_window(root, 1600, 750)
    root.configure(bg="#223344")  # Updated background color

    header_frame = tk.Frame(root, bg="#FFD700", height=50)  # Updated header color
    header_frame.pack(fill="x")

    welcome_message = f"WELCOME {username.upper()} !!!" if username else "WELCOME USER !!!"
    welcome_label = tk.Label(header_frame, text=welcome_message, font=("Arial", 12, "bold"), bg="#223344", fg="white")
    welcome_label.pack(side="left", padx=10)

    def logout():
        root.destroy()
        login.open_login_page()

    logout_btn = tk.Button(header_frame, text="LOG OUT", bg="#FFD700", fg="black", width=10,
                           command=logout)  # Updated button color
    logout_btn.pack(side="right", padx=5, pady=5)

    def close_window():
        root.destroy()

    close_btn = tk.Button(header_frame, text="CLOSE", bg="#FFD700", fg="black", width=10,
                          command=close_window)  # Updated button color
    close_btn.pack(side="right", padx=5, pady=5)

    title_frame = tk.Frame(root, bg="#223344")  # Updated title frame color
    title_frame.pack(fill="x", pady=10)

    title_label = tk.Label(title_frame, text="HOMEPAGE", font=("Arial", 20, "bold"), bg="#223344", fg="white")
    title_label.pack(side="left", padx=10)

    date_time_label = tk.Label(title_frame, font=("Arial", 20), bg="#223344", fg="white")
    date_time_label.pack(side="right", padx=10)

    def update_datetime():
        if not date_time_label.winfo_exists():
            return
        now = datetime.datetime.now()
        formatted_date = now.strftime("%A, %d %b %Y")
        current_time = strftime("%H:%M:%S")
        date_time_label.config(text=f"{formatted_date} {current_time}")
        date_time_label.after(1000, update_datetime)

    update_datetime()

    sub_header_frame = tk.Frame(root, bg="#FFD700", height=40)  # Updated sub-header color
    sub_header_frame.pack(fill="x")

    org_connect_label = tk.Label(sub_header_frame, text="ORGANISATION CONNECT", font=("Arial", 12, "bold"),
                                 bg="#223344", fg="white")
    org_connect_label.pack(side="left", padx=10)

    create_btn = tk.Button(sub_header_frame, text="CREATE", bg="#FFD700", fg="black", width=10,
                           command=lambda: open_create_org_page(username))  # Updated button color
    create_btn.pack(side="right", padx=5, pady=5)

    join_btn = tk.Button(sub_header_frame, text="JOIN", bg="#FFD700", fg="black", width=10,
                         command=lambda: open_join_org_page(username))  # Updated button color
    join_btn.pack(side="right", padx=5, pady=5)

    def refresh_page():
        fetch_and_display_organizations()

    refresh_btn = tk.Button(sub_header_frame, text="Refresh", bg="#FFD700", fg="black", width=10,
                            command=refresh_page)  # Updated button color
    refresh_btn.pack(side="right", padx=5, pady=5)

    divider_line = tk.Frame(root, bg="white", height=2)
    divider_line.pack(fill="x")

    content_frame = tk.Frame(root, bg="#223344")  # Updated content frame color
    content_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(content_frame, bg="#313244")  # Updated left panel color
    left_frame.place(relx=0.0, relwidth=0.67, relheight=1.0)

    left_label = tk.Label(left_frame, text="Organisations", bg="#313244", fg="white", font=("Arial", 12))
    left_label.pack(pady=10)

    canvas = tk.Canvas(left_frame, bg="#313244")  # Updated canvas color
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#313244")  # Updated scrollable frame color

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    separator = tk.Frame(content_frame, bg="white", width=2)
    separator.place(relx=0.67, relheight=1.0)

    right_frame = tk.Frame(content_frame, bg="#45475A")  # Updated right panel color
    right_frame.place(relx=0.67, relwidth=0.33, relheight=1.0)

    calendar_frame = tk.Frame(right_frame, bg="#45475A")  # Updated calendar frame color
    calendar_frame.place(relwidth=1, relheight=0.5)

    today = datetime.date.today()
    calendar = Calendar(calendar_frame, selectmode="day", year=today.year, month=today.month, day=today.day,
                        font=("Arial", 14), background="#89B4FA", foreground="black",
                        bordercolor="#45475A")  # Updated calendar colors
    calendar.pack(padx=10, pady=10, expand=True, fill="both")

    selected_date_label = tk.Label(calendar_frame, text="", bg="#45475A", fg="white", font=("Arial", 12))
    selected_date_label.pack(pady=5)

    def date_selected(event):
        selected_date = calendar.get_date()
        selected_date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y").date()
        if selected_date_obj == datetime.date(2025, 2, 11):
            selected_date_label.config(text="Review 1 Presentation scheduled for this date.")
        else:
            selected_date_label.config(text="Nothing scheduled for now.")

    calendar.bind("<<CalendarSelected>>", date_selected)

    notifications_frame = tk.Frame(right_frame, bg="#585B70")  # Updated notifications panel color
    notifications_frame.place(relwidth=1, relheight=0.45, rely=0.55)

    notifications_label = tk.Label(notifications_frame, text="Notifications", bg="#585B70", fg="white",
                                   font=("Arial", 12, "bold"))
    notifications_label.pack(pady=10)

    notification_text = tk.Text(notifications_frame, bg="#313244", fg="white", font=("Arial", 10), height=8,
                                wrap="word")
    notification_text.insert("1.0", "No new notifications.\n")
    notification_text.config(state="disabled")
    notification_text.pack(fill="both", expand=True, padx=10, pady=5)

    def delete_organization(org_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Do you really want to delete '{org_name}'?")
        if not confirm:
            return

        credentials = simpledialog.askstring(
            "Verification",
            "Enter Organization Password and Admin Email separated by a comma:"
        )

        if not credentials or "," not in credentials:
            messagebox.showerror("Error", "Both fields are required in the format 'password,email'!")
            return

        org_password, admin_email = map(str.strip, credentials.split(",", 1))

        if not org_password or not admin_email:
            messagebox.showerror("Error", "Password and email cannot be empty.")
            return

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT org_name FROM organizations WHERE org_name = %s AND LOWER(email) = %s AND org_password = %s",
                (org_name, admin_email.lower(), org_password)
            )
            result = cursor.fetchone()

            if result:
                members_table = f"{org_name}_members"
                cursor.execute(f"DROP TABLE IF EXISTS {members_table}")
                cursor.execute("DELETE FROM organizations WHERE org_name = %s", (org_name,))
                connection.commit()
                messagebox.showinfo("Success", f"Organization '{org_name}' deleted successfully.")
                fetch_and_display_organizations()
            else:
                messagebox.showerror("Error", "Invalid organization password or admin email.")

            connection.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def edit_organization(org_name):
        open_edit_org_page(org_name)

    def fetch_and_display_organizations():
        # Clear existing organization widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Fetch admin organizations
            cursor.execute(f"SELECT org_name FROM organizations WHERE admin = %s", (username,))
            admin_orgs = cursor.fetchall()

            for org_name, in admin_orgs:
                create_org_panel(scrollable_frame, f"Admin - {org_name}", "#89B4FA", org_name, True)  # Updated color

            # Fetch member organizations
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            for table_name, in tables:
                if table_name.endswith("_members"):
                    cursor.execute(f"SELECT user FROM {table_name} WHERE user = %s", (username,))
                    if cursor.fetchone():
                        org_name = table_name.replace("_members", "")
                        create_org_panel(scrollable_frame, f"Member - {org_name}", "#89B4FA", org_name,
                                         False)  # Updated color

            connection.close()
        except mysql.connector.Error as err:
            print("Error:", err)

    def create_org_panel(parent, text, color, org_name, is_admin):
        panel = tk.Frame(parent, bg=color, height=100, width=1000)
        panel.pack_propagate(False)
        panel.pack(pady=10, padx=5, fill="x")

        org_label = tk.Label(panel, text=text, font=("Arial", 25, "bold"), bg=color)
        org_label.pack(anchor="w", padx=10, pady=5)

        def open_dashboard():
            root.destroy()
            if is_admin:
                import admindash
                admindash.open_admin_dashboard(username, org_name)
            else:
                import userdash  # Updated import
                userdash.open_user_dashboard(org_name)  # Updated function call

        view_btn = tk.Button(panel, text="VIEW", bg="#FFD700", fg="black", width=12, height=2,  # Updated button color
                             command=open_dashboard)
        view_btn.place(relx=0.5, rely=0.5, anchor="center")

        if is_admin:
            edit_btn = tk.Button(panel, text="EDIT", bg="#FFD700", fg="black", width=12, height=2,
                                 # Updated button color
                                 command=lambda: edit_organization(org_name))
            edit_btn.place(relx=0.7, rely=0.5, anchor="center")

        delete_btn = tk.Button(panel, text="DELETE", bg="#FFD700", fg="black", width=12, height=2,
                               # Updated button color
                               command=lambda: delete_organization(org_name))
        delete_btn.place(relx=0.85, rely=0.5, anchor="center")

    fetch_and_display_organizations()
    root.mainloop()


if __name__ == "__main__":
    open_homepage("TestUser ")  # Replace "TestUser " with the actual username when integrating
