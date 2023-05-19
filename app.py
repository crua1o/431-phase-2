from flask import Flask, render_template, request, redirect, url_for, session
# The Session instance is not used for direct access, you should always use flask.session
from flask_session import Session
import sqlite3 as sql
import hash_passwords

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'LionAuction'
Session(app)

host = 'http://127.0.0.1:5000/'


# validate user against Users table
def validate():
    connection = sql.connect('users.db')
    # hash session password to check against database
    password = hash_passwords.hash_password(session["password"])

    # check if given email and hashed password exist in database
    cursor = connection.execute('SELECT * FROM Users WHERE email=? AND hashed_pass=?;',
                                (session["email"], password))
    user = cursor.fetchone()
    # no user in table
    if user is None:
        connection.close()
        return False

    connection.close()
    return True


# confirms role of a User with database
def confirm_role(email, role):
    connection = sql.connect('users.db')
    # list of roles a User is
    roles = []
    # check if given email is in Bidders database
    cursor = connection.execute('SELECT * FROM Bidders WHERE email=?;', (email,))
    if cursor.fetchone() is not None and role == "Bidder":
        roles.append("Bidder")

    # check if Seller
    cursor = connection.execute('SELECT * FROM Sellers WHERE email=?;', (email,))
    if cursor.fetchone() is not None and role == "Seller":
        roles.append("Seller")

    # check if Helpdesk
    cursor = connection.execute('SELECT * FROM Helpdesk WHERE email=?;', (email,))
    if cursor.fetchone() is not None and role == "Helpdesk":
        roles.append("Helpdesk")

    connection.close()
    # returns list of roles for that user
    return roles


# gets appropriate categories based on quantity
def get_categories(quantity):
    connection = sql.connect('users.db')
    cursor = []
    # want only parent categories (navbar)
    if quantity == "parents":
        cursor = connection.execute("SELECT DISTINCT parent_category FROM Categories "
                                    "ORDER BY parent_category")

    # want all categories (auction form, "all" category in navbar)
    elif quantity == "all":
        cursor = connection.execute("SELECT DISTINCT category_name FROM Categories "
                                    "ORDER BY category_name")

    # want children of a category
    else:
        cursor = connection.execute("SELECT category_name FROM Categories WHERE parent_category = ?", (quantity,))

    # Fetch all the results
    results = cursor.fetchall()
    new_result = [cat[0] for cat in results]

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return new_result


# get personal info from bidders table
def get_personal_info(email):
    connection = sql.connect('users.db')

    # get Bidder info
    query = """
        SELECT B.email, B.first_name, B.last_name, B.age, B.gender, B.major, 
               A.street_num, A.street_name, A.zipcode,
               Z.city, Z.state
        FROM Bidders B, Address A, Zipcode_Info Z, Credit_Cards W
        WHERE B.email = ? AND B.home_address_id = A.address_id AND A.zipcode = Z.zipcode"""

    # if a Bidder has a credit card
    test = connection.execute \
        ("SELECT C.credit_card_num[-4:] FROM Credit_Cards C WHERE C.owner_email = ?", (session['email'],)).fetchall()

    if test:
        query = """
            SELECT B.email, B.first_name, B.last_name, B.age, B.gender, 
            B.major, Address.street_num, Address.street_name, Address.zipcode, Zipcode_info.city, 
            Zipcode_info.state, Credit_Cards.credit_card_num[-4:]
            FROM Bidders B
            JOIN Address ON B.home_address_id = Address.address_id
            JOIN Zipcode_Info ON Address.zipcode = Zipcode_Info.zipcode
            JOIN Credit_Cards ON B.email = Credit_Cards.owner_email
            WHERE B.email = ?
            """

    result = connection.execute(query, (email,)).fetchone()
    if test:
        # convert from tuple to list
        result_list = list(result)
        # trim cred card info
        result_list[-1] = result_list[-1][-4:]
        # back to tuple
        result = tuple(result_list)

    if not result:
        print("failed to get results")
    connection.close()
    return result


