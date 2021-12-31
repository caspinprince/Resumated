import os
from flask_dance.contrib.google import make_google_blueprint, google
from app import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.oauth import blueprint

app.register_blueprint(blueprint, url_prefix='/signup_google')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_home')
@login_required
def user_home():
    return render_template('user_home.html')


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
                next = url_for('user_home')

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

if __name__ == '__main__':
    app.run(debug=True)

