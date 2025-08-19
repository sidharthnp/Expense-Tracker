import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedStyle
import pandas as pd
import datetime
import os
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Expense Tracker")
        self.geometry("900x700")  # Increased height for additional elements
        self.configure(bg="#F0F2F5")

        self.transactions = []
        self.predefined_persons = ["", "", "", "", ""]  # 5 empty slots for predefined persons

        # Apply modern theme
        style = ThemedStyle(self)
        style.set_theme("arc")

        # Header
        header_frame = tk.Frame(self, bg="#4A90E2")
        header_frame.pack(fill="x")

        title_label = tk.Label(header_frame, text="Expense Tracker", font=("Arial", 16, "bold"), fg="white", bg="#4A90E2")
        title_label.pack(pady=10)

        # Input Fields
        input_frame = tk.Frame(self, bg="#F0F2F5")
        input_frame.pack(pady=10)

        # Row 0: Amount and Person
        tk.Label(input_frame, text="Amount:", bg="#F0F2F5").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Person:", bg="#F0F2F5").grid(row=0, column=2, sticky="w")
        self.person_entry = tk.Entry(input_frame)
        self.person_entry.grid(row=0, column=3, padx=5, pady=5)

        # Row 1: Date and Remarks
        tk.Label(input_frame, text="Date (YYYY-MM-DD):", bg="#F0F2F5").grid(row=1, column=0, sticky="w")
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        # Set default date to today
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)

        tk.Label(input_frame, text="Remarks:", bg="#F0F2F5").grid(row=1, column=2, sticky="w")
        self.remarks_entry = tk.Entry(input_frame, width=30)
        self.remarks_entry.grid(row=1, column=3, padx=5, pady=5)

        # Predefined Persons Frame
        person_frame = tk.Frame(self, bg="#F0F2F5")
        person_frame.pack(pady=5)

        tk.Label(person_frame, text="Select Person:", bg="#F0F2F5").pack(side=tk.LEFT, padx=5)
        
        # Person buttons
        self.person_buttons = []
        for i in range(5):
            btn = tk.Button(person_frame, text=f"Person {i+1}", width=10, bg="#9B59B6", fg="white",
                           command=lambda idx=i: self.select_person(idx))
            btn.pack(side=tk.LEFT, padx=5)
            self.person_buttons.append(btn)
            
        # Person Settings Button
        settings_btn = tk.Button(person_frame, text="⚙️", width=3, bg="#34495E", fg="white",
                               command=self.open_person_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)

        # Category Selection
        self.selected_category = tk.StringVar()
        category_frame = tk.Frame(self, bg="#F0F2F5")
        category_frame.pack(pady=5)

        tk.Label(category_frame, text="Select Category:", bg="#F0F2F5").pack(side=tk.LEFT, padx=5)

        categories = ["Food", "Shopping", "Salary", "Rent", "Petrol", "Miscellaneous"]
        for cat in categories:
            btn = tk.Button(category_frame, text=cat, width=10, bg="#FF6F61", fg="white",
                            command=lambda c=cat: self.selected_category.set(c))
            btn.pack(side=tk.LEFT, padx=5)

        # Income / Expense Selection
        self.transaction_type = tk.StringVar(value="Expense")
        type_frame = tk.Frame(self, bg="#F0F2F5")
        type_frame.pack(pady=5)

        income_button = tk.Button(type_frame, text="Income", width=10, bg="#2ECC71", fg="white",
                                  command=lambda: self.transaction_type.set("Income"))
        income_button.pack(side=tk.LEFT, padx=5)

        expense_button = tk.Button(type_frame, text="Expense", width=10, bg="#E74C3C", fg="white",
                                   command=lambda: self.transaction_type.set("Expense"))
        expense_button.pack(side=tk.LEFT, padx=5)

        # Add Transaction Button
        add_button = tk.Button(self, text="Add Transaction", bg="#3498DB", fg="white", command=self.add_transaction)
        add_button.pack(pady=5)

        # Import CSV Button - NEW
        import_button = tk.Button(self, text="Import from CSV", bg="#8E44AD", fg="white", command=self.import_from_csv)
        import_button.pack(pady=5)

        # Transaction List with Scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.transaction_list = tk.Listbox(list_frame, height=10, width=80, yscrollcommand=scrollbar.set)
        self.transaction_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.transaction_list.yview)

        # Control Buttons with Icons
        control_frame = tk.Frame(self, bg="#F0F2F5")
        control_frame.pack(pady=10)

        self.load_icons()

        self.calc_button = tk.Button(control_frame, image=self.calc_icon, compound=tk.LEFT, text="Total Income/Expense",
                                     bg="#F39C12", fg="white", command=self.calculate_totals)
        self.calc_button.pack(side=tk.LEFT, padx=5)

        self.export_button = tk.Button(control_frame, image=self.export_icon, compound=tk.LEFT, text="Export All",
                                       bg="#34495E", fg="white", command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.export_person_button = tk.Button(control_frame, image=self.person_icon, compound=tk.LEFT, text="Export Person-wise",
                                              bg="#1ABC9C", fg="white", command=self.export_person_data)
        self.export_person_button.pack(side=tk.LEFT, padx=5)

        # Pie chart canvas
        self.pie_chart_canvas = None
        
        # Load saved person names if available
        self.load_person_settings()

    def load_icons(self):
        """Loads and resizes icons."""
        self.calc_icon = self.load_icon("calc.png")
        self.export_icon = self.load_icon("export.png")
        self.person_icon = self.load_icon("user.png")

    def load_icon(self, filename):
        """Loads an icon with proper resizing."""
        try:
            image = Image.open(filename)
            image = image.resize((20, 20), Image.LANCZOS)  # ANTIALIAS is deprecated, using LANCZOS instead
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading icon {filename}: {e}")
            return None
    
    def select_person(self, index):
        """Set the person entry field to the selected predefined person."""
        if self.predefined_persons[index]:
            self.person_entry.delete(0, tk.END)
            self.person_entry.insert(0, self.predefined_persons[index])
    
    def open_person_settings(self):
        """Open a dialog to configure the predefined persons."""
        settings_window = tk.Toplevel(self)
        settings_window.title("Person Settings")
        settings_window.geometry("300x250")
        settings_window.configure(bg="#F0F2F5")
        settings_window.resizable(False, False)
        
        tk.Label(settings_window, text="Configure Predefined Persons", font=("Arial", 12, "bold"), 
                 bg="#F0F2F5").pack(pady=10)
        
        entries = []
        for i in range(5):
            frame = tk.Frame(settings_window, bg="#F0F2F5")
            frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(frame, text=f"Person {i+1}:", bg="#F0F2F5", width=10).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=20)
            entry.pack(side=tk.LEFT, padx=5)
            entry.insert(0, self.predefined_persons[i])
            entries.append(entry)
        
        def save_settings():
            for i in range(5):
                self.predefined_persons[i] = entries[i].get()
            self.update_person_buttons()
            self.save_person_settings()
            settings_window.destroy()
        
        save_btn = tk.Button(settings_window, text="Save", bg="#2ECC71", fg="white", command=save_settings)
        save_btn.pack(pady=10)
    
    def update_person_buttons(self):
        """Update the person buttons with the current names."""
        for i in range(5):
            display_name = self.predefined_persons[i] if self.predefined_persons[i] else f"Person {i+1}"
            self.person_buttons[i].config(text=display_name[:10] + "..." if len(display_name) > 10 else display_name)
    
    def save_person_settings(self):
        """Save person settings to a file."""
        try:
            with open("person_settings.txt", "w") as f:
                for person in self.predefined_persons:
                    f.write(f"{person}\n")
        except Exception as e:
            print(f"Error saving person settings: {e}")
    
    def load_person_settings(self):
        """Load person settings from a file if it exists."""
        try:
            if os.path.exists("person_settings.txt"):
                with open("person_settings.txt", "r") as f:
                    lines = f.readlines()
                    for i in range(min(5, len(lines))):
                        self.predefined_persons[i] = lines[i].strip()
                self.update_person_buttons()
        except Exception as e:
            print(f"Error loading person settings: {e}")

    def import_from_csv(self):
        """Import transactions from a CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Check if the CSV has the expected columns
            required_columns = ["Timestamp", "Month", "Type", "Category", "Amount", "Person", "Date", "Remarks"]
            
            # If the CSV doesn't have all required columns, try to map the existing columns
            if not all(col in df.columns for col in required_columns):
                # Try to map columns based on the example CSV format
                if "Timestamp" in df.columns and "Month" in df.columns and "Type" in df.columns and \
                   "Category" in df.columns and "Amount" in df.columns and "Person" in df.columns and \
                   "Date" in df.columns and "Remarks" in df.columns:
                    pass  # All columns are present
                else:
                    # Try to guess the format based on the example you provided
                    try:
                        # If the CSV has a different structure, try to adapt
                        new_df = pd.DataFrame(columns=required_columns)
                        
                        # Map columns based on position if headers match expected format
                        column_mapping = {}
                        for i, col in enumerate(df.columns):
                            if i < len(required_columns):
                                column_mapping[col] = required_columns[i]
                        
                        # Create a new DataFrame with the mapped columns
                        for old_col, new_col in column_mapping.items():
                            new_df[new_col] = df[old_col]
                            
                        df = new_df
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not map CSV columns: {e}")
                        return
            
            # Process each row and add to transactions
            count = 0
            for _, row in df.iterrows():
                try:
                    timestamp = row["Timestamp"]
                    month = row["Month"]
                    transaction_type = row["Type"]
                    category = row["Category"]
                    amount = float(row["Amount"])
                    person = row["Person"]
                    date_str = row["Date"]
                    remarks = row["Remarks"] if "Remarks" in row and not pd.isna(row["Remarks"]) else ""
                    
                    # Create transaction tuple
                    transaction = (timestamp, month, transaction_type, category, amount, person, date_str, remarks)
                    
                    # Skip if already exists
                    if transaction in self.transactions:
                        continue
                        
                    # Add to transactions list
                    self.transactions.append(transaction)
                    
                    # Add to listbox display
                    remarks_display = f" - Remarks: {remarks}" if remarks else ""
                    self.transaction_list.insert(tk.END, f"{date_str} - {transaction_type} - {category}: {amount} (Person: {person}){remarks_display}")
                    
                    count += 1
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
                    
            messagebox.showinfo("Import Successful", f"Successfully imported {count} transactions from CSV.")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing CSV: {e}")

    def add_transaction(self):
        amount = self.amount_entry.get()
        person = self.person_entry.get()
        category = self.selected_category.get()
        transaction_type = self.transaction_type.get()
        date_str = self.date_entry.get()
        remarks = self.remarks_entry.get()

        if not amount or not category or not date_str:
            messagebox.showerror("Error", "Amount, Category, and Date are required!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return
            
        try:
            # Validate date format
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format!")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        month = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %Y")
        transaction = (timestamp, month, transaction_type, category, amount, person, date_str, remarks)

        # Check for duplicate entry
        if transaction in self.transactions:
            messagebox.showwarning("Warning", "Duplicate entry detected!")
            return

        self.transactions.append(transaction)
        
        # Format the display with remarks
        remarks_display = f" - Remarks: {remarks}" if remarks else ""
        self.transaction_list.insert(tk.END, f"{date_str} - {transaction_type} - {category}: {amount} (Person: {person}){remarks_display}")
        
        # Clear input fields
        self.amount_entry.delete(0, tk.END)
        # Don't clear person field to make it easier for multiple entries for same person
        self.remarks_entry.delete(0, tk.END)
        # Reset date to today
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))

    def calculate_totals(self):
        if not self.transactions:
            messagebox.showerror("Error", "No transactions available to calculate!")
            return

        df = pd.DataFrame(self.transactions, columns=["Timestamp", "Month", "Type", "Category", "Amount", "Person", "Date", "Remarks"])
        monthly_totals = df.groupby(["Month", "Type"])["Amount"].sum().unstack().fillna(0)

        total_income = monthly_totals["Income"].sum() if "Income" in monthly_totals else 0
        total_expense = monthly_totals["Expense"].sum() if "Expense" in monthly_totals else 0

        self.display_pie_chart(total_income, total_expense)

    def display_pie_chart(self, total_income, total_expense):
        if self.pie_chart_canvas:
            self.pie_chart_canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 4))
        labels = ["Income", "Expense"]
        values = [total_income, total_expense]
        colors = ["#2ECC71", "#E74C3C"]
        ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.set_title("Income vs Expense")

        self.pie_chart_canvas = FigureCanvasTkAgg(fig, self)
        self.pie_chart_canvas.get_tk_widget().pack()

    def export_data(self):
        if not self.transactions:
            messagebox.showerror("Error", "No transactions to export!")
            return
            
        df = pd.DataFrame(self.transactions, columns=["Timestamp", "Month", "Type", "Category", "Amount", "Person", "Date", "Remarks"])
        
        # Ask user for export location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return  # User cancelled
            
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Export Success", f"All data exported successfully to {file_path}!")

    def export_person_data(self):
        if not self.transactions:
            messagebox.showerror("Error", "No transactions to export!")
            return
            
        df = pd.DataFrame(self.transactions, columns=["Timestamp", "Month", "Type", "Category", "Amount", "Person", "Date", "Remarks"])
        persons = df["Person"].dropna().unique()
        
        if len(persons) == 0:
            messagebox.showinfo("Info", "No person-specific data to export!")
            return
        
        # Ask user for export directory
        export_dir = filedialog.askdirectory()
        if not export_dir:
            return  # User cancelled
            
        for person in persons:
            person_file = os.path.join(export_dir, f"{person}_expenses.csv")
            df[df["Person"] == person].to_csv(person_file, index=False)
        
        messagebox.showinfo("Export Success", f"Person-wise data exported successfully to {export_dir}!")


if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
