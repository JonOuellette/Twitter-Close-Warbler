import os
from unittest import TestCase

from models import db, User, Message, Follows

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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.user1 = User.signup(
            username="TestUsername1",
            email="testu1@email.com",
            password="HASHED_PASSWORD",
            bio=None,
            location=None,
            image_url=None,
            header_image_url=None,
        )

        self.user2 = User.signup(
            username="testUsername2",
            email="TestEmail2",
            password="HASHED_PASSWORD",
            bio=None,
            location=None,
            image_url=None,
            header_image_url=None
        )

        db.session.commit()
        self.client = app.test_client()


    def tearDown(self):
        """Clean up after each test"""
        db.session.rollback()
        

    def test_message_model(self):
        """Does basic model work?"""
        # Create new messages for user1 and user2
        
        msg1 = Message(text = "Test message 1.", user_id=self.user1.id)
        msg2 = Message(text = "Test message 2.", user_id=self.user2.id)        
        
        db.session.add_all([msg1, msg2])
        db.session.commit()

        
        #Check that the length of message list for users1 == 1
        self.assertEqual(len(self.user1.messages), 1)
        #Check that there is content in user1 message
        self.assertIn(msg1, self.user1.messages)
        #Check that the text in user1 message is shown
        self.assertEqual(self.user1.messages[0].text, "Test message 1.")
        #Check that the length of message list for user2 == 1
        self.assertEqual(len(self.user2.messages), 1)
        #Check that there is content in user2 message
        self.assertIn(msg2, self.user2.messages)
        #Check that the text in user2 message is shown 
        self.assertEqual(self.user2.messages[0].text, "Test message 2.")


    def test_add_message(self):
        """Check that messages can be added."""

        #Create new messages for both user1 and user2
        msg1 = Message(text = "Test message 1.", user_id=self.user1.id)
        msg2 = Message(text = "Test message 2.", user_id=self.user2.id)        
        db.session.commit()

        #add msg1 and msg2 to message lists
        self.user1.messages.append(msg1)
        self.user2.messages.append(msg2)

        #Check that there is content in msg1 and msg2
        self.assertIn(msg1, self.user1.messages)
        self.assertIn(msg2, self.user2.messages)


    def test_like_message(self):
        """Check that messages can be liked and unliked."""

        #Create new messages for both user1 and user2.
        msg1 = Message(text = "Test message 1.", user_id=self.user1.id)
        msg2 = Message(text = "Test message 2.", user_id=self.user2.id)        
        db.session.commit()

        #Add msg2 to user1's liked messages.
        self.user1.likes.append(msg2)
        #Add msg1 to user2's liked messages.
        self.user2.likes.append(msg1)

        #Check that msg2 is in user1's likes list.
        self.assertIn(msg2, self.user1.likes)
        #Check that msg1 is in user2's likes list.
        self.assertIn(msg1, self.user2.likes)

        #Remove msg2 from user1's likes list.
        self.user1.likes.remove(msg2)  
        #Remove msg1 from user2's likes list.
        self.user2.likes.remove(msg1)

        #Check that msg2 is NOT in user1's likes list.
        self.assertNotIn(msg2, self.user1.likes)
        #Check that msg1 is NOT in user2's likes list.
        self.assertNotIn(msg1, self.user2.likes)


    def test_delete_message(self):
        """Check that messages can be deleted."""

         #Create new messages for both user1 and user2.
        msg1 = Message(text = "Test message 1.", user_id=self.user1.id)
        msg2 = Message(text = "Test message 2.", user_id=self.user2.id)        
        db.session.commit()  

        #Add msg2 to user1's liked messages.
        self.user1.likes.append(msg2)
        #Add msg1 to user2's liked messages.
        self.user2.likes.append(msg1)

        #Check that there is content in msg1 and msg2
        self.assertIn(msg1, self.user1.messages)
        self.assertIn(msg2, self.user2.messages)

        #Remove msg1 from user1's messages list
        self.user1.messages.remove(msg1)
        #Remove msg2 from user2's messages list
        self.user2.messages.remove(msg2)

        #Check that msg1 is NOT in user1's messages list
        self.assertNotIn(msg1, self.user1.messages)
        #Check that msg2 is NOT in user2's messages list
        self.assertNotIn(msg2, self.user2.messages)