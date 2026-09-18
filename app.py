import streamlit as st
import sqlite3
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="NORI STREET",
    page_icon="🛍️",
    layout="wide"
)

DB_FILE = "store.db"

# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():

    conn = get_db()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price_ntd INTEGER NOT NULL,
        image TEXT NOT NULL,
        inventory INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_ntd INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        unit_price_ntd INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)

    # Create default admin
    admin = conn.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@store.local",)
    ).fetchone()

    if not admin:
        conn.execute(
            """
            INSERT INTO users
            (name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Store Admin",
                "admin@store.local",
                generate_password_hash("Admin123!"),
                "admin",
                datetime.now().isoformat()
            )
        )

    # Create sample products
    product_count = conn.execute(
        "SELECT COUNT(*) AS count FROM products"
    ).fetchone()["count"]

    if product_count == 0:

        products = [
            (
                "Street Watch",
                "Japanese street-style watch with a clean everyday design.",
                1890,
                "images/watch.svg",
                30
            ),
            (
                "Canvas Tote",
                "Lightweight tote bag for school, shopping and daily use.",
                790,
                "images/tote.svg",
                45
            ),
            (
                "Urban Cap",
                "Simple adjustable cap inspired by Japanese streetwear.",
                590,
                "images/cap.svg",
                60
            ),
            (
                "Daily Sneakers",
                "Comfortable low-top sneakers for everyday city walks.",
                2490,
                "images/sneakers.svg",
                20
            ),
            (
                "Minimal Backpack",
                "Compact backpack with space for school essentials.",
                1590,
                "images/backpack.svg",
                25
            ),
            (
                "Graphic Tee",
                "Relaxed-fit graphic T-shirt with a casual street look.",
                890,
                "images/tee.svg",
                50
            )
        ]

        for product in products:
            conn.execute(
                """
                INSERT INTO products
                (name, description, price_ntd, image, inventory, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (*product, datetime.now().isoformat())
            )

    conn.commit()
    conn.close()


init_db()

# =========================
# SESSION STATE
# =========================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "role" not in st.session_state:
    st.session_state.role = None

if "name" not in st.session_state:
    st.session_state.name = None

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "shop"


# =========================
# HELPERS
# =========================

def money(value):
    return f"NT${value:,}"


def get_products():

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return products


def get_product(product_id):

    conn = get_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id=?",
        (product_id,)
    ).fetchone()

    conn.close()

    return product


def cart_items():

    result = []

    for product_id, quantity in st.session_state.cart.items():

        product = get_product(product_id)

        if product:
            result.append({
                "product": product,
                "quantity": quantity,
                "subtotal": product["price_ntd"] * quantity
            })

    return result


def cart_total():

    return sum(
        item["subtotal"]
        for item in cart_items()
    )


def cart_count():

    return sum(
        st.session_state.cart.values()
    )


def send_order_email(user, order, items):

    smtp_host = os.environ.get("SMTP_HOST")

    if not smtp_host:
        return False

    message = EmailMessage()

    message["Subject"] = f"Your NORI STREET Order #{order['id']}"

    message["From"] = os.environ.get(
        "SMTP_FROM",
        "no-reply@example.com"
    )

    message["To"] = user["email"]

    lines = [
        f"Hi {user['name']},",
        "",
        "Thank you for shopping at NORI STREET!",
        "",
        f"Order #{order['id']}",
        f"Total: {money(order['total_ntd'])}",
        ""
    ]

    for item in items:

        subtotal = (
            item["unit_price_ntd"]
            * item["quantity"]
        )

        lines.append(
            f"{item['product_name']} × "
            f"{item['quantity']} - "
            f"{money(subtotal)}"
        )

    lines += [
        "",
        "Your order has been successfully placed.",
        "",
        "NORI STREET"
    ]

    message.set_content("\n".join(lines))

    port = int(
        os.environ.get("SMTP_PORT", "587")
    )

    with smtplib.SMTP(
        smtp_host,
        port,
        timeout=10
    ) as server:

        server.starttls()

        server.login(
            os.environ["SMTP_USERNAME"],
            os.environ["SMTP_PASSWORD"]
        )

        server.send_message(message)

    return True


# =========================
# LOGIN
# =========================

def login_page():

    st.title("🔐 Login")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        type="primary"
    ):

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email.lower().strip(),)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            st.session_state.user_id = user["id"]
            st.session_state.role = user["role"]
            st.session_state.name = user["name"]

            st.success("Login successful!")

            st.rerun()

        else:

            st.error(
                "Invalid email or password."
            )


