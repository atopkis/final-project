# final-project

This program allows users view data in an 
informative way about movies for a year specified by the user. The program works by scraping and crawling through the many pages of movie titles from the from the website https://movieweb.com/movies/ which displays a list of movies for every year. Information about each movie is then accessed through the http://www.omdbapi.com. This information is then put into a database with two tables with the movie Genre acting as the one to many relationship connecting the tables. Lastly, a series of interactive prompts have been formulated that allows users to select which information visualization method they would like to see.

In order to make the data requests from the http://www.omdbapi.com the user must first have an API Key. By going to the site and clicking 'API Key' at the top of the screen, and then typing in your e-mail address a specific API Key will be sent to you. However, since this program requires making so many requests it is recommended to use this specific API Key: 'da18398e'. This API Key has been granted access to making unlimited requests daily. In order to incorporate the API Key into the program it is recommended that you create a 'secrets.py' file which should contain the API Key as a variable. By entering 'from secrets import * ' into the main program file the user will be able to succesfully make requests. 

In order to view the different data visualization methods the user must have a plotly account. To do this go to the site 'https://plot.ly/accounts/login/?action=login' and click sign up and fill in the necessary info. If plotly has not yet been downloaded then in the python shell the user must enter the command 'pip install plotly'.


The code itself is organized into 4 main functions

getmovieweb_page:
This function takes in a year as its input. The year serves as an addition to the baseurl and specifies which years movie titles will be scraped from https://movieweb.com/movies/ . This function returns a list of movies for the specified years

omdb_request:
This function uses the list of movies from the getmovieweb_page function as its input. Then, using the omdbapi, information about each movie is extracted and set to variables. This is done through a for loop that iterates through the each movie title in the list of movies. Each movies various information (genre, actor, runtime, boxoffice, etc;)
is then put into the insert_movie_data function. 

insert_movie_data:
This function takes the various variables that represent different pieces of information for each movie and inserts them into the 'MovieData' table in the data base. 

something:
This function processes the commands entered by the user in the interactive_prompt function. Based on the command that the user enters a plotly graph will be created that presents the data in four unique interesting ways.

User Guide:
In order to run the program simply run the file 'finalproj.py'. Make sure that you have also created the 'secrets.py' file with the API key specified above. Make sure these files are located in the same directory. Next the user will be asked to enter a year or 'help' to view the next options in the command prompt. (The cache file that I submitted only has the data for the years 2005 and 2015. I recommend typing in only these two years or the program will take 30+ minutes to run)

**
 This is the API Key that must be used when running the program because it has been granted'da18398e' unlimited requests
**


