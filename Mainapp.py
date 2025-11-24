import json
from tkinter import *
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys
from winotify import Notification
#from win10toast import ToastNotifier
# from plyer import notification

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)





class Subscriptions:
    def __init__(self, App, Bought, Renewal, USD, JMD,):
        self.App = App
        self.Bought = Bought
        self.Renewal = Renewal
        self.USD = USD
        self.JMD = JMD


    def days_left(self):
        renewal_date = datetime.strptime(self.Renewal, "%Y-%m-%d").date()
        today = datetime.today().date()
        delta = (renewal_date - today).days

        return (renewal_date - today).days
    
    

class AppManager:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def remove_product(self, App):
        self.products = [p for p in self.products if p.App != App]
    

    def to_list(self):
        return [
            {
                "App": p.App,
                "Bought": p.Bought,
                "Renewal": p.Renewal,
                "USD": p.USD,
                "JMD": p.JMD
            }
            for p in self.products  
        ]
    
    def from_list(self, data_list):
        self.products = []  
        for d in data_list:
            try:
                App = d.get("App")
                Bought = d.get("Bought")
                Renewal = d.get("Renewal")
                USD = d.get("USD")
                JMD = d.get("JMD")
                
              
                subscription = Subscriptions(App, Bought, Renewal, USD, JMD)
                self.products.append(subscription)
                
    
            except (TypeError, ValueError):
                continue  
    
    def save_to_file(self, filename):
        try:
            with open(filename, 'w') as f:  
                json.dump(self.to_list(), f, indent=2)  
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
        return False
        
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data_list = json.load(f)
                self.from_list(data_list)
            return True
        except FileNotFoundError:
            print("File not found. Starting with empty inventory.")  
            self.products = []
            return True
        except Exception as e:
            print(f"Error loading from file: {e}")
            return False
    
def check_renewals_background():
    while True:
        try:
            check_notifications(manager)  
        except Exception as e:
            print(f"Notification error: {e}")
        time.sleep(3600) 

    
def check_notifications(manager):
    for subscription in manager.products:
        delta = subscription.days_left()
        if delta <=7:
            toast = Notification(
                app_id="Subscription Manager",
                title='Renewal Notice',
                msg=f'Subscription for {subscription.App} renews in {delta} days Cancel If needed before then',
                duration='long'
                
            )
            toast.show()
