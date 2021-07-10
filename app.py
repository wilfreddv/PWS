from flask import Flask, request, redirect, url_for, session, flash, jsonify
from flask import render_template as rt

import re

from datetime import timedelta

from scripts.db_reservations import Reservations
from scripts.db_users import User

from scripts import util, config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY


#Error handlers
@app.errorhandler(404)
def page_not_found(*args):
    return rt("404.html")


#Main pages
@app.route('/')
def login():
    if session:
        return redirect(url_for('main'))

    return rt('login.html')


@app.route('/main/', methods=["POST","GET"])
def main():
    if session:
        reservations = Reservations('databases/reservations.db')
        schedule = reservations.fetchall()
        reservations.close()
        username = session['username']
        admin = session['admin']
        return rt('main.html', schedule=schedule, username=username, admin=admin)
    else:
        return redirect(url_for('login'))


@app.route('/admin/')
def admin():
    if session and session['admin'] == 1:
        user = User()
        users = user.list_all()
        users = sorted(users)
        return rt('admin.html', username=session['username'], users=users)
    else:
        return redirect(url_for('main'))

#Redirects
@app.route('/_form_redirect', methods=["POST"])
def form_redirect():
    if session:
        form = request.form

        if form:
            form = util.restructure_form(form)
            reservations = Reservations('databases/reservations.db')

            err = reservations.update(form)
            if err:
                open('errors.log','a').write("\n"+err)
                flash("Er is een fout opgetreden. Probeer het opnieuw of neem contact op met de beheerder.")

    return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


#AJAX
@app.route('/login')
def login_redirect():
    session.clear()
    username = request.args.get('username', 0, type=str)
    password = request.args.get('password', 0, type=str)

    if password == "" or username == "":
        return jsonify(result="Voer een gebruikersnaam en wachtwoord in...")
    #Make sure nobody's been tinkering with the POST after login.html
    if not re.fullmatch(r'[A-Z]{3}', username):
        return jsonify(result='Gebruikersnaam of wachtwoord is onjuist.')
    else:
        try:
            user = User()
            #user.validate() will assert to False if passwords do not match
            #or when username does not exist
            isAdmin = user.validate(username, password)
        except AssertionError:
            return jsonify(result="Gebruikersnaam of wachtwoord is onjuist.")

    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

    session['username'] = username
    session['admin'] = isAdmin
    return jsonify(success=1)


@app.route('/add_user')
def add_user():
    if session and session['admin']:
        try:
            username = request.args.get('username', 0, type=str)
            password = request.args.get('password', 0, type=str)
            ctrlPassword = request.args.get('ctrlPassword', 0, type=str)
            isAdmin = request.args.get('isAdmin', 0, type=str)

            if not re.fullmatch(r'[A-Z]{3}',username):
                return jsonify(result='Gebruikersnaam moet uit 3 hoofletters bestaan')

            if password == '':
                return jsonify(result='Voer een wachtwoord in')

            if password != ctrlPassword:
                return jsonify(result='Wachtwoorden komen niet overeen')

            user = User()
            try:
                err = user.new(username, password, isAdmin)
            except AssertionError:
                return jsonify(result='Gebruikersnaam bestaat al!')
            if err:
                return jsonify(result="Er is iets fout gegaan... Probeer opnieuw of neem contact op met de beheerder")


            return jsonify(result='Gebruiker "{}" succesvol aangemaakt!'.format(username), success=1)
        except Exception as e:
            return str(e)

    else:
        return rt("404.html")


@app.route('/remove_user')
def remove_user():
    if session and session['admin']:
        username = request.args.get('username', 0, type=str)

        user = User()
        err = user.remove(username)
        if err:
            return jsonify(result="Er is iets fout gegaan... Probeer opnieuw of neem contact op met de beheerder")

        return jsonify(result="Gebruiker '{}' succesvol verwijderd!".format(username), success=1)
    else:
        return rt("404.html")

if __name__ == '__main__':
    app.run(debug=True)
