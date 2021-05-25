import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # query for each stock's amount of shares, symbol and company's name
    transactions = db.execute(
        "SELECT SUM(shares) AS COUNT, symbol, name FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])

    # query for user's cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    # create new element in cash dict and add current cash balance
    cash[0]['total_cash'] = cash[0]['cash']

    # go over each row of transactions query
    for transaction in transactions:

        # store lookup on each symbol in a dictionary
        dict = lookup(transaction['symbol'])

        # create a new element in each row and assign the lookup price as value
        transaction['current_price'] = dict['price']

        # count the total price of current share price times amount of shares
        transaction['total'] = transaction['current_price'] * transaction['COUNT']

        # increment total cash balance with each symbol's total share price value
        cash[0]['total_cash'] += transaction['total']

    # render index.html template
    return render_template("index.html", transactions=transactions, cash=cash)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Add additional cash"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure user provides input
        if not request.form.get("cash"):
            return apology("missing amount", 400)

        # Ensure user inputs a positive integer
        if float(request.form.get("cash")) <= 0:
            return apology("input a positive integer", 400)

        # update user's cash balance
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", request.form.get("cash"), session["user_id"])

        # redirect user to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add_cash.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # call lookup function on the symbol provided by the user
        quote = lookup(request.form.get("symbol"))

        # if input not found in IEX database, return apology
        if quote is None:
            return apology("incorrect symbol", 400)

        # ensure user inputs a positive integer
        if not request.form.get("shares", type=int) or request.form.get("shares", type=int) <= 0:
            return apology("input a positive integer", 400)

        # store time via the now function
        now = datetime.now()

        # edit time into a date string with a selected date format
        time = now.strftime("%Y-%m-%d %H:%M:%S")

        # query for current user's cash balance
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        # count total price of selected shares
        shares = float(request.form.get("shares")) * quote['price']

        # make sure user's cash disposal is greater than or equal to the amount of shares selected
        if cash[0]['cash'] >= shares:

            # insert what the user bought and the amount of shares bought
            db.execute("INSERT INTO transactions (user_id, symbol, name, shares, date, price) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], quote['symbol'],  quote['name'], request.form.get("shares"), time, quote['price'])

            # update user's cash balance
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", shares, session["user_id"])

            # redirect user to homepage
            return redirect("/")

        # if cash disposal lower than price of shares, return apology
        else:
            return apology("not enough cash", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure password was submitted
        if not request.form.get("current_password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide new password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password matches password confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and password confirmation must match", 400)

        # Query database for username
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Ensure current password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
            return apology("invalid password", 403)

        # Update hash in table with new password
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(
            request.form.get("password"), method='pbkdf2:sha256', salt_length=8), session["user_id"])

        # Log user out for safety reasons
        return redirect("/logout")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # query for all transactions made for current user
    history = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])

    # render a new template with a transaction history
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # call lookup function on the symbol provided by the user
        quote = lookup(request.form.get("symbol"))

        # if input not found in IEX database, return apology
        if quote is None:
            return apology("incorrect symbol", 400)

        # return a new html which prints out details of selected company
        return render_template("quoted.html", quote=quote)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password matches password confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and password confirmation must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username doesn't exist
        if len(rows) == 1:
            return apology("user already exists", 400)

        # Register the user (insert into db) and store hash of the password
        register = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"),
                              generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))

        # Remember which user has logged in
        session["user_id"] = register

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure user selects a valid symbol
        if not request.form.get("symbol"):
            return apology("must select a symbol", 400)

        # ensure user inputs a positive integer
        if not request.form.get("shares", type=int) or request.form.get("shares", type=int) <= 0:
            return apology("input a positive integer", 400)

        # query for amount of shares for selected symbol
        shares = db.execute("SELECT SUM(shares) AS COUNT FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol HAVING SUM(shares) > 0",
                            session["user_id"], request.form.get("symbol"))

        # ensure user has enough shares to sell
        if request.form.get("shares", type=int) > shares[0]['COUNT']:
            return apology("ya broke, you ain't got so many shares - lower the number", 400)

        # store time via the now function
        now = datetime.now()

        # edit time into a date string with a selected date format
        time = now.strftime("%Y-%m-%d %H:%M:%S")

        # call lookup function on the symbol provided by the user
        quote = lookup(request.form.get("symbol"))

        # count total price of selected shares
        total_shares = float(request.form.get("shares")) * quote['price']

        # insert what the user sold and the amount of shares sold
        db.execute("INSERT INTO transactions (user_id, symbol, name, shares, date, price) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], quote['symbol'],  quote['name'], (-request.form.get("shares", type=int)), time, quote['price'])

        # update user's cash balance
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_shares, session["user_id"])

        # redirect user to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # query for all stocks (symbols) that user currently owns
        sell = db.execute(
            "SELECT SUM(shares), symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])

        return render_template("sell.html", sell=sell)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
