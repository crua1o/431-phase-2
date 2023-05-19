# Colin Rualo CMPSC 431W
# LionAuction Phase 2

## Context
This web application is for the fictional LionAuction, an e-commerce
application that allows university students to put up goods for auction
and bid on those goods through auctions.

## Features
The application contains a variety of webpages for different user roles. All webpages
contain a navbar to direct to other webpages for other functions.
It also contains a main python file for functionality and another file
that hashes/un-hashes a user password. 

### Webpages:
1. login: login page for all users. validates credentials against database.
2. bidder_homepage: homepage for bidders which produces user info and participating auctions.
3. seller_homepage: homepage for sellers which produces seller info and participating auctions.
4. helpdesk_homepage: homepage for helpdesk
5. category: displays auction listings for a certain category, or all listings
6. auction_form: page for a Seller to create an auction, which will be inserted into the Listings database.
7. edit_auction: page for a Seller to edit one of their auctions. The auction will be updated in the database.
8. credit_cards: page for a user to view their credit card information and add another.

### Other:

1. app.py: utilizes Flask framework to provide functionality and direction to the application.
2. hash_passwords: hashes an input password using SHA-256
3. users.sql: some SQL commands to create database tables.
4. users.db: database that contains all schema for application




## Organization
1. All webpages (.html files) are stored in templates subfolder within the project folder.
2. The main stylesheet (style.css) and sample company logo are stored in the static subfolder within the project folder.
3. Python files (.py) are stored in the main project folder.
4. Data (.csv files) are located in the LionAuctionDataset-v5 subfolder.

## Instructions
I used Python 3.11.1, and imported Flask and SQLite libraries for the main python file, 
and csv and hashlib libraries into the hash_passwords file. 
To run: use an IDE such as PyCharm or Visual Studio Code, open the Python file and run it from the IDE.
Run app.py once inside the project folder.


## Sources
[https://www.w3schools.com/bootstrap/bootstrap_ref_css_tables.asp](https://www.w3schools.com/bootstrap/bootstrap_ref_css_tables.asp)

[https://mdbootstrap.com/docs/standard/extended/mega-menu/#](https://mdbootstrap.com/docs/standard/extended/mega-menu/#)

[https://jinja.palletsprojects.com/en/3.1.x/templates/#length](https://jinja.palletsprojects.com/en/3.1.x/templates/#length)