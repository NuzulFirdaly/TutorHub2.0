from flask import *
from Forms import *
from Models import *
import shelve
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tutormeplease' #this is to encrypt data passing along our server, this includes our session data

# Tutors
@app.route("/", methods=['GET'])
def home():
    if session.get('istutor') == True:
        course_array = []
        coursedb = shelve.open('databases/courses.db')
        for courses in coursedb:
            course_array.append(coursedb[courses])
        coursedb.close()
        # to retrieve the tutors profile pic and username
        userdb = shelve.open('databases/user.db')
        userobjectarray = []
        for courseobjects in course_array:
            userobject = userdb[courseobjects.tutor]
            if userobject not in userobjectarray:
                userobjectarray.append(userobject)
            else:
                continue
        userdb.close()
        return  render_template('tutor_interface/tutorhome.html', course_array=course_array, userobjectarray=userobjectarray)
    else:
        course_array = []
        coursedb = shelve.open('databases/courses.db')
        for courses in coursedb:
            course_array.append(coursedb[courses])
        coursedb.close()
        # to retrieve the tutors profile pic and username
        userdb = shelve.open('databases/user.db')
        userobjectarray = []
        for courseobjects in course_array:
            userobject = userdb[courseobjects.tutor]
            if userobject not in userobjectarray:
                userobjectarray.append(userobject)
            else:
                continue
        userdb.close()


        return render_template('home.html', course_array=course_array, userobjectarray=userobjectarray)
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
                    session['email'] = user.get_user_email()
                    session['username'] = user.get_username()
                    session['firstname'] = user.get_user_firstname()
                    session['lastname'] = user.get_user_lastname()
                    session['description'] = user.get_user_description()
                    session['language'] = user.get_user_language()
                    session['proficiency'] = user.get_user_language_proficiency()
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
                    #checking is user is being certified, if so they cant go to becometutor
                    pendingdb = shelve.open('databases/pendingtutor.db')
                    if session['user_id'] in pendingdb:
                        session['verifying'] = True
                    pendingdb.close()
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
            confirm = request.form['confirm']
            password = request.form['password']
            firstname= request.form['first_name']
            lastname= request.form['last_name']
            if confirm != password:
                sameerror = 'password does not match'
                return render_template('register.html', form=createUserForm,sameerror=sameerror)
            #Validating form(if similar)
            if username == password:
                print('similar error')
                similarerror = 'Username and password cannot be the same'
                return render_template('register.html', form=createUserForm, similarerror=similarerror)

            #retrieving user.db
            print('opening db')
            db = shelve.open('databases/user.db')
            print('successfully opened db')
            #i think got error because its running a for loop on an empty database. so need do an if statement
            #if db is empty just create the user
            if len(db) == 0:
                user = User(email, username, password, firstname, lastname)  # user object
                db[user.get_user_id()] = user
                # testing code
                print("successfully posted")
                db.close()
                return redirect(url_for("home"))
            else:
                for user in db:
                    user = db[user]
                    print('checking each loop')
                    if user.get_user_email() == email:
                        print('email error')
                        emailerror = 'This email is in use, please enter another email.'
                        return render_template('register.html', form=createUserForm, emailerror=emailerror)
                    elif user.get_username() == username:
                        print('no email error')
                        usernameerror = 'This username is in use, please enter another username.'
                        return render_template('register.html', form=createUserForm, usernameerror=usernameerror)
                    else:
                        print('no username error')
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

app.config['CERT_UPLOADS'] = 'static/pendingcerts'
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
        recent = userObj.get_user_recent()
        db.close()

        coursedb = shelve.open('databases/courses.db', 'r')
        userdb = shelve.open('databases/user.db', 'r')
        recent.reverse()
        recentcourse = {}

        for id in recent:
            recentcourse[coursedb[id]] = userdb[coursedb[id].tutor]

        coursedb.close()
        userdb.close()
        return render_template("profile/profile_main.html", coursearray=recentcourse)

