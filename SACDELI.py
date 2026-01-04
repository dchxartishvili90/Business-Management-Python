import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- 1. მონაცემთა ბაზა ---
class SalesDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL, stock REAL DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS customers
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT UNIQUE, bonus_points REAL DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, customer_id INTEGER, 
             qty REAL, total_gel REAL, used_points REAL, tarigi TEXT)''')
        self.conn.commit()

    def get_all_products(self):
        return pd.read_sql_query("SELECT * FROM products", self.conn)

    def get_customer(self, phone):
        self.cursor.execute("SELECT id, name, bonus_points FROM customers WHERE phone=?", (phone,))
        return self.cursor.fetchone()

    def add_customer(self, name, phone):
        try:
            self.cursor.execute("INSERT INTO customers (name, phone, bonus_points) VALUES(?,?,0)", (name, phone))
            self.conn.commit()
            return True
        except: return False

    def add_product(self, name, price, stock):
        self.cursor.execute("INSERT OR REPLACE INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        self.conn.commit()

    def finalize_sale_transaction(self, p_id, c_id, qty, total_cash, points_used, points_earned):
        try:
            self.conn.execute("BEGIN TRANSACTION")
            # მარაგიდან ჩამოკლება
            self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, p_id))
            # ქულების განახლება
            if c_id:
                net_points = points_earned - points_used
                self.cursor.execute("UPDATE customers SET bonus_points = bonus_points + ? WHERE id = ?", (net_points, c_id))
            # გაყიდვის ჩაწერა
            tarigi = datetime.date.today().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO sales (product_id, customer_id, qty, total_gel, used_points, tarigi) VALUES (?,?,?,?,?,?)", 
                               (p_id, c_id, qty, total_cash, points_used, tarigi))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
            return False

    def get_revenue_by_product(self):
        return pd.read_sql_query("SELECT p.name, SUM(s.total_gel) as total_revenue FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.name", self.conn)

# --- 2. აპლიკაცია ---
class SalesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Pro v4.6")
        self.root.geometry("1000x850")
        self.db = SalesDatabase("Business_v4.db")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.sale_tab = ttk.Frame(self.notebook)
        self.stock_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.sale_tab, text="🛒 გაყიდვები")
        self.notebook.add(self.stock_tab, text="📦 საწყობი")
        self.notebook.add(self.stats_tab, text="📊 ანალიტიკა")

        self.setup_sale_tab()
        self.setup_stock_tab()
        self.setup_stats_tab()
        self.refresh_all()
        
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.draw_charts() if self.notebook.index("current") == 2 else None)

    def setup_sale_tab(self):
        # კლიენტის სექცია
        f_cust = tk.LabelFrame(self.sale_tab, text="კლიენტის მართვა", padx=10, pady=10)
        f_cust.pack(fill="x", padx=10, pady=5)
        
        tk.Label(f_cust, text="ნომერი:").grid(row=0, column=0)
        self.ent_phone = tk.Entry(f_cust); self.ent_phone.grid(row=0, column=1, padx=5)
        self.ent_phone.bind("<KeyRelease>", self.live_search)
        
        self.lbl_cust_info = tk.Label(f_cust, text="სტატუსი: სტუმარი", fg="blue", font=("Arial", 10, "bold"))
        self.lbl_cust_info.grid(row=0, column=2, padx=10)
        
        tk.Button(f_cust, text="+ რეგისტრაცია", command=self.quick_reg).grid(row=0, column=3)

        # გაყიდვის სექცია
        f_sale = tk.LabelFrame(self.sale_tab, text="ახალი ტრანზაქცია", padx=10, pady=10)
        f_sale.pack(fill="x", padx=10, pady=5)
        
        tk.Label(f_sale, text="პროდუქტი:").grid(row=0, column=0)
        self.cb_prod = ttk.Combobox(f_sale); self.cb_prod.grid(row=0, column=1, padx=5)
        
        tk.Label(f_sale, text="რაოდენობა:").grid(row=0, column=2)
        self.ent_qty = tk.Entry(f_sale, width=8); self.ent_qty.insert(0, "1"); self.ent_qty.grid(row=0, column=3, padx=5)
        
        tk.Button(self.sale_tab, text="გაყიდვის გაფორმება", bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), command=self.do_sale).pack(pady=10)

        self.tree_sales = ttk.Treeview(self.sale_tab, columns=("ID", "პროდუქტი", "რაოდენობა", "ჯამი", "თარიღი"), show='headings')
        for col in self.tree_sales['columns']: self.tree_sales.heading(col, text=col)
        self.tree_sales.pack(fill="both", expand=True, padx=10)

    def setup_stock_tab(self):
        f_add = tk.LabelFrame(self.stock_tab, text="პროდუქტის დამატება", padx=10, pady=10)
        f_add.pack(fill="x", padx=10, pady=10)
        tk.Label(f_add, text="სახელი:").grid(row=0, column=0)
        self.ent_pname = tk.Entry(f_add); self.ent_pname.grid(row=0, column=1)
        tk.Label(f_add, text="ფასი:").grid(row=1, column=0)
        self.ent_pprice = tk.Entry(f_add); self.ent_pprice.grid(row=1, column=1)
        tk.Label(f_add, text="მარაგი:").grid(row=2, column=0)
        self.ent_pstock = tk.Entry(f_add); self.ent_pstock.grid(row=2, column=1)
        tk.Button(f_add, text="შენახვა", command=self.save_product).grid(row=3, column=1, pady=5)

        self.tree_stock = ttk.Treeview(self.stock_tab, columns=("ID", "სახელი", "ფასი", "მარაგი"), show='headings')
        for col in self.tree_stock['columns']: self.tree_stock.heading(col, text=col)
        self.tree_stock.pack(fill="both", expand=True, padx=10)

    def setup_stats_tab(self):
        self.fig_container = ttk.Frame(self.stats_tab)
        self.fig_container.pack(fill="both", expand=True)

    def quick_reg(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.geometry("250x150")
        tk.Label(reg_win, text="სახელი:").pack(); e_n = tk.Entry(reg_win); e_n.pack()
        tk.Label(reg_win, text="ტელეფონი:").pack(); e_p = tk.Entry(reg_win); e_p.pack()
        def save():
            if self.db.add_customer(e_n.get(), e_p.get()):
                self.ent_phone.delete(0, 'end'); self.ent_phone.insert(0, e_p.get())
                self.live_search()
                reg_win.destroy()
        tk.Button(reg_win, text="შენახვა", command=save).pack()

    def live_search(self, e=None):
        phone = self.ent_phone.get().strip()
        if len(phone) >= 4:
            c = self.db.get_customer(phone)
            if c: self.lbl_cust_info.config(text=f"კლიენტი: {c[1]} | ქულები: {int(c[2])}", fg="green")
            else: self.lbl_cust_status = self.lbl_cust_info.config(text="არ მოიძებნა", fg="red")
        else: self.lbl_cust_info.config(text="სტატუსი: სტუმარი", fg="blue")

    def do_sale(self):
        try:
            p_name = self.cb_prod.get()
            qty = float(self.ent_qty.get())
            phone = self.ent_phone.get().strip()
            
            self.db.cursor.execute("SELECT id, price, stock FROM products WHERE name=?", (p_name,))
            p = self.db.cursor.fetchone()
            if not p or p[2] < qty:
                messagebox.showerror("Error", "მარაგი არ არის!")
                return
            
            total = p[1] * qty
            earned_pts = total * 5  # 1 ლარი = 5 ქულა
            used_pts = 0
            
            cust = self.db.get_customer(phone)
            c_id = cust[0] if cust else None
            
            if cust and cust[2] >= 100:
                if messagebox.askyesno("ბონუსი", f"გამოვიყენოთ {int(cust[2])} ქულა?"):
                    used_pts = cust[2]
                    total -= (used_pts / 100) # 100 ქულა = 1 ლარი
            
            if self.db.finalize_sale_transaction(p[0], c_id, qty, max(0, total), used_pts, earned_pts):
                messagebox.showinfo("OK", f"წარმატებულია! ჯამი: {max(0, total):.2f} GEL")
                self.refresh_all()
                self.live_search()
        except Exception as e: messagebox.showerror("Error", str(e))

    def save_product(self):
        self.db.add_product(self.ent_pname.get(), float(self.ent_pprice.get()), float(self.ent_pstock.get()))
        self.refresh_all()

    def draw_charts(self):
        for w in self.fig_container.winfo_children(): w.destroy()
        df = self.db.get_revenue_by_product()
        if not df.empty:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.pie(df['total_revenue'], labels=df['name'], autopct='%1.1f%%')
            canvas = FigureCanvasTkAgg(fig, master=self.fig_container)
            canvas.draw(); canvas.get_tk_widget().pack()

    def refresh_all(self):
        prods = self.db.get_all_products()
        self.cb_prod['values'] = list(prods['name'])
        for i in self.tree_stock.get_children(): self.tree_stock.delete(i)
        for _, r in prods.iterrows(): self.tree_stock.insert("", "end", values=list(r))
        sales_df = pd.read_sql_query("SELECT s.id, p.name, s.qty, s.total_gel, s.tarigi FROM sales s JOIN products p ON s.product_id=p.id ORDER BY s.id DESC", self.db.conn)
        for i in self.tree_sales.get_children(): self.tree_sales.delete(i)
        for _, r in sales_df.iterrows(): self.tree_sales.insert("", "end", values=list(r))

if __name__ == "__main__":
    root = tk.Tk(); app = SalesApp(root); root.mainloop()