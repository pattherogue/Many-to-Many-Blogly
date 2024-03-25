import datetime
from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy database instance
db = SQLAlchemy()

# Default image URL for users
DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"

# Define the User model
class User(db.Model):
    """Site user."""

    # Set the table name
    __tablename__ = "users"

    # Define columns for the User table
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False, default=DEFAULT_IMAGE_URL)

    # Define relationship with Post table
    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

    # Define a property to get the full name of the user
    @property
    def full_name(self):
        """Return full name of user."""
        return f"{self.first_name} {self.last_name}"

# Define the Post model
class Post(db.Model):
    """Blog post."""

    # Set the table name
    __tablename__ = "posts"

    # Define columns for the Post table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Define a property to get a nicely-formatted date
    @property
    def friendly_date(self):
        """Return nicely-formatted date."""
        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p")

# Define the PostTag model
class PostTag(db.Model):
    """Tag on a post."""

    # Set the table name
    __tablename__ = "posts_tags"

    # Define columns for the PostTag table
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

# Define the Tag model
class Tag(db.Model):
    """Tag that can be added to posts."""

    # Set the table name
    __tablename__ = 'tags'

    # Define columns for the Tag table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    # Define relationship with Post table through PostTag table
    posts = db.relationship(
        'Post',
        secondary="posts_tags",
        backref="tags",
    )

# Function to connect the database to the Flask app
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)
