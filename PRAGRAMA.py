import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import datetime

# --- 1. მონაცემთა ბაზის ფენა ---
class SalesDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL, stock REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS customers 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT UNIQUE, bonus_points REAL DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, customer_id INTEGER, 
             qty REAL, total_gel REAL, used_points REAL, tarigi TEXT)''')
        self.conn.commit()

    def get_customer_by_phone(self, phone):
        self.cursor.execute("SELECT id, name, bonus_points FROM customers WHERE phone = ?", (phone,))
        return self.cursor.fetchone()

    def add_new_customer(self, name, phone):
        try:
            self.cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
            self.conn.commit()
            return True
        except: return False

    def finalize_sale_transaction(self, p_id, c_id, qty, total_cash, points_used, points_earned):
        try:
            self.conn.execute("BEGIN TRANSACTION")
            # 1. მარაგის შემცირება
            self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, p_id))
            # 2. ბონუსების მართვა
            if c_id:
                net_change = points_earned - points_used
                self.cursor.execute("UPDATE customers SET bonus_points = bonus_points + ? WHERE id = ?", (net_change, c_id))
            # 3. გაყიდვის ჩაწერა
            tarigi = datetime.date.today().strftime("%Y-%m-%d")
            self.cursor.execute("""INSERT INTO sales (product_id, customer_id, qty, total_gel, used_points, tarigi) 
                                   VALUES (?, ?, ?, ?, ?, ?)""", (p_id, c_id, qty, total_cash, points_used, tarigi))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
            return False

# --- 2. აპლიკაციის ინტერფეისი ---
class SalesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise POS System v4.0")
        self.root.geometry("600x700")
        self.db = SalesDatabase("Business_Final_v4.db")

        # --- UI Layout ---
        tk.Label(root, text="გამყიდველის პანელი", font=('Arial', 14, 'bold')).pack(pady=10)

        # მომხმარებლის ძებნა
        frame_cust = tk.LabelFrame(root, text="მომხმარებელი (ბონუს სისტემა)")
        frame_cust.pack(pady=10, padx=20, fill="x")
        tk.Label(frame_cust, text="ტელეფონი:").grid(row=0, column=0, padx=5)
        self.ent_phone = tk.Entry(frame_cust); self.ent_phone.grid(row=0, column=1, pady=5)
        
        # გაყიდვის სექცია
        frame_sale = tk.LabelFrame(root, text="გაყიდვის გაფორმება")
        frame_sale.pack(pady=10, padx=20, fill="x")
        
        tk.Label(frame_sale, text="პროდუქტი:").grid(row=0, column=0, padx=5)
        self.cursor = self.db.cursor
        self.cursor.execute("SELECT name FROM products")
        products = [r[0] for r in self.cursor.fetchall()]
        self.combo_prod = ttk.Combobox(frame_sale, values=products); self.combo_prod.grid(row=0, column=1, pady=5)
        
        tk.Label(frame_sale, text="რაოდენობა:").grid(row=1, column=0, padx=5)
        self.ent_qty = tk.Entry(frame_sale); self.ent_qty.grid(row=1, column=1, pady=5); self.ent_qty.insert(0, "1")

        tk.Button(root, text="გაყიდვის დასრულება", bg="green", fg="white", font=('Arial', 10, 'bold'),
                  command=self.execute_sale).pack(pady=20)

        # მომხმარებლის რეგისტრაცია (სწრაფი ღილაკი)
        tk.Button(root, text="ახალი მომხმარებლის რეგისტრაცია", command=self.reg_customer_window).pack()

    def execute_sale(self):
        try:
            prod_name = self.combo_prod.get()
            qty = float(self.ent_qty.get())
            phone = self.ent_phone.get().strip()

            self.cursor.execute("SELECT id, price, stock FROM products WHERE name = ?", (prod_name,))
            product = self.cursor.fetchone()

            if not product or product[2] < qty:
                messagebox.showerror("შეცდომა", "პროდუქტი არ არის ან მარაგი არასაკმარისია!")
                return

            p_id, price, stock = product
            total_price = price * qty
            used_points = 0
            points_earned = total_price * 0.05 * 100 # 5% ბონუსი
            
            customer = self.db.get_customer_by_phone(phone)
            c_id = customer[0] if customer else None

            if customer:
                c_points = customer[2]
                if c_points >= 100 and messagebox.askyesno("ბონუსი", f"მომხმარებელს აქვს {c_points} ქულა. გამოვიყენოთ?"):
                    points_in_gel = c_points / 100
                    if points_in_gel >= total_price:
                        used_points = total_price * 100
                        total_price = 0
                    else:
                        used_points = c_points
                        total_price -= points_in_gel

            if self.db.finalize_sale_transaction(p_id, c_id, qty, total_price, used_points, points_earned):
                messagebox.showinfo("წარმატება", f"გაიყიდა! გადასახდელი: {total_price:.2f} GEL")
            else:
                messagebox.showerror("შეცდომა", "ტრანზაქცია ჩაიშალა!")

        except ValueError:
            messagebox.showerror("შეცდომა", "შეიყვანეთ სწორი რაოდენობა!")

    def reg_customer_window(self):
        # პატარა ფანჯარა რეგისტრაციისთვის
        reg_win = tk.Toplevel(self.root)
        reg_win.title("რეგისტრაცია")
        tk.Label(reg_win, text="სახელი:").pack()
        name_ent = tk.Entry(reg_win); name_ent.pack()
        tk.Label(reg_win, text="ტელეფონი:").pack()
        phone_ent = tk.Entry(reg_win); phone_ent.pack()
        
        def save():
            if self.db.add_new_customer(name_ent.get(), phone_ent.get()):
                messagebox.showinfo("OK", "დარეგისტრირდა!")
                reg_win.destroy()
            else: messagebox.showerror("Error", "ნომერი უკვე არსებობს!")
        
        tk.Button(reg_win, text="შენახვა", command=save).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesApp(root)
    root.mainloop()