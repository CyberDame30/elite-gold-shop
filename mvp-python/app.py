# app.py — Flask MVP Jewelry Shop (SQLite version)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import (
    init_db,
    create_user,
    find_user_by_email,
    check_password,
    create_order,
    get_all_orders
)
from forms import RegisterForm, LoginForm
from auth import login_required


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "dev-secret-key"


# ============================
# INIT DATABASE
# ============================
init_db()


# ============================
# STATIC CATALOG (MVP)
# ============================
CATALOG = {
    1: {
        "id": 1,
        "name": "Gold Ring Classic",
        "price": 350,
        "image": "/static/img/ring1.jpg",
        "desc": "Класична золота каблучка",
        "gold_type": "Yellow",
        "gem": "None",
        "category": "rings"
    },
    2: {
        "id": 2,
        "name": "Diamond Pendant",
        "price": 1200,
        "image": "/static/img/pendant1.jpg",
        "desc": "Підвіс з діамантом",
        "gold_type": "White",
        "gem": "Diamond",
        "category": "pendants"
    },
    3: {
        "id": 3,
        "name": "Emerald Earrings",
        "price": 900,
        "image": "/static/img/earrings1.jpg",
        "desc": "Сережки зі смарагдами",
        "gold_type": "Rose",
        "gem": "Emerald",
        "category": "earrings"
    }
}


# ============================
# CONSTANTS FOR CUSTOM BUILDER
# ============================
GOLD_TYPES = ["Yellow Gold", "White Gold", "Rose Gold"]
COLORS = ["Natural", "Polished", "Matte"]
CARATS = ["9K", "14K", "18K", "22K"]
PURITIES = ["375", "585", "750", "999"]
GEMS = ["None", "Diamond", "Sapphire", "Emerald", "Ruby"]


# ============================
# HOME PAGE
# ============================
@app.route("/")
def index():
    return render_template("index.html")


# ============================
# ADMIN PANEL
# ============================
@app.route("/admin")
@login_required
def admin():
    if session.get("role") != "admin":
        flash("Доступ дозволений лише адміністратору!", "danger")
        return redirect(url_for("account"))

    orders = get_all_orders()
    return render_template("admin.html", orders=orders)