def register_page():

    st.title("📝 Create Account")

    name = st.text_input("Name")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button(
        "Create Account",
        type="primary"
    ):

        if not name or not email:
            st.error("Please fill in all fields.")
            return

        if len(password) < 6:
            st.error(
                "Password must be at least 6 characters."
            )
            return

        if password != confirm:
            st.error("Passwords do not match.")
            return

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (name,email,password_hash,role,created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email.lower().strip(),
                    generate_password_hash(password),
                    "customer",
                    datetime.now().isoformat()
                )
            )

            conn.commit()

            st.success(
                "Account created! You can now log in."
            )

        except sqlite3.IntegrityError:

            st.error(
                "This email is already registered."
            )

        finally:

            conn.close()


# =========================
# SHOP
# =========================

def shop_page():

    st.title("NORI STREET")

    st.subheader(
        "Japanese-inspired everyday streetwear"
    )

    st.caption(
        "All prices are shown in NT$"
    )

    products = get_products()

    columns = st.columns(3)

    for index, product in enumerate(products):

        with columns[index % 3]:

            if os.path.exists(product["image"]):

                st.image(
                    product["image"],
                    use_container_width=True
                )

            st.markdown(
                f"### {product['name']}"
            )

            st.write(
                product["description"]
            )

            st.markdown(
                f"**{money(product['price_ntd'])}**"
            )

            st.caption(
                f"Inventory: {product['inventory']}"
            )

            if product["inventory"] > 0:

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=product["inventory"],
                    value=1,
                    step=1,
                    key=f"shop_qty_{product['id']}"
                )

                if st.button(
                    "Add to Cart",
                    key=f"add_{product['id']}"
                ):

                    current = st.session_state.cart.get(
                        product["id"],
                        0
                    )

                    if (
                        current + quantity
                        <= product["inventory"]
                    ):

                        st.session_state.cart[
                            product["id"]
                        ] = current + quantity

                        st.success(
                            f"Added {quantity} item(s)!"
                        )

                    else:

                        st.error(
                            "Not enough inventory."
                        )

            else:

                st.error("Out of stock")


# =========================
# CART
# =========================

def cart_page():

    st.title("🛒 Shopping Cart")

    items = cart_items()

    if not items:

        st.info("Your cart is empty.")

        if st.button("Continue Shopping"):
            st.session_state.page = "shop"
            st.rerun()

        return

    for item in items:

        product = item["product"]
        product_id = product["id"]

        col1, col2, col3, col4 = st.columns(
            [1, 3, 2, 2]
        )

        with col1:

            if os.path.exists(product["image"]):

                st.image(
                    product["image"],
                    width=100
                )

        with col2:

            st.write(
                f"**{product['name']}**"
            )

            st.write(
                money(product["price_ntd"])
            )

        with col3:

            quantity = st.number_input(
                "Quantity",
                min_value=0,
                max_value=product["inventory"],
                value=item["quantity"],
                step=1,
                key=f"cart_qty_{product_id}"
            )

            if quantity != item["quantity"]:

                if quantity == 0:

                    st.session_state.cart.pop(
                        product_id,
                        None
                    )

                else:

                    st.session_state.cart[
                        product_id
                    ] = quantity

                st.rerun()

        with col4:

            st.write(
                f"**{money(item['subtotal'])}**"
            )

            if st.button(
                "Remove",
                key=f"remove_{product_id}"
            ):

                st.session_state.cart.pop(
                    product_id,
                    None
                )

                st.rerun()

        st.divider()

    st.subheader(
        f"Total: {money(cart_total())}"
    )

    if st.button(
        "Proceed to Checkout",
        type="primary"
    ):

        if not st.session_state.user_id:

            st.warning(
                "Please log in before checkout."
            )

            st.session_state.page = "login"

        else:

            st.session_state.page = "checkout"

        st.rerun()


# =========================
# CHECKOUT
# =========================

