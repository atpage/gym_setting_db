import unittest

from gym_setting_db import get_engine, get_session, create_tables, Color


class TestQardioDataset(unittest.TestCase):
    def setUp(self):
        self.engine = get_engine()
        self.session = get_session(engine=self.engine)

    def test_creating_tables(self):
        create_tables()
        #self.assertTrue( ... )
        
    def test_querying_table(self):
        results = self.session.query(Color).all()
        #self.assertTrue( ... )


if __name__ == '__main__':
    unittest.main()
