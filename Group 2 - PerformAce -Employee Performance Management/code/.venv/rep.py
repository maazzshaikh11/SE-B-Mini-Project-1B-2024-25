import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tkinter.simpledialog as simpledialog
import os

# MySQL connection config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TuViZa@2345',
    'database': 'tasks'
}

ADMIN_DATE = datetime(2025, 4, 15)

class ReportApp:
    def __init__(self, master):
        self.master = master
        master.title("Submission Report")

        # Center the window on the screen
        window_width = 800
        window_height = 400
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        master.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        self.tree = ttk.Treeview(master, columns=("Name", "Submission", "Remark", "Rating", "Score", "Position"),
                                 show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(pady=20)

        self.tree.bind("<Double-1>", self.on_item_double_click)  # Bind double-click for editing
        self.tree.bind("<ButtonRelease-1>", self.on_item_click)  # Bind single-click to view details

        btn_frame = tk.Frame(master)
        btn_frame.pack()

        tk.Button(btn_frame, text="Download CSV", command=self.export_csv).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Download PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=10)

        self.modified_records = []  # Temporary storage for modified data
        self.load_data()

    def on_item_double_click(self, event):
        """ Allows editing of Remark and Rating on double-click """
        item = self.tree.selection()[0]
        col = self.tree.identify_column(event.x)

        if col == "#3":  # Remark column
            old_value = self.tree.item(item, "values")[2]
            new_value = self.prompt_for_input("Edit Remark", old_value)
            if new_value is not None:
                self.tree.item(item,
                               values=(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1], new_value,
                                       self.tree.item(item, "values")[3], self.tree.item(item, "values")[4],
                                       self.tree.item(item, "values")[5]))
                self.save_modified_data(item, "remark", new_value)  # Save change locally
        elif col == "#4":  # Rating column
            old_value = self.tree.item(item, "values")[3]
            new_value = self.prompt_for_input("Edit Rating", old_value)
            if new_value is not None and new_value.isdigit():
                new_value = int(new_value)
                new_score = self.calculate_score(new_value, self.tree.item(item, "values")[1])
                self.tree.item(item, values=(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1],
                                             self.tree.item(item, "values")[2], new_value,
                                             new_score,
                                             self.tree.item(item, "values")[5]))
                self.save_modified_data(item, "rating", new_value, new_score)  # Save change locally

    def on_item_click(self, event):
        """ Opens the details window for the clicked item """
        # No need to check selected row, view all data directly
        self.view_task_details()

    def prompt_for_input(self, title, old_value):
        """ Prompt for user input """
        input_value = simpledialog.askstring(title, f"Current Value: {old_value}\nEnter new value:")
        return input_value

    def calculate_score(self, rating, submission_status):
        """ Calculate score based on submission status """
        if submission_status == "Early":
            return 1.2 * rating
        elif submission_status == "On Time":
            return 1 * rating
        elif submission_status == "Late":
            return 0.8 * rating
        return 0

    def load_data(self):
        self.records = []
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Fetch column names for '111_estate_submissions' table
            cursor.execute("SHOW COLUMNS FROM `111_estate_submissions`")
            all_columns = [col[0] for col in cursor.fetchall()]

            # Select even-indexed columns (names are stored in these columns)
            names = all_columns[1::2]  # Even-indexed columns (2, 4, 6, etc.)
            # Select odd-indexed columns (dates are stored in these columns)
            dates = all_columns[2::2]  # Odd-indexed columns (3, 5, 7, etc.)

            # Query the data from '111_estate_submissions'
            cursor.execute("SELECT * FROM `111_estate_submissions`")
            rows = cursor.fetchall()

            # Loop through each row to get names (from even columns) and dates (from odd columns)
            for row in rows:
                for name_col, date_col in zip(names, dates):
                    name = name_col  # Column name is used as the name
                    date_str = row[all_columns.index(date_col)]

                    try:
                        submitted_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                    except:
                        submitted_date = ADMIN_DATE

                    # Determine submission status
                    if submitted_date < ADMIN_DATE:
                        submission = "Early"
                        factor = 1.2
                    elif submitted_date == ADMIN_DATE:
                        submission = "On Time"
                        factor = 1.0
                    else:
                        submission = "Late"
                        factor = 0.8

                    rating = 10  # Default static rating
                    remark = "N/A"
                    score = factor * rating

                    # Add the record to the temporary list (modified_records)
                    self.modified_records.append([name, submission, remark, rating, score])

            # Calculate position based on score
            self.modified_records.sort(key=lambda x: x[4], reverse=True)
            for i, rec in enumerate(self.modified_records):
                rec.append(i + 1)

            # Insert rows into treeview widget
            for row in self.modified_records:
                self.tree.insert('', 'end', values=row)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def save_modified_data(self, item, field, new_value, new_score=None):
        """ Save modified data into the temporary records array """
        index = self.tree.index(item)
        if field == "remark":
            self.modified_records[index][2] = new_value  # Update remark
        elif field == "rating":
            self.modified_records[index][3] = new_value  # Update rating
            if new_score is not None:
                self.modified_records[index][4] = new_score  # Update score

        # Recalculate the position
        self.modified_records.sort(key=lambda x: x[4], reverse=True)
        for i, rec in enumerate(self.modified_records):
            rec[5] = i + 1  # Update position

    def refresh_data(self):
        """ Refresh the data and re-sort the rows """
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Reinsert the modified data
        for row in self.modified_records:
            self.tree.insert('', 'end', values=row)

    def view_task_details(self):
        """ This method has been intentionally left blank. """
        pass

    def export_csv(self):
        try:
            # Ensure the directory exists
            if not os.path.exists("C:/reports"):
                os.makedirs("C:/reports")

            file_path = "C:/reports/report.csv"
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Submission", "Remark", "Rating", "Score", "Position"])
                for row in self.modified_records:
                    writer.writerow(row)
            messagebox.showinfo("Export", f"CSV file saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def export_pdf(self):
        try:
            # Ensure the directory exists
            if not os.path.exists("C:/reports"):
                os.makedirs("C:/reports")

            file_path = "C:/reports/report.pdf"
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, height - 50, "Submission Report")

            y = height - 80
            headers = ["Name", "Submission", "Remark", "Rating", "Score", "Position"]
            c.setFont("Helvetica", 10)
            for i, header in enumerate(headers):
                c.drawString(50 + i * 80, y, header)

            y -= 20
            for row in self.modified_records:
                for i, val in enumerate(row):
                    c.drawString(50 + i * 80, y, str(val))
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()
            messagebox.showinfo("Export", f"PDF file saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()
