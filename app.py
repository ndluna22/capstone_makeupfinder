import os
import requests
import json
import urllib3


from flask import Flask, jsonify, Response, render_template, request, flash, redirect, session, g, abort, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import psycopg2


from forms import UserAddForm, LoginForm, ReviewForm, ProfileEditForm, SelectFields
from models import db, connect_db, User, Review, Favorite, Product, Category, Tag, Brand


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

secretskey = os.environ.get('KEY')

API_URL = 'http://makeup-api.herokuapp.com/api/v1/products.json'

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
with app.app_context():
    connect_db(app)


#############################################################
toolbar = DebugToolbarExtension(app)
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    do_logout()
    flash(f"Logged Out!")
    return redirect("/login")


##############################################################################
# General user routes:


@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    reviews = (Review
               .query
               .filter(Review.user_id == user_id)
               .order_by(Review.timestamp.desc())
               .limit(100)
               .all())

    liked_favorites = [product.id for product in g.user.favorites]

    return render_template('users/show.html', user=user,  reviews=reviews, favorites=liked_favorites)


@app.route('/users/<int:user_id>/reviews')
def reviews_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    reviews = (Review
               .query
               .filter(Review.user_id == user_id)
               .order_by(Review.timestamp.desc())
               .limit(100)
               .all())

    return render_template('reviews/show.html', user=user,  reviews=reviews)


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    # IMPLEMENT THIS
    if not g.user:
        flash("Please Register or Login!", "danger")
        return redirect("/")

    user = g.user
    form = ProfileEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            profile.username = form.username.data
            profile.email = form.email.data
            profile.image_url = form.image_url.data
            profile.header_image_url = form.header_image_url.data
            profile.bio = form.email.data

            db.session.commit()

            return redirect(f"/users/{g.user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('/users/edit.html', form=form, user_id=user.id)


@app.route('/users/<int:user_id>/favorites')
def show_favorites(user_id):
    """Show Favorites List."""  # when click on favorites

    if not g.user:
        flash("Please Register or Login!", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    favorites = (Favorite
                 .query
                 .filter(Favorite.user_id == user_id)
                 .limit(100)
                 .all())
    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products.json')
    products_data = res.json()
    # snagging messages in order from the database;
    # user.messages won't be in order by default

    return render_template('users/favorites.html', user=user, favorites=favorites, products_data=products_data)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Please Register or Login!", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Reviews routes:

@app.route('/products/<int:product_id>/reviews/new', methods=["GET", "POST"])
def reviews_add(product_id):
    """Add a review:

    Show form if GET. If valid, update review and redirect to user page.
    """

    if not g.user:
        flash("Please Register or Login!", "danger")
        return redirect("/")

    form = ReviewForm()

    product = Product.query.get_or_404(product_id)

    if form.validate_on_submit():
        new_review = Review(text=request.form['text'],
                            product=product)

        db.session.add(new_review)
        db.session.commit()
        flash(f"Review added!")
        form = ReviewForm()

        return redirect(f"/products/{product_id}")
    else:
        return render_template('reviews/new.html', form=form)


@app.route('/products/<int:product_id>/reviews/<int:review_id>/delete', methods=["POST"])
def reviews_delete(review_id, product_id):
    """Delete a review."""

    if not g.user:
        flash("Please Register or Login!", "danger")
        return redirect("/")

    review = Review.query.get_or_404(review_id)
    if review.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    db.session.delete(review)
    db.session.commit()
    flash(f"Review now deleted!")

    return redirect(f"/products/{product_id}")

##############################################################################
# Products


@app.route('/products', methods=["GET"])
def products_show():

    products = Product.query.all()

    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products.json')
    show_products = res.json()

    return render_template("products/show.html", products=products, show_products=show_products)


@app.route('/products/<int:product_id>', methods=['GET', 'POST'])
def get_product_id(product_id):
    """Show a id product."""

    product = Product.query.get_or_404(product_id)

    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products/{product_id}.json')
    product_unique = res.json()

    reviews = (Review
               .query
               .filter(Review.product_id == product_id)
               .order_by(Review.timestamp.desc())
               .limit(100)
               .all())

    form = ReviewForm()

    if not g.user:
        flash("Please Register or Login!", "danger")
        return redirect("/")

    if form.validate_on_submit():
        new_review = Review(text=request.form['text'],
                            product=product,
                            user_id=g.user.id)

        db.session.add(new_review)
        db.session.commit()
        flash(f"Review added!")
        form = ReviewForm()

        return redirect(f"/products/{product_id}")
    else:

        return render_template('products/index.html', reviews=reviews, product_unique=product_unique, product=product, form=form)


@app.route('/products/<int:product_id>/favorite', methods=['POST'])
def add_favorite(product_id):
    """Toggle a favorite message for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    favorite_product = Product.query.get_or_404(product_id)

    user_favorites = g.user.favorites

    if favorite_product in user_favorites:
        g.user.favorites = [
            favorite for favorite in user_favorites if favorite != favorite_product]
        flash(f"Removed from your favorites!")
    else:
        g.user.favorites.append(favorite_product)
        flash(f"Added to your favorites!")
    db.session.commit()

    return redirect(f"/products/{product_id}")

##############################################################################
# Categories


@app.route('/categories', methods=["GET"])
def all_categories():
    """Show all brands."""
    products = Product.query.all()
    return render_template('categories/show.html', products=products)


@app.route('/categories/<string:name>', methods=["GET"])
def each_category(name):
    """Show each brand name."""
    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products.json?product_type={name}')
    category_data = res.json()

    # if this is keyword is not in api, return "none"

    return render_template('categories/index.html', name=name, category_data=category_data)

##############################################################################
# Brand


@app.route('/brands', methods=["GET"])
def all_brands():
    """Show all brands."""
    products = Product.query.all()

    return render_template('brands/show.html', products=products)


@app.route('/brands/<string:name>', methods=["GET"])
def each_brand(name):
    """Show each brand name."""
    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products.json?brand={name}')
    brand_data = res.json()

    # if this is keyword is not in api, return "none"

    return render_template('brands/index.html', name=name, brand_data=brand_data)

##############################################################################
# Tags


@app.route('/tags', methods=["GET"])
def all_tags():
    """Show tags."""

    products = Product.query.all()

    return render_template('tags/show.html', products=products)


@app.route('/tags/<string:name>', methods=["GET"])
def each_tag(name):
    """Show tags."""
    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products.json?product_tags={name}')
    tag_data = res.json()

    products = Product.query.all()

    return render_template('tags/index.html', name=name, tag_data=tag_data, products=products)


##############################################################################
# Extra

##############################################################################
# Search
@app.route('/results', methods=["GET"])
def search_result():
    """Show results."""
    res = requests.get(
        f'http://makeup-api.herokuapp.com/api/v1/products.json')
    products = res.json()

    # if this is keyword is not in api, return "none"

    return render_template('results.html',  products=products)


##############################################################################
# Homepage and error pages
@app.route('/_autocomplete', methods=['GET'])
def autocomplete():  # can use for autocomplete

    words = ["lipstick", "blush", "pencil", "eyeshadow", "lip liner", "foundation", "eyeliner",
             "bronzer", "eyeliner", "bronzer", "eyebrow", "mascara", "nail polish", "bronzer"]
    return Response(json.dumps(words), mimetype='application/json')


@app.route('/', methods=['GET', 'POST'])
def homepage():
    """Show homepage:

    - anon users: no reviews
    - logged in: 100 most recent reviews
    """

    form = SelectFields()

    if form.validate_on_submit():  # for the main search bar
        name = form.name.data
        return redirect(f'/tags/{name}')

    products = Product.query.all()
    return render_template("home.html", form=form, products=products)

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


@ app.errorhandler(404)
def not_found(e):
    """404 error page"""

    return render_template('404.html'), 404
