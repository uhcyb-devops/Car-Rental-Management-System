<div align="center">

# 🚗 DriveEase

### Car Rental Management System — A Sleek Desktop App for Fleet, Customer & Rental Management

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-4B8BBE?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![SQLite](https://img.shields.io/badge/Database-SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#-license)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)](#)

</div>

---

## 📖 Overview

**DriveEase** is a modern, desktop Car Rental Management System built with **Python's Tkinter** for the interface and **SQLite** for persistent storage. It replaces messy spreadsheets and paper logs with a clean, sidebar-navigated dashboard that tracks your entire fleet, customer base, and rental transactions in real time — complete with automatic cost calculation on every return.

Single file, zero configuration — just run it and the database sets itself up.

---

## ✨ Features

### 📊 Dashboard
- Live KPI cards: **Total Cars**, **Available Cars**, **Rented Cars**, **Customers**, and **Total Revenue**
- Quick-glance table of the 8 most recent rental transactions
- Auto-refreshes every time you navigate back to it

### 🚘 Fleet Management (Cars)
- Add, update, and delete cars with brand, model, year, plate number, and daily rate
- Status tracking: **Available**, **Rented**, or **Maintenance**
- Duplicate plate number protection (unique constraint + friendly error handling)
- Click-to-edit: select any row to instantly load it into the form

### 👤 Customer Management
- Add, update, and delete customer records
- Stores name, phone, email, and driver's license number
- Click-to-edit workflow identical to the Cars page for consistency

### 📋 Rentals & Returns
- Start a new rental by selecting an available car and a customer from searchable dropdowns
- Optional due date field for planned return tracking
- One-click **Return Car** automatically:
  - Calculates total days rented (minimum 1-day charge, even for same-day returns)
  - Computes total cost using the car's daily rate
  - Marks the car as **Available** again
  - Updates the rental status to **Completed**
- Full rental history table with rent date, due date, return date, cost, and status

### 🎨 Design
- Custom dark sidebar with gold accent theme
- Consistent, reusable styled buttons, entry fields, and data tables across every page
- Responsive layout with a minimum window size for smaller screens

---

## 🗺️ Application Flow

```
Launch App → Initialize Database → Main Window
                                         │
                        ┌────────────────┼────────────────┬────────────────┐
                        │                │                │                │
                   Dashboard          Cars            Customers         Rentals
                  (KPIs + Recent)   (Fleet CRUD)     (Customer CRUD)   (Book & Return)
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.8** or higher
- Tkinter (included with most standard Python installations)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/drive-ease.git

# 2. Move into the project directory
cd drive-ease

# 3. Run the application
python car_rental_system.py
```

> No external packages required — the project uses only Python's standard library (`tkinter`, `sqlite3`, `datetime`).

On first launch, `car_rental.db` is created automatically in the project folder, along with the `cars`, `customers`, and `rentals` tables — no manual setup needed.

---

## 🧩 Project Structure

```
drive-ease/
├── car_rental_system.py    # Complete application — UI, database layer, and logic in one file
├── car_rental.db             # Auto-generated on first run (SQLite database)
└── README.md                  # Project documentation
```

---

## 🖼️ Preview

```
============================================================
  🚗 DriveEase                 Dashboard
============================================================
  🏠 Dashboard        Overview of your fleet, customers
  🚘 Cars              and active rentals
  👤 Customers
  📋 Rentals          ┌───────────┬───────────┬───────────┬───────────┬───────────┐
                       │ TOTAL     │ AVAILABLE │ RENTED    │ CUSTOMERS │ REVENUE   │
                       │ CARS: 12  │ CARS: 8   │ CARS: 4   │ 27        │ $4,250.00 │
                       └───────────┴───────────┴───────────┴───────────┴───────────┘

  ⏻ Exit               Recent Rentals
                       ┌────┬─────────────────────┬──────────┬────────────┬───────────┐
                       │ ID │ Car                 │ Customer │ Rent Date  │ Status    │
                       ├────┼─────────────────────┼──────────┼────────────┼───────────┤
                       │ 14 │ Toyota Corolla      │ Ali Khan │ 2026-08-09 │ Active    │
                       │ 13 │ Honda Civic         │ Sana Raz │ 2026-08-05 │ Completed │
                       └────┴─────────────────────┴──────────┴────────────┴───────────┘
```

---

## 💰 How Rental Cost Calculation Works

When a car is returned, DriveEase automatically works out the bill:

1. Calculates the number of days between the rental date and today's date
2. Applies a **minimum 1-day charge**, even if the car is returned the same day
3. Multiplies the days by the car's daily rate to get the total cost
4. Updates the rental record and frees up the car for the next customer

---

## 🛠️ Tech Stack

| Layer          | Technology            |
|----------------|------------------------|
| Language        | Python 3               |
| GUI Framework   | Tkinter / ttk           |
| Database        | SQLite                 |
| Architecture    | Single-file, class-based pages |

---

## 🔮 Future Enhancements

- [ ] Search and filter bars on Cars, Customers, and Rentals tables
- [ ] Overdue rental alerts based on due dates
- [ ] Printable rental invoices/receipts (PDF export)
- [ ] Multi-user login with role-based access
- [ ] Car image uploads for each fleet entry
- [ ] Monthly/yearly revenue charts and analytics
- [ ] Migration path to a client-server database (PostgreSQL/MySQL)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](../../issues) or submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute it.

---

<div align="center">

### ⭐ If you find this project useful, consider giving it a star!

**Made with 💻 for smoother fleet management**

</div>

