from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "$ecr3d_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
toolbar = DebugToolbarExtension


@app.route('/')
def home_page():
    """If logged in show user's home page, if not show registration page"""
    if session["user_id"]:
        user = User.query.get(session["user_id"])
        return redirect(f'/users/{user.username}')

    else:
        return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def registration():
    """shows registration form and handle it"""

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(
            username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id

        return redirect("/users/{new_user.username}")

    else:
        return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Shows login form and handle login"""

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        password = form.password.data

        user = User.authenticate(name, password)

        if user:
            session["user_id"] = user.id
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Incorrect user/password"]

    return render_template("login.html", form=form)


@app.route("/users/<username>", methods=["GET"])
def secret(username):
    """Shows page of the logged in users, return error if not logged in"""
    user = User.query.filter_by(username=username).first()

    if "user_id" not in session:
        flash("You must be logged in!")
        return redirect("/login")

    if user:
        if session["user_id"] == user.id:
            return render_template("secret.html", user=user)
        else:
            flash("You don't have permission to do that!")
            return redirect('/')


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("user_id")

    return redirect("/")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Handle user deletion"""

    user = User.query.filter_by(username=username).first()

    if user:
        if session["user_id"] == user.id:
            db.session.delete(user)
            db.session.commit()
            session.pop("user_id")
            flash("User Deleted")
            return redirect("/")
        else:
            flash("You don't have permission to do that!")
            return redirect('/login')

    else:
        flash("Invalid Request")
        return redirect('/')


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def feedback(username):
    """Show form to add feedback and handle submission"""
    user = User.query.filter_by(username=username).first()
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = user.username
        new_feed = Feedback(title=title, content=content, username=username)
        db.session.add(new_feed)
        db.session.commit()
        return redirect('/')

    elif user:
        if session["user_id"] == user.id:
            return render_template('/add_feed.html', form=form, user=user)
        else:
            flash("You don't have permission to do that!")
            return redirect('/')

    else:
        flash("Invalid Request")
        return redirect('/')


@app.route("/feedback/<int:feedback_id>/update", methods=["GET"])
def feedback_edit(feedback_id):
    """Validate and show feedback edit form"""
    feedback = Feedback.query.get_or_404(feedback_id)

    if session["user_id"] == feedback.user.id:
        form = FeedbackForm()
    return render_template('/edit_feed.html', form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/update", methods=["POST"])
def handle_feed_edit(feedback_id):
    """Handle editing a feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm()

    if form.validate_on_submit():
        if feedback and session["user_id"] == feedback.user.id:
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            return redirect("/")
        else:
            flash("You don't have permission to do that!")
            return redirect('/')


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def handle_delete_feed(feedback_id):
    """Handle deleting a feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm()

    if feedback and session["user_id"] == feedback.user.id:
        db.session.delete(feedback)
        db.session.commit()
        return redirect("/")
    else:
        flash("You don't have permission to do that!")
        return redirect('/')
