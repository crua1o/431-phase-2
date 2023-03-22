Colin Rualo CMPSC431W 002

# 431 Phase 2 Progress Report
## Context
This application is for the fictional LionAuction, where a User can log in to the site. This project specifically
 focuses on the user login form and authentication, utilizing python, Flask, and HTML/CSS.

## Features
There are eight files that make up the website design:
1. app.py: provides functionality to the website using Flask. This includes page redirection, form submission, and database queries.
Incorporated is SQLite, which was used to set up the database. Important functions:
  a. validate(): validates a user's input to the Users database and returns True if the information is found.
  b. login(): addresses user input via validate(), and returns the appropriate webpage accordingly.
  c. index(): route for the login page.
  d. homepage(): route for homepage if user authentication is successful.


2. homepage.html: html file to create the homepage once the user is logged in.
3. style.css: custom css file to enhance login visuals.
4. login.html: html file to create login page. If the User enters valid credentials they'll be redirected to homepage.

## Organization
app.py is organized by route:
  a. login(): addresses user input via validate(), and returns the appropriate webpage accordingly.
  b. index(): route for the login page.
  c. homepage(): route for homepage if user authentication is successful.

## Instructions
style.css should be placed in the static folder of the Pycharm project.
login.html and homepage.html should be placed in the templates folder of the Pycharm project.
app.py should be placed in the Pycharm project.
To run: run app.py in the Pycharm project. Click on the specified port in the Run environment to open webpage.