@app.route('/profile/profile_edit', methods=['GET', 'POST'])
def profileedit():
    db = shelve.open('databases/user.db', 'r')
    userObj = db[session['user_id']]
    db.close()
    if session.get('loggedin') != True:
        return redirect(url_for("home"))
    else:
        form = ProfileEditForm(request.form)
        form.description.data = session['description']
        form.language.data = session['language']
        form.proficiency.data = session['proficiency']
        if request.method == 'POST' and form.validate():
            print("posting")
            username = request.form['username']
            userObj.set_user_username(username)
            session['username'] = username

            firstname = request.form['firstname']
            userObj.set_user_firstname(firstname)
            session['firstname'] = firstname

            lastname = request.form['lastname']
            userObj.set_user_lastname(lastname)
            session['lastname'] = lastname

            description = request.form['description']
            userObj.set_user_description(description)
            session['description'] = description

            language = request.form['language']
            userObj.set_user_language(language)
            session['language'] = language

            proficiency = request.form['proficiency']
            userObj.set_user_language_proficiency(proficiency)
            session['proficiency'] = proficiency

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
                    db.close()

            db = shelve.open('databases/user.db', 'w')
            db[session['user_id']] = userObj
            db.close()
            flash('Changes Saved')
            return(redirect(url_for('profileedit')))

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
            short_description = request.form['short_description']
            description = request.form['description']
            course = Courses(course_title,category,subcategory,description,session['user_id'],short_description)
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
            #posting the course_id to the tutors.courses
            tutordb = shelve.open('databases/tutor.db')
            tutorobject = tutordb[session['user_id']]
            tutorobject.courses.append(course.course_id)
            tutordb[session['user_id']] =  tutorobject
            tutordb.close()
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
@app.route("/addpricing/<course_id>", methods=['GET','POST'])
def addpricing(course_id):
    form = AddPricingForm(request.form)
    #retrieving the courses to add the pricing inside
    coursedb = shelve.open('databases/courses.db')
    courseobject = coursedb[course_id]
    coursedb.close()
    #calculating all of the session approximate hours
    sessioncount = 0
    totalhours = 0
    for sessions in courseobject.sessions:
        totalhours += int(sessions.time_approx)
        sessioncount +=1

    if request.method == 'POST' and form.validate():
        hourlyrate = request.form['hourlyrate']
        maximumhourspersession = request.form['maximumhourspersession']
        minimumdays = request.form['minimumdays']
        maximumdays = request.form['maximumdays']
        courseobject.hourlyrate = hourlyrate
        courseobject.maximumhoursperssion = maximumhourspersession
        courseobject.minimumdays = minimumdays
        courseobject.maximumdays = maximumdays
        #posting inside coursedb
        coursesdb = shelve.open('databases/courses.db')
        coursesdb[course_id] = courseobject
        coursesdb.close()
        return redirect(url_for('home'))
    return render_template('tutor_interface/addpricing.html',form=form,totalhours=totalhours,sessioncount=sessioncount,session_list_objects=courseobject.sessions)

@app.route('/mycourses',methods=['GET'])
def mycourses():
    if session.get('istutor') == True:
        #retrieving user object
        userdb = shelve.open('databases/user.db')
        userobject = userdb[session['user_id']]
        userdb.close()
        #retrieving tutor object to retrieve their courses id
        tutordb = shelve.open('databases/tutor.db')
        tutorobject = tutordb[session['user_id']]
        tutordb.close()
        coursesarray = []
        #retrieving
        coursedb = shelve.open('databases/courses.db')
        for course_id in tutorobject.courses:
            coursesarray.append(coursedb[course_id])
        coursedb.close()
        return render_template('tutor_interface/mycourses.html', userobject=userobject,coursesarray=coursesarray)
    else:
        pass

@app.route('/updatecourse/<course_id>',methods=['GET','POST'])
def updatecourse(course_id):
    coursedb = shelve.open('databases/courses.db')
    courseobject = coursedb[course_id]
    coursedb.close()

    return render_template('tutor_interface/updatecourse.html', courseobject=courseobject, course_id=course_id)

@app.route('/editcourse/<course_id>',methods=['GET','POST'])
def editcourse(course_id):
    form = CreateCourseForm(request.form)
    form.subcategory.choices = [(subcategory,subcategory) for subcategory in subcategoryArr]
    coursedb = shelve.open('databases/courses.db')
    courseobject = coursedb[course_id]
    coursedb.close()
    form.course_title.data = courseobject.course_title
    form.category.data = courseobject.category
    form.subcategory.data = courseobject.subcategory
    form.short_description.data = courseobject.short_description
    form.description.data = courseobject.description
    if request.method == 'POST' and form.validate():
        course_title = request.form['course_title']
        category = request.form['category']
        subcategory = request.form['subcategory']
        print("trying to post this subcategory data")
        short_description = request.form['short_description']
        description = request.form['description']
        courseobject.course_title = course_title
        courseobject.category = category
        courseobject.subcategory = subcategory
        courseobject.short_description = short_description
        courseobject.description = description
        if request.files['image'].filename != "":
            image = request.files[
                "image"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print("That image extension is not allowed")
                return render_template('/tutor_interface/editcourse.html', form=form, extensionerror=extensionerror)
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["COURSE_THUMBNAIL_UPLOADS"], filename))

                course_thumbnail_pic = filename
                courseobject.course_thumbnail = course_thumbnail_pic
        #posting to coursedb
        coursedb = shelve.open('databases/courses.db')
        coursedb[course_id] = courseobject
        return redirect(url_for('updatecourse', course_id=courseobject.course_id))

    return render_template('tutor_interface/editcourse.html', form=form)