# get seller info from sellers table + bidders table if necessary
def get_seller_info(email):
    # roles = list of confirmed roles
    connection = sql.connect('users.db')
    query = ""
    test = connection.execute("SELECT email FROM Bidders WHERE email = ?", (email,)).fetchone()
    # if email in Bidders (Seller is also a Bidder)
    if test:
        query = """
                SELECT B.email, B.first_name, B.last_name, S.balance, C.credit_card_num[-4:],
                B.age, B.gender, B.major, A.street_num, A.street_name, A.zipcode, Z.city, Z.state 
                FROM Bidders B, Sellers S, Address A, Zipcode_info Z, Credit_Cards C
                JOIN Address ON B.home_address_id = A.address_id
                JOIN Zipcode_Info ON A.zipcode = Z.zipcode
                JOIN Credit_Cards ON B.email = C.owner_email
                JOIN Sellers on B.email = S.email
                WHERE B.email = ?"""

    # local vendor or just a Seller
    else:
        query = """
                SELECT Sellers.email, Local_Vendors.business_name, 
                Sellers.balance, Local_Vendors.customer_service_number
                FROM Sellers
                JOIN Local_Vendors ON Sellers.email = Local_Vendors.email
                WHERE Sellers.email = ?"""

        result = connection.execute(query, (email,)).fetchone()

        # not a local vendor, not a bidder
        if result is None:
            query = "SELECT * FROM Sellers WHERE Sellers.email = ?"

    result = connection.execute(query, (email,)).fetchone()
    connection.close()
    return result


# get a bidder's participating auctions (auctions they have bid in)
def get_participating_auctions():
    connection = sql.connect('users.db')
    query = ""
    if session["role"] == "Bidder":

        # perform the SQL query

        query = """
            SELECT A.category, A.auction_title, A.product_name, A.product_description,
            A.quantity, A.status, max(bid_price), A.seller_email
            FROM Auction_Listings A
            JOIN Bids ON Bids.listing_id = A.listing_id
            WHERE bidder_email = ? AND status = 1
            """

    result = connection.execute(query, (session["email"],)).fetchall()
    if not result:
        print("failed to get results")
    connection.close()
    return result


# get current bids on a certain auction
def get_current_bids(list_id):
    connection = sql.connect('users.db')
    # get count of bids with Bids.listing_id == auction_listing[1]
    query2 = "SELECT COUNT(*) FROM Bids B, Auction_Listings A " \
             "WHERE B.seller_email = A.seller_email AND B.listing_id = A.listing_id AND B.listing_id = ?"

    result2 = connection.execute(query2, (list_id,)).fetchone()
    return result2


# gets appropriate listings based on session variable
def get_listings():
    connection = sql.connect('users.db')
    session['current_bids'] = None

    # browsing all listings
    if session.get("category_name") == "all":
        query = "SELECT * FROM Auction_Listings WHERE status = 1"

        # get all listings
        result = connection.execute(query).fetchall()

        session['current_bids'] = []
        for listing in result:
            # access listing id
            list_id = listing[1]
            # get current bids, trim parens and comma
            curr_bid = get_current_bids(list_id)[0]

            # store current bids in list
            session['current_bids'].append(curr_bid)

        connection.close()
        return result

    # get listings of a certain Seller
    elif session.get("category_name") == "my_listings":
        query = """SELECT * FROM Auction_Listings A WHERE seller_email = ? ORDER BY status"""
        result = connection.execute(query, (session["email"],)).fetchall()

        session['current_bids'] = []
        for listing in result:
            # access listing id
            list_id = listing[1]
            # get current bids, trim parens and comma
            curr_bid = get_current_bids(list_id)[0]

            # store current bids in list
            session['current_bids'].append(curr_bid)

        connection.close()
        return result

    # get listings of a certain category
    query = "SELECT * FROM Auction_Listings WHERE status = 1 AND category = ?"
    result = connection.execute(query, (session["category_name"],)).fetchall()

    session['current_bids'] = []
    for listing in result:
        # access listing id
        list_id = listing[1]
        # get current bids, trim parens and comma
        curr_bid = get_current_bids(list_id)[0]

        # store current bids in list
        session['current_bids'].append(curr_bid)

    print(session['current_bids'])
    if not result:
        print("failed to get current bids results")

    connection.close()
    return result


