import tkinter as tk
from tkinter import messagebox ,filedialog
import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import smtplib
from email.message import EmailMessage
from tkinter import filedialog
import json
import sqlite3
from tkinter import simpledialog


def setup_database():
    conn=sqlite3.connect("Business_data.db")
    cursor=conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   product_name TEXT,
                   quantity INTEGER,
                   price_gel REAL,
                   total_usd REAL,
                   sale_data TEXT
                   )
                ''')
    conn.commit()
    conn.close()



def save_settings():
    data={
        "last_email":ent_email.get(),
        "last_path":ent_path.get()
    }
    with open("settings.json","w") as f:
        json.dump(data,f)

def load_settings():
    if os.path.exists("settings.json"):
        try:

            with open("settings.json","r") as f:
                data=json.load(f)
                ent_email.delete(0,tk.END)
                ent_email.insert(0,data.get("last_email",""))
                ent_path.delete(0,tk.END)
                ent_path.insert(0,data.get("last_path",""))
        except:
            pass


def insert_sales_to_db(df):
    conn = sqlite3.connect("Business_data.db")
    cursor = conn.cursor()
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT INTO sales (product_name, quantity, price_gel, total_usd, sale_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['produkti'], row['gayiduli'], row['pasi'], row['Total_USD'], date_now))
    
    conn.commit()
    conn.close()

def get_total_sales():
    try:
        conn=sqlite3.connect("Business_data.db")
        cursor=conn.cursor()
        cursor.execute("SELECT SUM(total_usd)FROM sales WHERE product_name = 'xorci'")
        result=cursor.fetchone()
        total_sum=result[0]if result[0] else 0
        total_count=result[1]if result[1] else 0

        conn.close()
        messagebox.showinfo("BIZNES STATISTIKA",
                            f"JAMURI GAYIDVEBI:${total_sum:,.2f}\n"
                            f"SUL GANXORCIELDA:{total_count} TRANSAQCIA")
    except Exception as e:
                messagebox.showerror("SHECDOMA",str(e))


def amoghe_kuri_pro():
    try:
        ticker=yf.Ticker("USDGEL=X")
        data=ticker.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1],4)
        return None
    except:
        return None
def send_email(file_excel,file_chart,reciver):
    email_sender="dchxartishvili90@gmail.com"
    email_password="xpts ravx gvse bwkv"
    email_reciver="dchkhartishvili@yahoo.com"

    msg=EmailMessage()
    msg['Subject']=f"Sales Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = email_sender
    msg['to']= reciver
    msg.set_content("GAMARJOBA,TANDARTUL FAILSHI IXILAVT REPORTS")
    for file in [file_excel,file_chart]:
        with open(file,'rb') as f:
            file_data=f.read()
            file_name=file
            msg.add_attachment(file_data,maintype='application',subtype='octet-stream',filename=file)

    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(email_sender,email_password)
        smtp.send_message(msg)

def select_file():
    filepath=filedialog.askopenfilename(
        title="airchiet Gayidvebis faili",
        filetypes=(("CSV Failebi","*.csv"),("yvela faili","*.*"))

    )
    if filepath:
        ent_path.delete(0, tk.END)
        ent_path.insert(0,filepath)

def get_product_stats():
    target_product=simpledialog.askstring("DZEBNA","ROMELI PRODUKTI STATISTIKA GSURS? (mag:xorci)")
    if not target_product:
        return
    try:
        conn=sqlite3.connect("Business_data.db")
        cursor=conn.cursor()
        query="SELECT SUM(total_usd),SUM(quantity)FROM sales WHERE product_name=?"
        cursor.execute(query,(target_product,))

        result=cursor.fetchone()
        total_sum=result[0] if result[0] else 0
        total_qty=result[1] if result[1] else 0
        conn.close()

        messagebox.showinfo("SHEDEGEI",
              f"PRODUKTI:{target_product}\n"
              f"JAMURI SHEMOSAVALI:${total_sum:,.2f}\n"
              f"SUL GAYIDULIA:{total_qty} ERTEULI")
    except Exception as e:
        messagebox.showerror("SHECDOMA", f" ver moidzebna {e}")



def reset_database():
    confirm = messagebox.askyesno("დადასტურება", "დარწმუნებული ხართ, რომ გსურთ ბაზის სრულად გასუფთავება?")
    if confirm:
        try:
            conn = sqlite3.connect("Business_data.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sales") # შლის ყველა ჩანაწერს
            conn.commit()
            conn.close()
            messagebox.showinfo("წარმატება", "ბაზა გასუფთავდა!")
        except Exception as e:
            messagebox.showerror("შეცდომა", str(e))

def run_automation():
    save_settings()

    rate=amoghe_kuri_pro()
    if not rate:
        messagebox.showerror("SHECDOMA ,VALUUTIS KURSS AMOGEBA VERMOXERXDA")
        return
    input_file=ent_path.get()
    reciver_mail=ent_email.get()
    if not input_file or not os.path.exists(input_file):
        messagebox.showwarning("GTXOVT JER AIRCHIOT FAILI")
        return
    try:
        df=pd.read_csv(input_file)
        df['Total_GEL']=df['pasi'] * df['gayiduli']
        df['Total_USD']=(df['Total_GEL']/rate).round(2)

        insert_sales_to_db(df)

        date_str=datetime.now().strftime("%Y-%m-%d")
        output_file=f"Final_report_{date_str}.xlsx"
        chart_name=f"Chart_{date_str}.png"
        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer,sheet_name='sales_analysis',index=False)
            pd.DataFrame({'Date':[date_str],'Rate':[rate]}).to_excel(writer,sheet_name='Exchange_Rate',index=False)
        plt.figure(figsize=(8,5))
        plt.bar(df['produkti'],df['Total_USD'],color='green')
        plt.title("GAYIDVEBI LARSHI")
        plt.savefig(chart_name)
        plt.close()

        lbl_status.config(text=f"STATUSI REPORTI MZADAA (Rate:{rate})",fg="#2ecc71")
        messagebox.showinfo("WARMATEBA",f"FAILI '{output_file}' WARMATEBIT SHEIQMNA!")
        send_email(output_file, chart_name,reciver_mail)
    except Exception as e:
        messagebox.showerror("SHECDOMA", f"DAMISHAVEBISAS MOXDA SECDOMA:{e}")

setup_database()
root = tk.Tk()

root.title("Business Assistant v2.0")
root.geometry("400x350")
root.configure(bg="#2c3e50") # მუქი ფონი

lbl_title = tk.Label(
    root, 
    text="Sales Automation Tool", 
    fg="#ecf0f1", 
    bg="#2c3e50", 
    font=("Helvetica", 16, "bold")
)
lbl_title.pack(pady=25)

# სტატუსის პანელი (ჩარჩოში ჩასმული)
status_frame = tk.Frame(root, bg="#34495e", bd=2, relief="groove")
status_frame.pack(pady=10, padx=20, fill="x")

lbl_status = tk.Label(
    status_frame, 
    text="სტატუსი: მზადყოფნაში", 
    fg="#bdc3c7", 
    bg="#34495e", 
    font=("Segoe UI", 10)
)
lbl_status.pack(pady=15)

# თანამედროვე ღილაკი
def on_enter(e):
    btn['background'] = '#27ae60' # მაუსის მიტანისას ფერი იცვლება

def on_leave(e):
    btn['background'] = '#2ecc71' # მაუსის მოცილებისას ბრუნდება

btn = tk.Button(
    root, 
    text="🚀 გაუშვი ავტომატიზაცია", 
    command=run_automation,
    bg="#2ecc71", 
    fg="white", 
    font=("Helvetica", 12, "bold"),
    activebackground="#27ae60",
    activeforeground="white",
    cursor="hand2",
    bd=0,
    padx=20,
    pady=10
)
btn_stats = tk.Button(
    root, 
    text="📊 ნახე ჯამური სტატისტიკა", 
    command=get_total_sales,
    bg="#3498db", # ლურჯი ფერი
    fg="white", 
    font=("Helvetica", 11, "bold"),
    width=25,
    cursor="hand2",
    bd=0,
    pady=10
)
btn_stats.pack(pady=10)


btn.pack(pady=30)

# ეფექტების მიბმა ღილაკზე
btn.bind("<Enter>", on_enter)
btn.bind("<Leave>", on_leave)

# ფაილის არჩევის სექცია
lbl_file = tk.Label(root, text="არჩეული ფაილი:", bg="#2c3e50", fg="white")
lbl_file.pack(pady=5)

ent_path = tk.Entry(root, width=40)
ent_path.pack(pady=5)

btn_browse = tk.Button(root, text="ფაილის ძებნა 📂", command=select_file)
btn_browse.pack(pady=5)

# მეილის ჩასაწერი ველი
lbl_email = tk.Label(root, text="გასაგზავნი მეილი:", bg="#2c3e50", fg="white")
lbl_email.pack(pady=5)

ent_email = tk.Entry(root, width=40)
ent_email.insert(0, "dchkhartishvili@yahoo.com") # Default მნიშვნელობა
ent_email.pack(pady=5)

btn_reset = tk.Button(
    root, 
    text="🗑 ბაზის გასუფთავება", 
    command=reset_database, 
    bg="#e74c3c", # წითელი
    fg="white", 
    font=("Helvetica", 10), 
    width=25
)
btn_reset.pack(pady=5)

load_settings()
root.mainloop()