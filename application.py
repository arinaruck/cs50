from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT * FROM users WHERE id = :username", username = session["user_id"])
    stocks = db.execute("SELECT * FROM history WHERE username = :username", username = rows[0]["username"])
    shares = db.execute("SELECT * FROM shares WHERE username = :username", username = rows[0]["username"])
    cash = rows[0]["cash"]
    info = []
    total = []
    i = 0
    for share in shares:
        info.append(lookup(share["symbol"]))
        i += 1
    total = []
    summ = 0
    for j in range(i):
        total.append((info[j]["price"]*shares[j]["shares"]))
        summ += total[j]
        total[j] = usd(total[j]) 
        info[j]["price"] = usd(info[j]["price"])
    summ += cash    
    cash = usd(cash)
    summ = usd(summ)
    return render_template("index.html", shares = shares, info = info, i = i, total = total, summ = summ, cash = cash ) 

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        
        if not request.form.get("shares"):
            return apology("must provide the number of shares")
        elif not request.form.get("buy_symbol"):
            return apology("must provide symbol")
        else:
            try: shares = float(request.form.get("shares"))
            except: return apology("the number of share must be a positive number")  
            if (shares-int(shares) != 0):
                return apology("number of shares must be an integer")
            elif (shares < 1):
                return apology("the number of shares is not valid")
            else:
                shares = int(shares)            
            stock = lookup(request.form.get("buy_symbol"))
            if stock == None:
                return apology("stock name is not valid")    
                
        rows = db.execute("SELECT * FROM users WHERE id = :username", username = session["user_id"])
        cash = rows[0]["cash"]
        
#        return apology(str(session["user_id"]))
        if cash >= stock["price"]*shares:
            f = db.execute("INSERT INTO history (price, shares, symbol, username, action) VALUES(:price, :shares, :symbol, :username, :action)", price = stock["price"], shares = request.form.get("shares"), symbol = stock["symbol"],  username = rows[0]["username"], action = "buy")
            if f == None:
                return apology(str(stock["price"]))
            ff = db.execute("UPDATE users SET cash = cash - :spent WHERE id = :username", spent = stock["price"]*shares, username = session["user_id"])
            if ff == None:
                return apology(":(((")
            fff = db.execute("INSERT INTO shares (combo, symbol, shares, username) VALUES (:combo, :symbol, :shares, :username)", combo = (rows[0]["username"] + stock["symbol"]), symbol = stock["symbol"], shares = shares, username = rows[0]["username"])
            if fff == None:
#                return apology(str(bought)+username)
                ffff =db.execute("UPDATE shares SET shares = shares + :bought WHERE combo = :combo",  bought =shares, combo = (rows[0]["username"] + stock["symbol"])) 
                if ffff == None:
                    return apology(":(((((")
            return redirect(url_for("index"))
        else:
            return apology("Looks like you don't have enough cash")
    else:
        return render_template("buy.html")      
        

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    rows = db.execute("SELECT * FROM users WHERE id = :username", username = session["user_id"])
    stocks = db.execute("SELECT * FROM history WHERE username = :username", username = rows[0]["username"])
    shares = db.execute("SELECT * FROM shares WHERE username = :username", username = rows[0]["username"])
    cash = rows[0]["cash"]
    info = []
    total = []
    i = 0
    for stock in stocks:
        info.append(usd(float(stock["price"])*int(stock["shares"])))
        i += 1
    return render_template("history.html", stocks = stocks, info = info, i = i) 


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        
        if not request.form.get("symbol"):
            return apology("must provide stock name")
        else:
            stock = lookup(request.form.get("symbol"))
            if stock == None:
                return apology("stock name is not valid")
            else:
                return render_template("quoted.html", stockname = stock["name"], stockprice = usd(stock["price"]))
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username!")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        
        elif not request.form.get("password_again"):
            return apology("must confirm password")
            
        password = request.form.get("password")    
        confirmation_pass = request.form.get("password_again")    
        
        if (password != confirmation_pass):
            return apology("Ooops! Seems like passwords are not the same")    
            
        p_hash = pwd_context.encrypt(password)  
        # query database for username
        result = db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=p_hash)
        if not result:
            return apology("This user is already registered")


        # redirect user to home page
        return redirect(url_for("index"))
    else:
        return render_template("register.html")    
        
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    """Register user."""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username!")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        
        elif not request.form.get("new_password"):
            return apology("must enter new password")
            
        elif not request.form.get("new_password_again"):
            return apology("must confirm new password")    
            
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")    
            
        new_password = request.form.get("new_password")    
        confirmation_pass = request.form.get("new_password_again")    
        
        if (new_password != confirmation_pass):
            return apology("Ooops! Seems like passwords are not the same")    
            
        p_hash = pwd_context.encrypt(new_password)  
  
        result = db.execute("UPDATE users SET hash = :hash WHERE username = :username", hash=p_hash, username=request.form.get("username"))
        if not result:
            return apology("This user is already registered")

        return redirect(url_for("success"))
    else:
        return render_template("change_password.html")  
        
@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":
        
        if not request.form.get("shares"):
            return apology("must provide the number of shares")
        elif not request.form.get("sell_symbol"):
            return apology("must provide symbol")
        else:
            try: sell_shares = float(request.form.get("shares"))
            except: return apology("the number of shares must be a positive number")  
            if (sell_shares-int(sell_shares) != 0):
                return apology("the number of shares must be an integer")
            elif (sell_shares < 1):
                return apology("the number of shares is not valid")
            else:
                sell_shares = int(sell_shares)            
                stock = lookup(request.form.get("sell_symbol"))
                if stock == None:
                    return apology("stock name is not valid")    
                rows = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
                cash = rows[0]["cash"]
                share = db.execute("SELECT * FROM shares where combo = :combo", combo = (rows[0]["username"] + request.form.get("sell_symbol")))
                if (share == None) or (len(share) == 0):
                    return apology("Ooops! You can't do that!")
                if sell_shares < int(share[0]["shares"]):
                    f=db.execute("INSERT INTO history (price, shares, symbol, username, action) VALUES(:price, :shares, :symbol, :username, :action)", price = stock["price"], shares = request.form.get("shares"), symbol = stock["symbol"],  username = rows[0]["username"], action = "sell")
                    if f == None:
                        return apology(str(stock["price"]))
                    ff=db.execute("UPDATE users SET cash = cash + :earned WHERE id = :id", earned = stock["price"]*sell_shares, id = session["user_id"])
                    if ff == None:
                        return apology(":(((")
                    fff = db.execute("UPDATE shares SET shares = shares - :sold WHERE combo = :combo",  sold =sell_shares, combo = (rows[0]["username"] + stock["symbol"]))   
                    if fff == None:
                        return apology("Seems like you don't own any of those shares")    
                    return redirect(url_for("index"))
                else:
                    return apology("You don't have enough shares to sell")
    else:
        return render_template("sell.html")
