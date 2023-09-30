"""User View tests"""

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/warbler-test')

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

#Stops from using CSRF while testing
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for user-related routes."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

         #  TODO: helper function that calls user.signup
        u1 = User.signup("test1", "email1@email.com", "password", None)
        u2 = User.signup("test2", "email2@email.com", "password", None)

        db.session.commit()

        self.u1 = User.query.filter_by(username="test1").first()
        self.u2 = User.query.filter_by(username="test2").first()

        self.client = app.test_client()


    def tearDown(self):
        """ Clean up fouled transactions """

        db.session.rollback()

    def test_user_profile(self):
        """Test viewing user profile page."""
        with self.client as c:
            resp = c.get(f"/users/{self.u1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@test1', html)

    def test_user_profile_edit(self):
        """Test editing user profile page."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.get(f"/users/{self.u1.id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Your Profile.', html)

    def test_user_followers(self):
        """Test viewing user followers page."""
        with self.client as c:
            resp = c.get(f"/users/{self.u1.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Followers', html)

    def test_user_following(self):
        """Test viewing user following page."""
        with self.client as c:
            resp = c.get(f"/users/{self.u1.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Following', html)

    def test_user_likes(self):
        """Test viewing user likes page."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.get(f"/users/{self.u1.id}/likes")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Likes', html)

    def test_add_message(self):
        """Test adding a message."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        """Test deleting a message."""
        m = Message(text="Test Message", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.post(f"/messages/{m.id}/delete")

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.get(m.id)
            self.assertIsNone(msg)
    
    def test_unauthenticated_add_message(self):
        """Test adding a message while unauthenticated."""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(Message.query.all()), 0)

    def test_unauthenticated_delete_message(self):
        """Test deleting a message while unauthenticated."""
        m = Message(text="Test Message", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/messages/{m.id}/delete")

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.get(m.id)
            self.assertIsNotNone(msg)

    def test_add_message_as_another_user(self):
        """Test adding a message as another user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.post(f"/users/{self.u2.id}/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 403)
            self.assertEqual(len(Message.query.all()), 0)

    def test_delete_message_as_another_user(self):
        """Test deleting a message as another user."""
        m = Message(text="Test Message", user_id=self.u2.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.post(f"/messages/{m.id}/delete")

            self.assertEqual(resp.status_code, 403)

            msg = Message.query.get(m.id)
            self.assertIsNotNone(msg)