import os
from flask_dance.contrib.google import make_google_blueprint, google
from web_app import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from web_app.models import User
from web_app.forms import LoginForm, RegistrationForm, EditProfileForm
from web_app.oauth import blueprint
from datetime import datetime, timedelta
from utilities import time_diff
app.register_blueprint(blueprint, url_prefix='/signup_google')

@app.route('/')
def home():
    if current_user.is_authenticated:
        users = User.query.all()
        return render_template('user_home.html', users=users)
    else:
        return render_template('home.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You logged out!")
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.password_check(form.password.data) and user is not None:
            login_user(user, remember=form.remember_me.data)
            flash('Logged in!')

            next = request.args.get('next')

            if next is None or not next[0]=='/':
                next = url_for('home')

            return redirect(next)

    return render_template('login.html', form=form)

@app.route('/signup_google', methods=['GET', 'POST'])
def signup_google():
    return redirect(url_for('google.login'))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for signing up!")
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = EditProfileForm(request.form)
    user = User.query.filter_by(username=username).first_or_404()
    last_seen = time_diff(user.last_online)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.headline = form.headline.data
        user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('user', username=user.username))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.username.data = user.username
        form.headline.data = user.headline
        form.about_me.data = user.about_me
    return render_template('user.html', user=user, form=form, last_seen=last_seen)

@app.route('/explore')
@login_required
def explore():
    return render_template('home.html')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        user.last_online = datetime.utcnow()
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)