# takes creation form and inserts into table
@app.route('/create_auction', methods=['GET', 'POST'])
def create_auction():
    if request.method == "POST":
        # connect to database
        connection = sql.connect('users.db')

        # get values from form
        email = session['email']

        def get_next_listing_id():
            # Get the highest selling_id value from the Auction_Listings table
            result = connection.execute('SELECT MAX(listing_id) FROM Auction_Listings').fetchone()

            # Set the new selling_id value to be the highest value + 1
            new_listing_id = result[0] + 1

            # Print the new selling_id value
            return new_listing_id

        listing_id = get_next_listing_id()
        chosen_category = request.form['category']
        auction_title = request.form['auction_title']
        product_name = request.form['product_name']
        description = request.form['description']
        quantity = request.form['quantity']
        reserve_price = request.form['reserve_price']
        # convert reserve price from int type to '$___'
        reserve_price = f'${reserve_price}'
        max_bids = request.form['max_bids']
        status = 1

        # above items are in the correct order to be inserted in DB

        # insert entries into table
        connection.execute('INSERT INTO Auction_Listings (seller_email, listing_id, category, auction_title, '
                           'product_name, product_description, quantity, reserve_price, max_bids, status) '
                           'VALUES (?,?,?,?,?,?,?,?,?,?);',
                           (email, listing_id, chosen_category, auction_title, product_name, description,
                            quantity, reserve_price, max_bids, status))
        connection.commit()
        connection.close()
        return redirect(url_for('auction_form'))


# takes edit form and updates table
@app.route('/edit_auction', methods=['GET', 'POST'])
def edit_auction():
    # connect to database
    connection = sql.connect('users.db')
    if request.method == "GET":
        # identify listing from url
        listing_id = request.args.get('id')

        # select auction information from Auction_Listings based on ID and email

        # get values from form
        email = session['email']
        query = "SELECT * FROM Auction_Listings WHERE seller_email = ? AND listing_id = ?"
        result = connection.execute(query, (email, listing_id)).fetchone()

        # reserve price represented as $____, remove $ and convert to int
        result_list = list(result)
        result_list[7] = int(result_list[7][1:])  # remove the dollar sign convert the remaining string to an integer
        result = tuple(result_list)
        return render_template('edit_auction.html', category_result=session["root_categories"], old_listing=result)

    elif request.method == "POST":
        reserve_price = request.form['reserve_price']

        # dictionary to hold form values
        form_contents = {'seller_email': session['email'],
                         'listing_id': request.form['listing_id'],
                         'category': request.form['category'],
                         'auction_title': request.form['auction_title'],
                         'product_name': request.form['product_name'],
                         'product_description': request.form['description'],
                         'quantity': request.form['quantity'],  # convert quantity from int type to '$___'
                         'reserve_price': f'${reserve_price}',
                         'max_bids': request.form['max_bids'],
                         'status': 1}

        # Construct the SET clause of the SQL statement
        set_clause = ', '.join([f'{key} = ?' for key in form_contents.keys()])

        # Construct the SQL statement
        query = f'UPDATE Auction_Listings SET {set_clause} WHERE listing_id = {form_contents["listing_id"]}'

        # Create a tuple of the new values and the primary key value
        values = tuple(form_contents.values())

        # Execute the SQL statement
        connection.execute(query, values)

        # Commit the changes
        connection.commit()

        # Close the connection
        connection.close()

        return redirect(url_for('index'))


# bid on auction
@app.route('/create_bid', methods=['GET', 'POST'])
def create_bid():
    if request.method == "POST":
        # connect to database
        connection = sql.connect('users.db')

        # new bid_id
        def get_next_bid_id():
            # Get the highest selling_id value from the Auction_Listings table
            result = connection.execute('SELECT MAX(bid_id) FROM Bids').fetchone()

            # Set the new selling_id value to be the highest value + 1
            new_bid_id = result[0] + 1

            # Print the new selling_id value
            return new_bid_id

        form_contents = {'bid_id': get_next_bid_id(),  # bid id
                         'seller_email': request.form['seller_email'],  # seller email
                         'listing_id': request.form['listing_id'],   # listing id
                         'bidder_email': session['email'],  # bidder email
                         'bid_price': request.form['bid-price']  # bid price
                         }

        # insert entries into table
        connection.execute('INSERT INTO Bids (bid_id, seller_email, listing_id, bidder_email, bid_price) '
                           'VALUES (?,?,?,?,?);',
                           (form_contents['bid_id'], form_contents['seller_email'], form_contents['listing_id'],
                            form_contents['bidder_email'], form_contents['bid_price']))
        connection.commit()
        connection.close()

        # get subcategories from given category
        subcategories = get_categories(session["category_name"])

        # get listings for that category
        listings = get_listings()
        return render_template('category.html', category_result=session["root_categories"],
                               current_category=session["category_name"], subcategories=subcategories,
                               listings=listings, current_bids_list=session['current_bids'])


