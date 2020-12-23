from flask import Flask, render_template, request, redirect, url_for, session
from Forms import *
from Models import *
import shelve


app = Flask(__name__)
app.config['SECRET_KEY'] = 'tutormeplease' #this is to encrypt data passing along our server, this includes our session data


@app.route("/")
def home():
    return render_template('home.html')
@app.route('/login', methods=['GET', 'POST'])
def Login():
    if session.get('loggedin') == True:
        return redirect(url_for('home'))
    else:
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            print("posting")
            db = shelve.open('databases/user.db', 'r')
            username = request.form['username']
            pw = request.form['password']
            #for loop to check every users in db whether they have the same username and password
            for user in db:
                user = db[user]
                if user.get_username() == username and pbkdf2_sha256.verify(pw, user.get_user_pw()) == True:
                    session['user_id'] = user.get_user_id()
                    session['name'] = user.get_user_fullname()
                    session['profile_pic'] = user.get_user_profile_pic()
                    session['loggedin'] = True
                    db.close()
                    try:
                        if request.form['remember']:
                            session['remember'] = True
                    except:
                        pass
                    #this means that the for loop found a match, and our session data is now in used.
                    return redirect(url_for('home'))
                print("checking")
            #for loops ends and has no match...
            db.close()
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def createUser():
    if session.get('loggedin') == True:
        return redirect(url_for("home"))
    else:
        createUserForm = CreateUserForm(request.form)
        if request.method == 'POST' and createUserForm.validate():
            print("posting")
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            firstname= request.form['first_name']
            lastname= request.form['last_name']

            #Validating form(if similar)
            if username == password:
                similarerror = 'Username and password cannot be the same'
                return render_template('register.html', form=createUserForm, similarerror=similarerror)

            #retrieving user.db
            db = shelve.open('databases/user.db', 'r')
            for user in db:
                user = db[user]
                if user.get_user_email() == email:
                    emailerror = 'This email is in use, please enter another email.'
                    return render_template('register.html', form=createUserForm, emailerror=emailerror)
                if user.get_username() == username:
                    usernameerror = 'This username is in use, please enter another username.'
                    return render_template('register.html', form=createUserForm, usernameerror=usernameerror)
            db.close()

            #posting to user.db
            db = shelve.open('databases/user.db')
            user = User(email,username,password,firstname,lastname) #user object
            db[user.get_user_id()] = user

            #testing code
            print("successfully posted")
            db.close()
            return redirect(url_for("home"))
    return render_template('register.html', form=createUserForm)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if session.get('loggedin') == True:
        session.clear()
        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


if __name__ =='__main__':
    app.run(debug=True)