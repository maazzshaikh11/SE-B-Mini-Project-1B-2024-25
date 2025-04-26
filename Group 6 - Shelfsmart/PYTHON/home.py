import tkinter as tk
from tkinter import messagebox

# Admin defined prices for products
PRODUCTS = {
    "Snacks": {
        "Chips": 15,
        "Cookies": 20,
        "Soda": 10,
        "Candy": 5,
        "Nuts": 30,
    },
    "Grocery": {
        "Rice": 45,
        "Wheat": 50,
        "Oil": 0,
        "Sugar": 40,
        "Salt": 40,
    },
    "Stationery": {
        "Pen": 10,
        "Notebook": 60,
        "Pencil": 5,
        "Eraser": 5,
        "Sharpener": 5,
    }
}

cart = {}

def update_cart():
    cart_text = "Your Cart:\n"
    total = 0
    for category in PRODUCTS:
        for product, price in PRODUCTS[category].items():
            if product in cart and cart[product] > 0:
                cart_text += f"{product}: {cart[product]} x ₹{price} = ₹{cart[product] * price}\n"
                total += cart[product] * price
    cart_text += f"\nTotal: ₹{total:.2f}"
    cart_label.config(text=cart_text)

def change_quantity(product, change, quantity_label):
    """Change the quantity of a product"""
    if product not in cart:
        cart[product] = 0
    cart[product] += change
    
    if cart[product] < 0:
        cart[product] = 0
    
    # Update the quantity label in the category window
    quantity_label.config(text=str(cart[product]))
    update_cart()

