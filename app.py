"""
Smart Canteen Token System
==========================
A small Streamlit web app that lets students place canteen orders, get a
sequential token number, and track the order status. The canteen operator
can update the status of every order. Orders are saved in data/orders.json.

Run with:  streamlit run app.py

How the file is organised (easy to explain in a viva):
  1. Settings        - menu, statuses, file paths
  2. Data functions  - load/save JSON, create order, update status, search
  3. UI helpers      - small functions that draw reusable pieces of the page
  4. Pages           - one function per page in the sidebar
  5. main()          - sets up the page and shows the selected page
"""

import html
import json
import os
from datetime import datetime

import streamlit as st

# ---------------------------------------------------------------------------
# 1. SETTINGS
# ---------------------------------------------------------------------------

# Folder paths are built from the location of this file, so the app works
# no matter which folder you start it from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_FILE = os.path.join(DATA_DIR, "orders.json")

CURRENCY = "₹"
MAX_QTY = 20          # maximum quantity of one item in a single order
MAX_NAME_LEN = 40     # maximum length of the customer name

# The canteen menu. Change prices or add items here - the app updates itself.
MENU = [
    {"id": "samosa", "emoji": "🥟", "name": "Samosa", "price": 15},
    {"id": "sandwich", "emoji": "🥪", "name": "Veg Sandwich", "price": 40},
    {"id": "dosa", "emoji": "🥞", "name": "Masala Dosa", "price": 60},
    {"id": "burger", "emoji": "🍔", "name": "Veg Burger", "price": 50},
    {"id": "chole", "emoji": "🍛", "name": "Chole Bhature", "price": 70},
    {"id": "noodles", "emoji": "🍜", "name": "Veg Noodles", "price": 60},
    {"id": "tea", "emoji": "🍵", "name": "Tea", "price": 10},
    {"id": "coffee", "emoji": "🥤", "name": "Cold Coffee", "price": 40},
]

# Order life cycle, in order. The first one is the default for new orders.
STATUSES = ["Pending", "Preparing", "Ready", "Completed"]

STATUS_COLORS = {
    "Pending": "#f59e0b",     # amber
    "Preparing": "#3b82f6",   # blue
    "Ready": "#10b981",       # green
    "Completed": "#6b7280",   # grey
}

STATUS_MESSAGES = {
    "Pending": "Your order has been received and is waiting to be prepared.",
    "Preparing": "Your food is being prepared. Please wait a little.",
    "Ready": "Your order is READY! Please collect it from the counter.",
    "Completed": "This order has been collected. Thank you!",
}

PAGES = [
    "🍽️ Place Order",
    "📋 Order Management",
    "🔍 Track Order",
    "⚙️ Admin / Reset",
]

# Small amount of CSS to make the page look clean. Kept short on purpose.
CUSTOM_CSS = """
<style>
.banner {
    background: linear-gradient(90deg, #f97316, #ef4444);
    color: white;
    padding: 18px 24px;
    border-radius: 14px;
    margin-bottom: 14px;
}
.banner h1 { color: white; margin: 0; font-size: 1.9rem; }
.banner p  { color: #fff3e6; margin: 4px 0 0 0; }
.food-emoji { font-size: 2.4rem; line-height: 1.1; }
.badge {
    color: white;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    white-space: nowrap;
}
.token-card {
    background: #fff7e6;
    color: #1f2937;
    border: 2px dashed #f97316;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    margin-bottom: 10px;
}
.token-card .label  { font-size: 1rem; color: #6b7280; }
.token-card .number { font-size: 3.2rem; font-weight: 800; color: #ea580c; }
</style>
"""


# ---------------------------------------------------------------------------
# 2. DATA FUNCTIONS (JSON storage and business logic)
# ---------------------------------------------------------------------------

def default_data():
    """Return a fresh, empty data structure."""
    return {"last_token": 0, "orders": []}


def save_data(data):
    """
    Save data to orders.json safely.
    We first write to a temporary file and then replace the real file, so a
    crash in the middle of writing can never leave a half-written JSON file.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_file, DATA_FILE)


def ensure_files():
    """Create the data folder, orders.json and assets folder if missing."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        save_data(default_data())

    assets_note = os.path.join(ASSETS_DIR, "README.txt")
    if not os.path.exists(assets_note):
        with open(assets_note, "w", encoding="utf-8") as f:
            f.write("Put screenshots and images for the project here.\n")


