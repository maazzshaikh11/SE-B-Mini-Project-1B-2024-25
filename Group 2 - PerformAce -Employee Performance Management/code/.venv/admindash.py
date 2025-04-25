import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
from time import strftime
import mysql.connector
import subprocess  # <-- Import added for Activity button
import login
from create_sections import open_create_sections_page
from tasks import open_task_manager
from tview import open_task_view_page

# Color Scheme
BACKGROUND_COLOR = "#223344"
LEFT_PANEL_COLOR = "#313244"
SCROLLABLE_FRAME_COLOR = "#89B4FA"
RIGHT_PANEL_COLOR = "#45475A"
NOTIFICATIONS_COLOR = "#585B70"
TEXT_COLOR = "white"
BUTTON_TEXT_COLOR = "black"
BUTTON_COLOR = "#FFD700"

def open_admin_dashboard(username=None, orgname=""):
    root = tk.Tk()
    root.title("Admin Dashboard")
    root.geometry("1600x750")

    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    center_window(root, 1600, 750)
    root.configure(bg=BACKGROUND_COLOR)

    header_frame = tk.Frame(root, bg=BUTTON_COLOR, height=50)
    header_frame.pack(fill="x")

    welcome_message = f"WELCOME TO {orgname.upper()} !!!" if orgname else "WELCOME ADMIN !!!"
    welcome_label = tk.Label(header_frame, text=welcome_message, font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    welcome_label.pack(side="left", padx=10)

    def logout():
        root.destroy()
        login.open_login_page()

    logout_btn = tk.Button(header_frame, text="LOG OUT", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, width=10, command=logout)
    logout_btn.pack(side="right", padx=5, pady=5)

    def close_window():
        root.destroy()

    close_btn = tk.Button(header_frame, text="CLOSE", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, width=10, command=close_window)
    close_btn.pack(side="right", padx=5, pady=5)

    def go_back():
        root.destroy()
        import homepage
        homepage.open_homepage(username)

    back_btn = tk.Button(header_frame, text="BACK", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, width=10, command=go_back)
    back_btn.pack(side="right", padx=5, pady=5)

    title_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
    title_frame.pack(fill="x", pady=10)

    title_text = f"ADMIN DASHBOARD - {orgname.upper()}" if orgname else "ADMIN DASHBOARD"
    title_label = tk.Label(title_frame, text=title_text, font=("Arial", 20, "bold"), bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    title_label.pack(side="left", padx=10)

    date_time_label = tk.Label(title_frame, font=("Arial", 20), bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    date_time_label.pack(side="right", padx=10)

    def update_datetime():
        now = datetime.datetime.now()
        formatted_date = now.strftime("%A, %d %b %Y")
        current_time = strftime("%H:%M:%S")
        date_time_label.config(text=f"{formatted_date} {current_time}")
        root.after(1000, update_datetime)

    update_datetime()

    sub_header_frame = tk.Frame(root, bg=BUTTON_COLOR, height=40)
    sub_header_frame.pack(fill="x")

    org_connect_label = tk.Label(sub_header_frame, text="ORGANIZATION CONNECT", font=("Arial", 12, "bold"),
                                 bg=BUTTON_COLOR, fg=TEXT_COLOR)
    org_connect_label.pack(side="left", padx=10)

    create_btn = tk.Button(sub_header_frame, text="CREATE SECTION", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, width=15,
                           command=lambda: open_create_sections_page(orgname))
    create_btn.pack(side="right", padx=5, pady=5)

    # Refresh Button
    refresh_btn = tk.Button(sub_header_frame, text="Refresh", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, width=10,
                            command=lambda: fetch_and_display_organizations())
    refresh_btn.pack(side="right", padx=5, pady=5)

    # Activity Button
    def open_task_stats():
        try:
            subprocess.Popen(["python", "task_stats.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Task Statistics: {e}")

    activity_btn = tk.Button(sub_header_frame, text="Activity", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, width=10,
                             command=open_task_stats)
    activity_btn.pack(side="right", padx=5, pady=5)

    divider_line = tk.Frame(root, bg="white", height=2)
    divider_line.pack(fill="x")

    content_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
    content_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(content_frame, bg=LEFT_PANEL_COLOR)
    left_frame.place(relx=0.0, relwidth=0.67, relheight=1.0)

    left_label = tk.Label(left_frame, text="Organizations", bg=LEFT_PANEL_COLOR, fg=TEXT_COLOR, font=("Arial", 12))
    left_label.pack(pady=10)

    canvas = tk.Canvas(left_frame, bg=LEFT_PANEL_COLOR)
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=SCROLLABLE_FRAME_COLOR)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    separator = tk.Frame(content_frame, bg="white", width=2)
    separator.place(relx=0.67, relheight=1.0)

    right_frame = tk.Frame(content_frame, bg=RIGHT_PANEL_COLOR)
    right_frame.place(relx=0.67, relwidth=0.33, relheight=1.0)

    calendar_frame = tk.Frame(right_frame, bg=RIGHT_PANEL_COLOR)
    calendar_frame.place(relwidth=1, relheight=0.5)

    today = datetime.date.today()
    calendar = Calendar(calendar_frame, selectmode="day", year=today.year, month=today.month, day=today.day,
                        font=("Arial", 14), background=BUTTON_COLOR, foreground="black", bordercolor=RIGHT_PANEL_COLOR)
    calendar.pack(padx=10, pady=10, expand=True, fill="both")

    selected_date_label = tk.Label(calendar_frame, text="No tasks scheduled for this date.", bg=RIGHT_PANEL_COLOR, fg=TEXT_COLOR, font=("Arial", 12))
    selected_date_label.pack(pady=5)

    tasks_by_date = {}

    def date_selected(event):
        selected_date = calendar.get_date()
        selected_date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y").date()
        selected_date_str = selected_date_obj.strftime("%Y-%m-%d")
        if selected_date_str in tasks_by_date:
            tasks = tasks_by_date[selected_date_str]
            selected_date_label.config(text="\n".join(tasks))
        else:
            selected_date_label.config(text="No tasks scheduled for this date.")

    calendar.bind("<<CalendarSelected>>", date_selected)

    notifications_frame = tk.Frame(right_frame, bg=NOTIFICATIONS_COLOR)
    notifications_frame.place(relwidth=1, relheight=0.45, rely=0.55)

    notifications_label = tk.Label(notifications_frame, text="Notifications", bg=NOTIFICATIONS_COLOR, fg=TEXT_COLOR,
                                   font=("Arial", 12, "bold"))
    notifications_label.pack(pady=10)

    notification_text = tk.Text(notifications_frame, bg=LEFT_PANEL_COLOR, fg=TEXT_COLOR, font=("Arial", 10), height=8,
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
                database="tasks"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            org_prefix = f"{orgname.lower()}_"
            relevant_tables = [t[0] for t in tables if t[0].lower().startswith(org_prefix)]

            if not relevant_tables:
                messagebox.showinfo("No Data", "No sections found for this organization.")

            for table_name in relevant_tables:
                section_name = table_name.replace(f"{orgname.lower()}_", "").replace("_tasks", "")
                create_section_panel(scrollable_frame, f"Section - {section_name}", SCROLLABLE_FRAME_COLOR, section_name)

            fetch_upcoming_tasks(cursor, orgname)
            check_tables_for_tasks(cursor)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching sections: {err}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'connection' in locals(): connection.close()

    def create_section_panel(parent, text, color, section_name):
        panel = tk.Frame(parent, bg=color, height=100, width=1050)
        panel.pack_propagate(False)
        panel.pack(pady=10, padx=5, fill="x")

        section_label = tk.Label(panel, text=text, font=("Arial", 20), bg=color, fg=BUTTON_TEXT_COLOR)
        section_label.pack(side="left", padx=10)

        add_button = tk.Button(panel, text="Add", command=lambda: open_task_manager(orgname, section_name), bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
        add_button.pack(side="right", padx=5)

        view_button = tk.Button(panel, text="View", command=lambda: open_task_view_page(orgname, section_name), bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
        view_button.pack(side="right", padx=5)

    def fetch_upcoming_tasks(cursor, orgname):
        try:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            task_tables = [t[0] for t in tables if t[0].startswith(f"{orgname.lower()}_") and t[0].endswith("_tasks")]

            if not task_tables:
                notification_text.config(state="normal")
                notification_text.delete("1.0", tk.END)
                notification_text.insert(tk.END, "No tasks found for this organization.")
                notification_text.config(state="disabled")
                return

            notification_text.config(state="normal")
            notification_text.delete("1.0", tk.END)
            notification_text.insert(tk.END, "Upcoming Tasks:\n\n")

            displayed_tasks = set()

            for table in task_tables:
                section = table.replace(f"{orgname.lower()}_", "").replace("_tasks", "")
                cursor.execute(
                    f"SELECT `task_name`, `task_type`, `submission_date` FROM `{table}` WHERE `submission_date` >= CURDATE() ORDER BY `submission_date` ASC"
                )
                tasks = cursor.fetchall()

                for task in tasks:
                    name, ttype, date = task
                    if name not in displayed_tasks:
                        notification_text.insert(tk.END, f"Section: {section}\nTask: {name}\nType: {ttype}\nSubmission Date: {date}\n")
                        notification_text.insert(tk.END, "-" * 126 + "\n")
                        displayed_tasks.add(name)

                        sdate = date.strftime("%Y-%m-%d")
                        if sdate not in tasks_by_date:
                            tasks_by_date[sdate] = []
                        tasks_by_date[sdate].append(f"{name} - {ttype}")

            notification_text.config(state="disabled")

        except mysql.connector.Error as err:
            notification_text.config(state="normal")
            notification_text.delete("1.0", tk.END)
            notification_text.insert(tk.END, f"Error fetching tasks: {err}\n")
            notification_text.config(state="disabled")

    def check_tables_for_tasks(cursor):
        global tasks_by_date
        tasks_by_date = {}

        try:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            for table in tables:
                cursor.execute(f"SHOW COLUMNS FROM `{table[0]}`")
                columns = [c[0] for c in cursor.fetchall()]

                if all(col in columns for col in ["task_name", "task_type", "submission_date"]):
                    cursor.execute(f"SELECT task_name, task_type, submission_date FROM `{table[0]}`")
                    tasks = cursor.fetchall()

                    for name, ttype, date in tasks:
                        sdate = date.strftime("%Y-%m-%d")
                        if sdate not in tasks_by_date:
                            tasks_by_date[sdate] = []
                        tasks_by_date[sdate].append(f"{name} - {ttype}")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error checking tables for tasks: {err}")

    fetch_and_display_organizations()
    root.mainloop()

if __name__ == "__main__":
    open_admin_dashboard("test_user", "Test Organization")
