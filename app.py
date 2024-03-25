# Import necessary modules and classes from Flask and models
from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

# Initialize Flask application
app = Flask(__name__)

# Configure the database URI and disable track modifications to suppress warnings
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'

# Enable or disable Debug Toolbar features
toolbar = DebugToolbarExtension(app)

# Connect to the database and create all tables
connect_db(app)
db.create_all()

# Define a route for the homepage
@app.route('/')
def root():
    """Show recent list of posts, most-recent first."""
    # Query the database for the most recent posts and limit to 5
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    # Render the homepage template with the retrieved posts
    return render_template("posts/homepage.html", posts=posts)

# Define an error handler for 404 NOT FOUND errors
@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    # Render the 404 page template with appropriate status code
    return render_template('404.html'), 404

# Define routes for user-related actions

# Route to display all users
@app.route('/users')
def users_index():
    """Show a page with info on all users"""
    # Query the database for all users, ordered by last name then first name
    users = User.query.order_by(User.last_name, User.first_name).all()
    # Render the index template with the retrieved users
    return render_template('users/index.html', users=users)

# Route to display form for creating a new user
@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""
    # Render the new user form template
    return render_template('users/new.html')

# Route to handle form submission for creating a new user
@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for creating a new user"""
    # Create a new User object with data from the form
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)
    # Add the new user to the database session and commit changes
    db.session.add(new_user)
    db.session.commit()
    # Flash a success message
    flash(f"User {new_user.full_name} added.")
    # Redirect to the users index page
    return redirect("/users")

# Route to display information about a specific user
@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""
    # Query the database for the user with the specified ID
    user = User.query.get_or_404(user_id)
    # Render the user profile template with the retrieved user data
    return render_template('users/show.html', user=user)

# Route to display form for editing an existing user
@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""
    # Query the database for the user with the specified ID
    user = User.query.get_or_404(user_id)
    # Render the edit user form template with the retrieved user data
    return render_template('users/edit.html', user=user)

# Route to handle form submission for updating an existing user
@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""
    # Query the database for the user with the specified ID
    user = User.query.get_or_404(user_id)
    # Update user data based on form input
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']
    # Add the updated user to the database session and commit changes
    db.session.add(user)
    db.session.commit()
    # Flash a success message
    flash(f"User {user.full_name} edited.")
    # Redirect to the users index page
    return redirect("/users")

# Route to handle form submission for deleting an existing user
@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""
    # Query the database for the user with the specified ID
    user = User.query.get_or_404(user_id)
    # Delete the user from the database session and commit changes
    db.session.delete(user)
    db.session.commit()
    # Flash a success message
    flash(f"User {user.full_name} deleted.")
    # Redirect to the users index page
    return redirect("/users")



##############################################################################
# Posts route

# Route to display form for creating a new post for a specific user
@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    """Show a form to create a new post for a specific user"""
    # Query the database for the user with the specified ID
    user = User.query.get_or_404(user_id)
    # Retrieve all tags from the database
    tags = Tag.query.all()
    # Render the new post form template with user and tag data
    return render_template('posts/new.html', user=user, tags=tags)

# Route to handle form submission for creating a new post for a specific user
@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new post for a specific user"""
    # Query the database for the user with the specified ID
    user = User.query.get_or_404(user_id)
    # Extract tag IDs from the form data
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    # Query the database for tags with the extracted IDs
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    # Create a new post object with data from the form
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user,
                    tags=tags)
    # Add the new post to the database session and commit changes
    db.session.add(new_post)
    db.session.commit()
    # Flash a success message
    flash(f"Post '{new_post.title}' added.")
    # Redirect to the user's page
    return redirect(f"/users/{user_id}")

# Route to display information about a specific post
@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a page with info on a specific post"""
    # Query the database for the post with the specified ID
    post = Post.query.get_or_404(post_id)
    # Render the post details template with the retrieved post data
    return render_template('posts/show.html', post=post)

# Route to display form for editing an existing post
@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Show a form to edit an existing post"""
    # Query the database for the post with the specified ID
    post = Post.query.get_or_404(post_id)
    # Retrieve all tags from the database
    tags = Tag.query.all()
    # Render the edit post form template with post and tag data
    return render_template('posts/edit.html', post=post, tags=tags)