def is_valid_order(order):
    """Check that one order read from the file has all the fields we need."""
    if not isinstance(order, dict):
        return False
    required = ["token", "customer", "time", "items", "total", "status"]
    if any(key not in order for key in required):
        return False
    return isinstance(order["token"], int) and isinstance(order["items"], list)


def load_data():
    """
    Read orders.json and return the data.
    - Missing file     -> create a new empty one.
    - Corrupted file   -> keep a backup copy and start with empty data.
    - Old list format  -> converted to the current format.
    """
    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        # The file could not be read: save a backup and start fresh.
        try:
            os.replace(DATA_FILE, os.path.join(DATA_DIR, "orders.corrupt.json"))
        except OSError:
            pass
        data = default_data()
        save_data(data)
        return data

    # Accept a plain list of orders too (older/simple format).
    if isinstance(raw, list):
        raw = {"last_token": 0, "orders": raw}
    if not isinstance(raw, dict):
        raw = default_data()

    orders = [o for o in raw.get("orders", []) if is_valid_order(o)]
    last_token = raw.get("last_token", 0)
    if not isinstance(last_token, int):
        last_token = 0

    # Make sure the next token can never repeat an existing one.
    highest = max([o["token"] for o in orders], default=0)
    return {"last_token": max(last_token, highest), "orders": orders}


def create_order(customer_name, quantities):
    """
    Build and save a new order.
    quantities is a dict like {"Samosa": 2, "Tea": 1}.
    Returns (order, None) on success or (None, "error message") on failure.
    """
    items = []
    for menu_item in MENU:
        try:
            qty = int(quantities.get(menu_item["name"], 0))
        except (TypeError, ValueError):
            qty = 0

        if qty < 0 or qty > MAX_QTY:
            return None, f"Quantity must be between 0 and {MAX_QTY}."
        if qty > 0:
            items.append({
                "name": menu_item["name"],
                "price": menu_item["price"],
                "qty": qty,
                "subtotal": menu_item["price"] * qty,
            })

    if not items:
        return None, "Your cart is empty. Please select at least one item."

    # Clean the name: remove extra spaces and limit the length.
    name = " ".join(str(customer_name or "").split())[:MAX_NAME_LEN] or "Guest"

    data = load_data()
    token = data["last_token"] + 1          # sequential, never repeats
    order = {
        "token": token,
        "customer": name,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "items": items,
        "total": sum(item["subtotal"] for item in items),
        "status": STATUSES[0],              # every new order starts as Pending
    }
    data["orders"].append(order)
    data["last_token"] = token
    save_data(data)
    return order, None


def update_status(token, new_status):
    """Change the status of one order. Returns True if it worked."""
    if new_status not in STATUSES:
        return False
    data = load_data()
    for order in data["orders"]:
        if order["token"] == token:
            order["status"] = new_status
            save_data(data)
            return True
    return False


def find_order(token):
    """Return the order with this token number, or None if not found."""
    for order in load_data()["orders"]:
        if order["token"] == token:
            return order
    return None


def get_stats(orders):
    """Count total orders and the number of orders in each status."""
    stats = {"Total": len(orders)}
    for status in STATUSES:
        stats[status] = sum(1 for o in orders if o["status"] == status)
    return stats


def clear_all_orders():
    """Delete every order and restart token numbering from 1."""
    save_data(default_data())


# ---------------------------------------------------------------------------
# 3. UI HELPERS
# ---------------------------------------------------------------------------

def money(amount):
    """Format a number as a price, e.g. 120 -> '₹120'."""
    return f"{CURRENCY}{amount}"


def status_badge(status):
    """Return a small coloured HTML badge for an order status."""
    color = STATUS_COLORS.get(status, "#6b7280")
    return f'<span class="badge" style="background:{color}">{html.escape(status)}</span>'


def set_flash(kind, message):
    """Remember a message to show on the next page refresh."""
    st.session_state["flash"] = (kind, message)


def show_flash():
    """Show (and then forget) the message saved by set_flash()."""
    flash = st.session_state.pop("flash", None)
    if not flash:
        return
    kind, message = flash
    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.error(message)


