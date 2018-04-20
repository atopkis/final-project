import unittest
from finalproj import *



omdb_request(2005)


class TestDatabase(unittest.TestCase):

    def test_api_processing(self):
        c=getmovieweb_page(1923)
        baseurl= 'http://www.omdbapi.com/'
        for x in c:
            response = omdb_cache_request(baseurl, params={'apikey':'da18398e', 't':x})
        self.assertEqual(len(response), 25)
        self.assertIn('Director', response)
        self.assertIn('The White Sister', response['Title'])

    def test_genre_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT Genre FROM MovieGenre'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Comedy',), result_list)
        self.assertEqual(len(result_list), 33)

    def test_moviedata_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = 'SELECT MovieTitle, LeadingActor, RunTime FROM MovieData'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn('The Chronicles of Narnia: The Lion, the Witch and the Wardrobe', result_list[0][0])
        self.assertEqual(len(result_list), 908)
        self.assertEqual(143, result_list[0][2])
        self.assertEqual('Georgie Henley', result_list[0][1])


        statement='''
        SELECT MovieTitle, RottenTomatoesRating, RunTime, IMDScore
        FROM MovieData
        WHERE RottenTomatoesRating AND RunTime AND IMDScore NOT NULL
        '''
        cur.execute(statement)
        b=cur.fetchall()
        self.assertEqual(len(b), 869)
        self.assertEqual(type(b[0][2]), type(124))
        self.assertIn(('Pride & Prejudice', 85.0, 129, '78.0'), b)
        self.assertEqual('69.0', b[0][3])

    def test_join(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement='''
        SELECT Genre, COUNT(Genre)
        FROM MovieGenre
        JOIN MovieData
        ON MovieData.GenreId=MovieGenre.GenreId
        GROUP BY MovieGenre.Genre
        '''
        results=cur.execute(statement)
        result_list=results.fetchall()
        self.assertEqual(len(result_list), 18)
        self.assertNotIn('MusicVideo', result_list)







unittest.main(verbosity=2)
