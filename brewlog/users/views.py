from flask import render_template, redirect

from brewlog import app

@app.route('/auth/select', endpoint='auth-select-provider')
def select_provider():
    return render_template('auth/select.html')

@app.route('/auth/logout', endpoint='auth-logout')
def logout():
    return redirect('/')

@app.route('/profile', endpoint='profile')
def profile():
    return render_template('account/profile.html')
