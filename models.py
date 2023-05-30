"""SQLAlchemy models for Makeup."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import os


bcrypt = Bcrypt()
db = SQLAlchemy()


class Favorite(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='cascade'),
        unique=True
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    # this allows message table to get information from this review table
    reviews = db.relationship('Review', backref="user",
                              cascade="all,delete-orphan")

    favorites = db.relationship(  # this allows likes to get information from this user table
        'Product',
        secondary='favorites'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Postreview(db.Model):

    __tablename__ = 'post_reviews'

    review_id = db.Column(db.Integer, db.ForeignKey(
        'reviews.id'), primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), primary_key=True)


class Review(db.Model):
    """An individual review ("Makeup")."""

    __tablename__ = 'reviews'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE')
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='cascade')
    )

    products = db.relationship(
        'Review', secondary="post_reviews", backref="reviews")
    # product_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('users.id', ondelete='CASCADE')
    # )

    # this allows user table to get information from this message table


class Product(db.Model):
    """Products in the system."""

    __tablename__ = 'products'

    id = db.Column(
        db.Integer,
        primary_key=True,

    )

    no = db.Column(
        db.Text,
        nullable=True,

    )
    brand = db.Column(
        db.Text,
        nullable=True,

    )

    name = db.Column(
        db.Text,
        nullable=True,

    )

    image_link = db.Column(
        db.Text,
        default="/static/images/makeup-1961208.png",
        nullable=True,

    )

    tag_list = db.Column(
        db.Text,
        nullable=True,

    )

    api_featured_image = db.Column(
        db.Text,
        nullable=True,

    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id', ondelete='cascade')
    )

    tag_id = db.Column(
        db.Integer,
        db.ForeignKey('tags.id', ondelete='cascade')
    )

    reviews = db.relationship('Review', backref="product",
                              cascade="all,delete-orphan")

    # def __init__(self, id, no, brand, name, description):
    #     self.id = id
    #     self.no = no
    #     self.brand = brand
    #     self.name = name
    #     self.description = description


class Category(db.Model):
    """Categories in the system."""

    __tablename__ = 'categories'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    product_type = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    tag_list = db.Column(db.Text,
                         nullable=False,
                         )

    products = db.relationship('Product', backref="tags")


class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    name = db.Column(db.Text,
                     nullable=False,
                     unique=True)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
