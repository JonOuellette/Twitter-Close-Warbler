"""User View tests"""

import os
from unittest import TestCase

from models import db, Message, User, Likes, Follows

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

class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        # Create test users
        self.user1 = User.signup(
            username="TestUsername1",
            email="TestEmail1",
            password="TestPassword1",
            bio="None",
            location="None",
            image_url=None,
            header_image_url=None            
        )
        self.user1_id = 1111
        self.user1.id = self.user1_id

        self.user2 = User.signup(
            email="TestEmail2",
            username="TestUsername2",
            password="TestPassword2",
            bio="None",
            location="None",
            image_url=None,
            header_image_url=None    
        )
        self.user2_id = 2222
        self.user2.id = self.user2_id

        self.user3 = User.signup(
            
            username="TestUsername3",
            email="TestEmail3",
            password="TestPassword3",
            bio="None",
            location="None",
            image_url=None,
            header_image_url=None
            )
        self.user3_id = 3333
        self.user3.id = self.user3_id

        db.session.commit()

        # Setup followers
        follower1 = self.user1.following.append(self.user2)
        follower2 = self.user2.following.append(self.user1)
        follower3 = self.user3.following.append(self.user1)

        db.session.commit()

        # Setup test message
        self.msg = Message(id=0000, text='Test Message', user_id=self.user2.id)
        db.session.add(self.msg)
        db.session.commit()

        self.MSG = "MSG"

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_signup(self):
        """Test Sign Up root route"""
        with self.client as client:
            #Get the homepage
            res = client.get('/')
            html = res.get_data(as_text=True)
            #Check that the request was successful
            self.assertEqual(res.status_code, 200)
            #Check that the homepage was rendered
            self.assertIn("<h1>What's Happening?</h1>", html)
            self.assertIn("<h4>New to Warbler?</h4>", html)


    def test_login(self):
        """Check login route"""
        with self.client as client:
            #Get login page
            res = client.get('/login')
            html = res.get_data(as_text=True)
            #Check that the response was successful
            self.assertEqual(res.status_code, 200)
            #Check that the user was taken to the login form
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)


    def test_logout(self):
        """Check logout route"""
        #Begin session with user1
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            #Logout user 1
            res = client.get("/logout")
            #Check that the response was successful
            self.assertEqual(res.status_code, 302)
            #Check that the user is taken back to the login page
            self.assertEqual(res.location, 'http://localhost/login')


    def test_show_users(self):
        """Check show users route"""
        with self.client as client:
            #Get list of all users
            res = client.get("/users")
            #Check that user1 is among the response data
            self.assertIn("@TestUsername1", str(res.data))
            #Check that user2 is among the response data
            self.assertIn("@TestUsername2", str(res.data))

    def test_show_user_detail(self):
        """Check user detail route"""
        with self.client as client:
            #Get user1's details page
            res = client.get(f"/users/{self.user1_id}")
            html = res.get_data(as_text=True)
            #Check that the response was successful
            self.assertEqual(res.status_code, 200)
            #Check that the response data is present in user1's details
            self.assertIn("@TestUsername1", str(res.data))

    def test_show_user_following(self):
        """Check user following route"""
        # user in session
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            #Get user1's list of followers
            res = client.get(f"/users/{self.user1_id}/followers")
            #Check taht response was successful
            self.assertEqual(res.status_code, 200)
            #Check that the response data is present in user1's following list
            self.assertIn("@TestUsername1", str(res.data))


    def test_show_user_followers(self):
        """Check user followers route"""
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            #Get user1's followers
            res = client.get(f'users/{self.user1_id}/followers')

            #Check that response was successful
            self.assertEqual(res.status_code, 200)
            #Check that the response data is present in user1's followers list
            self.assertIn("@TestUsername1", str(res.data))


    def test_show_follow_user(self):
        """Check route when you follow a user"""

        #Start a session with user 1
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            res = client.post(f'users/follow/{self.user1.id}')

            # Check that response was successful
            self.assertEqual(res.status_code, 302)
            #Check that the follow was added to user1's list of followers
            self.assertEqual(res.location, f'http://localhost/users/{self.user1_id}/following')

            
    def test_show_add_like(self):
        """Show route when message is likes"""
        
        #Start a session with user1
        with self.client as client:
            id = self.msg.id
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            #User navigates to url to toggle "like" on
            res = client.post("/messages/0000/like", follow_redirects=True)
            #Check that the response was successful, and "like" was toggled off
            self.assertEqual(res.status_code, 200)

    def test_show_unlike(self):
        """Show route when message is unliked"""
        # Get message from DB
        msg = Message.query.filter(Message.text=="Test Message").one()
        
        #Check that message is in db
        self.assertIsNotNone(msg)
        #Check that user is not the creator of the message
        self.assertNotEqual(msg.user_id, self.user1_id)

        #Start a session with user1
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1_id
            
            #User navigates to URL to toggle "like" off
            resp = client.post(f"/messages/{msg.id}/like", follow_redirects=True)
            #Check that the response was successful, and "like" was toggled off
            self.assertEqual(resp.status_code, 200)