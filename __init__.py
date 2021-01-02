from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from Forms import *
from Models import *
import shelve
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tutormeplease' #this is to encrypt data passing along our server, this includes our session data


@app.route("/", methods=['GET'])
def home():
    if session.get('istutor') == True:
        return  render_template('tutor_interface/tutorhome.html')
    else:
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
                    #checking is user is a tutor, if so redirect them to the tutor interface
                    tutordb = shelve.open('databases/tutor.db','r')
                    if session['user_id'] in tutordb:
                        session['istutor'] = True
                    tutordb.close()
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
            db.close()
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

@app.route('/profile/profile_main', methods=['GET', 'POST'])
def profilemain():
    if session.get('loggedin') != True:
        return redirect(url_for("home"))
    else:
        db = shelve.open('databases/user.db', 'r')
        userObj = db[session['user_id']]
        session['email'] = userObj.get_user_email()
        return render_template("profile/profile_main.html")

@app.route('/profile/profile_edit', methods=['GET', 'POST'])
def profileedit():
    if session.get('loggedin') != True:
        return redirect(url_for("home"))
    else:
        form = ProfileEditForm(request.form)
        if request.method == 'POST' and form.validate():
            print("posting")
            username = request.form['username']
            if request.files['image'].filename != "":
                image = request.files["image"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
                if not allowed_image(image.filename):
                    extensionerror = "That image extension is not allowed"
                    print(extensionerror)
                    return render_template('/profile/profile_edit.html', form=form, extensionerror=extensionerror)
                else:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["PROFILE_PIC_UPLOADS"], filename))
                    profile_pic = filename
                    session['profile_pic'] = profile_pic
                    db = shelve.open('databases/user.db', 'r')
                    userObj = db[session['user_id']]
                    userObj.set_user_profile_pic(profile_pic)
        return render_template('profile/profile_edit.html', form=form)

categories = {'GRAPHICS & DESIGN':['LOGO DESIGN','BRAND STYLE GUIDES','GAME ART','RESUME DESIGN'],
              'DIGITAL MARKETING':['SOCIAL MEDIA ADVERTISING','SEO','PODCAST MARKETING','SURVEY','WEB TRAFFIC'],
              'WRITING & TRANSLATION':['ARTICLES & BLOG POSTS'],
             'PROGRAMMING & TECH':['WEB PROGRAMMING','E-COMMERCE DEVELOPMENT','MOBILE APPLS','DESKTOP APPLICATIONS','DATABASES','USER TESTING']
              }
subcategoryArr = []
for key,values in categories.items():
    subcategoryArr.extend(values)

app.config["COURSE_THUMBNAIL_UPLOADS"] = 'static/images/coursethumbnails'
@app.route('/createcourse',methods=['GET', 'POST'])
def createcourse():
    if (session.get('loggedin') != True) or (session.get('istutor') != True):
        return redirect(url_for("home"))
    else:
        # retrieving user object by using user session id
        form = CreateCourseForm(request.form)
        if request.method == "POST" and form.validate():
            course_title = request.form['course_title']
            category = request.form['category']
            subcategory = request.form['subcategory']
            description = request.form['description']
            course = Courses(course_title,category,subcategory,description,session['user_id'])
            if request.files['image'].filename != "":
                image = request.files["image"] #our name attribute inside our input form field.  this will return a file object in this case should be image/png
                if not allowed_image(image.filename):
                    extensionerror = "That image extension is not allowed"
                    print("That image extension is not allowed")
                    return render_template('/tutor_interface/createcourse.html', form=form, extensionerror=extensionerror)
                else:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["COURSE_THUMBNAIL_UPLOADS"],filename))


                    course_thumbnail_pic = filename
                    course.course_thumbnail = course_thumbnail_pic
            #posting course object to courses.db
            db = shelve.open('databases/courses.db')
            db[course.course_id] = course
            db.close()
            return redirect(url_for('createsession',course_id=course.course_id))
    return render_template('tutor_interface/createcourse.html', form=form)

