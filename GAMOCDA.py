import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF

# --- 1. მონაცემთა ბაზა ---
class SalesDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL, stock REAL DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, qty REAL, total_gel REAL, tarigi TEXT)''')
        self.conn.commit()

    def add_product(self, name, price, stock):
        self.cursor.execute("SELECT id, stock FROM products WHERE name = ?", (name,))
        res = self.cursor.fetchone()
        if res:
            p_id, current_stock = res
            new_stock = current_stock + stock
            self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, p_id))
            self.conn.commit()
            return "updated"
        else:
            try:
                self.cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
                self.conn.commit()
                return "added"
            except: return False

    def get_all_product_names(self):
        self.cursor.execute("SELECT name FROM products")
        return [row[0] for row in self.cursor.fetchall()]

    def record_sale_with_inventory(self, product_name, qty_to_sell, date):
        self.cursor.execute("SELECT id, price, stock FROM products WHERE name = ?", (product_name,))
        res = self.cursor.fetchone()
        if res:
            p_id, p_price, current_stock = res
            if current_stock < qty_to_sell: return "limit"
            new_stock = current_stock - qty_to_sell
            self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, p_id))
            total = round(p_price * qty_to_sell, 2)
            self.cursor.execute("INSERT INTO sales (product_id, qty, total_gel, tarigi) VALUES (?, ?, ?, ?)", (p_id, qty_to_sell, total, date))
            self.conn.commit()
            return total
        return None

    def get_sales_df(self):
        return pd.read_sql_query("SELECT s.id, s.tarigi, p.name as product, s.qty, s.total_gel FROM sales s JOIN products p ON s.product_id = p.id", self.conn)

    def get_total_turnover(self):
        self.cursor.execute("SELECT SUM(total_gel) FROM sales")
        res = self.cursor.fetchone()
        return round(res[0], 2) if res[0] else 0

    def get_revenue_by_product(self):
        return pd.read_sql_query("SELECT p.name, SUM(s.total_gel) as total_revenue FROM sales s JOIN products p ON s.product_id = p.id GROUP BY name", self.conn)

    def get_stock_report(self):
        return pd.read_sql_query("SELECT name, stock FROM products ORDER BY stock ASC", self.conn)

# --- 2. მთავარი აპლიკაცია ---
class SalesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Management System v3.0")
        self.root.geometry("1000x950")
        self.db = SalesDatabase("Business_Final.db")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.main_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="გაყიდვები")
        self.notebook.add(self.stats_tab, text="ანალიტიკა")
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_stats())

        # --- Tab 1: Inventory & Sales ---
        tk.Label(self.main_tab, text="პროდუქტის რეგისტრაცია / მარაგის შევსება", font=('Arial', 10, 'bold')).pack(pady=5)
        self.new_p_name = tk.Entry(self.main_tab); self.new_p_name.pack(); self.new_p_name.insert(0, "სახელი")
        self.new_p_price = tk.Entry(self.main_tab); self.new_p_price.pack(); self.new_p_price.insert(0, "ფასი")
        self.new_p_stock = tk.Entry(self.main_tab); self.new_p_stock.pack(); self.new_p_stock.insert(0, "მარაგი")
        tk.Button(self.main_tab, text="ბაზაში დამატება", command=self.register_product, bg="orange").pack(pady=5)

        tk.Label(self.main_tab, text="გაყიდვა", font=('Arial', 10, 'bold')).pack(pady=10)
        self.product_combo = ttk.Combobox(self.main_tab, values=self.db.get_all_product_names())
        self.product_combo.pack()
        self.qty_entry = tk.Entry(self.main_tab); self.qty_entry.pack(); self.qty_entry.insert(0, "1")
        tk.Button(self.main_tab, text="გაყიდვის გაფორმება", command=self.make_sale, bg="green", fg="white").pack(pady=5)

        self.tree = ttk.Treeview(self.main_tab, columns=("ID", "Date", "Product", "Qty", "GEL"), show='headings')
        for col in self.tree['columns']: self.tree.heading(col, text=col)
        self.tree.pack(pady=10, fill="both", expand=True)

        # --- Tab 2: Analytics ---
        self.total_label = tk.Label(self.stats_tab, text="შემოსავალი: 0 GEL", font=('Arial', 14, 'bold'))
        self.total_label.pack(pady=10)
        
        self.stock_tree = ttk.Treeview(self.stats_tab, columns=("Product", "Stock"), show='headings', height=5)
        self.stock_tree.heading("Product", text="პროდუქტი"); self.stock_tree.heading("Stock", text="ნაშთი")
        self.stock_tree.tag_configure('low', background='#ffcccc')
        self.stock_tree.pack(pady=5, fill="x")

        tk.Button(self.stats_tab, text="PDF REპორტი", command=self.generate_pdf, bg="purple", fg="white").pack(pady=5)
        self.refresh_ui()

    def register_product(self):
        try:
            name = self.new_p_name.get().strip()
            price = float(self.new_p_price.get())
            stock = float(self.new_p_stock.get())
            res = self.db.add_product(name, price, stock)
            messagebox.showinfo("OK", "ბაზა განახლდა!")
            self.product_combo['values'] = self.db.get_all_product_names()
            self.refresh_ui()
        except: messagebox.showerror("Error", "შეამოწმეთ ციფრები")

    def make_sale(self):
        try:
            p_name = self.product_combo.get()
            qty_raw = self.qty_entry.get().replace(',', '.')
            qty = float("".join(c for c in qty_raw if c.isdigit() or c == '.'))
            res = self.db.record_sale_with_inventory(p_name, qty, datetime.date.today().strftime("%Y-%m-%d"))
            if res == "limit": messagebox.showwarning("Limit", "მარაგი არ არის!")
            elif res: self.refresh_ui(); messagebox.showinfo("OK", f"ჯამი: {res} GEL")
        except: messagebox.showerror("Error", "შეიყვანეთ რაოდენობა")

    def refresh_ui(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for _, row in self.db.get_sales_df().iterrows(): self.tree.insert("", "end", values=list(row))

    def update_stats(self):
        self.total_label.config(text=f"საერთო შემოსავალი: {self.db.get_total_turnover()} GEL")
        for i in self.stock_tree.get_children(): self.stock_tree.delete(i)
        for _, row in self.db.get_stock_report().iterrows():
            tag = 'low' if row['stock'] < 5 else ''
            self.stock_tree.insert("", "end", values=list(row), tags=(tag,))
        self.show_chart()

    def show_chart(self):
        df = self.db.get_revenue_by_product()
        if df.empty: return
        for widget in self.stats_tab.winfo_children():
            if "canvas" in str(widget).lower(): widget.destroy()
        plt.close('all')
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.pie(df['total_revenue'], labels=df['name'], autopct='%1.1f%%', startangle=140)
        canvas = FigureCanvasTkAgg(fig, master=self.stats_tab)
        canvas.draw(); canvas.get_tk_widget().pack(pady=10)

    def generate_pdf(self):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Sales Report", ln=True, align='C')
        pdf.set_font("Arial", size=12); pdf.ln(10)
        pdf.cell(200, 10, txt=f"Total Revenue: {self.db.get_total_turnover()} GEL", ln=True)
        plt.savefig("temp.png")
        pdf.image("temp.png", x=10, y=None, w=160)
        pdf.output("Business_Report.pdf")
        messagebox.showinfo("PDF", "Report Created!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesApp(root)
    root.mainloop()