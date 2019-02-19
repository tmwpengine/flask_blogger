from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from flask_app.app import app, db
from flask_app.app.forms import LoginForm, SignUpForm, UpdateUserForm, PostForm
from flask_app.app.models import User, Post


@app.route('/all_posts')
@login_required
def all_posts():
    posts, next_page, prev_page = get_paginator_attributes()

    return render_template('home.html', title='All Posts', posts=posts.items, next_page=next_page, prev_page=prev_page)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('home'))

    posts, next_page, prev_page = get_paginator_attributes()

    return render_template(
        'home.html',
        title='Home',
        form=form,
        posts=posts.items,
        next_page=next_page,
        prev_page=prev_page
    )


@app.route('/user/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)


@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateUserForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()

        flash('Your changes have been saved.')

        return redirect(url_for('update_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio

    return render_template('update_profile.html', title='Update Profile', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignUpForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("You're all signed up")

        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash(f"User {username} was not found")
        return redirect(url_for('home'))

    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('profile', username=username))

    current_user.follow(user)
    db.session.commit()

    flash(f"You are now following {username}!")

    return redirect(url_for('profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash(f"User {username} was not found")
        return redirect(url_for('home'))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('profile', username=username))

    current_user.unfollow(user)
    db.session.commit()

    flash(f"You are no longer following {username}")

    return redirect(url_for('profile', username=username))


def get_paginator_attributes():
    posts = current_user.followed_posts().paginate(
        request.args.get('page', 1, type=int),
        app.config['PAGINATION_LIMIT_PER_PAGE'],
        False
    )

    next_page = url_for('home', page=posts.next_num) if posts.has_next else None
    prev_page = url_for('home', page=posts.prev_num) if posts.has_prev else None

    return posts, next_page, prev_page
