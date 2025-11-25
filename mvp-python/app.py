# app.py - main Flask app for MVP
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import init_db, create_user, find_user_by_email, check_password, create_order
from forms import RegisterForm, LoginForm
from auth import login_required
from pathlib import Path

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "dev-secret-change-me"  # for lab use only

# initialize DB
init_db()

# available options for product creation
GOLD_TYPES = ["Yellow Gold", "White Gold", "Rose Gold"]
COLORS = ["Natural", "Polished", "Matte"]
CARATS = ["9K", "14K", "18K", "22K"]
PURITIES = ["375", "585", "750", "999"]  # examples
GEMS = ["None", "Diamond", "Sapphire", "Emerald", "Ruby"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            create_user(form.email.data, form.password.data)
            flash("Registered. Now login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Email already exists or error", "danger")
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        row = find_user_by_email(form.email.data)
        if row and check_password(row[2], form.password.data):
            session["user_id"] = row[0]
            session["user_email"] = row[1]
            session["role"] = row[3]
            flash("Logged in", "success")
            return redirect(url_for("account"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("index"))

@app.route("/product", methods=["GET","POST"])
@login_required
def product():
    if request.method == "POST":
        # read selections and create a cart item in session
        gold_type = request.form.get("gold_type")
        color = request.form.get("color")
        carat = request.form.get("carat")
        purity = request.form.get("purity")
        gem = request.form.get("gem")
        qty = int(request.form.get("qty", 1))
        # price calc (simple): base by carat + gem premium
        base_price_map = {"9K": 100, "14K": 200, "18K": 350, "22K": 500}
        gem_price = {"None": 0, "Diamond": 800, "Sapphire": 200, "Emerald": 250, "Ruby": 300}
        price_each = base_price_map.get(carat, 200) + gem_price.get(gem, 0)
        desc = f"{gold_type}, {color}, {carat}, purity {purity}, gem: {gem}"
        cart = session.get("cart", [])
        cart.append({"desc": desc, "qty": qty, "price": price_each})
        session["cart"] = cart
        flash("Added to cart", "success")
        return redirect(url_for("cart"))
    return render_template("product.html", gold_types=GOLD_TYPES, colors=COLORS, carats=CARATS, purities=PURITIES, gems=GEMS)

@app.route("/cart", methods=["GET","POST"])
@login_required
def cart():
    if request.method == "POST":
        # checkout
        cart = session.get("cart", [])
        if not cart:
            flash("Cart empty", "warning")
            return redirect(url_for("product"))
        items = [{"product_desc": c["desc"], "qty": c["qty"], "price": c["price"]} for c in cart]
        order_id = create_order(session["user_id"], items)
        session.pop("cart", None)
        return render_template("order_success.html", order_id=order_id)
    cart = session.get("cart", [])
    total = sum(c["qty"]*c["price"] for c in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/account")
@login_required
def account():
    return render_template("account.html", email=session.get("user_email"), role=session.get("role"))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
