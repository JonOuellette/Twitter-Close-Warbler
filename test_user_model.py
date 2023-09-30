"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/warbler-test')


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

############### setup and teardown ###############
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        # Create Users
        self.user1 = User.signup(
            username="TestUsername1",
            email="TestEmail1",
            password="TestPassword1",
            bio=None,
            location=None,
            image_url=None,
            header_image_url=None,
        )
        self.user1.id=1111
        
        self.user2 = User.signup(
            username="TestUsername2",
            email="TestEmail2",
            password="TestPassword2",
            bio=None,
            location=None,
            image_url=None,
            header_image_url=None,
        )
        self.user2.id = 2222


    def tearDown(self):
        db.session.rollback()


################ follow tests ###############


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    

    def test_user_follows(self):
        """Check user follow model."""
        #User1 following user2?
        self.user1.following.append(self.user2)
        db.session.commit()

        #Check that user 1 is following 1 user.
        self.assertEqual(len(self.user1.following), 1)
        #Check that user2 is not following anyone
        self.assertEqual(len(self.user2.following), 0)
        #Check that user2 is being followed by 1 follower
        self.assertEqual(len(self.user2.followers), 1)
        #Check that user 1 is not being followed by anyone
        self.assertEqual(len(self.user1.followers), 0)
        #Check that user2 has one follower (user1)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        #Check that user1 is followint 1 user (user2)
        self.assertEqual(self.user1.following[0].id, self.user2.id)


    def test_is_following(self):
        #User 1 is following user2
        self.user1.following.append(self.user2)
        db.session.commit()

        #Check that user1 is following user2
        self.assertTrue(self.user1.is_following(self.user2))
        #Check if user2 is NOT following user1
        self.assertFalse(self.user2.is_following(self.user1))

    
    def test_is_followed_by(self):
        #User2 is followed by user1
        self.user2.followers.append(self.user1)
        db.session.commit
        
        #Check that user 2 is being followed by 
        self.assertTrue(self.user2.is_followed_by(self.user1))
        #Check that user 1 is NOT being followed by user2
        self.assertFalse(self.user1.is_followed_by(self.user2))


############### Signup tests ###############

def test_valid_signup(self):
    # find user in DB
    user_test = User.query.filter_by(username=self.user1.username).first()
    # confirm user is available
    self.assertIsNotNone(user_test)
    # confirm username matches created user
    self.assertEqual(user_test.username, "TestUsername1")
    # confirm email matches created email
    self.assertEqual(user_test.email, "TestEmail1")
    # confirm password is NOT the entered password
    self.assertNotEqual(user_test.password, "sdfwhe")
    # Bcrypt strings should start with $2b$
    self.assertTrue(user_test.password.startswith("$2b$"))

def test_invalid_username_signup(self):
    wrong_username = User.signup("username", None, "sdfsahf", None)
    user_id = 102012
    wrong_username.id = user_id
    with self.assertRaises(IntegrityError):
        db.session.commit()
    

def test_invalid_email_signup(self):
    wrong_email = User.signup("username", None, "password", None)
    user_id = 102012
    wrong_email.id = user_id
    with self.assertRaises(IntegrityError):
        db.session.commit()

def test_invalid_password_signup(self):
    with self.assertRaises(ValueError):
        User.signup("username", "bob@Bob.com", None, None)


############### authentication tests ###############

def test_valid_authentication(self):
    # Find user in db
    user = User.query.get(self.user1.id)
    # Create user with username and password
    authenticated = User.authenticate(self.user1.username, "TestPassword1")
    # Confirm user exists by checking that it is not None.
    self.assertIsNotNone(authenticated)
    # Check if user id created equals original user id
    self.assertEqual(user, authenticated)

def test_invalid_username(self):
    # Check that user is not authenticated with the wrong username entered.
    self.assertFalse(User.authenticate("WrongUsername", "password"))

def test_invalid_password(self):
    # Check that user is not authenticated with the wrong password entered.
    self.assertFalse(User.authenticate(self.user1.username, "WrongPassword"))