def checkout_page():

    st.title("💳 Checkout")

    items = cart_items()

    if not items:

        st.warning("Your cart is empty.")
        return

    st.subheader("Order Summary")

    for item in items:

        st.write(
            f"{item['product']['name']} × "
            f"{item['quantity']} — "
            f"{money(item['subtotal'])}"
        )

    st.divider()

    st.markdown(
        f"## Total: {money(cart_total())}"
    )

    st.info(
        "This is a demo payment process. "
        "It does not charge a real card."
    )

    card_name = st.text_input(
        "Name on Card"
    )

    card_number = st.text_input(
        "Card Number",
        placeholder="1234 5678 9012 3456"
    )

    expiry = st.text_input(
        "Expiry",
        placeholder="12/30"
    )

    cvv = st.text_input(
        "CVV",
        type="password"
    )

    if st.button(
        "Pay & Place Order",
        type="primary"
    ):

        digits = "".join(
            c for c in card_number
            if c.isdigit()
        )

        if len(digits) < 12:

            st.error(
                "Please enter a valid demo card number."
            )

            return

        conn = get_db()

        try:

            # Re-check inventory
            for item in items:

                product = conn.execute(
                    "SELECT * FROM products WHERE id=?",
                    (item["product"]["id"],)
                ).fetchone()

                if (
                    not product
                    or product["inventory"]
                    < item["quantity"]
                ):

                    raise ValueError(
                        f"Not enough inventory for "
                        f"{item['product']['name']}."
                    )

            total = cart_total()

            # Create order
            cursor = conn.execute(
                """
                INSERT INTO orders
                (user_id,total_ntd,status,created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    st.session_state.user_id,
                    total,
                    "Paid",
                    datetime.now().isoformat()
                )
            )

            order_id = cursor.lastrowid

            email_items = []

            # Deduct inventory
            for item in items:

                product = item["product"]
                quantity = item["quantity"]

                conn.execute(
                    """
                    UPDATE products
                    SET inventory = inventory - ?
                    WHERE id=?
                    """,
                    (
                        quantity,
                        product["id"]
                    )
                )

                conn.execute(
                    """
                    INSERT INTO order_items
                    (order_id,product_id,
                     product_name,unit_price_ntd,quantity)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        product["id"],
                        product["name"],
                        product["price_ntd"],
                        quantity
                    )
                )

                email_items.append({
                    "product_name": product["name"],
                    "unit_price_ntd": product["price_ntd"],
                    "quantity": quantity
                })

            conn.commit()

            user = conn.execute(
                "SELECT * FROM users WHERE id=?",
                (st.session_state.user_id,)
            ).fetchone()

            order = conn.execute(
                "SELECT * FROM orders WHERE id=?",
                (order_id,)
            ).fetchone()

            # Send email if SMTP is configured
            try:

                send_order_email(
                    user,
                    order,
                    email_items
                )

            except Exception:

                pass

            st.session_state.cart = {}

            st.success(
                f"Order #{order_id} completed!"
            )

            st.session_state.page = "orders"

            st.rerun()

        except Exception as error:

            conn.rollback()

            st.error(str(error))

        finally:

            conn.close()


# =========================
# ORDER HISTORY
# =========================

def orders_page():

    st.title("📦 Order History")

    conn = get_db()

    orders = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (st.session_state.user_id,)
    ).fetchall()

    conn.close()

    if not orders:

        st.info("You have no orders yet.")
        return

    for order in orders:

        with st.expander(
            f"Order #{order['id']} — "
            f"{money(order['total_ntd'])}"
        ):

            st.write(
                f"Date: {order['created_at']}"
            )

            st.write(
                f"Status: {order['status']}"
            )

            conn = get_db()

            items = conn.execute(
                """
                SELECT *
                FROM order_items
                WHERE order_id=?
                """,
                (order["id"],)
            ).fetchall()

            conn.close()

            for item in items:

                st.write(
                    f"{item['product_name']} × "
                    f"{item['quantity']} — "
                    f"{money(item['unit_price_ntd'] * item['quantity'])}"
                )


# =========================
# ADMIN
# =========================

