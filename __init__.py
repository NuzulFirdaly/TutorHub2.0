from flask import Flask, render_template, request, redirect, url_for, session
from Forms import *
from Models import *
import shelve
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tutormeplease' #this is to encrypt data passing along our server, this includes our session data


@app.route("/", methods=['GET'])
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
                    #making session['verifying'] by checking if user is inside pendingtutor.db
                    db = shelve.open('databases/pendingtutor.db')
                    if session['user_id'] in db:
                        session['verifying'] = True
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
                else:
                    db.close()

                    #posting to user.db after no errors
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

@app.route('/becometutor', methods=['GET', 'POST'])
def tutorpage():
    if session.get('loggedin') != True:
        return redirect(url_for("home"))

    return render_template('becometutor.html')

@app.route('/tutor_onboarding')
def tutor_onboarding():
    if session.get('loggedin') != True:
        return redirect(url_for("home"))
    if session.get('verifying') ==True:
        return redirect(url_for("finish"))

    return render_template('/tutor_onboarding/tutor_onboarding.html')

app.config["PROFILE_PIC_UPLOADS"] = "static/images/profilepictures" #initializiing path for future references
app.config["ALLOWED_PROFILE_PIC_TYPE"] = ["PNG","JPG","JPEG"]

def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit('.')[1]
    if ext.upper() in app.config["ALLOWED_PROFILE_PIC_TYPE"]:
        return True
    else:
        return False


@app.route('/tutor_onboarding/personal_info', methods=['GET', 'POST'])
def tutor_onboarding_personal_info():
    form = PersonalInfoForm(request.form)
    if session.get('loggedin') != True:
        return redirect(url_for("home"))
    if session.get('verifying') == True:
        return redirect(url_for("finish"))
    else:
        #retrieving user object by using user session id
        db = shelve.open('databases/user.db')
        userObj = db[session['user_id']]
        db.close()

        session['firstname'] = userObj.get_user_firstname()
        session['lastname'] = userObj.get_user_lastname()
        session['profile_pic'] = userObj.get_user_profile_pic()
        if userObj.get_user_description() != "":
            session['description'] = userObj.get_user_description()
        if request.method == 'POST' and form.validate():

            firstname = request.form['first_name']
            lastname = request.form['last_name']
            description = request.form['description']
            language = request.form['language']
            proficiency = request.form['proficiency']
            #validating image upload, not using filefield inside forms, and also if user inputs a file then execute this line else continue
            if request.files['image'].filename != "":
                image = request.files["image"] #our name attribute inside our input form field.  this will return a file object in this case should be image/png
                if not allowed_image(image.filename):
                    extensionerror = "That image extension is not allowed"
                    print("That image extension is not allowed")
                    return render_template('/tutor_onboarding/personal_info.html', form=form, extensionerror=extensionerror)
                else:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["PROFILE_PIC_UPLOADS"],filename))

                    #updating userObj's profile pic if user decides to change their profile pic

                    profile_pic = filename
                    userObj.set_user_profile_pic(profile_pic)
            #updating user obj
            userObj.set_user_firstname(firstname)
            userObj.set_user_lastname(lastname)
            userObj.set_user_description(description)
            userObj.set_user_language({language:proficiency})

            #posting updated user obj to db #updating session
            session['name'] = userObj.get_user_fullname()
            session['profile_pic'] = userObj.get_user_profile_pic()
            db = shelve.open('databases/user.db','w')
            db[session['user_id']] = userObj
            db.close
            return  redirect(url_for('tutor_onboarding_professional_info'))

        return render_template('/tutor_onboarding/personal_info.html',form=form)

app.config['CERT_UPLOADS'] = 'databases/pendingcerts'
@app.route('/tutor_onboarding/professional_info', methods=['GET', 'POST'])
def tutor_onboarding_professional_info():
    form = ProfessionalInfoForm(request.form)
    if session.get('loggedin') != True:
        return redirect(url_for("home"))
    if session.get('verifying') ==True:
        return redirect(url_for("finish"))
    else:
        if request.method == 'POST' and form.validate():
            occupation = request.form['occupation']
            fromyear = request.form['fromyear']
            toyear = request.form['toyear']
            college_country = request.form['college_country']
            college_name = request.form['college_name']
            major = request.form['major']
            graduateyear = request.form['graduateyear']
            dob = request.form['dob']
            nric = request.form['nric']
            p1 = PendingTutor(session['user_id'],occupation, fromyear, toyear, college_country, college_name, major, graduateyear, dob, nric)
            #do a validation on certificate file
            if request.files:
                cert = request.files['cert']

                if cert.filename == "" :
                    emptyfileerror = 'cert not uploaded'
                    return render_template('/tutor_onboarding/professional_info.html',form=form, emptyfileerror=emptyfileerror)
                else:
                    cert.save(os.path.join(app.config['CERT_UPLOADS'],cert.filename))
                    p1.certificate = cert.filename

            #posting p1
            db = shelve.open('databases/pendingtutor.db','w')
            db[session['user_id']] = p1
            db.close()
            session['verifying'] = True
            return redirect(url_for('finish'))
    return render_template('/tutor_onboarding/professional_info.html',form=form)
@app.route('/tutor_onboarding/finish')
def finish():
   return render_template('tutor_onboarding/finish.html')

if __name__ =='__main__':
    app.run(debug=True)