def create_category_window(category, products):
    category_window = tk.Toplevel(root)
    category_window.title(category)
    category_window.geometry("700x800")
    
    category_window.config(bg="#f0f8ff")
    
    # Title with modern styling
    title_frame = tk.Frame(category_window, bg="#f0f8ff")
    title_frame.pack(fill=tk.X, pady=20)
    
    tk.Label(title_frame,
             text=f"🛍️ {category} - Select Products",
             font=("Segoe UI", 28, "bold"),
             bg="#f0f8ff",
             fg="#2c3e50").pack()
    
    # Create scrollable frame for products
    canvas = tk.Canvas(category_window, bg="#f0f8ff", highlightthickness=0)
    scrollbar = tk.Scrollbar(category_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    for product, price in products.items():
        # Create card-like frame for each product
        frame = tk.Frame(scrollable_frame, bg="white", relief="solid", borderwidth=1)
        frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Product name with modern styling
        tk.Label(frame,
                text=product,
                width=20,
                anchor="w",
                font=("Segoe UI", 14),
                bg="white",
                fg="#2c3e50").grid(row=0, column=0, padx=10, pady=10)
        
        # Price with modern styling
        tk.Label(frame,
                text=f"💰 ₹{price:.2f}",
                width=10,
                font=("Segoe UI", 14),
                bg="white",
                fg="#e74c3c").grid(row=0, column=1, padx=10, pady=10)
        
        # Show current quantity in cart
        current_quantity = cart.get(product, 0)
        quantity_label = tk.Label(frame,
                                text=str(current_quantity),
                                width=5,
                                anchor="center",
                                font=("Segoe UI", 14),
                                bg="white",
                                fg="#2c3e50")
        quantity_label.grid(row=0, column=3, padx=10, pady=10)
        
        # Quantity buttons with modern styling
        minus_btn = tk.Button(frame,
                            text="➖",
                            command=lambda p=product, q=quantity_label: change_quantity(p, -1, q),
                            font=("Segoe UI", 14),
                            bg="#e74c3c",
                            fg="white",
                            activebackground="#c0392b",
                            relief="flat",
                            borderwidth=0,
                            cursor="hand2")
        minus_btn.grid(row=0, column=2, padx=5, pady=10)
        
        plus_btn = tk.Button(frame,
                           text="➕",
                           command=lambda p=product, q=quantity_label: change_quantity(p, 1, q),
                           font=("Segoe UI", 14),
                           bg="#2ecc71",
                           fg="white",
                           activebackground="#27ae60",
                           relief="flat",
                           borderwidth=0,
                           cursor="hand2")
        plus_btn.grid(row=0, column=4, padx=5, pady=10)

def show_category(category):
    """Show the products in a selected category"""
    create_category_window(category, PRODUCTS[category])

def create_main_window(user_id=None):
    global root, cart_label
    root = tk.Tk()
    root.title("Grocery Shopping")
    
    # Make window full screen
    root.state('zoomed')
    
    # Set modern color scheme with gradient background
    root.config(bg="#f0f8ff")  # Light blue background
    
    # Create main container with padding
    main_container = tk.Frame(root, bg="#f0f8ff")
    main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    
    # Header section with gradient effect
    header_frame = tk.Frame(main_container, bg="#f0f8ff")
    header_frame.pack(fill=tk.X, pady=(0, 30))
    
    # Title with modern styling and gradient effect
    title_frame = tk.Frame(header_frame, bg="#f0f8ff")
    title_frame.pack(fill=tk.X)
    
    # Welcome message with user ID
    welcome_label = tk.Label(title_frame, 
                           text=f"👋 Welcome, User #{user_id if user_id else 'Guest'}!",
                           font=("Segoe UI", 16),
                           bg="#f0f8ff",
                           fg="#4a4a4a")
    welcome_label.pack(anchor="w")
    
    # Main title with modern styling
    title_label = tk.Label(title_frame, 
                          text="🛍️ Grocery Shopping",
                          font=("Segoe UI", 36, "bold"),
                          bg="#f0f8ff",
                          fg="#2c3e50")
    title_label.pack(pady=(5, 0))
    
    # Create two-column layout with modern styling
    content_frame = tk.Frame(main_container, bg="#f0f8ff")
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Left column for categories with card-like appearance
    left_frame = tk.Frame(content_frame, bg="#f0f8ff")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
    
    # Categories label with modern styling
    categories_label = tk.Label(left_frame, 
                              text="📦 Categories",
                              font=("Segoe UI", 24, "bold"),
                              bg="#f0f8ff",
                              fg="#2c3e50")
    categories_label.pack(pady=(0, 15))
    
    # Create scrollable frame for categories with modern styling
    canvas = tk.Canvas(left_frame, bg="#f0f8ff", highlightthickness=0)
    scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Add category buttons with modern styling
    for category in PRODUCTS:
        btn_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
        btn_frame.pack(pady=8, fill=tk.X)
        
        btn = tk.Button(btn_frame, 
                       text=f"📦 {category}",
                       width=25,
                       height=2,
                       command=lambda c=category: show_category(c),
                       font=("Segoe UI", 12),
                       bg="#4169e1",  # Royal Blue
                       fg="white",
                       activebackground="#1e40af",
                       relief="flat",
                       borderwidth=0,
                       cursor="hand2",
                       padx=20)
        btn.pack(fill=tk.X, padx=5)
    
    # Right column for cart and payment with modern styling
    right_frame = tk.Frame(content_frame, bg="#f0f8ff")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
    
    # Cart section with card-like appearance
    cart_frame = tk.Frame(right_frame, bg="white", relief="solid", borderwidth=1)
    cart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    # Cart title with modern styling
    cart_title_frame = tk.Frame(cart_frame, bg="white")
    cart_title_frame.pack(fill=tk.X, pady=(15, 10))
    
    tk.Label(cart_title_frame,
             text="🛒 Your Shopping Cart",
             font=("Segoe UI", 24, "bold"),
             bg="white",
             fg="#2c3e50").pack(side=tk.LEFT, padx=15)
    
    # Cart content with modern styling
    cart_label = tk.Label(cart_frame,
                         text="Your Cart:\nTotal: ₹0.00",
                         anchor="w",
                         justify="left",
                         font=("Segoe UI", 14),
                         bg="white",
                         fg="#34495e",
                         padx=15,
                         pady=10)
    cart_label.pack(fill=tk.X, pady=10)
    
    # Payment button with modern styling
    payment_btn = tk.Button(right_frame,
                          text="💳 Proceed to Payment",
                          width=25,
                          height=2,
                          command=go_to_payment_page,
                          bg="#4169e1",  # Royal Blue
                          fg="white",
                          activebackground="#1e40af",
                          font=("Segoe UI", 14, "bold"),
                          relief="flat",
                          borderwidth=0,
                          cursor="hand2")
    payment_btn.pack(pady=20)

    root.mainloop()

def go_to_payment_page():
    """Open the payment page"""
    total = 0
    for category in PRODUCTS:
        for product, price in PRODUCTS[category].items():
            if product in cart and cart[product] > 0:
                total += cart[product] * price
    
    if total == 0:
        messagebox.showinfo("Payment", "Your cart is empty. Please add products to your cart before proceeding.")
    else:
        # Show payment page with UPI ID input and total amount
        create_payment_page(total)

def create_payment_page(total_amount):
    """Create the payment page"""
    payment_window = tk.Toplevel(root)
    payment_window.title("Payment")
    payment_window.geometry("500x400")
    
    # Set modern color scheme
    payment_window.config(bg="#f0f8ff")  # Light blue background
    
    # Header with modern styling
    header_frame = tk.Frame(payment_window, bg="#f0f8ff")
    header_frame.pack(fill=tk.X, pady=20)
    
    tk.Label(header_frame, text="💳 Payment Page", font=("Segoe UI", 24, "bold"), bg="#f0f8ff", fg="#2c3e50").pack()
    
    # Display total amount with modern styling
    amount_frame = tk.Frame(payment_window, bg="white", relief="solid", borderwidth=1)
    amount_frame.pack(fill=tk.X, padx=40, pady=10)
    
    tk.Label(amount_frame, text=f"Total Amount: ₹{total_amount:.2f}", font=("Segoe UI", 18), bg="white", fg="#e74c3c").pack(pady=10)
    
    # UPI ID Entry with modern styling
    upi_frame = tk.Frame(payment_window, bg="#f0f8ff")
    upi_frame.pack(fill=tk.X, padx=40, pady=10)
    
    tk.Label(upi_frame, text="Enter UPI ID", font=("Segoe UI", 14), bg="#f0f8ff", fg="#2c3e50").pack(anchor="w")
    upi_entry = tk.Entry(upi_frame, font=("Segoe UI", 14), relief="solid", borderwidth=1)
    upi_entry.pack(fill=tk.X, pady=5)
    
    # Confirm Payment Button with modern styling
    def confirm_payment():
        upi_id = upi_entry.get()
        if not upi_id:
            messagebox.showerror("Error", "Please enter a valid UPI ID.")
            return
        response = messagebox.askyesno("Payment Confirmation", f"Your total is ₹{total_amount:.2f}. Do you want to proceed with the payment?")
        if response:
            # Show payment success message
            success_window = tk.Toplevel(payment_window)
            success_window.title("Payment Success")
            success_window.geometry("400x200")
            success_window.config(bg="#f0f8ff")
            
            # Center the success window
            screen_width = success_window.winfo_screenwidth()
            screen_height = success_window.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 200) // 2
            success_window.geometry(f"400x200+{x}+{y}")
            
            # Success message
            tk.Label(success_window,
                    text="✅ Payment Successful!",
                    font=("Segoe UI", 16, "bold"),
                    bg="#f0f8ff",
                    fg="#27ae60").pack(pady=20)
            
            # Thank you message
            tk.Label(success_window,
                    text="Thank you for shopping with us!",
                    font=("Segoe UI", 12),
                    bg="#f0f8ff",
                    fg="#34495e").pack(pady=10)
            
            # OK button
            ok_btn = tk.Button(success_window,
                             text="OK",
                             command=lambda: [success_window.destroy(), payment_window.destroy()],
                             font=("Segoe UI", 12, "bold"),
                             bg="#4169e1",
                             fg="white",
                             activebackground="#1e40af",
                             relief="flat",
                             borderwidth=0,
                             cursor="hand2",
                             width=10)
            ok_btn.pack(pady=20)
            
            # Make the success window modal
            success_window.transient(payment_window)
            success_window.grab_set()
            payment_window.wait_window(success_window)
            
            # Clear cart and close payment window
            clear_cart()
            
            # Open feedback window
            try:
                from feedback import create_feedback_window
                create_feedback_window()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open feedback window: {str(e)}")
    
    confirm_btn = tk.Button(payment_window, text="Confirm Payment", width=20, height=2, command=confirm_payment, bg="#4169e1", fg="white", font=("Segoe UI", 14, "bold"), relief="flat", borderwidth=0, cursor="hand2")
    confirm_btn.pack(pady=20)

def clear_cart():
    """Clear the cart after payment"""
    global cart
    cart = {}
    update_cart()

if __name__ == "__main__":
    create_main_window("default_user")  # Set a default user ID when running directly