class UI:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self.root.title("Subscription Manager")
        self.root.geometry("1200x720")
        self.root.resizable(False,FALSE)
        self.root.configure(bg='#000000')  
        
        self.colors = {
            'primary': '#10b981',      
            'primary_dark': '#059669', 
            'primary_light': '#34d399',
            'secondary': '#1f2937',    
            'accent': '#065f46',       
            'background': '#000000',   
            'surface': '#111827',      
            'text_primary': '#ffffff', 
            'text_secondary': '#d1d5db',
            'success': '#10b981',      
            'warning': '#f59e0b',      
            'danger': '#ef4444',       
        }
        
        self.configure_styles()
        self.create_widgets()
        

        app_data_dir = os.path.join(os.getenv('APPDATA'), 'SubscriptionManager')
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
        self.data_file = os.path.join(app_data_dir, 'subscriptions.json')
        

        self.manager.load_from_file(self.data_file)
        self.refresh_treeview()
        
    
        self.root.bind('<Return>', lambda event: self.add_subscription())
        self.root.bind('<Delete>', lambda event: self.delete_subscription())
        self.root.bind('<Control-s>', lambda event: self.save_data())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
    
        style.configure('Treeview',
                    background=self.colors['surface'],
                    foreground=self.colors['text_primary'],
                    fieldbackground=self.colors['surface'],
                    rowheight=30,
                    borderwidth=0,
                    font=('Arial', 10))
    
        style.map('Treeview', 
              background=[('selected', self.colors['primary'])],
              foreground=[('selected', self.colors['text_primary'])])
    
        style.configure('Treeview.Heading',
                    background=self.colors['secondary'],
                    foreground=self.colors['text_primary'],
                    relief='flat',
                    font=('Arial', 11, 'bold'))
    
        style.configure('Primary.TButton',
                    background=self.colors['primary'],
                    foreground=self.colors['text_primary'],
                    borderwidth=0,
                    focuscolor='none',
                    font=('Arial', 10, 'bold'))
    
        style.map('Primary.TButton',
              background=[('active', self.colors['primary_dark']),
                         ('pressed', self.colors['accent'])])
    
        style.configure('Custom.TEntry',
                    fieldbackground=self.colors['surface'],
                    foreground=self.colors['text_primary'],
                    borderwidth=1,
                    relief='solid')
        
    def create_widgets(self):

        main_frame = Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
        header_frame = Frame(main_frame, bg=self.colors['background'])
        header_frame.pack(fill=X, pady=(0, 10))
        
        title_label = Label(header_frame, 
                          text="💚 Subscription Manager",
                          font=('Arial', 16, 'bold'),
                          bg=self.colors['background'],
                          fg=self.colors['primary'])
        title_label.pack(side=LEFT)
        
        self.stats_label = Label(header_frame,
                               text="Total: $0.00 USD | $0.00 JMD",
                               font=('Arial', 10),
                               bg=self.colors['background'],
                               fg=self.colors['text_secondary'])
        self.stats_label.pack(side=RIGHT)
        

        input_frame = Frame(main_frame, bg=self.colors['background'])
        input_frame.pack(fill=X, pady=(0, 10))
        
        
        self.entries = {}
        labels = ['App Name', 'Date Bought', 'Renewal Date', 'USD', 'JMD']
        placeholders = ['App Name', 'YYYY-MM-DD', 'YYYY-MM-DD', '0.00', '0.00']
        
        for i, (label, placeholder) in enumerate(zip(labels, placeholders)):
            Label(input_frame, text=label + ":", bg=self.colors['background'], 
                  fg=self.colors['text_primary'], font=('Arial', 9)).grid(row=0, column=i*2, sticky='w', padx=(0, 5))
            
            entry = ttk.Entry(input_frame, style='Custom.TEntry', width=15, font=('Arial', 9))
            entry.grid(row=0, column=i*2+1, padx=(0, 10), pady=5)
            entry.insert(0, placeholder)
            

            entry.bind('<FocusIn>', lambda e, entry=entry, ph=placeholder: self.clear_placeholder(e, entry, ph))
            entry.bind('<FocusOut>', lambda e, entry=entry, ph=placeholder: self.add_placeholder(e, entry, ph))
            
            self.entries[label] = entry
        
   
        add_button = ttk.Button(input_frame, text="Add", style='Primary.TButton', 
                               command=self.add_subscription, width=10)
        add_button.grid(row=0, column=10, padx=5)
        
        delete_button = ttk.Button(input_frame, text="Delete", style='Primary.TButton',
                                  command=self.delete_subscription, width=10)
        delete_button.grid(row=0, column=11, padx=5)
        

        tree_frame = Frame(main_frame, bg=self.colors['background'])
        tree_frame.pack(fill=BOTH, expand=True)
        
    
        self.tree = ttk.Treeview(tree_frame, columns=("App", "Bought", "Renewal", "USD", "JMD"), show='headings')
        self.tree.heading("App", text="Application")
        self.tree.heading("Bought", text="Date Bought")
        self.tree.heading("Renewal", text="Renewal Date")
        self.tree.heading("USD", text="Price (USD)")
        self.tree.heading("JMD", text="Price (JMD)")
        
        self.tree.column("App", width=200)
        self.tree.column("Bought", width=120)
        self.tree.column("Renewal", width=120)
        self.tree.column("USD", width=100)
        self.tree.column("JMD", width=100)
        
        self.tree.pack(fill=BOTH, expand=True, side=LEFT)
        
  
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        
       
        save_frame = Frame(main_frame, bg=self.colors['background'])
        save_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(save_frame, text="Save Data", style='Primary.TButton',
                  command=self.save_data).pack(side=RIGHT)
        
       

        
    
        
    def clear_placeholder(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, END)

    def add_placeholder(self, event, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)

    def is_valid_date(self, date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_subscription(self):
        try:
            app_name = self.entries['App Name'].get().strip()
            date_bought = self.entries['Date Bought'].get().strip()
            renewal_date = self.entries['Renewal Date'].get().strip()
            price_usd = self.entries['USD'].get().strip()
            price_jmd = self.entries['JMD'].get().strip()
            

            if (app_name == "App Name" or 
                renewal_date == "YYYY-MM-DD" or price_usd == "0.00" or price_jmd == "0.00"):
                messagebox.showerror("Error", "Please fill in all fields with actual values")
                return
                


            if not self.is_valid_date(date_bought):
                messagebox.showerror("Error", "Date Bought must be in YYYY-MM-DD format")
                return

            if not self.is_valid_date(renewal_date):
                messagebox.showerror("Error", "Renewal Date must be in YYYY-MM-DD format")
                return
         
            price_usd = float(price_usd)
            price_jmd = float(price_jmd)
            
            if not all([app_name, date_bought, renewal_date]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            subscription = Subscriptions(app_name, date_bought, renewal_date, price_usd, price_jmd)
            self.manager.add_product(subscription)
            
            messagebox.showinfo("Success", f"Subscription '{app_name}' added successfully!")
            self.clear_fields()
            self.refresh_treeview()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for prices")

    def clear_fields(self):
        placeholders = {
            'App Name': 'App Name',
            'Date Bought': 'YYYY-MM-DD', 
            'Renewal Date': 'YYYY-MM-DD',
            'USD': '0.00',
            'JMD': '0.00'
        }
        
        for label, entry in self.entries.items():
            entry.delete(0, END)
            entry.insert(0, placeholders[label])

    def refresh_treeview(self):
  
        for item in self.tree.get_children():
            self.tree.delete(item)
        

        for product in self.manager.products:
            self.tree.insert('', END, values=(
                product.App,
                product.Bought,
                product.Renewal,
                f"${product.USD:.2f}",
                f"${product.JMD:.2f}"
            ))
  
        total_usd = sum(p.USD for p in self.manager.products)
        total_jmd = sum(p.JMD for p in self.manager.products)
        self.stats_label.config(text=f"Total: ${total_usd:.2f} USD | ${total_jmd:.2f} JMD")

        

    def delete_subscription(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a subscription to delete")
            return
        
        for item in selected:
            values = self.tree.item(item, 'values')
            app_name = values[0]
            self.manager.remove_product(app_name)
        
        messagebox.showinfo("Success", "Subscription(s) deleted successfully!")
        self.refresh_treeview()

    def save_data(self):
        if self.manager.save_to_file(self.data_file):
            messagebox.showinfo("Success", "Data saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save data")

    def on_closing(self):
        if messagebox.askyesno("Quit", "Save before quitting?"):
            self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk() 
    manager = AppManager()
    app = UI(root, manager)
    threading.Thread(target=check_renewals_background, daemon=True).start()
    root.mainloop()
  
