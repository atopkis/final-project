import unittest
from finalproj import *

omdb_request(2005)

class TestDatabase(unittest.TestCase):
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



unittest.main()