def admin_page():

    st.title("⚙️ Admin Dashboard")

    tabs = st.tabs([
        "Products",
        "Add Product",
        "Orders"
    ])

    # ---------------------
    # PRODUCTS
    # ---------------------

    with tabs[0]:

        products = get_products()

        for product in products:

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [1, 3, 2, 2]
                )

                with col1:

                    if os.path.exists(
                        product["image"]
                    ):

                        st.image(
                            product["image"],
                            width=100
                        )

                with col2:

                    st.write(
                        f"### {product['name']}"
                    )

                    st.write(
                        product["description"]
                    )

                with col3:

                    st.write(
                        f"Price: "
                        f"**{money(product['price_ntd'])}**"
                    )

                    st.write(
                        f"Inventory: "
                        f"**{product['inventory']}**"
                    )

                with col4:

                    if st.button(
                        "Edit",
                        key=f"edit_{product['id']}"
                    ):

                        st.session_state[
                            "editing_product"
                        ] = product["id"]

                        st.rerun()

                    if st.button(
                        "Delete",
                        key=f"delete_{product['id']}"
                    ):

                        conn = get_db()

                        conn.execute(
                            "DELETE FROM products WHERE id=?",
                            (product["id"],)
                        )

                        conn.commit()
                        conn.close()

                        st.rerun()

        # Edit form
        if "editing_product" in st.session_state:

            product = get_product(
                st.session_state["editing_product"]
            )

            if product:

                st.divider()

                st.subheader(
                    f"Edit: {product['name']}"
                )

                name = st.text_input(
                    "Name",
                    value=product["name"]
                )

                description = st.text_area(
                    "Description",
                    value=product["description"]
                )

                price = st.number_input(
                    "Price (NT$)",
                    min_value=0,
                    value=product["price_ntd"]
                )

                inventory = st.number_input(
                    "Inventory",
                    min_value=0,
                    value=product["inventory"]
                )

                image = st.text_input(
                    "Image path",
                    value=product["image"]
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Save Changes",
                        type="primary"
                    ):

                        conn = get_db()

                        conn.execute(
                            """
                            UPDATE products
                            SET name=?,
                                description=?,
                                price_ntd=?,
                                image=?,
                                inventory=?
                            WHERE id=?
                            """,
                            (
                                name,
                                description,
                                price,
                                image,
                                inventory,
                                product["id"]
                            )
                        )

                        conn.commit()
                        conn.close()

                        del st.session_state[
                            "editing_product"
                        ]

                        st.rerun()

                with col2:

                    if st.button("Cancel"):

                        del st.session_state[
                            "editing_product"
                        ]

                        st.rerun()

    # ---------------------
    # ADD PRODUCT
    # ---------------------

    with tabs[1]:

        st.subheader("Add New Product")

        name = st.text_input(
            "Product Name",
            key="new_name"
        )

        description = st.text_area(
            "Description",
            key="new_description"
        )

        price = st.number_input(
            "Price (NT$)",
            min_value=0,
            value=100,
            key="new_price"
        )

        inventory = st.number_input(
            "Inventory",
            min_value=0,
            value=10,
            key="new_inventory"
        )

        image = st.text_input(
            "Image path",
            value="images/watch.svg",
            key="new_image"
        )

        if st.button(
            "Add Product",
            type="primary"
        ):

            conn = get_db()

            conn.execute(
                """
                INSERT INTO products
                (name,description,price_ntd,
                 image,inventory,created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    description,
                    price,
                    image,
                    inventory,
                    datetime.now().isoformat()
                )
            )

            conn.commit()
            conn.close()

            st.success(
                "Product added successfully!"
            )

            st.rerun()

    # ---------------------
    # ORDERS
    # ---------------------

    with tabs[2]:

        conn = get_db()

        orders = conn.execute(
            """
            SELECT
                orders.*,
                users.name,
                users.email
            FROM orders
            JOIN users
            ON users.id = orders.user_id
            ORDER BY orders.id DESC
            """
        ).fetchall()

        conn.close()

        for order in orders:

            st.write(
                f"**Order #{order['id']}**"
            )

            st.write(
                f"Customer: {order['name']} "
                f"({order['email']})"
            )

            st.write(
                f"Total: {money(order['total_ntd'])}"
            )

            st.write(
                f"Status: {order['status']}"
            )

            st.divider()


# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.title("NORI STREET")

    if st.session_state.user_id:

        st.write(
            f"👋 Hi, {st.session_state.name}"
        )

        st.caption(
            f"Role: {st.session_state.role}"
        )

        if st.button(
            f"🛒 Cart ({cart_count()})"
        ):

            st.session_state.page = "cart"
            st.rerun()

        if st.button("🏠 Shop"):

            st.session_state.page = "shop"
            st.rerun()

        if st.session_state.role == "customer":

            if st.button("📦 Order History"):

                st.session_state.page = "orders"
                st.rerun()

        if st.session_state.role == "admin":

            if st.button("⚙️ Admin"):

                st.session_state.page = "admin"
                st.rerun()

        if st.button("Logout"):

            st.session_state.user_id = None
            st.session_state.role = None
            st.session_state.name = None
            st.session_state.cart = {}
            st.session_state.page = "shop"

            st.rerun()

    else:

        if st.button("🏠 Shop"):

            st.session_state.page = "shop"
            st.rerun()

        if st.button("🔐 Login"):

            st.session_state.page = "login"
            st.rerun()

        if st.button("📝 Register"):

            st.session_state.page = "register"
            st.rerun()


# =========================
# ROUTING
# =========================

if st.session_state.page == "shop":

    shop_page()

elif st.session_state.page == "cart":

    cart_page()

elif st.session_state.page == "checkout":

    checkout_page()

elif st.session_state.page == "orders":

    if st.session_state.user_id:
        orders_page()
    else:
        login_page()

elif st.session_state.page == "admin":

    if st.session_state.role == "admin":
        admin_page()
    else:
        login_page()

elif st.session_state.page == "login":

    login_page()

elif st.session_state.page == "register":

    register_page()
