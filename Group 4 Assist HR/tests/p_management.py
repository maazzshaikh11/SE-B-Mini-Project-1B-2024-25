payroll_window = Toplevel(parent)
payroll_window.title("Payroll Management")
payroll_window.configure(background="#FFDD95")

columns = ("Name", "Role", "Department", "Compensation", "Status")
tree = ttk.Treeview(payroll_window, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

payroll_data = [
    ("Alice Johnson", "Manager", "HR", "$80,000", "Paid"),
    ("Bob Smith", "Developer", "IT", "$95,000", "Unpaid"),
    ("Charlie Brown", "Executive", "Marketing", "$70,000", "Paid"),
    ("David White", "Analyst", "Finance", "$85,000", "Unpaid"),
    ("Eve Adams", "Representative", "Sales", "$60,000", "Paid")
]

for payroll in payroll_data:
    tree.insert("", "end", values=payroll)

Button(payroll_window, text="Close", command=payroll_window.destroy, font=('Arial', 15, 'bold')).pack(pady=10)

if __name__ == "__main__":
    window = Tk()
    employee_management(window)
    payroll_management(window)
    window.mainloop()