@app.route('/category/<category>')
def category(category):
    choicesArray = categories[category]
    return jsonify({'subcategories' : choicesArray})

#Sessions By Nuzul
@app.route('/createsession/<course_id>', methods=['GET','POST'])
def createsession(course_id):
    #retrieving course obj so can retrieve the sessions array
    db = shelve.open('databases/courses.db')
    course = db[course_id]
    db[course_id] = course
    db.close()
    print('retrieving from shelve')
    session_list_objects = course.sessions
    return render_template('tutor_interface/createsession.html', session_list_objects=session_list_objects, course_id = course_id)

@app.route('/updatesession/<course_id>/<session_no>',methods=['GET','POST'])
def updatesession(course_id,session_no):
    #retrieving the session object from the course.sessions list of objects. maybe this just for delete
    db = shelve.open('databases/courses.db')
    course_object = db[course_id]
    print(course_object)
    db.close()
    print((int(session_no)-1))
    for sessions in course_object.sessions:
        print(sessions)
    sessionobject = course_object.sessions[(int(session_no)-1)] #basically we are using the session no as the index for the session list in the course object.
    print(sessionobject)
    form = UpdateSessionForm(request.form)
    if request.method == "POST" and form.validate():
        sessionobject.session_title = request.form['session_title']
        sessionobject.session_description = request.form['session_description']
        sessionobject.time_approx = request.form['time_approx']
        updatedsessionobject = sessionobject
        print(updatedsessionobject)
        print('setting session object')
        #updating the session and posting back to courses.db
        db = shelve.open('databases/courses.db')
        courseobject = db[course_id]
        for sessions in courseobject.sessions:
            print(sessions)
        courseobject.sessions[int(session_no) - 1] = updatedsessionobject
        db[course_id] = course_object
        db.close()
        print('object posted now should be redirecting')
        return redirect(url_for("createsession",course_id=course_id))

    return render_template('tutor_interface/updatesession.html', form=form,sessionobject=sessionobject)

@app.route("/addnewsession/<course_id>",methods=["GET","POST"])
def addnewsession(course_id):
    form = UpdateSessionForm(request.form)

    #retrive previous sessions there is inside the course to get the new course number
    #actually dont need coz session_no is a class attribute so can just call it
    #oh my god, cannot use class attribute or else other user's new session also increases the number
    coursedb = shelve.open('databases/courses.db')
    course = coursedb[course_id]
    coursedb.close()
    sessionobject = Session()
    if request.method == "POST" and form.validate():
        sessionobject.session_title = request.form['session_title']
        sessionobject.session_description = request.form['session_description']
        sessionobject.time_approx = request.form['time_approx']
        #getting the len of the list and making that the session no
        sessionobject.session_no = len(course.sessions) + 1
        updatedsessionobject = sessionobject
        #posting new session object the course object sessions array
        coursedb = shelve.open('databases/courses.db')
        courseobject = coursedb[course_id]
        courseobject.sessions.append(updatedsessionobject)
        coursedb[course_id] = courseobject
        coursedb.close()
        return redirect(url_for("createsession",course_id=course_id))
    return render_template('tutor_interface/addnewsession.html', form=form)

@app.route("/deletesession/<course_id>/<session_no>", methods=['POST'])
def deletesession(course_id,session_no):
    coursedb = shelve.open('databases/courses.db')
    courseobject = coursedb[course_id]
    sessionlist = courseobject.sessions
    #removing the session the users wants to delete
    sessionlist.pop(int(session_no)-1)
    newsessionlist = []
    #in case the user deletes a session inbetween so we must reorder the session no
    for index, sessions in enumerate(sessionlist,1):
        sessions.session_no = index
        newsessionlist.append(sessions)
    courseobject.sessions = newsessionlist
    coursedb[course_id] = courseobject
    coursedb.close()
    return redirect(url_for("createsession", course_id=course_id))
if __name__ =='__main__':
    app.run(debug=True)