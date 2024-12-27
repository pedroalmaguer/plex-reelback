import unittest
from app import app, db, User, SessionHistory, SessionHistoryMetadata

class TestORM(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taut.db'
        self.app = app.test_client()
        db.create_all()

        # Add test data
        user = User(user_id=1, username='test_user')
        db.session.add(user)
        session = SessionHistory(user_id=1, started=1000, stopped=2000, media_type='movie', rating_key='1234')
        db.session.add(session)
        metadata = SessionHistoryMetadata(rating_key='1234', full_title='Test Movie', duration=1200)
        db.session.add(metadata)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_query(self):
        user = User.query.filter_by(user_id=1).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test_user')

    def test_session_query(self):
        sessions = SessionHistory.query.filter_by(user_id=1).all()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].media_type, 'movie')

    def test_join_query(self):
        movies = db.session.query(
            SessionHistoryMetadata.full_title,
            db.func.count(SessionHistory.rating_key)
        ).join(SessionHistory, SessionHistory.rating_key == SessionHistoryMetadata.rating_key)\
        .filter(SessionHistory.user_id == 1)\
        .group_by(SessionHistoryMetadata.full_title)\
        .all()
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0][0], 'Test Movie')

if __name__ == '__main__':
    unittest.main(exit=False)