# ============================
# REGISTRATION
# ============================
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # check if exists
        existing = find_user_by_email(email)
        if existing:
            return render_template("register.html", form=form, message="Користувач вже існує")

        # create account
        create_user(email, password, role="user")

        flash("Акаунт створено!", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


# ============================
# LOGIN
# ============================
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = find_user_by_email(form.email.data)

        if user and check_password(user[2], form.password.data):
            session["user_id"] = user[0]
            session["user_email"] = user[1]
            session["role"] = user[3]

            flash("Успішний вхід!", "success")
            return redirect(url_for("account"))

        flash("Невірний email або пароль", "danger")

    return render_template("login.html", form=form)


# ============================
# LOGOUT
# ============================
@app.route("/logout")
def logout():
    session.clear()
    flash("Ви вийшли з акаунту", "info")
    return redirect(url_for("index"))


# ============================
# CATALOG WITH FILTERS
# ============================
@app.route("/catalog")
def catalog():
    products = list(CATALOG.values())

    # filters
    category = request.args.get("category")
    gold = request.args.get("gold")
    gem = request.args.get("gem")
    price_min = request.args.get("price_min")
    price_max = request.args.get("price_max")

    if category:
        products = [p for p in products if p["category"] == category]

    if gold:
        products = [p for p in products if p["gold_type"] == gold]

    if gem:
        products = [p for p in products if p["gem"] == gem]

    if price_min:
        products = [p for p in products if p["price"] >= int(price_min)]

    if price_max:
        products = [p for p in products if p["price"] <= int(price_max)]

    return render_template(
        "catalog.html",
        products=products,
        gold_types=["Yellow", "White", "Rose"],
        gems=["None", "Diamond", "Sapphire", "Emerald", "Ruby"],
        categories=[
            ("rings", "Каблучки"),
            ("earrings", "Сережки"),
            ("pendants", "Підвіски")
        ]
    )


# ============================
# PRODUCT PAGE
# ============================
@app.route("/product/<int:product_id>")
def product_card(product_id):
    if product_id not in CATALOG:
        flash("Товар не знайдено!", "danger")
        return redirect(url_for("catalog"))

    return render_template("product_card.html", product=CATALOG[product_id])


# ============================
# ADD TO CART
# ============================
@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    if product_id not in CATALOG:
        flash("Товар не знайдено!", "danger")
        return redirect(url_for("catalog"))

    item = CATALOG[product_id]

    cart = session.get("cart", [])
    cart.append({"desc": item["name"], "qty": 1, "price": item["price"]})
    session["cart"] = cart

    flash("Товар додано у кошик!", "success")
    return redirect(url_for("cart"))


# ============================
# CUSTOM JEWELRY BUILDER
# ============================
@app.route("/custom", methods=["GET", "POST"])
@login_required
def custom():
    if request.method == "POST":
        gold = request.form.get("gold_type")
        color = request.form.get("color")
        carat = request.form.get("carat")
        purity = request.form.get("purity")
        gem = request.form.get("gem")
        qty = int(request.form.get("qty", 1))

        base_price = {"9K": 100, "14K": 200, "18K": 350, "22K": 500}
        gem_price = {"None": 0, "Diamond": 800, "Sapphire": 200, "Emerald": 250, "Ruby": 300}

        price_each = base_price[carat] + gem_price[gem]
        desc = f"{gold}, {color}, {carat}, проба {purity}, камінь: {gem}"

        cart = session.get("cart", [])
        cart.append({"desc": desc, "qty": qty, "price": price_each})
        session["cart"] = cart

        flash("Ваш виріб додано у кошик!", "success")
        return redirect(url_for("cart"))

    return render_template(
        "custom.html",
        gold_types=GOLD_TYPES,
        colors=COLORS,
        carats=CARATS,
        purities=PURITIES,
        gems=GEMS,
    )


# ============================
# CART
# ============================
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        cart = session.get("cart", [])

        if not cart:
            flash("Кошик порожній!", "warning")
            return redirect(url_for("catalog"))

        items = [
            {"product_desc": i["desc"], "qty": i["qty"], "price": i["price"]}
            for i in cart
        ]

        order_id = create_order(session["user_id"], items)
        session.pop("cart", None)

        return render_template("order_success.html", order_id=order_id)

    cart_items = session.get("cart", [])
    total = sum(i["qty"] * i["price"] for i in cart_items)

    return render_template("cart.html", cart=cart_items, total=total)


# ======================================
# CHECKOUT (ORDER DETAILS FORM)
# ======================================
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = session.get("cart", [])

    if not cart:
        flash("Ваш кошик порожній!", "warning")
        return redirect(url_for("cart"))

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        city = request.form.get("city")
        address = request.form.get("address")
        delivery_method = request.form.get("delivery_method")
        payment_method = request.form.get("payment_method")
        comment = request.form.get("comment")

        items = [
            {"product_desc": c["desc"], "qty": c["qty"], "price": c["price"]}
            for c in cart
        ]

        order_id = create_order(
            session["user_id"], items,
            customer_name, phone, email, city, address,
            delivery_method, payment_method, comment
        )

        session.pop("cart", None)

        return render_template("order_success.html", order_id=order_id)

    return render_template("checkout.html", cart=cart)




# ============================
# ACCOUNT
# ============================
@app.route("/account")
@login_required
def account():
    return render_template(
        "account.html",
        email=session.get("user_email"),
        role=session.get("role")
    )


# ============================
# RUN APP
# ============================
if __name__ == "__main__":
    app.run(port=5000, debug=True)



    

