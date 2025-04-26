import tkinter as tk
from tkinter import messagebox
import mysql.connector
from PIL import Image, ImageTk

import home  # Keep as is

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shubham@1905",
    "database": "inventory"
}

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
        return None

def register():
    def submit_registration():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()

        if not new_username or not new_password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        conn = connect_db()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO user_table (username, password) VALUES (%s, %s)", (new_username, new_password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            register_window.destroy()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        finally:
            cursor.close()
            conn.close()

    register_window = tk.Toplevel(root)
    register_window.title("Register")
    register_window.geometry("500x500")
    register_window.configure(bg="#E0F7FA")

    header = tk.Label(register_window, text="User Registration", font=("Helvetica", 18, "bold"), bg="#E0F7FA", fg="#00796B")
    header.pack(pady=20)

    frame = tk.Frame(register_window, bg="white", bd=2, relief="ridge", padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(frame, text="New Username", bg="white", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=10)
    new_username_entry = tk.Entry(frame, font=("Helvetica", 12), width=25)
    new_username_entry.grid(row=0, column=1, pady=10)

    tk.Label(frame, text="New Password", bg="white", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=10)
    new_password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12), width=25)
    new_password_entry.grid(row=1, column=1, pady=10)

    register_btn = tk.Button(frame, text="Register", command=submit_registration, bg="#00796B", fg="white", font=("Helvetica", 12), width=20, bd=0)
    register_btn.grid(row=2, columnspan=2, pady=20)

def login(user_type):
    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in both fields.")
            return

        conn = connect_db()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM user_table WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()

            if user:
                messagebox.showinfo("Success", f"{user_type.capitalize()} Login Successful!")
                login_window.destroy()
                root.destroy()
                if user_type == "admin":
                    # Import and open admin dashboard
                    try:
                        from admindashboard import create_admin_dashboard
                        create_admin_dashboard()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to open admin dashboard: {str(e)}")
                else:
                    # Open home page for regular users
                    try:
                        import home
                        home.create_main_window(user[0])
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to open home page: {str(e)}")
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error during login: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    login_window = tk.Toplevel(root)
    login_window.title(f"{user_type.capitalize()} Login")
    login_window.geometry("500x500")
    login_window.configure(bg="#E3F2FD")

    header = tk.Label(login_window, text=f"{user_type.capitalize()} Login", font=("Helvetica", 18, "bold"), bg="#E3F2FD", fg="#0D47A1")
    header.pack(pady=20)

    frame = tk.Frame(login_window, bg="white", bd=2, relief="ridge", padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(frame, text="Username", bg="white", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=10)
    username_entry = tk.Entry(frame, font=("Helvetica", 12), width=25)
    username_entry.grid(row=0, column=1, pady=10)

    tk.Label(frame, text="Password", bg="white", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=10)
    password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12), width=25)
    password_entry.grid(row=1, column=1, pady=10)

    login_btn = tk.Button(frame, text="Login", command=attempt_login, bg="#0D47A1", fg="white", font=("Helvetica", 12), width=20, bd=0)
    login_btn.grid(row=2, columnspan=2, pady=20)

    if user_type == "user":
        tk.Label(frame, text="New user?", bg="white", font=("Helvetica", 10)).grid(row=3, column=0, pady=5)
        tk.Button(frame, text="Register Here", command=register, bg="#FF7043", fg="white", font=("Helvetica", 10), bd=0).grid(row=3, column=1, pady=5)

def create_gui():
    global root
    root = tk.Tk()
    root.title("Login Selection")

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window to full screen
    root.geometry(f"{screen_width}x{screen_height}")
    root.state('zoomed')

    # Load and place background image
    bg_image = Image.open("inventry.jpg")
    bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(root, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Keep a reference to the image to avoid garbage collection
    canvas.bg_photo = bg_photo

    # Place widgets on top of background
    canvas.create_text(screen_width // 2, 80, text="Welcome to ShelfSmart Login", font=("Helvetica", 22, "bold"), fill="#01579B")

    user_btn = tk.Button(root, text="User Login", command=lambda: login("user"), font=("Helvetica", 14),
                         width=20, height=2, bg="#0288D1", fg="white", bd=0)
    admin_btn = tk.Button(root, text="Admin Login", command=lambda: login("admin"), font=("Helvetica", 14),
                          width=20, height=2, bg="#00796B", fg="white", bd=0)

    # Place buttons on canvas
    canvas.create_window(screen_width // 2, 200, window=user_btn)
    canvas.create_window(screen_width // 2, 300, window=admin_btn)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