@app.route('/editcoursesession/<course_id>',methods=['GET', 'POST'])
def editcoursesession(course_id):
    # retrieving course obj so can retrieve the sessions array
    db = shelve.open('databases/courses.db')
    course = db[course_id]
    db[course_id] = course
    db.close()
    print('retrieving from shelve')
    session_list_objects = course.sessions
    return render_template('tutor_interface/editcoursesession.html', session_list_objects=session_list_objects,course_id=course_id)

@app.route('/editupdatesession/<course_id>/<session_no>',methods=['GET','POST'])
def editupdatesession(course_id,session_no):
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
        return redirect(url_for("editcoursesession",course_id=course_id))

    return render_template('tutor_interface/updatesession.html', form=form,sessionobject=sessionobject)

@app.route("/editdeletesession/<course_id>/<session_no>", methods=['POST'])
def editdeletesession(course_id,session_no):
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
    return redirect(url_for("editcoursesession", course_id=course_id))

@app.route("/editaddnewsession/<course_id>",methods=["GET","POST"])
def editaddnewsession(course_id):
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
        return redirect(url_for("editcoursesession",course_id=course_id))
    return render_template('tutor_interface/addnewsession.html', form=form)

@app.route('/deletecourse/<course_id>',methods=['POST'])
def deletecourse(course_id):
    print(session['user_id'])
    #removing course_id from tutor
    tutordb = shelve.open('databases/tutor.db')
    tutorobject = tutordb[session['user_id']]
    tutorobject.courses.remove(course_id)
    tutordb[session['user_id']] = tutorobject
    tutordb.close()
    #removing course_id from course db
    coursedb = shelve.open('databases/courses.db')
    coursedb.pop(course_id)
    coursedb.close()
    # removing the session the users wants to delete
    return redirect(url_for("mycourses"))
@app.route('/viewcourse/<course_id>', methods=['GET','POST'])
def viewcourse(course_id):
    if session.get('istutor') == True:
        coursedb = shelve.open('databases/courses.db')
        courseobject = coursedb[course_id]
        coursedb.close()
        # retrieving tutor's userobject from course.tutor
        userdb = shelve.open('databases/user.db')
        userobject = userdb[courseobject.tutor]
        userdb.close()
        return render_template('viewcourse.html', courseobject=courseobject,userobject=userobject)
    elif session.get('loggedin') != True:
        coursedb = shelve.open('databases/courses.db')
        courseobject = coursedb[course_id]
        coursedb.close()
        #retrieving tutor's userobject from course.tutor
        userdb = shelve.open('databases/user.db')
        userobject = userdb[courseobject.tutor]
        userdb.close()
        return render_template('viewcourse.html', courseobject=courseobject,userobject=userobject)

    else:
        coursedb = shelve.open('databases/courses.db')
        courseobject = coursedb[course_id]
        coursedb.close()

        db = shelve.open('databases/user.db', 'w')
        userObj = db[session['user_id']]
        recent = userObj.get_user_recent()
        if course_id not in recent:
            if len(recent) < 9:
                recent.append(course_id)
            else:
                recent.pop(0)
                recent.append(course_id)
        else:
            if course_id != recent[-1]:
                recent.remove(course_id)
                recent.append(course_id)

        userObj.set_user_recent(recent)
        db[session['user_id']] = userObj
        db.close()

        return render_template('viewcourse.html', courseobject=courseobject)
#Institution User here
@app.route("/InstitutionUser/AllInstitutions")
def AllInstitutions():
    return render_template('InstitutionUser/AllInstitutions.html')

@app.route("/InstitutionUser/InstitutionPage")
def InstitutionPage():
    return render_template('InstitutionUser/InstitutionPage.html')

@app.route("/InstitutionUser/AllInstitutionCourses")
def AllInstitutionCourses():
    return render_template('InstitutionAdmin/AllInstitutionCourses.html')

#Instituion Admin Here
@app.route("/InstitutionAdmin/FinishedRegistration")
def FinishedRegistration():
    return render_template('InstitutionAdmin/FinishedRegistration.html')

app.config["LICENSE_UPLOAD"] = "static/images/InstitutionLicense" #initializiing path for future references

