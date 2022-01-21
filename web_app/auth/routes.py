from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from web_app.models import User
from web_app import db
from web_app.auth.forms import LoginForm, RegistrationForm
from web_app.auth import bp

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You logged out!")
    return redirect(url_for('general.home'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_check(password=form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Logged in!')

            next = request.args.get('next')

            if next is None or not next[0]=='/':
                next = url_for('general.home')

            return redirect(next)

    return render_template('auth/login.html', form=form)

@bp.route('/signup_google', methods=['GET', 'POST'])
def signup_google():
    return redirect(url_for('google.login'))



@bp.route('/signup', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)