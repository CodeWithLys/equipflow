Smart Inventory System: Python x Oracle APEX

# TechInnovators Equipment Inventory Tracking System

A full-stack web application that integrates **Oracle APEX** with a **Python desktop client** to streamline equipment check-in/check-out, track employee history, and provide actionable insights for inventory management.

![Oracle APEX](https://img.shields.io/badge/Oracle%20APEX-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![REST API](https://img.shields.io/badge/REST%20API-FF6C37?style=for-the-badge&logo=rest&logoColor=white)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Overview

This project was developed for **TechInnovators Inc.** (fictional) to address the challenge of managing a growing inventory of engineering equipment.  
The solution combines an **Oracle APEX portal** for administrators with a **Python client** for employees, ensuring a seamless and efficient workflow.

**Problem Solved:** Inefficient manual tracking, misplaced equipment, and lack of visibility into usage trends.

---

## 🛠 Tech Stack

- **Backend & Admin Portal:** Oracle APEX 22.2, ORDS, Oracle Database 21c, PL/SQL  
- **Employee Client:** Python 3.9+, Tkinter  
- **API Communication:** REST APIs (`requests`)  
- **QR Codes:** `qrcode`, `opencv-python`, `pillow`  
- **Version Control:** Git, GitHub  

---

## 🏗 System Architecture

The system uses a **3-tier architecture**:

1. **Presentation Layer:**  
   - Oracle APEX (Admin Portal)  
   - Python Tkinter (Employee Client)  

2. **Application Layer:**  
   - ORDS (REST APIs)  
   - PL/SQL business logic  

3. **Data Layer:**  
   - Oracle Database 21c  


---

+-------------------+ HTTPS / REST API +-----------------------+
| Python Client | <------------------------> | Oracle APEX Server |
| (Tkinter GUI) | | (Admin & APIs) |
+-------------------+ +-----------------------+
|
| SQL/PLSQL
v
+-----------------------+
| Oracle Database |
| (Data Layer) |
+-----------------------+

## ✨ Features

### **Admin Portal (Oracle APEX)**
- Dashboard with KPIs and analytics  
- CRUD operations for equipment  
- Low-stock alerts & maintenance tracking  
- QR code generation for assets  
- Audit logs of all transactions  

### **Employee Client (Python)**
- Secure login via Employee ID  
- View equipment history  
- Return items via QR code scanning  
- Real-time API integration  

---

## ⚙️ Installation & Setup

### Prerequisites
- Oracle Database 21c+  
- Oracle APEX 22.2+  
- Oracle REST Data Services (ORDS)  
- Python 3.9+  

### 1. Database & APEX Setup
1. Run SQL scripts in `database-scripts/` to create schema and seed data.  
2. Import `apex-application/techinnovators_app.sql` into your APEX workspace.  
3. Configure ORDS for REST access.  

### 2. Python Client Setup
```bash
# Clone repo
git clone https://github.com/your-username/techinnovators-inventory-system.git
cd techinnovators-inventory-system/python-client

# Install dependencies
pip install -r requirements.txt

# Configure API in config.py
BASE_URL = "https://your-apex-instance/ords/techinnovators/"

# Run client
python main.py

## 📖 Usage

### For Administrators
- Log into the **Oracle APEX application**.  
- Manage inventory (add, update, remove items).  
- Approve checkouts and track equipment usage.  
- View reports and analytics dashboards.  

### For Employees
- Launch the **Python desktop client**.  
- Log in with your **Employee ID**.  
- View your current and past checked-out equipment.  
- Return items quickly by scanning your **QR code**.  

📘 For full details, see the [User Manual](Documentation/User_Manual.pdf).


## 🤝 Contributing

Contributions are welcome!  
If you'd like to help improve this project, please follow these steps:

1. **Fork** the repository.  
2. Create a new branch:  
   ```bash
   git checkout -b feature/your-feature-name


## 📜 License

This project was created for **educational purposes** as part of the  
**IFS325 - Advanced Computing** course at the **University of the Western Cape**.  

You are free to **fork and adapt** the project for personal or learning use,  
but it is **not intended for commercial deployment**.  

---

**Developer:** Alyssa Krishna  
**Course:** IFS325 - Advanced Computing  
**University:** University of the Western Cape  
**Date:** September 2025  

![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