@app.route("/InstitutionAdmin/RegisterInstitution", methods=["GET", "POST"])
def RegisterInstitution():
    form = RegisterInstitutionForm(request.form)
    if request.method == 'POST' and form.validate():
        #print("CAN U PLS WORK")
        institution_name = request.form['institution_name']
        institution_address = request.form['institution_address']
        postal_code = request.form['postal_code']
        institution_email = request.form['institution_email']
        website = request.form['website']
        office_no = request.form['office_no']
        admin_firstname = request.form['admin_firstname']
        admin_lastname = request.form['admin_lastname']
        admin_contact = request.form['admin_contact']
        admin_email = request.form['admin_email']


        if request.files['documents'].filename != "":
            image = request.files["documents"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return render_template('/InstitutionAdmin/RegisterInstitution.html', form=form, extensionerror=extensionerror)
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["LICENSE_UPLOAD"], filename))
                License = filename
                InstitutionObj = PendingInstitution(institution_name, institution_address, postal_code, institution_email, website, office_no, admin_firstname, admin_lastname, admin_contact, admin_email, License)
                db = shelve.open('databases/PendingInstitution.db', 'w')
                name = institution_name

                if len(db) == 0:
                    db[name.replace(' ','_')] = InstitutionObj
                else:
                    for insName in db:
                        if insName.lower() == name.lower():
                            error = 'This institution has been registered already'
                            return render_template('InstitutionAdmin/RegisterInstitution.html', form=form, error=error)
                        else:
                            db[name.replace(' ','_')] = InstitutionObj

                db.close()
                # print(InstitutionObj)
                # redirect
                return redirect(url_for('FinishedRegistration'))


    return render_template('InstitutionAdmin/RegisterInstitution.html', form=form)


app.config["SOCIALMEDIA_UPLOAD"] = "static/images/Institutionpictures" #initializiing path for future references

@app.route("/InstitutionAdmin/InstitutionPage_admin", methods=["GET", "POST"])
def AllInstitutions_admin():
    db = shelve.open('databases/Institution.db')
    name = 'Nanyang_Polytechnic'
    user = db[name]
    bannerlist = user.get_banner()
    smlist = user.get_sm()
    return render_template('InstitutionAdmin/InstitutionPage_admin.html', bannerarray=bannerlist, smarray=smlist)

app.config["BANNER_UPLOAD"] = "static/images/Institutionpictures/banner"
app.config["SOCIALMEDIA_UPLOAD"] = "static/images/Institutionpictures/socialmedia"

@app.route("/InstitutionAdmin/InstitutionPage_admin/<id>", methods=["GET", "POST"])
def editinstitution(id):
    if request.method == 'POST':
        if id == 'addbanner':
            # here
            if request.files['Uploadaddbanner'].filename != "":
                image = request.files[
                    "Uploadaddbanner"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
                if not allowed_image(image.filename):
                    extensionerror = "That image extension is not allowed"
                    print(extensionerror)
                    return redirect(url_for('AllInstitutions_admin',extensionerror=extensionerror))
                else:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["BANNER_UPLOAD"], filename))
                    banner = filename

                    db = shelve.open('databases/Institution.db', 'w')
                    name = 'Nanyang_Polytechnic'
                    user = db[name]
                    bannerlist = user.get_banner()
                    if banner not in bannerlist:
                        bannerlist.append(banner)
                        user.set_banner(bannerlist)
                        db[name] = user
            return redirect(url_for('AllInstitutions_admin', bannerarray=bannerlist))

        if id == 'deletebanner':
            db = shelve.open('databases/Institution.db', 'w')
            name = 'Nanyang_Polytechnic'
            user = db[name]
            bannerlist = user.get_banner()
            if request.form['bannerdelete']:
                print(request.form['bannerdelete'])
                print(bannerlist)
                bannerlist.remove(request.form['bannerdelete'])
                user.set_banner(bannerlist)
                db[name] = user

            return redirect(url_for('AllInstitutions_admin', bannerarray=bannerlist))

        if id == 'addsm':
            # here
            if request.files['uploadaddsm'].filename != "":
                image = request.files["uploadaddsm"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
                if not allowed_image(image.filename):
                    extensionerror = "That image extension is not allowed"
                    print(extensionerror)
                    return redirect(url_for('AllInstitutions_admin', extensionerror=extensionerror))
                else:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["SOCIALMEDIA_UPLOAD"], filename))
                    sm = filename

                    db = shelve.open('databases/Institution.db', 'w')
                    name = 'Nanyang_Polytechnic'
                    user = db[name]
                    smlist = user.get_sm()
                    if sm not in smlist:
                        smlist.append(sm)
                        user.set_sm(smlist)
                        db[name] = user
            return redirect(url_for('AllInstitutions_admin', bannerarray=smlist))

        if request.form['updatesocialmedia']:
            pass
    return redirect(url_for('AllInstitutions_admin'))

print('please work')
if __name__ =='__main__':
    app.run(debug=True)

#Erika