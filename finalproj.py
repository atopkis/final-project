import json
import requests
from bs4 import BeautifulSoup
from secrets import *
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go



MOVIEWEB_FNAME = 'movieweb.json'

OMDB_FNAME='omdb.json'

DBNAME= 'movies.db'




try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
except:
    print('Error fetching the database')

drop_statement = '''
    DROP TABLE IF EXISTS 'MovieData';
'''

drop_statement_2 = '''
        DROP TABLE IF EXISTS 'MovieGenre';
'''
cur.execute(drop_statement)
cur.execute(drop_statement_2)

movie_data_table = '''
    CREATE TABLE 'MovieData' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'MovieTitle' TEXT,
        'GenreId' TEXT,
        'RottenTomatoesRating' REAL,
        'MetacriticScore' TEXT,
        'IMDScore' TEXT,
        'BoxOffice' INTEGER,
        'LeadingActor' TEXT,
        'SupportingActor' TEXT,
        'RunTime' INTEGER NOT NULL,
        'ReleasedDate' TEXT
        );
        '''
cur.execute(movie_data_table)
conn.commit()

movie_genre_table = '''
    CREATE TABLE 'MovieGenre' (
        'GenreId' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Genre' TEXT
        );
        '''

cur.execute(movie_genre_table)
conn.commit()


