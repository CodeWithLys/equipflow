Smart Inventory System: Python x Oracle APEX

A full-stack web application that integrates **Oracle APEX** with a **Python desktop client** to streamline equipment check-in / check-out, track employee history, and provide actionable inventory insights.

![Oracle APEX](https://img.shields.io/badge/Oracle%20APEX-F80000?style=for-the-badge\&logo=oracle\&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![REST API](https://img.shields.io/badge/REST%20API-FF6C37?style=for-the-badge\&logo=rest\&logoColor=white)

---

## 📖 Table of Contents

* [Overview](#-overview)
* [Tech Stack](#-tech-stack)
* [System Architecture](#-system-architecture)
* [Features](#-features)
* [Installation & Setup](#-installation--setup)
* [Usage](#-usage)
* [API Documentation](#-api-documentation)
* [Contributing](#-contributing)
* [License](#-license)

---

## 🚀 Overview

This project was developed for **TechInnovators Inc.** (fictional) to manage a growing inventory of engineering equipment. It pairs an **Oracle APEX admin portal** with a **Python Tkinter client** for employees to provide a simple, reliable check-in / check-out workflow and reporting.

**Problems solved:** reduces manual tracking, prevents misplaced equipment, and gives visibility into usage trends.

---

## 🛠 Tech Stack

* **Backend & Admin Portal:** Oracle APEX, ORDS, Oracle Database, PL/SQL
* **Employee Client:** Python 3.9+, Tkinter
* **API Communication:** REST (`requests`)
* **QR Codes / Vision:** `qrcode`, `opencv-python`, `pillow`
* **Version Control:** Git, GitHub

---

## 🏗 System Architecture

The system follows a 3-tier architecture: Presentation (APEX + Python client), Application (ORDS + PL/SQL), and Data (Oracle DB).

```
┌───────────────────┐           HTTPS / REST API           ┌────────────────────┐
│   Python Client   │ ◄───────────────────────────────► │  Oracle APEX Server │
│   (Tkinter GUI)   │                                       │  (Admin & APIs)     │
└───────────────────┘                                       └────────────────────┘
            │                                                         │
            │                          SQL / PL/SQL                    │
            ▼                                                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     Oracle Database (Data Layer)                          │
│    - Tables: EQUIPMENT, EMPLOYEES, ORDERS, ORDER_ITEMS, INVENTORIES, etc.  │
│    - Stored procedures / business logic (PL/SQL)                          │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Admin Portal (Oracle APEX)

* Dashboard with KPIs and analytics
* Full CRUD for equipment and employees
* Low-stock alerts and maintenance scheduling
* QR asset tag generation
* Audit logs and transaction history

### Employee Client (Python)

* Login with Employee ID
* View current and past checked-out items
* Return items via QR code scan (webcam)
* Real-time communication with REST API

---

## ⚙️ Installation & Setup

### Prerequisites

* Oracle Database (21c+ recommended)
* Oracle APEX (22.x+)
* Oracle REST Data Services (ORDS)
* Python 3.9+ and pip

### Database & APEX

1. Run SQL scripts in `database-scripts/` to create schema and seed sample data.
2. Import `apex-application/techinnovators_app.sql` into your APEX workspace.
3. Configure ORDS and enable the REST modules used by the Python client.

### Python Client

```bash
# Clone the repo
git clone https://github.com/your-username/techinnovators-inventory-system.git
cd techinnovators-inventory-system/python-client

# Install dependencies
pip install -r requirements.txt

# Edit the API endpoint in config.py
# Example:
# BASE_URL = "https://oracleapex/ords/nexora/"

# Run the client
python main.py
```

---

## 📖 Usage

### For Administrators

* Log into the Oracle APEX admin portal.
* Manage inventory (add/update/remove items).
* Approve and process checkouts/returns.
* View analytics and export reports.

### For Employees

* Open the Python client.
* Log in with your Employee ID.
* View current assigned equipment and transaction history.
* Return items by scanning your employee QR code.

For step-by-step instructions and screenshots, see: `Documentation/User_Manual.pdf`

---

## 🔗 API Documentation

Key endpoints:

|                 Endpoint | Method | Description                             |
| -----------------------: | :----: | --------------------------------------- |
|   `checkout/` |  POST  | Check out an item to an employee        |
|     `return/` |  POST  | Process an equipment return             |
| `history/{id}` |   GET  | Get transaction history for an employee |

(Full technical API docs live in `Documentation/Technical_Documentation.pdf`.)

---

## 🤝 Contributing

Contributions are welcome — follow this simple workflow:

1. **Fork** the repository.
2. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

3. Make your changes, then **commit**:

```bash
git add .
git commit -m "Add: short description of changes"
```

4. **Push** your branch:

```bash
git push origin feature/your-feature-name
```

5. Open a **Pull Request** describing your changes.

Please include tests where applicable and keep commits focused and descriptive.

---

## 📜 License

This project was created for **educational purposes** as part of the **IFS325 - Advanced Computing** course at the **University of the Western Cape**.

You are free to fork and adapt the project for learning or personal use. This repository is **not intended for commercial deployment** without prior permission from the author.

---

**Developer:** Alyssa Krishna
**Course:** IFS325 — Advanced Computing
**University:** University of the Western Cape
**Date:** September 2025

![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

---