def show_dashboard():
    """Show the summary numbers at the top of every page."""
    stats = get_stats(load_data()["orders"])
    cols = st.columns(5)
    cols[0].metric("📦 Total Orders", stats["Total"])
    cols[1].metric("🟠 Pending", stats["Pending"])
    cols[2].metric("🔵 Preparing", stats["Preparing"])
    cols[3].metric("🟢 Ready", stats["Ready"])
    cols[4].metric("⚪ Completed", stats["Completed"])


def show_order_details(order):
    """Show the full summary of one order (used after ordering and in tracking)."""
    st.markdown(
        f"**Customer:** {html.escape(order['customer'])} &nbsp;|&nbsp; "
        f"**Time:** {html.escape(order['time'])} &nbsp;|&nbsp; "
        f"**Status:** " + status_badge(order["status"]),
        unsafe_allow_html=True,
    )
    rows = [
        {
            "Item": item["name"],
            "Price": money(item["price"]),
            "Qty": item["qty"],
            "Subtotal": money(item["subtotal"]),
        }
        for item in order["items"]
    ]
    st.table(rows)
    st.markdown(f"### Total: {money(order['total'])}")


def show_token_card(order):
    """Show the big token number box."""
    st.markdown(
        f"""
        <div class="token-card">
            <div class="label">Your Token Number</div>
            <div class="number">#{order['token']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 4. PAGES
# ---------------------------------------------------------------------------

def place_order_callback():
    """
    Runs when the 'Place Order' button is clicked.
    It reads the quantities from the page, saves the order, then clears the
    form so the next student can order straight away.
    """
    quantities = {
        item["name"]: st.session_state.get(f"qty_{item['id']}", 0) for item in MENU
    }
    customer = st.session_state.get("customer_name", "")

    order, error = create_order(customer, quantities)
    if error:
        set_flash("warning", error)
        return

    st.session_state["last_order"] = order
    set_flash("success", f"Order placed! Your token number is #{order['token']}.")

    # Reset the form fields.
    for item in MENU:
        st.session_state[f"qty_{item['id']}"] = 0
    st.session_state["customer_name"] = ""


def hide_token_callback():
    """Hide the token card of the last order."""
    st.session_state.pop("last_order", None)


def page_place_order():
    """Menu cards, bill calculation and the Place Order button."""
    # Show the token of the order that was just placed.
    last_order = st.session_state.get("last_order")
    if last_order:
        st.subheader("🎟️ Your Order Token")
        show_token_card(last_order)
        show_order_details(last_order)
        st.caption("Please remember your token number. Use the 'Track Order' page to check the status.")
        st.button("Hide token", on_click=hide_token_callback)
        st.divider()

    st.subheader("🍽️ Menu")
    st.text_input(
        "Your name (optional)",
        key="customer_name",
        max_chars=MAX_NAME_LEN,
        placeholder="e.g. Aman",
    )

    # One card per menu item, 3 cards per row (Streamlit stacks them on phones).
    quantities = {}
    cols = st.columns(3)
    for index, item in enumerate(MENU):
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"<div class='food-emoji'>{item['emoji']}</div>", unsafe_allow_html=True)
                st.markdown(f"**{item['name']}**")
                st.caption(money(item["price"]))
                quantities[item["name"]] = st.number_input(
                    "Quantity",
                    min_value=0,
                    max_value=MAX_QTY,
                    step=1,
                    key=f"qty_{item['id']}",
                )

    # Live bill: recalculated every time a quantity changes.
    st.subheader("🧾 Your Bill")
    bill_rows = []
    total = 0
    for item in MENU:
        qty = int(quantities[item["name"]])
        if qty > 0:
            subtotal = item["price"] * qty
            total += subtotal
            bill_rows.append({
                "Item": item["name"],
                "Price": money(item["price"]),
                "Qty": qty,
                "Subtotal": money(subtotal),
            })

    if bill_rows:
        st.table(bill_rows)
        st.markdown(f"### Total: {money(total)}")
    else:
        st.info("Select at least one item to see your bill.")

    st.button("✅ Place Order", type="primary", on_click=place_order_callback)


def page_order_management():
    """Operator view: list all orders and change their status."""
    st.subheader("📋 Order Management")

    orders = load_data()["orders"]
    if not orders:
        st.info("No orders yet. Orders placed by students will appear here.")
        return

    choice = st.selectbox("Show orders", ["All"] + STATUSES)
    shown = [o for o in orders if choice == "All" or o["status"] == choice]
    shown = sorted(shown, key=lambda o: o["token"], reverse=True)   # newest first

    if not shown:
        st.info(f"No orders with status '{choice}'.")
        return

    for order in shown:
        with st.container(border=True):
            left, right = st.columns([3, 2])

            with left:
                st.markdown(
                    f"#### Token #{order['token']} &nbsp; " + status_badge(order["status"]),
                    unsafe_allow_html=True,
                )
                st.caption(f"{order['customer']}  •  {order['time']}")
                for item in order["items"]:
                    st.write(f"{item['qty']} × {item['name']}  —  {money(item['subtotal'])}")
                st.markdown(f"**Total: {money(order['total'])}**")

            with right:
                current = order["status"] if order["status"] in STATUSES else STATUSES[0]
                new_status = st.selectbox(
                    "Change status",
                    STATUSES,
                    index=STATUSES.index(current),
                    key=f"status_{order['token']}",
                )
                if st.button("Update", key=f"update_{order['token']}"):
                    if update_status(order["token"], new_status):
                        set_flash("success", f"Token #{order['token']} is now '{new_status}'.")
                    else:
                        set_flash("error", "Could not update the order. Please try again.")
                    st.rerun()


def page_track_order():
    """Student view: search an order by token number."""
    st.subheader("🔍 Track Your Order")

    # A form lets the user press Enter or click the button to search.
    with st.form("track_form"):
        token_text = st.text_input("Enter your token number", placeholder="e.g. 5")
        submitted = st.form_submit_button("Check Status")

    if not submitted:
        return

    token_text = token_text.strip().lstrip("#")
    if not token_text:
        st.warning("Please enter a token number.")
        return
    if not token_text.isdigit():
        st.error("Token number must be a whole number, for example 5.")
        return

    order = find_order(int(token_text))
    if order is None:
        st.error(f"No order found with token #{int(token_text)}.")
        return

    show_token_card(order)
    progress = (STATUSES.index(order["status"]) + 1) / len(STATUSES)
    st.progress(progress)
    st.markdown(
        "**Status:** " + status_badge(order["status"]) + " &nbsp; " + STATUS_MESSAGES[order["status"]],
        unsafe_allow_html=True,
    )
    show_order_details(order)


def page_admin():
    """Clear all demo data, but only after the user confirms."""
    st.subheader("⚙️ Admin / Reset Demo Data")
    st.write(f"Orders are stored in: `{DATA_FILE}`")

    order_count = len(load_data()["orders"])
    st.write(f"Orders currently saved: **{order_count}**")

    # Step 1: ask the user to click the reset button.
    # Step 2: show a warning and ask for a final confirmation.
    if not st.session_state.get("confirm_reset", False):
        if st.button("🗑️ Clear all demo data"):
            st.session_state["confirm_reset"] = True
            st.rerun()
    else:
        st.warning(
            "⚠️ This will permanently delete ALL orders and restart token "
            "numbers from #1. Are you sure?"
        )
        yes_col, no_col, _ = st.columns([1, 1, 2])
        if yes_col.button("Yes, delete everything", type="primary"):
            clear_all_orders()
            st.session_state.pop("last_order", None)
            st.session_state["confirm_reset"] = False
            set_flash("success", "All orders were deleted. Token numbers will start from #1 again.")
            st.rerun()
        if no_col.button("Cancel"):
            st.session_state["confirm_reset"] = False
            st.rerun()


# ---------------------------------------------------------------------------
# 5. MAIN
# ---------------------------------------------------------------------------

def main():
    """Set up the page and show whichever page is selected in the sidebar."""
    # set_page_config must be the first Streamlit command.
    st.set_page_config(page_title="Smart Canteen Token System", page_icon="🍽️", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    ensure_files()   # create data files automatically if they are missing

    st.markdown(
        """
        <div class="banner">
            <h1>🍽️ Smart Canteen Token System</h1>
            <p>Order food, get your token, skip the queue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("Menu")
    page = st.sidebar.radio("Go to", PAGES)
    st.sidebar.caption("Student mini project • Python + Streamlit")

    show_flash()
    show_dashboard()
    st.divider()

    if page == PAGES[0]:
        page_place_order()
    elif page == PAGES[1]:
        page_order_management()
    elif page == PAGES[2]:
        page_track_order()
    else:
        page_admin()


# Streamlit runs this file as a script, so __name__ is "__main__".
if __name__ == "__main__":
    main()
