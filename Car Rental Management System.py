import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date


# ============================================================
#                        DATABASE LAYER
# ============================================================

DB_NAME = "car_rental.db"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            plate_number TEXT UNIQUE NOT NULL,
            daily_rate REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            license_no TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            rent_date TEXT NOT NULL,
            due_date TEXT,
            return_date TEXT,
            total_cost REAL,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY (car_id) REFERENCES cars (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
#                    THEME - COLORS & FONTS
# ============================================================

SIDEBAR_BG = "#1b1f2a"
SIDEBAR_ACTIVE = "#2c3242"
ACCENT = "#e0a63e"
BG = "#f4f5f7"
CARD = "#ffffff"
TEXT_DARK = "#1b1f2a"
TEXT_MUTED = "#6b7280"
GREEN = "#2e9e6b"
RED = "#d9534f"
BLUE = "#3b7dd8"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUB = ("Segoe UI", 11)
FONT_LABEL = ("Segoe UI", 10)
FONT_CARD_VAL = ("Segoe UI", 22, "bold")
FONT_CARD_TITLE = ("Segoe UI", 10)
FONT_NAV = ("Segoe UI", 11)


# ============================================================
#                REUSABLE WIDGET FACTORIES
# ============================================================

def make_btn(parent, text, cmd, bg=ACCENT, fg="#1b1f2a", w=16):
    return tk.Button(
        parent, text=text, command=cmd, bg=bg, fg=fg,
        font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
        activebackground=bg, activeforeground=fg, width=w, pady=8
    )


def make_entry(parent, w=28):
    return tk.Entry(
        parent, font=FONT_LABEL, width=w, relief="solid", bd=1,
        highlightthickness=1, highlightbackground="#d1d5db",
        highlightcolor=ACCENT
    )


def make_table(parent, cols, heads, widths):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Custom.Treeview",
        background=CARD, fieldbackground=CARD,
        foreground=TEXT_DARK, rowheight=28, font=("Segoe UI", 10)
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=SIDEBAR_BG, foreground="white",
        font=("Segoe UI", 10, "bold")
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "white")]
    )

    tree = ttk.Treeview(
        parent, columns=cols, show="headings",
        style="Custom.Treeview", selectmode="browse"
    )

    for c, h, w in zip(cols, heads, widths):
        tree.heading(c, text=h)
        tree.column(c, width=w, anchor="center")

    return tree


# ============================================================
#                       DASHBOARD PAGE
# ============================================================

class DashboardPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        tk.Label(self, text="Dashboard", font=FONT_TITLE, bg=BG, fg=TEXT_DARK)\
            .pack(anchor="w", padx=30, pady=(25, 5))
        tk.Label(
            self, text="Overview of your fleet, customers and active rentals",
            font=FONT_SUB, bg=BG, fg=TEXT_MUTED
        ).pack(anchor="w", padx=30, pady=(0, 20))

        self.cards = tk.Frame(self, bg=BG)
        self.cards.pack(fill="x", padx=30)

        tk.Label(self, text="Recent Rentals", font=("Segoe UI", 13, "bold"), bg=BG,
                 fg=TEXT_DARK).pack(anchor="w", padx=30, pady=(25, 10))

        wrap = tk.Frame(self, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        cols = ("id", "car", "customer", "rent_date", "status")
        heads = ("ID", "Car", "Customer", "Rent Date", "Status")
        self.tree = make_table(wrap, cols, heads, (50, 220, 180, 130, 100))
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def card(self, parent, title, value, color):
        c = tk.Frame(parent, bg=CARD)
        c.pack(side="left", fill="both", expand=True, padx=8, ipady=14)
        tk.Frame(c, bg=color, height=4).pack(fill="x")
        tk.Label(c, text=str(value), font=FONT_CARD_VAL, bg=CARD, fg=TEXT_DARK)\
            .pack(anchor="w", padx=18, pady=(14, 0))
        tk.Label(c, text=title, font=FONT_CARD_TITLE, bg=CARD, fg=TEXT_MUTED)\
            .pack(anchor="w", padx=18, pady=(0, 6))

    def refresh(self):
        for w in self.cards.winfo_children():
            w.destroy()

        conn = get_conn()
        cur = conn.cursor()

        total = cur.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
        avail = cur.execute("SELECT COUNT(*) FROM cars WHERE status='Available'").fetchone()[0]
        rented = cur.execute("SELECT COUNT(*) FROM cars WHERE status='Rented'").fetchone()[0]
        custs = cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        revenue = cur.execute(
            "SELECT COALESCE(SUM(total_cost),0) FROM rentals WHERE status='Completed'"
        ).fetchone()[0]

        self.card(self.cards, "TOTAL CARS", total, BLUE)
        self.card(self.cards, "AVAILABLE CARS", avail, GREEN)
        self.card(self.cards, "RENTED CARS", rented, RED)
        self.card(self.cards, "CUSTOMERS", custs, ACCENT)
        self.card(self.cards, "REVENUE ($)", f"{revenue:,.2f}", GREEN)

        for r in self.tree.get_children():
            self.tree.delete(r)

        rows = cur.execute("""
            SELECT r.id, c.brand || ' ' || c.model, cu.name, r.rent_date, r.status
            FROM rentals r
            JOIN cars c ON r.car_id = c.id
            JOIN customers cu ON r.customer_id = cu.id
            ORDER BY r.id DESC LIMIT 8
        """).fetchall()

        for row in rows:
            self.tree.insert("", "end", values=row)

        conn.close()


# ============================================================
#                          CARS PAGE
# ============================================================

class CarsPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.selected_id = None

        tk.Label(self, text="Cars", font=FONT_TITLE, bg=BG, fg=TEXT_DARK)\
            .pack(anchor="w", padx=30, pady=(25, 15))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # ---------------- Form Panel ----------------
        form = tk.Frame(body, bg=CARD, width=300)
        form.pack(side="left", fill="y", padx=(0, 15))
        form.pack_propagate(False)

        tk.Label(form, text="Car Details", font=("Segoe UI", 13, "bold"), bg=CARD,
                 fg=TEXT_DARK).pack(anchor="w", padx=18, pady=(18, 10))

        self.entries = {}
        for label, key in [
            ("Brand", "brand"), ("Model", "model"), ("Year", "year"),
            ("Plate Number", "plate_number"), ("Daily Rate ($)", "daily_rate")
        ]:
            tk.Label(form, text=label, font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED)\
                .pack(anchor="w", padx=18, pady=(8, 2))
            e = make_entry(form)
            e.pack(anchor="w", padx=18)
            self.entries[key] = e

        tk.Label(form, text="Status", font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED)\
            .pack(anchor="w", padx=18, pady=(8, 2))
        self.status_var = tk.StringVar(value="Available")
        ttk.Combobox(
            form, textvariable=self.status_var,
            values=["Available", "Rented", "Maintenance"],
            state="readonly", width=24
        ).pack(anchor="w", padx=18)

        btns = tk.Frame(form, bg=CARD)
        btns.pack(pady=20, padx=18, fill="x")
        make_btn(btns, "Add Car", self.add_car).pack(fill="x", pady=4)
        make_btn(btns, "Update", self.update_car, bg=BLUE, fg="white").pack(fill="x", pady=4)
        make_btn(btns, "Delete", self.delete_car, bg=RED, fg="white").pack(fill="x", pady=4)
        make_btn(btns, "Clear", self.clear_form, bg="#e5e7eb", fg=TEXT_DARK).pack(fill="x", pady=4)

        # ---------------- Table Panel ----------------
        table_wrap = tk.Frame(body, bg=CARD)
        table_wrap.pack(side="left", fill="both", expand=True)

        cols = ("id", "brand", "model", "year", "plate", "rate", "status")
        heads = ("ID", "Brand", "Model", "Year", "Plate No.", "Rate/Day", "Status")
        self.tree = make_table(table_wrap, cols, heads, (40, 100, 100, 60, 110, 90, 100))
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_conn()
        rows = conn.execute(
            "SELECT id, brand, model, year, plate_number, daily_rate, status "
            "FROM cars ORDER BY id DESC"
        ).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.selected_id = v[0]
        self.entries["brand"].delete(0, "end"); self.entries["brand"].insert(0, v[1])
        self.entries["model"].delete(0, "end"); self.entries["model"].insert(0, v[2])
        self.entries["year"].delete(0, "end"); self.entries["year"].insert(0, v[3])
        self.entries["plate_number"].delete(0, "end"); self.entries["plate_number"].insert(0, v[4])
        self.entries["daily_rate"].delete(0, "end"); self.entries["daily_rate"].insert(0, v[5])
        self.status_var.set(v[6])

    def read_form(self):
        try:
            brand = self.entries["brand"].get().strip()
            model = self.entries["model"].get().strip()
            year = int(self.entries["year"].get().strip())
            plate = self.entries["plate_number"].get().strip()
            rate = float(self.entries["daily_rate"].get().strip())
            status = self.status_var.get()
            if not brand or not model or not plate:
                raise ValueError
            return brand, model, year, plate, rate, status
        except ValueError:
            messagebox.showerror("Invalid Input", "Check your fields - Year and Rate need to be numbers.")
            return None

    def add_car(self):
        data = self.read_form()
        if not data:
            return
        try:
            conn = get_conn()
            conn.execute(
                "INSERT INTO cars (brand, model, year, plate_number, daily_rate, status) "
                "VALUES (?,?,?,?,?,?)", data
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Car added.")
            self.clear_form()
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "That plate number is already in the system.")

    def update_car(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Pick a car from the table first.")
            return
        data = self.read_form()
        if not data:
            return
        conn = get_conn()
        conn.execute(
            "UPDATE cars SET brand=?, model=?, year=?, plate_number=?, daily_rate=?, status=? WHERE id=?",
            (*data, self.selected_id)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Car updated.")
        self.clear_form()
        self.refresh()

    def delete_car(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Pick a car from the table first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this car for good?"):
            return
        conn = get_conn()
        conn.execute("DELETE FROM cars WHERE id=?", (self.selected_id,))
        conn.commit()
        conn.close()
        self.clear_form()
        self.refresh()

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, "end")
        self.status_var.set("Available")
        self.selected_id = None


# ============================================================
#                       CUSTOMERS PAGE
# ============================================================

class CustomersPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.selected_id = None

        tk.Label(self, text="Customers", font=FONT_TITLE, bg=BG, fg=TEXT_DARK)\
            .pack(anchor="w", padx=30, pady=(25, 15))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # ---------------- Form Panel ----------------
        form = tk.Frame(body, bg=CARD, width=300)
        form.pack(side="left", fill="y", padx=(0, 15))
        form.pack_propagate(False)

        tk.Label(form, text="Customer Details", font=("Segoe UI", 13, "bold"), bg=CARD,
                 fg=TEXT_DARK).pack(anchor="w", padx=18, pady=(18, 10))

        self.entries = {}
        for label, key in [
            ("Full Name", "name"), ("Phone", "phone"),
            ("Email", "email"), ("License No.", "license_no")
        ]:
            tk.Label(form, text=label, font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED)\
                .pack(anchor="w", padx=18, pady=(8, 2))
            e = make_entry(form)
            e.pack(anchor="w", padx=18)
            self.entries[key] = e

        btns = tk.Frame(form, bg=CARD)
        btns.pack(pady=20, padx=18, fill="x")
        make_btn(btns, "Add Customer", self.add_customer).pack(fill="x", pady=4)
        make_btn(btns, "Update", self.update_customer, bg=BLUE, fg="white").pack(fill="x", pady=4)
        make_btn(btns, "Delete", self.delete_customer, bg=RED, fg="white").pack(fill="x", pady=4)
        make_btn(btns, "Clear", self.clear_form, bg="#e5e7eb", fg=TEXT_DARK).pack(fill="x", pady=4)

        # ---------------- Table Panel ----------------
        table_wrap = tk.Frame(body, bg=CARD)
        table_wrap.pack(side="left", fill="both", expand=True)

        cols = ("id", "name", "phone", "email", "license")
        heads = ("ID", "Name", "Phone", "Email", "License No.")
        self.tree = make_table(table_wrap, cols, heads, (40, 150, 110, 180, 110))
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_conn()
        rows = conn.execute(
            "SELECT id, name, phone, email, license_no FROM customers ORDER BY id DESC"
        ).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.selected_id = v[0]
        self.entries["name"].delete(0, "end"); self.entries["name"].insert(0, v[1])
        self.entries["phone"].delete(0, "end"); self.entries["phone"].insert(0, v[2])
        self.entries["email"].delete(0, "end"); self.entries["email"].insert(0, v[3])
        self.entries["license_no"].delete(0, "end"); self.entries["license_no"].insert(0, v[4])

    def add_customer(self):
        name = self.entries["name"].get().strip()
        if not name:
            messagebox.showerror("Invalid Input", "Name is required.")
            return
        conn = get_conn()
        conn.execute(
            "INSERT INTO customers (name, phone, email, license_no) VALUES (?,?,?,?)",
            (name, self.entries["phone"].get().strip(), self.entries["email"].get().strip(),
             self.entries["license_no"].get().strip())
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added.")
        self.clear_form()
        self.refresh()

    def update_customer(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Pick a customer first.")
            return
        name = self.entries["name"].get().strip()
        if not name:
            messagebox.showerror("Invalid Input", "Name is required.")
            return
        conn = get_conn()
        conn.execute(
            "UPDATE customers SET name=?, phone=?, email=?, license_no=? WHERE id=?",
            (name, self.entries["phone"].get().strip(), self.entries["email"].get().strip(),
             self.entries["license_no"].get().strip(), self.selected_id)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Customer updated.")
        self.clear_form()
        self.refresh()

    def delete_customer(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Pick a customer first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this customer for good?"):
            return
        conn = get_conn()
        conn.execute("DELETE FROM customers WHERE id=?", (self.selected_id,))
        conn.commit()
        conn.close()
        self.clear_form()
        self.refresh()

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, "end")
        self.selected_id = None


# ============================================================
#                        RENTALS PAGE
# ============================================================

class RentalsPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.selected_id = None
        self.car_map = {}
        self.customer_map = {}

        tk.Label(self, text="Rentals", font=FONT_TITLE, bg=BG, fg=TEXT_DARK)\
            .pack(anchor="w", padx=30, pady=(25, 15))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # ---------------- Form Panel ----------------
        form = tk.Frame(body, bg=CARD, width=300)
        form.pack(side="left", fill="y", padx=(0, 15))
        form.pack_propagate(False)

        tk.Label(form, text="New Rental", font=("Segoe UI", 13, "bold"), bg=CARD,
                 fg=TEXT_DARK).pack(anchor="w", padx=18, pady=(18, 10))

        tk.Label(form, text="Available Car", font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED)\
            .pack(anchor="w", padx=18, pady=(8, 2))
        self.car_var = tk.StringVar()
        self.car_combo = ttk.Combobox(form, textvariable=self.car_var, state="readonly", width=26)
        self.car_combo.pack(anchor="w", padx=18)

        tk.Label(form, text="Customer", font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED)\
            .pack(anchor="w", padx=18, pady=(8, 2))
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(form, textvariable=self.customer_var, state="readonly", width=26)
        self.customer_combo.pack(anchor="w", padx=18)

        tk.Label(form, text="Due Date (YYYY-MM-DD)", font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED)\
            .pack(anchor="w", padx=18, pady=(8, 2))
        self.due_entry = make_entry(form)
        self.due_entry.pack(anchor="w", padx=18)

        btns = tk.Frame(form, bg=CARD)
        btns.pack(pady=20, padx=18, fill="x")
        make_btn(btns, "Start Rental", self.start_rental).pack(fill="x", pady=4)
        make_btn(btns, "Return Car", self.return_car, bg=GREEN, fg="white").pack(fill="x", pady=4)
        make_btn(btns, "Refresh Lists", self.refresh, bg="#e5e7eb", fg=TEXT_DARK).pack(fill="x", pady=4)

        # ---------------- Table Panel ----------------
        table_wrap = tk.Frame(body, bg=CARD)
        table_wrap.pack(side="left", fill="both", expand=True)

        cols = ("id", "car", "customer", "rent_date", "due_date", "return_date", "cost", "status")
        heads = ("ID", "Car", "Customer", "Rent Date", "Due Date", "Return Date", "Cost", "Status")
        self.tree = make_table(table_wrap, cols, heads, (35, 140, 130, 95, 95, 95, 80, 90))
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh(self):
        conn = get_conn()

        cars = conn.execute(
            "SELECT id, brand, model, plate_number, daily_rate FROM cars WHERE status='Available'"
        ).fetchall()
        self.car_map = {f"{c[1]} {c[2]} ({c[3]}) - ${c[4]}/day": c[0] for c in cars}
        self.car_combo["values"] = list(self.car_map.keys())
        self.car_var.set("")

        custs = conn.execute("SELECT id, name, phone FROM customers").fetchall()
        self.customer_map = {f"{c[1]} ({c[2] or 'no phone'})": c[0] for c in custs}
        self.customer_combo["values"] = list(self.customer_map.keys())
        self.customer_var.set("")

        for r in self.tree.get_children():
            self.tree.delete(r)

        rows = conn.execute("""
            SELECT r.id, c.brand || ' ' || c.model || ' (' || c.plate_number || ')',
                   cu.name, r.rent_date, COALESCE(r.due_date,'-'),
                   COALESCE(r.return_date,'-'), COALESCE(r.total_cost,0), r.status
            FROM rentals r
            JOIN cars c ON r.car_id = c.id
            JOIN customers cu ON r.customer_id = cu.id
            ORDER BY r.id DESC
        """).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

        conn.close()

    def on_select(self, e):
        sel = self.tree.selection()
        if sel:
            self.selected_id = self.tree.item(sel[0])["values"][0]

    def start_rental(self):
        car_label = self.car_var.get()
        cust_label = self.customer_var.get()
        if not car_label or not cust_label:
            messagebox.showerror("Missing Info", "Pick a car and a customer.")
            return

        car_id = self.car_map[car_label]
        customer_id = self.customer_map[cust_label]
        due = self.due_entry.get().strip() or None

        conn = get_conn()
        conn.execute(
            "INSERT INTO rentals (car_id, customer_id, rent_date, due_date, status) "
            "VALUES (?,?,?,?,'Active')",
            (car_id, customer_id, date.today().isoformat(), due)
        )
        conn.execute("UPDATE cars SET status='Rented' WHERE id=?", (car_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Rental Started", "Car marked as rented.")
        self.due_entry.delete(0, "end")
        self.refresh()
        self.app.pages["DashboardPage"].refresh()

    def return_car(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Pick a rental from the table first.")
            return

        conn = get_conn()
        row = conn.execute(
            "SELECT car_id, rent_date, status FROM rentals WHERE id=?", (self.selected_id,)
        ).fetchone()
        if not row:
            conn.close()
            return

        car_id, rent_date_str, status = row
        if status == "Completed":
            messagebox.showinfo("Already Returned", "This one's already closed out.")
            conn.close()
            return

        daily_rate = conn.execute("SELECT daily_rate FROM cars WHERE id=?", (car_id,)).fetchone()[0]

        rent_date = datetime.strptime(rent_date_str, "%Y-%m-%d").date()
        days = max((date.today() - rent_date).days, 1)  # minimum 1-day charge, even for same-day returns
        total = round(days * daily_rate, 2)

        conn.execute(
            "UPDATE rentals SET return_date=?, total_cost=?, status='Completed' WHERE id=?",
            (date.today().isoformat(), total, self.selected_id)
        )
        conn.execute("UPDATE cars SET status='Available' WHERE id=?", (car_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Car Returned", f"Days: {days}\nTotal: ${total:.2f}")
        self.refresh()
        self.app.pages["DashboardPage"].refresh()


# ============================================================
#                MAIN APP WINDOW & NAVIGATION
# ============================================================

class CarRentalApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Car Rental Management System")
        self.geometry("1180x680")
        self.minsize(1000, 620)
        self.configure(bg=BG)

        init_db()

        self.nav_buttons = {}
        self.build_sidebar()

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}
        for Page in (DashboardPage, CarsPage, CustomersPage, RentalsPage):
            p = Page(self.content, self)
            self.pages[Page.__name__] = p
            p.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_page("DashboardPage")

    def build_sidebar(self):
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="🚗  DriveEase", bg=SIDEBAR_BG, fg="white",
            font=("Segoe UI", 13, "bold"), pady=28
        ).pack(fill="x")

        items = [
            ("🏠  Dashboard", "DashboardPage"),
            ("🚘  Cars", "CarsPage"),
            ("👤  Customers", "CustomersPage"),
            ("📋  Rentals", "RentalsPage"),
        ]

        for label, page in items:
            b = tk.Button(
                sidebar, text=label, anchor="w", bg=SIDEBAR_BG, fg="white",
                font=FONT_NAV, relief="flat", bd=0, padx=24, pady=14,
                activebackground=SIDEBAR_ACTIVE, activeforeground=ACCENT,
                cursor="hand2", command=lambda p=page: self.show_page(p)
            )
            b.pack(fill="x")
            self.nav_buttons[page] = b

        # Spacer pushes the Exit button to the bottom of the sidebar
        tk.Frame(sidebar, bg=SIDEBAR_BG).pack(fill="both", expand=True)

        tk.Button(
            sidebar, text="⏻  Exit", anchor="w", bg=SIDEBAR_BG, fg="#d9534f",
            font=FONT_NAV, relief="flat", bd=0, padx=24, pady=14,
            activebackground=SIDEBAR_ACTIVE, activeforeground="#ff6b6b",
            cursor="hand2", command=self.destroy
        ).pack(fill="x", side="bottom")

    def show_page(self, name):
        for key, btn in self.nav_buttons.items():
            btn.configure(bg=SIDEBAR_ACTIVE if key == name else SIDEBAR_BG)
        page = self.pages[name]
        page.tkraise()
        if hasattr(page, "refresh"):
            page.refresh()


# ============================================================
#                       PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = CarRentalApp()
    app.mainloop()