try:
    cache_file = open(OMDB_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_OMDB = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_OMDB= {}

try:
    cache_file = open(MOVIEWEB_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_MOVIEWEB_DICT = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_MOVIEWEB_DICT= {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def omdb_cache_request(baseurl, params=None):
    unique_ident = params_unique_combination(baseurl, params)
    if unique_ident in CACHE_OMDB:
        return CACHE_OMDB[unique_ident]

    else:
        resp = requests.get(baseurl, params)
        CACHE_OMDB[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_OMDB)
        f_ref = open(OMDB_FNAME,"w")
        f_ref.write(dumped_json_cache)
        f_ref.close() # Close the open file
        return CACHE_OMDB[unique_ident]


def movieweb_cache(url):
    if url in CACHE_MOVIEWEB_DICT:
        return CACHE_MOVIEWEB_DICT[url]
    else:
        resp=requests.get(url)
        CACHE_MOVIEWEB_DICT[url] = resp.text
        f_ref=open('movieweb.json', 'w')
        dumped_data=json.dumps(CACHE_MOVIEWEB_DICT)
        f_ref.write(dumped_data)
        f_ref.close()
        return CACHE_MOVIEWEB_DICT[url]


class GenreCreator:
    def __init__(self, genre):
        self.genre=genre

    def __str__(self):
        return self.genre


#Input: User types in a movie title
#Output: Object is made with movie titles and
def getmovieweb_page(year):
    pagination_list=[]
    baseurl='https://movieweb.com/movies/'
    baseurl= baseurl + str(year)
    page_text = movieweb_cache(baseurl)
    page_soup=BeautifulSoup(page_text, 'html.parser')


    pagination=page_soup.find(class_="pagination-items")
    for c in pagination:
        pagination_list.append(c)

    next_page=pagination_list[1]
    str_next_page=str((next_page.find('a')['href']))
    following_page=int(str_next_page.split('=')[-1])

    final_page=pagination_list[-1]
    str_final_page=str((final_page.find('a')['href']))
    last_page=int(str_final_page.split('=')[-1])

    full_year_movie_lst=[]
    for i in range(last_page + 1):
        if i >=1:
            details_url= baseurl +'/?page=' + str(i)
            c=get_movie_titles(details_url)
            for lst in c:
                full_year_movie_lst.append(lst)
    return full_year_movie_lst


def get_movie_titles(details_url):
    lst=[]
    page_text=movieweb_cache(details_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    movies_list = page_soup.find(class_="new-movies-items")
    movies_info= movies_list.find_all('section')
    for c in movies_info:
        movies_descrip = c.find(class_='movie-description')
        not_movies_title = movies_descrip.find('h2')
        movies_title= not_movies_title.text.strip()
        lst.append(movies_title)
    return lst

def genre_lst():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    genre_lst=[]
    baseurl='https://movieweb.com/movies/'
    page_text = movieweb_cache(baseurl)
    page_soup=BeautifulSoup(page_text, 'html.parser')
    genre_area=page_soup.find(class_='jump')
    for c in genre_area:
        genre=c.text.strip()
        b=GenreCreator(genre)
        genre=b.__str__()
        if genre not in genre_lst:
            genre_lst.append(genre)
    insert_movie_genre(genre_lst)

    id_dict={}
    query='SELECT * FROM MovieGenre'
    cur.execute(query)
    for genre in cur:
        Id=genre[0]
        gen=genre[1]
        id_dict[gen]=Id
    return id_dict
    conn.close()

def omdb_request(year):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    b=genre_lst()

    c=getmovieweb_page(year)
    baseurl= 'http://www.omdbapi.com/'
    for x in c:
        try:
            response = omdb_cache_request(baseurl, params={'apikey':api_key, 't':x})
        except:
            pass
        if 'Error' not in response:
            movie_title=response['Title']
            if response['Genre'] != 'N/A':
                genre=response['Genre'].split(',')[0]
            if genre in b:
                genre=b[genre]
            if 'BoxOffice' in response:
                if response['BoxOffice'] != 'N/A':
                    box_office=response['BoxOffice'][1:].split(',')
                    box_office=float(''.join(box_office))
                else:
                    box_office='N/A'
            if 'Ratings' in response:
               c=response['Ratings']
               for x in c:
                   if 'Rotten Tomatoes' in x['Source']:
                       rotten_score=int(x['Value'][:-1])

            if 'imdbRating' in response:
                if response['imdbRating'] != 'N/A':
                    IMD_score = float(response['imdbRating']) * 10
                else:
                    IMD_score = response['imdbRating']
            if 'Metascore' in response:
                if response['Metascore'] != 'N/A':
                    metacritic_score = int(response['Metascore'])
                else:
                    metacritic_score = response['Metascore']
            if response['Runtime'] != 'N/A':
                run_time=int(response['Runtime'].split()[0])
            elif response['Runtime'] == 'N/A':
                pass
            if response['Released'] != 'N/A':
                released_date=response['Released'][0:6]
            elif response['Released'] == 'N/A':
                pass
            if response['Actors'] != 'N/A':
                leading_role=response['Actors'].split(',')[0]
                try:
                    supporting_role=response['Actors'].split(',')[1]
                except:
                    pass
            elif response['Actors'] == 'N/A':
                pass

            insert_movie_data(movie_title, genre, rotten_score, metacritic_score, IMD_score, box_office,
            leading_role, supporting_role, run_time, released_date)
            update_tables()
    conn.close()

def insert_movie_genre(genre_lst):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    s='SELECT COUNT(*) FROM MovieGenre'
    cur.execute(s)

    for x in genre_lst:
        insertion=(None, x)
        statement= 'INSERT INTO "MovieGenre" '
        statement+='VALUES (?, ?)'
        cur.execute(statement, insertion)
        conn.commit()

    conn.close()

def insert_movie_data(movie_title, genre, rotten_score, metacritic_score, IMD_score, box_office,
leading_role, supporting_role, run_time, released_date):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()


    if movie_title not in DBNAME:
        insertion=(None, movie_title, genre, rotten_score, metacritic_score, IMD_score, box_office,
        leading_role, supporting_role, run_time, released_date)
        statement= 'INSERT INTO "MovieData" '
        statement+='VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
    conn.commit()

    conn.close()




def update_tables():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement='UPDATE MovieData '
    statement+='SET RottenTomatoesRating=NULL '
    statement+='WHERE RottenTomatoesRating="N/A"'
    cur.execute(statement)

    statement='UPDATE MovieData '
    statement+='SET MetacriticScore=NULL '
    statement+='WHERE MetacriticScore="N/A"'
    cur.execute(statement)

    statement='UPDATE MovieData '
    statement+='SET IMDScore=NULL '
    statement+='WHERE IMDScore="N/A"'
    cur.execute(statement)

    statement='UPDATE MovieData '
    statement+='SET BoxOffice=NULL '
    statement+='WHERE BoxOffice="N/A"'
    cur.execute(statement)
    conn.commit()
    conn.close()

def something(user_inp):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    if user_inp == 'Box Office Comparison':
        money_dict={}
        statement='''
        SELECT MovieTitle, BoxOffice
        FROM MovieData
        WHERE BoxOffice NOT NULL
        ORDER BY BoxOffice DESC
        LIMIT 15
        '''
        cur.execute(statement)
        b=cur.fetchall()
        for x in b:
            movie=x[0]
            money='$' + str(x[1])
            money_dict[movie]=money
        movier=list(money_dict.keys())
        keesh=list(money_dict.values())

        barz=go.Bar(
        x=movier,
        y=keesh,
        )
        data=[barz]
        layout = go.Layout(
        title='Bar Chart Comparing Box Office Scores For Top Movies of the Year',
        showlegend=False
        )
        fig = go.Figure(data=data, layout=layout)
        plot_url = py.plot(fig, filename='bar-graph')
        return b

    if user_inp == 'Box Office vs Rating':
        money_lst=[]
        ratings_lst=[]
        titles_lst=[]
        statement='''
        SELECT MovieTitle, BoxOffice, RottenTomatoesRating
        FROM MovieData
        WHERE RottenTomatoesRating AND BoxOffice NOT NULL
        LIMIT 15'''
        cur.execute(statement)
        b=cur.fetchall()
        for x in b:
            title=x[0]
            boxoffice=x[1]
            rottenscore=x[2]
            money_lst.append(boxoffice)
            ratings_lst.append(rottenscore)
            titles_lst.append(title)
        trace=go.Scatter(
        x=money_lst,
        y=ratings_lst,
        mode='markers+text',
        text=titles_lst,
        textposition='bottom'
        )
        data = [trace]
        layout = go.Layout(
        title='Scatter Plot Comparing Movies Box Office and Rotten Tomatoes Rating',
        showlegend=False
        )

        fig = go.Figure(data=data, layout=layout)
        plot_url = py.plot(fig, filename='text-chart-basic')
        return b

    if user_inp == 'Genre Distribution':
        genre_dict={}
        count=0
        statement='''
        SELECT Genre, COUNT(Genre)
        FROM MovieGenre
        JOIN MovieData
        ON MovieData.GenreId=MovieGenre.GenreId
        GROUP BY MovieGenre.Genre
        '''
        cur.execute(statement)
        b=cur.fetchall()
        for tup in b:
            genre=tup[0]
            genre_count=tup[1]
            if genre_count > 20:
                genre_dict[genre]=genre_count
            if genre_count <=20:
                count+=genre_count

        genre_dict['Other']=count
        genre=list(genre_dict.keys())
        genre_count=list(genre_dict.values())
        trace=go.Pie(labels=genre, values=genre_count)
        data=[trace]
        layout=go.Layout(
        title='Pie Chart of Distribution of Movie Genres From the Year',
        showlegend=False
        )
        fig=go.Figure(data=data, layout=layout)
        plot_url=py.plot(fig, filename='basic_pie_chart')
        return b

    if user_inp == 'Movie Rating Comparison':
        titles_lst=[]
        statement='''
        SELECT MovieTitle, RottenTomatoesRating, MetacriticScore, IMDScore
        FROM MovieData
        WHERE RottenTomatoesRating AND MetacriticScore AND IMDScore NOT NULL
        '''
        cur.execute(statement)
        b=cur.fetchall()
        for tup in b:
            title=tup[0]
            titles_lst.append(title)
        print(titles_lst)
        return titles_lst





#input is a list of movies for that year
#output is the desired plotly chart
def movie_rating_plotly(user_inp):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement='''
    SELECT MovieTitle, RottenTomatoesRating, MetacriticScore, IMDScore
    FROM MovieData
    WHERE RottenTomatoesRating AND MetacriticScore AND IMDScore NOT NULL AND MovieTitle='{}'
    '''.format(user_inp)

    cur.execute(statement)
    b=cur.fetchall()
    for tup in b:
        title=tup[0]
        rotten_score=tup[1]
        metacritic_score=tup[2]
        IMD_score=tup[3]
    trace=go.Bar(
    x=['Rotten Tomatoes Rating', 'Metacritic Score', 'IMDB Rating'],
    y=[rotten_score, metacritic_score, IMD_score]
    )
    data=[trace]
    layout=go.Layout(
    title='Bar Chart of Different Ratings Received For {}'.format(title),
    showlegend=False
    )
    fig=go.Figure(data=data, layout=layout)
    plot_url=py.plot(fig, filename='basic-bar')
    return b

    conn.close()

instructions=('''

|------------------------------------------------------------------------------|
|    Once your movie data is done loading enter one of the following commands: |
|                                                                              |
|    1. 'Box Office Comparison'                                                |
|                                                                              |
|    2. 'Box Office vs Rating'                                                 |
|                                                                              |
|    3. 'Genre Distribution'                                                   |
|                                                                              |
|    4. 'Movie Rating Comparison'                                              |
|------------------------------------------------------------------------------|
|     More Options:                                                            |
|                                                                              |
|    Enter 'exit' to leave the program                                         |
|                                                                              |
|    Enter 'help' to view the command options                                  |
|------------------------------------------------------------------------------|
''')



def interactive_prompt():
    command_words = ['Box Office Comparison','Box Office vs Rating','Genre Distribution','Movie Rating Comparison']
    user_input=input('Please enter a year or "help": ')
    run_once=0
    while user_input != 'exit':
        try:
            x=int(user_input)
            if x > 1922:
                if x < 2018:
                    print(instructions)
                    if run_once == 0:
                        omdb_request(x)
                        run_once=1
                    user_inp=input('Enter one of the command options: ')
                    if user_inp =='exit':
                        break
                    elif user_inp in command_words:
                        something(user_inp)
                        if user_inp == 'Movie Rating Comparison':
                            title_inp=input('Enter a movie name from the list of the movies: ')
                            movie_rating_plotly(title_inp)
                            continue
                    elif user_inp =='help':
                        continue
                    else:
                        print('Invalid Command')
                        continue

            else:
                user_input=input('Enter a year between 1922 and the current year or "help": ')
                if user_inp =='exit':
                    break

                continue

        except:
            if user_input == "help":
                user_input= input('Enter a year between 1922 and 2018 to view command options or "exit" to leave the program: ')
                continue
            else:
                user_input=input('Invalid Command. Please enter a year or "help": ')
                continue
    print('Goodbye')










if __name__=="__main__":
    interactive_prompt()
    #omdb_request(2015)
    #something('Movie Rating Comparison')
    #movie_rating_plotly('Iris')

    #interactive_prompt()
