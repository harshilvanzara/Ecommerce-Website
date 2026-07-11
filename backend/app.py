from flask import Flask, render_template, request, redirect, session
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    product TEXT
)
""")

conn.commit()
conn.close()

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
app.secret_key = "secret123"

def db():
    return sqlite3.connect("database.db")
@app.route("/")
def home_page():
    conn = sqlite3.connect("database.db")
    data = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()

    return render_template("index.html", orders=data)

@app.route('/')
def home():
    conn = db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("index.html", products=products)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = db()
        conn.execute("INSERT INTO users (username,password) VALUES (?,?)",(u,p))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone()
        conn.close()

        if user:
            session['user'] = user[0]
            return redirect('/')
        else:
            return "Invalid Login"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_product', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']

        conn = db()
        conn.execute("INSERT INTO products (name,price) VALUES (?,?)",(name,price))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template("add_product.html")

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    return redirect('/')

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    conn = db()

    items = []
    for i in cart:
        p = conn.execute("SELECT * FROM products WHERE id=?",(i,)).fetchone()
        if p:
            items.append(p)

    conn.close()
    return render_template("cart.html", items=items)

@app.route('/remove/<int:index>')
def remove(index):
    session['cart'].pop(index)
    return redirect('/cart')

@app.route('/order')
def order():
    if 'user' not in session:
        return redirect('/login')

    cart = session.get('cart', [])
    user_id = session['user']

    conn = db()

    for i in cart:
        p = conn.execute("SELECT * FROM products WHERE id=?",(i,)).fetchone()
        if p:
            conn.execute("INSERT INTO orders (user_id,product_name,price) VALUES (?,?,?)",(user_id,p[1],p[2]))

    conn.commit()
    conn.close()

    session['cart'] = []
    return "Order Placed Successfully!"

@app.route('/orders')
def orders():
    if 'user' not in session:
        return redirect('/login')

    conn = db()
    data = conn.execute("SELECT * FROM orders WHERE user_id=?",(session['user'],)).fetchall()
    conn.close()

    return render_template("orders.html", orders=data)

if __name__ == "__main__":
    app.run(debug=True)