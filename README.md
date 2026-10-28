# 🍽️ Smart Canteen Token System

A simple web application that lets college students order food, receive a token number, and track their order status, while the canteen operator manages every order from one screen. Built with **Python** and **Streamlit**, with orders saved in a local **JSON** file.

---

## 📌 Problem Statement

Long queues at college canteens waste students' break time and make it hard for canteen staff to handle orders in a fair, organised way. Students stand in line just to place an order, then wait again without knowing when their food will be ready.

## 🎯 Objectives

- Reduce waiting time by letting students place orders digitally.
- Give every order a unique, sequential token number.
- Let students check their order status without standing in the queue.
- Give the canteen operator a simple way to manage and update orders.
- Keep the system lightweight: no login, no paid APIs, no external database.

## ✨ Features

- Food menu displayed as cards, with prices
- Select items and quantities
- Automatic bill calculation
- Unique sequential token number for every order
- Order summary shown after placing an order
- Dashboard showing total, pending, preparing, ready and completed orders
- Order management section listing all orders (with a status filter)
- Operator can set status: **Pending → Preparing → Ready → Completed**
- Search an order by token number to check its status
- Orders saved in `data/orders.json` and kept after restarting the app
- Reset / clear demo data option with a confirmation step
- Input validation, empty-order handling, and safe handling of missing or corrupted data files

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.9+ | Core programming language |
| Streamlit | Web interface |
| JSON | Local storage of orders |

## 📁 Project Folder Structure

```
smart-canteen-token-system/
├── app.py              # Main application (UI + logic)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Files Git should ignore
├── data/
│   └── orders.json     # Saved orders (created automatically if missing)
└── assets/
    └── README.txt      # Place for screenshots and images
```

## 💻 Installation (Windows + VS Code)

### 1. Prerequisites

- Install **Python 3.9 or newer** from [python.org](https://www.python.org/downloads/). During installation, tick **"Add Python to PATH"**.
- Install **Visual Studio Code** from [code.visualstudio.com](https://code.visualstudio.com/).
- (Optional) Install the **Python** extension in VS Code.

Check that Python works by opening a terminal and running:

```bash
python --version
```

### 2. Open the project in VS Code

1. Unzip the project (or clone it from GitHub).
2. In VS Code choose **File → Open Folder…** and select the `smart-canteen-token-system` folder.
3. Open the terminal with **Terminal → New Terminal**.

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

> If PowerShell blocks the activation script, run this once and try again:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> Or simply use **Command Prompt** instead of PowerShell.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

If the `streamlit` command is not found, use:

```bash
python -m streamlit run app.py
```

The app opens automatically in your browser at **http://localhost:8501**. Press `Ctrl + C` in the terminal to stop it.

## 📖 How to Use

**Students**

1. Open **🍽️ Place Order**, enter your name (optional) and choose quantities for the items you want.
2. Check the bill, then click **✅ Place Order**.
3. Note your **token number** shown on screen.
4. Open **🔍 Track Order**, enter your token number and click **Check Status**.

**Canteen operator**

1. Open **📋 Order Management** to see all orders (newest first). Use the filter to show only some statuses.
2. For an order, choose a new status and click **Update**.
3. When the food is ready, set the status to **Ready**; after the student collects it, set it to **Completed**.

**Resetting demo data**

1. Open **⚙️ Admin / Reset** and click **Clear all demo data**.
2. Confirm with **Yes, delete everything** (or choose **Cancel**). Token numbers restart from #1.

## 🖼️ Screenshots

Add your screenshots to the `assets/` folder and link them here.

| Page | Screenshot |
|------|-----------|
| Dashboard / Place Order | `![Place Order](assets/place-order.png)` |
| Order Management | `![Order Management](assets/order-management.png)` |
| Track Order | `![Track Order](assets/track-order.png)` |

*(Replace the table above with the actual images once you have taken the screenshots.)*

## 🚀 Uploading to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Smart Canteen Token System"
git branch -M main
git remote add origin https://github.com/<your-username>/smart-canteen-token-system.git
git push -u origin main
```

## 🔮 Future Improvements

- Separate operator login so only staff can change statuses
- Auto-refresh the order list and track page
- Estimated waiting time for each order
- Editable menu and prices from the admin page
- Daily sales report and export to CSV
- Online payment (UPI) integration
- Switch from JSON to SQLite for larger canteens
- SMS or notification when an order is ready

## 👤 Author

**Syed Mishar Hamid**
B.Tech AI & Data Science, University of Kashmir
