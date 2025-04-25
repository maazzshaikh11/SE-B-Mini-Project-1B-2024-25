import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
from time import strftime
import mysql.connector
from tasks import open_task_manager
from tview2 import open_task_view_page


def open_user_dashboard(orgname="xyz", username="john"):
    root = tk.Tk()
    root.title("User Dashboard")
    root.geometry("1600x750")

    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    center_window(root, 1600, 750)
    root.configure(bg="#223344")

    header_frame = tk.Frame(root, bg="#A4D07B", height=50)
    header_frame.pack(fill="x")

    welcome_message = f"WELCOME TO {orgname.upper()} !!!" if orgname else "WELCOME USER !!!"
    welcome_label = tk.Label(header_frame, text=welcome_message, font=("Arial", 12, "bold"), bg="#A4D07B", fg="blue")
    welcome_label.pack(side="left", padx=10)

    def go_back():
        root.destroy()
        import homepage
        homepage.open_homepage()

    back_btn = tk.Button(header_frame, text="BACK", bg="lightyellow", fg="black", width=10, command=go_back)
    back_btn.pack(side="left", padx=5, pady=5)

    def logout():
        root.destroy()
        import login
        login.open_login_page()

    logout_btn = tk.Button(header_frame, text="LOG OUT", bg="lightyellow", fg="black", width=10, command=logout)
    logout_btn.pack(side="right", padx=5, pady=5)

    def close_window():
        root.destroy()

    close_btn = tk.Button(header_frame, text="CLOSE", bg="lightyellow", fg="black", width=10, command=close_window)
    close_btn.pack(side="right", padx=5, pady=5)

    title_frame = tk.Frame(root, bg="#223344")
    title_frame.pack(fill="x", pady=10)

    title_text = f"USER DASHBOARD - {orgname.upper()}" if orgname else "USER DASHBOARD"
    title_label = tk.Label(title_frame, text=title_text, font=("Arial", 20, "bold"), bg="#223344", fg="white")
    title_label.pack(side="left", padx=10)

    date_time_label = tk.Label(title_frame, font=("Arial", 20), bg="#223344", fg="white")
    date_time_label.pack(side="right", padx=10)

    def update_datetime():
        now = datetime.datetime.now()
        formatted_date = now.strftime("%A, %d %b %Y")
        current_time = strftime("%H:%M:%S")
        date_time_label.config(text=f"{formatted_date} {current_time}")
        root.after(1000, update_datetime)

    update_datetime()

    sub_header_frame = tk.Frame(root, bg="#A4D07B", height=40)
    sub_header_frame.pack(fill="x")

    org_connect_label = tk.Label(sub_header_frame, text="ORGANIZATION CONNECT", font=("Arial", 12, "bold"),
                                 bg="#A4D07B")
    org_connect_label.pack(side="left", padx=10)

    refresh_btn = tk.Button(sub_header_frame, text="Refresh", bg="lightgray", fg="black", width=10,
                            command=lambda: fetch_and_display_organizations())
    refresh_btn.pack(side="right", padx=5, pady=5)

    divider_line = tk.Frame(root, bg="white", height=2)
    divider_line.pack(fill="x")

    content_frame = tk.Frame(root, bg="#223344")
    content_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(content_frame, bg="#445566")
    left_frame.place(relx=0.0, relwidth=0.67, relheight=1.0)

    left_label = tk.Label(left_frame, text="Sections", bg="#445566", fg="white", font=("Arial", 12))
    left_label.pack(pady=10)

    canvas = tk.Canvas(left_frame, bg="#445566", highlightthickness=0)
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#445566")

    scrollable_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def resize_scrollable_frame(event):
        canvas.itemconfig(scrollable_id, width=event.width)

    canvas.bind("<Configure>", resize_scrollable_frame)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    separator = tk.Frame(content_frame, bg="white", width=2)
    separator.place(relx=0.67, relheight=1.0)

    right_frame = tk.Frame(content_frame, bg="#556677")
    right_frame.place(relx=0.67, relwidth=0.33, relheight=1.0)

    calendar_frame = tk.Frame(right_frame, bg="#556677")
    calendar_frame.place(relwidth=1, relheight=0.5)

    today = datetime.date.today()
    calendar = Calendar(calendar_frame, selectmode="day", year=today.year, month=today.month, day=today.day,
                        font=("Arial", 14), background="#A4D07B", foreground="black", bordercolor="#556677")
    calendar.pack(padx=10, pady=10, expand=True, fill="both")

    selected_date_label = tk.Label(calendar_frame, text="", bg="#556677", fg="white", font=("Arial", 12))
    selected_date_label.pack(pady=5)

    def date_selected(event):
        selected_date = calendar.get_date()
        selected_date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y").date()

        if selected_date_obj == datetime.date(2025, 2, 11):
            selected_date_label.config(text="Review 1 Presentation scheduled for this date.")
        else:
            selected_date_label.config(text="Nothing scheduled for now.")

    calendar.bind("<<CalendarSelected>>", date_selected)

    notifications_frame = tk.Frame(right_frame, bg="#667788")
    notifications_frame.place(relwidth=1, relheight=0.45, rely=0.55)

    notifications_label = tk.Label(notifications_frame, text="Notifications", bg="#667788", fg="white",
                                   font=("Arial", 12, "bold"))
    notifications_label.pack(pady=10)

    notification_text = tk.Text(notifications_frame, bg="#445566", fg="white", font=("Arial", 10), height=8,
                                wrap="word")
    notification_text.insert("1.0", "No new notifications.\n")
    notification_text.config(state="disabled")
    notification_text.pack(fill="both", expand=True, padx=10, pady=5)

    def fetch_and_display_organizations():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="TuViZa@2345",
                database="sections"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            org_prefix = f"{orgname.lower()}_"
            relevant_tables = [table_name[0] for table_name in tables if table_name[0].lower().startswith(org_prefix)]

            if not relevant_tables:
                messagebox.showinfo("No Data", "No sections found for this organization.")
                return

            for table_name in relevant_tables:
                section_name = table_name.replace(f"{orgname.lower()}_", "")
                create_section_panel(scrollable_frame, f"Section - {section_name}", "#A4D07B", section_name)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching sections: {err}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()

    def create_section_panel(parent, text, color, section_name):
        section_frame = tk.Frame(parent, bg=color, relief="solid", bd=2)
        section_frame.pack(fill="x", pady=5, padx=5)

        section_frame.grid_columnconfigure(0, weight=1)

        section_label = tk.Label(section_frame, text=text, bg=color, fg="black", font=("Arial", 12, "bold"))
        section_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        open_btn = tk.Button(section_frame, text="Open", bg="lightgreen", fg="black",
                             command=lambda: validate_and_open_tview(orgname, section_name, username))

        open_btn.grid(row=0, column=1, sticky="e", padx=10, pady=10)

    def validate_and_open_tview(orgname, section_name, username):
        print(f"[DEBUG] Opening TView with username: {username}")
        open_task_view_page(orgname, section_name, username)

    fetch_and_display_organizations()
    root.mainloop()