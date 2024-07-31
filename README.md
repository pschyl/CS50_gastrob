## gastrob

### Video Demo: https://youtu.be/3ClTmW-abpA

### Description: gastrob allows users to rate their job in the catering industry and look up existing ratings for specific employers they are intrested in. So the idea is to provide a transparent statistic insight for various restraurants and bars from an emloyees perspective. Users must be logged in to submit a rating, so they need to create an account and add a job to it. A login is not required for users who just want to lookup ratings for a specific restaurant. The website has an simple and minimalist design. The technologies used in the project are Flask as the framework, Python in the app.py, CSS and HTML for the templates and SQL to collect the data in a database and provide it to the user.

### Files:

#### static
js/script.js: Is used to create the pie charts for all the data the website displays for the user. it's needed for the templates browse.html, stats.html, stats_employer.html and stats_jobs.html. The file also contains a function which is used to display certain hidden html content on click.

gastro8.jpg: An image which is the center of the design of the website, it shows different areas of an restaurant and the people working there in a very simplified way and is displayed on every template.

styles.css: this file contains all the css for all templates. With hindsight, it's a poor design choice, in future projects, there will be a seperate css file for each template. 

#### templates
layout.html: layout blueprint for all templates. It contains the links for login and register if the user is logged out, the links to logout and the users profile if the user is logged in, the title picture gastro8.jpg and the navbar. It also contains a footer for design purporses but the links in it are empty.

index.html: simply the homepage which greets the visitor.

register.html: contains a html form for the user to create an account and a fast link to the login page if an account already exists.

login.html: html form for the user to login.

profil.html: contains information about the users account. They can update certain details about themselves, like gender and birthday, and see a cv of themselves with all jobs their added to their profile so far. 

profil_addjob.html: form for the user to add a job to their profile out of a list from possible employers.

addemployer.html: form for the user to add a employer to the database.

profil_history.html: table which displays all the ratings, the user has done so far.

rate.html: part of the website where it gets its most data from. The user rates a job they added to the profile in different categories such as worked overhours, tip earned and atmosphere, guests, management,etc. with a 5-star-system. Users can rate an active job (no ending date) once each month, so a trend in the restaurants performance is considered, and an inactive job only once overall in retrospect.

browse.html: the user can browse for an specific restaurant and check the provided data, if available. The data is based on all the ratings that have been submitted for this restaurant so far and includes averages, pie charts, basic information, statistics about the users who submitted the reviews.

stats.html: more general statistics about the registrated users, such as total amount, the ratio of gender amongst them, the average age and a pie chart for the age distribution.

stats_employer.html: more statstics about the employer in the database, in this case the total amount of registrated user, and the ratio of gastronomy types amongst the employer.

stats_jobs.html: more statistics about the jobs added to the database with pie charts for the ratio of different positions and employment types. 


#### .gitignore: file that contains the name of all files, that won't be pushed to GitHub.

#### app.py: 
the brain of the website. Contains the basic setup for flask, sqlite3 and session; controls the routes and the logic for all templates including different request types and the communication with the database. I decided to use the basic sqlite3 library and not the one form CS50. Creates the variables as return value for the templates which are displayed to the user