# Route to handle form submission for updating an existing post
@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handle form submission for updating an existing post"""
    # Query the database for the post with the specified ID
    post = Post.query.get_or_404(post_id)
    # Update post data based on form input
    post.title = request.form['title']
    post.content = request.form['content']
    # Extract tag IDs from the form data
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    # Query the database for tags with the extracted IDs and assign them to the post
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    # Add the updated post to the database session and commit changes
    db.session.add(post)
    db.session.commit()
    # Flash a success message
    flash(f"Post '{post.title}' edited.")
    # Redirect to the user's page
    return redirect(f"/users/{post.user_id}")

# Route to handle form submission for deleting an existing post
@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    """Handle form submission for deleting an existing post"""
    # Query the database for the post with the specified ID
    post = Post.query.get_or_404(post_id)
    # Delete the post from the database session and commit changes
    db.session.delete(post)
    db.session.commit()
    # Flash a success message
    flash(f"Post '{post.title}' deleted.")
    # Redirect to the user's page
    return redirect(f"/users/{post.user_id}")

##############################################################################
# Tags route

# Route to display information about all tags
@app.route('/tags')
def tags_index():
    """Show a page with info on all tags"""
    # Query the database for all tags
    tags = Tag.query.all()
    # Render the index template with the retrieved tags
    return render_template('tags/index.html', tags=tags)

# Route to display form for creating a new tag
@app.route('/tags/new')
def tags_new_form():
    """Show a form to create a new tag"""
    # Query the database for all posts
    posts = Post.query.all()
    # Render the new tag form template with posts
    return render_template('tags/new.html', posts=posts)

# Route to handle form submission for creating a new tag
@app.route("/tags/new", methods=["POST"])
def tags_new():
    """Handle form submission for creating a new tag"""
    # Extract post IDs from the form data
    post_ids = [int(num) for num in request.form.getlist("posts")]
    # Query the database for posts with the extracted IDs
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    # Create a new tag object with data from the form
    new_tag = Tag(name=request.form['name'], posts=posts)
    # Add the new tag to the database session and commit changes
    db.session.add(new_tag)
    db.session.commit()
    # Flash a success message
    flash(f"Tag '{new_tag.name}' added.")
    # Redirect to the tags index page
    return redirect("/tags")

# Route to display information about a specific tag
@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Show a page with info on a specific tag"""
    # Query the database for the tag with the specified ID
    tag = Tag.query.get_or_404(tag_id)
    # Render the tag details template with the retrieved tag data
    return render_template('tags/show.html', tag=tag)

# Route to display form for editing an existing tag
@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """Show a form to edit an existing tag"""
    # Query the database for the tag with the specified ID
    tag = Tag.query.get_or_404(tag_id)
    # Query the database for all posts
    posts = Post.query.all()
    # Render the edit tag form template with tag and post data
    return render_template('tags/edit.html', tag=tag, posts=posts)

# Route to handle form submission for updating an existing tag
@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    """Handle form submission for updating an existing tag"""
    # Query the database for the tag with the specified ID
    tag = Tag.query.get_or_404(tag_id)
    # Update tag data based on form input
    tag.name = request.form['name']
    # Extract post IDs from the form data
    post_ids = [int(num) for num in request.form.getlist("posts")]
    # Query the database for posts with the extracted IDs and assign them to the tag
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()
    # Add the updated tag to the database session and commit changes
    db.session.add(tag)
    db.session.commit()
    # Flash a success message
    flash(f"Tag '{tag.name}' edited.")
    # Redirect to the tags index page
    return redirect("/tags")

# Route to handle form submission for deleting an existing tag
@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    """Handle form submission for deleting an existing tag"""
    # Query the database for the tag with the specified ID
    tag = Tag.query.get_or_404(tag_id)
    # Delete the tag from the database session and commit changes
    db.session.delete(tag)
    db.session.commit()
    # Flash a success message
    flash(f"Tag '{tag.name}' deleted.")
    # Redirect to the tags index page
    return redirect("/tags")