# get categories based on category name
@app.route('/category', methods=['GET', 'POST'])
def category():
    # identify category from url
    session["category_name"] = request.args.get('name')

    # get subcategories from given category
    subcategories = get_categories(session["category_name"])

    # get listings for that category
    listings = get_listings()

    return render_template('category.html', category_result=session["root_categories"],
                           current_category=session["category_name"], subcategories=subcategories,
                           listings=listings, current_bids_list=session['current_bids'])


# Seller create an auction
@app.route('/auction_form', methods=['GET', 'POST'])
def auction_form():
    return render_template('auction_form.html', category_result=session["root_categories"])


@app.route('/add_cred_card', methods=['GET', 'POST'])
def cred_card():
    # connect to database
    connection = sql.connect('users.db')

    if request.method == "GET":

        # get all cred card info from user
        query = """SELECT * FROM Credit_Cards C WHERE C.owner_email = ?"""

        credit_cards = connection.execute(query, (session['email'],)).fetchall()

        return render_template('credit_cards.html', category_result=session["root_categories"],
                               credit_cards=credit_cards)

    elif request.method == "POST":
        form_contents = {
            'cc_num': request.form['cc-num'],
            'cc_type': request.form['cc-type'],
            'exp-month': request.form['exp-month'],
            'exp-year': request.form['exp-year'],
            'security-code': request.form['security-code'],
            'owner_email': session['email']
        }

        # insert entries into table
        connection.execute('INSERT INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, '
                           'security_code, owner_email) '
                           'VALUES (?,?,?,?,?,?);',
                           (form_contents['cc_num'], form_contents['cc_type'], form_contents['exp-month'],
                            form_contents['exp-year'], form_contents['security-code'], form_contents['owner_email']))
        connection.commit()
        connection.close()
        return redirect(url_for('cred_card'))


# new user signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route('/', methods=["GET", "POST"])
def index():
    if not session.get("email"):
        return redirect("/login")

    # set session vars
    session["category_name"] = "my_listings"
    session["all_categories"] = get_categories("all")
    session["root_categories"] = get_categories("Root")

    if session.get("role") == "Bidder":
        # get personal info from bidders table
        bidder_info = get_personal_info(session["email"])

        # get participating auctions from Bids/Auction Listings
        my_auctions_result = get_participating_auctions()

        return render_template('bidder_homepage.html', bidder_info=bidder_info,
                               my_auctions_result=my_auctions_result, category_result=session["root_categories"])

    elif session.get("role") == "Seller":
        # get seller info
        seller_info = get_seller_info(session["email"])
        # get auctions where Seller is selling
        seller_listings = get_listings()
        return render_template('seller_homepage.html', category_result=session["root_categories"],
                               seller_info=seller_info, len_seller_info=len(seller_info),
                               seller_listings=seller_listings)

    elif session.get("role") == "Helpdesk":
        return render_template('helpdesk_homepage.html', category_result=session["root_categories"])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # get email, password, role from form
        email = request.form['email']
        password = request.form['password']
        role = request.form['inlineRadioOptions']

        session["email"] = email
        session["password"] = password
        session["role"] = role

        if not validate():
            login_success = 0
            return render_template('login.html', login_success=login_success)

        else:
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    # clear session
    session["email"] = None
    session["password"] = None
    session["role"] = None
    session["category_name"] = None
    session['current_bids'] = None
    return redirect("/")


if __name__ == '__main__':
    app.debug = True
    app.run()
