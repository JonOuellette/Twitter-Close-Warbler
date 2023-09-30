"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    bio="None",
                                    location="None",
                                    image_url="None",
                                    header_image_url="None")

        self.testuser.id = 12345
        db.session.commit()

        self.testuser_message = Message(
                                        text="Test message.",
                                        user_id=self.testuser.id)
        db.session.add(self.testuser_message)
        db.session.commit()

        """Add message to session"""
        self.MSG = "MSG"


    def test_add_message_authorized(self):
        """Can an authorized user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = client.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(Message.text == "Hello").first()
            self.assertEqual(msg.text, "Hello")
    

    def test_add_message_unauthorized(self):
        """Access should be denied if user is not logged in."""

        with self.client as client:
            resp = client.post("messages/new", data={"text": "Hello"}, follow_redirects=True)

            #Check that status code = 200 to confirm response was received.
            self.assertEqual(resp.status_code, 200)
            #Check that user is not allowed access.
            self.assertIn("Access unauthorized", str(resp.data))


    def test_show_message_authorized_users(self):
        """Show messages from authorized users."""

        #Create a message by testuser.
        msg = Message(
                    id=1234,
                    text="Test message.",
                    user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        #Changing-session trick from above.
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            #Find msg in db.
            msg = Message.query.get(1234)
            res = client.get(f"/messages/{msg.id}")
            #Check that the response was successful
            self.assertEqual(res.status_code, 200)
            #Check that the msg content is in the response data.
            self.assertIn(msg.text, str(res.data))   



    def test_delete_others_message(self):
        """Users cannot delete others' messages."""

        #Create a second user to try to delete testuser's message.
        newUser = User.signup(username="newUser",
                            email="test@newUser.com",
                            password="HASHED_PASSWORD",
                            bio="None",
                            location="None",
                            image_url=None,
                            header_image_url=None)
        newUser.id=6789

        #Create message by testuser
        testuserMsg = Message(
                id="1357",
                text="Test message.",
                user_id=self.testuser.id)
        db.session.add_all([newUser, testuserMsg])
        db.session.commit()

        #newUser is logged in
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2222

            #newUser attempts to delete testuser's message.
            resp = client.post(f"/messages/1357/delete", follow_redirects=True)
            #Check that response was successful
            self.assertEqual(resp.status_code, 200)
            #Check that access was denied
            self.assertIn("Access unauthorized", str(resp.data))