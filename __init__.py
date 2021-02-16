from flask import *
from Forms import *
from Models import *
import shelve
import os
from werkzeug.utils import secure_filename
import json as JSON
import smtplib,ssl
from datetime import *

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
            db = shelve.open('databases/user.db', 'r')
            username = request.form['username']
            pw = request.form['password']
            #for loop to check every users in db whether they have the same username and password
            insadmindb = shelve.open('databases/Institutionadmin.db', 'r')
            for admin in insadmindb:
                if insadmindb[admin].get_username() == username and insadmindb[admin].get_password() == pw:
                    session['admin_id'] = insadmindb[admin].get_admin_id()
                    session['institution'] = insadmindb[admin].get_institution()
                    session['username'] = insadmindb[admin].get_username()
                    session['firstname'] = insadmindb[admin].get_admin_firstname()
                    session['lastname'] = insadmindb[admin].get_admin_lastname()
                    session['contact'] = insadmindb[admin].get_admin_contact()
                    session['email'] = insadmindb[admin].get_admin_email()
                    session['password'] = insadmindb[admin].get_password()
                    session['profilepic'] = insadmindb[admin].get_profilepic()
                    session['loggedin'] = True
                    return redirect(url_for('AllInstitutions_admin', name=insadmindb[admin].get_institution()))
            insadmindb.close()

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
                    session['cart'] = {}
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
                    # checking is user is an admin, if so they will redirect them to the admin interface
                    Institutiondb = shelve.open('databases/Institution.db')
                    if session['user_id'] in Institutiondb:
                        return (url_for('InstitutionPage_admin'))
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
                    userobject = db[user]
                    print('checking each loop')
                    if userobject.get_user_email() == email:
                        print('email error')
                        emailerror = 'This email is in use, please enter another email.'
                        return render_template('register.html', form=createUserForm, emailerror=emailerror)
                    elif userobject.get_username() == username:
                        print('no email error')
                        usernameerror = 'This username is in use, please enter another username.'
                        return render_template('register.html', form=createUserForm, usernameerror=usernameerror)
                    else:
                        print('no username error')
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

@app.route('/reviews/<item>/<id>', methods=['GET', 'POST'])
def review(item, id):
    from datetime import date
    if session.get('loggedin') != True:
        return redirect(url_for('home'))
    else:
        form = Review(request.form)
        if form.validate():
            rating = int(request.form['rating'])
            comment = request.form['comment']
            name = session['username']
            userid = session['user_id']
            today = date.today()
            date = today.strftime("%b-%d-%Y")
            if item == 'tutor':
                tutordb = shelve.open('databases/tutor.db')
                tutor = tutordb[id]
                if not tutor.reviews.get(userid):
                    tutor.overallrating += rating
                else:
                    tutor.overallrating -= tutor.reviews[userid][0]
                    tutor.overallrating += rating
                tutorreview = tutor.reviews
                tutorreview[userid] = [rating, comment, name, date]
                tutor.reviews = tutorreview
                tutordb[id] = tutor
                return redirect(url_for('viewtutor', tutor_id=id))
            elif item == 'course':
                coursedb = shelve.open('databases/courses.db')
                course = coursedb[id]
                fullrating = course.overallrating
                if not course.reviews.get(userid):
                    fullrating += rating
                else:
                    fullrating -= course.reviews[userid][0]
                    fullrating += rating
                coursereview = course.reviews
                coursereview[userid] = [rating, comment, name, date]
                course.overallrating = fullrating
                print(course.overallrating)
                course.reviews = coursereview
                coursedb[id] = course
                return redirect(url_for('viewcourse', course_id=id))
        else:
            error = "Rating has to be between 1 and 5. Comment cannot be empty"
            print(error)
            return redirect(url_for('viewcourse', course_id=id))

@app.route('/delete/reviews/<item>/<id>', methods=['POST', 'GET'])
def deletereview(item, id):
    if request.method == "POST":
        userid = session['user_id']
        if item == 'tutor':
            tutordb = shelve.open('databases/tutor.db')
            tutor = tutordb[id]
            tutorreview = tutor.reviews
            tutor.overallrating -= tutorreview[userid][0]
            tutorreview.pop(userid)
            tutor.reviews = tutorreview
            tutordb[id] = tutor
            return redirect(url_for('viewtutor', tutor_id=id))
        elif item == 'course':
            coursedb = shelve.open('databases/courses.db')
            course = coursedb[id]
            coursereview = course.reviews
            course.overallrating -= coursereview[userid][0]
            coursereview.pop(userid)
            course.reviews = coursereview
            coursedb[id] = course
            return redirect(url_for('viewcourse', course_id=id))
    else:
        return redirect(url_for('viewcourse', course_id=id))

@app.route('/report/reviews/<item>/<id>/<uservictim>/<userreport>/<comment>', methods=['POST', 'GET'])
def reportreview(item, id, uservictim, userreport, comment):
    db = shelve.open('databases/report.db')
    print(db.get(uservictim))
    if db.get(uservictim):
        report = db[uservictim]
        report.append([item, id, userreport, comment])
        db[uservictim] = report
        print(report)
    else:
        db[uservictim] = []
        report = db[uservictim]
        report.append([item, id, userreport, comment])
        db[uservictim] = report
    return redirect(url_for('viewcourse', course_id=id))

app.config['ITEM_UPLOADS'] = 'static/images/itemlisting'
@app.route('/itemcreation', methods=['POST', 'GET'])
def itemCreation():
    if session['istutor'] != True:
        return redirect(url_for('home'))
    else:
        form = ItemListing(request.form)
        if request.method == 'POST' and form.validate():
            name = request.form['name'].replace(' ', '_')
            price = '{:.2f}'.format(float(request.form['price']))
            user_id = session['user_id']
            username = session['username']
            userpic = session['profile_pic']

            count = 0
            db = shelve.open('databases/itemlist.db', 'r')
            for item in db:
                if db[item].get_user_id() == session['user_id']:
                    count += 1

            if count < 5:
                if not db.get(name):
                    if request.files['image'].filename != "":
                        image = request.files["image"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
                        if not allowed_image(image.filename):
                            extensionerror = "That image extension is not allowed"
                            print(extensionerror)
                            db = shelve.open('databases/itemlist.db')
                            itemlist = []
                            for item in db:
                                itemlist.append(db[item])
                            return render_template('/itemListing.html', form=form, extensionerror=extensionerror, itemlist=itemlist)
                        else:
                            filename = secure_filename(image.filename)
                            image.save(os.path.join(app.config["ITEM_UPLOADS"], filename))
                            itempic = filename
                            db = shelve.open('databases/itemlist.db', 'w')
                            item = Essentials(name, price, itempic, user_id, username, userpic)
                            db[name] = item
                            db.close()

                else:
                    db = shelve.open('databases/itemlist.db')
                    itemlist = []
                    for item in db:
                        itemlist.append(db[item])
                    logicerror = 'There is an item with this name.'
                    return render_template('/itemListing.html', form=form, logicerror=logicerror, itemlist=itemlist)
            else:
                db = shelve.open('databases/itemlist.db')
                itemlist = []
                for item in db:
                    itemlist.append(db[item])
                logicerror = 'You have reached the maximum of 5 items listed.'
                return render_template('/itemListing.html', form=form, logicerror=logicerror, itemlist=itemlist)
        else:
            db = shelve.open('databases/itemlist.db')
            itemlist = []
            for item in db:
                itemlist.append(db[item])
            error = 'Price should be $0 to $50.'
            return render_template('/itemListing.html', form=form, error=error, itemlist=itemlist)


        return redirect(url_for('viewitems', form=form))

@app.route('/itemdelete/<name>', methods=['POST', 'GET'])
def itemDelete(name):
    itemdb = shelve.open('databases/itemlist.db')
    itemdb.pop(name)
    return redirect(url_for('viewitems'))

@app.route("/itemlisting", methods=["POST","GET"])
def viewitems():
    db = shelve.open('databases/itemlist.db')
    itemlist = []

    for item in db:
        itemlist.append(db[item])

    form = ItemListing(request.form)

    return render_template('itemListing.html', form=form, itemlist=itemlist)

@app.route("/itemlisting/<action>", methods=["POST","GET"])
def orderitems(action):
    if action == 'order':
        if request.method == "POST":
            if session.get('loggedin') != True:
                return redirect(url_for('login'))
            else:
                item = request.form['add_cart'].split(',')
                name = item[0]
                cost = "{:.2f}".format(float(item[1]))
                db = shelve.open('databases/itemlist.db', 'r')
                picture = db[name].get_picture()
                db.close()
                print(session['cart'])
                if session['cart'].get(name):
                    cart = session['cart']
                    cart[name][1] += 1
                    cart[name][2] = "{:.2f}".format(float(cart[name][1]) * float(cart[name][0]))
                    session['cart'] = cart
                else:
                    cart = session['cart']
                    cart[name] = [cost, 1, cost, picture]
                    session['cart'] = cart

                flash('Added')
                return redirect(url_for('viewitems'))
    elif action == 'list':
        form = ItemListing(request.form)
        return redirect(url_for('itemCreation', form=form))

@app.route("/itemlisting/viewCart/<id>", methods = ["POST"])
def deleteitem(id):
    cart = session['cart']
    cart.pop(id)
    session['cart'] = cart
    return redirect(url_for('viewCart'))

@app.route("/itemlisting/viewCart", methods = ["POST","GET"])
def viewCart():
    return render_template('viewCart.html')

@app.route("/itemlisting/cart/<action>", methods=["POST","GET"])
def editcart(action):
    if action == "plus":
        name = request.form["add_item"]
        cart = session['cart']
        quantity = cart[name][1]
        quantity += 1
        cart[name][1] = quantity
        item_price = float(cart[name][0]) * float(cart[name][1])
        cart[name][2] = "{:.2f}".format(item_price)
        session['cart'] = cart

    if action == "minus":
        name = request.form.get("minus_item")
        cart = session['cart']
        quantity = cart[name][1]
        if quantity > 1:
            quantity -= 1
            cart[name][1] = quantity
            item_price = float(cart[name][0]) * float(cart[name][1])
            cart[name][2] = "{:.2f}".format(item_price)
        else:
            cart[name][1] = 1
            cart[name][2] = cart[name][0]
        session['cart'] = cart

    return redirect(url_for('viewCart'))

@app.route("/itemlisting/cart/placeorder/<item>", methods =["GET","POST"])
def placeOrder(item):
    form = Payment(request.form)
    if request.method == "POST" and form.validate():
        cardnumber = request.form['cardnumber']
        expirydate = request.form['expirydate']
        security = request.form['security']
        try:
            int(cardnumber)
            if expirydate[2] == '/':
                expirydate.replace('/', '')
                try:
                    expiry = expirydate.replace('/', '')
                    int(expiry)

                    if int(expiry[0] + expiry[1]) <= 12:
                        try:
                            int(security)
                            if item == 'cart':
                                return redirect(url_for('receipt'))
                            elif item =='booking':
                                return redirect(url_for('finishedpaying'))

                        except:

                            error = 'CVV should be 3 digits.'
                            return render_template("payment.html", form=form, securityerror=error)
                    else:
                        error = 'Month has to be 0-12.'
                        return render_template("payment.html", form=form, expiryerror=error)
                except:
                    error = 'Expiry Date must be in the format of mm/yy.'
                    return render_template("payment.html", form=form, expiryerror=error)
            else:
                error = 'Expiry Date must be in the format of mm/yy.'
                return render_template("payment.html", form=form, expiryerror=error)
        except:
            error = 'Card number must be 16 digits.'
            return render_template("payment.html", form=form, cardnumbererror=error)

    return render_template("payment.html", form=form)

@app.route("/itemlisting/placeorder/receipt", methods =["GET","POST"])
def receipt():
    cart = session['cart']
    session['cart'] = {}
    return render_template("receipt.html", order=cart)


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

@app.route('/profile/profile_view', methods=['GET', 'POST'])
def viewprofile():
    return render_template('profile/profile_view.html')

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
    if (session.get('loggedin') != True) or (session.get('istutor') != True):
        return redirect(url_for("home"))
    else:
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
        # Rating System
        if len(courseobject.reviews) != 0:
            rating = round(courseobject.overallrating / len(courseobject.reviews), 1)
        else:
            rating = 0
        form = Review(request.form)
        if session['user_id'] in courseobject.reviews:
            form.rating.data = str(courseobject.reviews[session['user_id']][0])
            form.comment.data = courseobject.reviews[session['user_id']][1]
            print(courseobject.reviews)
        return render_template('viewcourse.html', courseobject=courseobject, form=form, rating=rating ,userobject=userobject)
    elif session.get('loggedin') != True:
        coursedb = shelve.open('databases/courses.db')
        courseobject = coursedb[course_id]
        coursedb.close()
        # retrieving tutor's userobject from course.tutor
        userdb = shelve.open('databases/user.db')
        userobject = userdb[courseobject.tutor]
        userdb.close()

        # Rating System
        if len(courseobject.reviews) != 0:
            rating = round(courseobject.overallrating / len(courseobject.reviews), 1)
        else:
            rating = 0
        form = Review(request.form)
        return render_template('viewcourse.html', courseobject=courseobject, form=form, rating=rating,  userobject=userobject)
    else:
        coursedb = shelve.open('databases/courses.db')
        courseobject = coursedb[course_id]
        coursedb.close()
        userdb = shelve.open('databases/user.db')
        userobject = userdb[courseobject.tutor]
        userdb.close()
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

        #Rating System
        if len(courseobject.reviews) != 0:
            rating = round(courseobject.overallrating/len(courseobject.reviews),1)
        else:
            rating = 0
        form = Review(request.form)
        if session['user_id'] in courseobject.reviews:
            form.rating.data = str(courseobject.reviews[session['user_id']][0])
            form.comment.data = courseobject.reviews[session['user_id']][1]
            print(courseobject.reviews)

        return render_template('viewcourse.html', courseobject=courseobject, form=form, rating=rating ,userobject=userobject)
eventsbro = [{'todo':'NODEJS Tutorial','date':'2021-01-25'},{'todo' : 'bruhhh', 'date':'2021-01-26' }]
@app.route('/myschedule/<tutor_id>',methods=['GET','POST'])
def myschedule(tutor_id):
    events = eventsbro
    return render_template('tutor_interface/myschedule.html',events=events, tutor_id = tutor_id)
@app.route('/myschedule/submit_entry',methods=['POST'])
def submit_entry():
    #i would like to not touch json ever again pls
    req = request.get_json()
    print("\n==== Debugging request===== \n ")
    print(repr(req))
    json_string = json.dumps(req) #https://stackoverflow.com/questions/4162642/single-vs-double-quotes-in-json
    stringed = str(req)
    #to get the tutor id from the json
    splitted = stringed.split("\'")
    print(splitted)
    tutor_id = splitted[1]
    #getting the todolist
    dictparsed = JSON.loads(json_string) #https://stackoverflow.com/questions/19483351/converting-json-string-to-dictionary-not-list
    print("\n==== Debugging Tutor_id ===== \n ")
    print(tutor_id)
    print(type(tutor_id))
    print("\n==== Debugging dict_parsed ===== \n ")
    print(repr(dictparsed))
    print(type(dictparsed))

    print("\n==== todoList ===== \n ")

    todoList = dictparsed[tutor_id]
    #posting todolist to calendar db tutor_id : todoList
    db = shelve.open("databases/calendar.db")
    db[tutor_id] = todoList
    db.close()
    for i in todoList:
        print(i)
    response = make_response(jsonify({"message":"JSON received"}),200)
    return response
@app.route("/submitSelectedList",methods=['GET','POST'])
def submitselectedlist():
    print("\n==== SELECTED LIST request===== \n ")

    req = request.get_json()
    print("\n==== Debugging request===== \n ")
    print(repr(req))
    json_string = json.dumps(req)  # https://stackoverflow.com/questions/4162642/single-vs-double-quotes-in-json
    stringed = str(req)
    # to get the tutor id from the json
    splitted = stringed.split("\'")
    print(splitted)
    tutor_id = splitted[1]
    course_id = splitted[3]
    # getting the todolist
    selectedList = JSON.loads(json_string)  # https://stackoverflow.com/questions/19483351/converting-json-string-to-dictionary-not-list
    print("\n==== Debugging Tutor_id ===== \n ")
    print(tutor_id)
    print(type(tutor_id))
    print("\n==== Debugging dict_parsed ===== \n ")
    print(repr(selectedList))
    print(type(selectedList))

    print("\n==== todoList ===== \n ")
    #checking all the todolist and updating the category
    # getting todoList
    db = shelve.open("databases/calendar.db")
    todoList = db[tutor_id]
    db.close()
    for i in todoList:
        print(i)
        print(type(i))
    print("\n==== getting the course name ===== \n ")
    coursedb = shelve.open('databases/courses.db')
    for courses in coursedb:
        if courses == course_id:
            coursename = coursedb[course_id].course_title

    print("\n==== selectList loo[ ===== \n ")
    #getting all the date objects to update the todolist at calendardb
    # for j in selectedList:
    #     print(j)
    #     print(type(j))
    jsonified_list = json.loads(selectedList[2])
    print("This is the jsonified list")
    print(jsonified_list)
    print(type(jsonified_list))
    for bookings in jsonified_list:
        for availabledates in todoList:
            if bookings['id'] == availabledates['id']:
                #updating category with coursename
                availabledates['category'] = coursename
    #posting updated todolist back
    db = shelve.open("databases/calendar.db")
    db[tutor_id] = todoList
    db.close()
    print("updated!")
    print(todoList)
    response = make_response(jsonify({"message": "JSON received"}), 200)
    return response

@app.route('/finishedpaying',methods=["GET","POST"])
def finishedpaying():
    return render_template("finishedpaying.html")
@app.route("/myschedule/fetch/<tutor_id>", methods=['GET', 'POST'])
def fetchCalendar(tutor_id):
    calendardb = shelve.open("databases/calendar.db")
    calendarlist = calendardb[tutor_id]
    calendardb.close()
    return jsonify(calendarlist)

@app.route('/viewtutor/<tutor_id>',methods=['GET','POST'])
def viewtutor(tutor_id):
    if session.get('istutor') == True:#tutor
        tutordb = shelve.open('databases/tutor.db')
        tutorobject = tutordb[tutor_id]
        tutordb.close()
        userdb = shelve.open('databases/user.db')
        userobject = userdb[tutor_id]
        userdb.close()

        coursesarray = []
        # retrieving
        coursedb = shelve.open('databases/courses.db')
        for course_id in tutorobject.courses:
            coursesarray.append(coursedb[course_id])
        coursedb.close()

        if len(tutorobject.reviews) != 0:
            rating = round(tutorobject.overallrating / len(tutorobject.reviews), 1)
        else:
            rating = 0
        form = Review(request.form)
        if session['user_id'] in tutorobject.reviews:
            form.rating.data = str(tutorobject.reviews[session['user_id']][0])
            form.comment.data = tutorobject.reviews[session['user_id']][1]
            print(tutorobject.reviews)

        return render_template('viewtutor.html', tutorobject=tutorobject, userobject=userobject,
                               coursesarray=coursesarray, form=form, rating=rating)

    elif session.get('loggedin') != True:#not loggedin

        tutordb = shelve.open('databases/tutor.db')
        tutorobject = tutordb[tutor_id]
        tutordb.close()
        userdb = shelve.open('databases/user.db')
        userobject = userdb[tutor_id]
        userdb.close()

        coursesarray = []
        # retrieving
        coursedb = shelve.open('databases/courses.db')
        for course_id in tutorobject.courses:
            coursesarray.append(coursedb[course_id])
        coursedb.close()

        if len(tutorobject.reviews) != 0:
            rating = round(tutorobject.overallrating / len(tutorobject.reviews), 1)
        else:
            rating = 0
        form = Review(request.form)
        return render_template('viewtutor.html', tutorobject=tutorobject, userobject=userobject,
                               coursesarray=coursesarray, form=form, rating=rating)

    else: # loggedin not a tutor

        tutordb = shelve.open('databases/tutor.db')
        tutorobject = tutordb[tutor_id]
        tutordb.close()
        userdb = shelve.open('databases/user.db')
        userobject = userdb[tutor_id]
        userdb.close()

        coursesarray = []
        # retrieving
        coursedb = shelve.open('databases/courses.db')
        for course_id in tutorobject.courses:
            coursesarray.append(coursedb[course_id])
        coursedb.close()

        if len(tutorobject.reviews) != 0:
            rating = round(tutorobject.overallrating / len(tutorobject.reviews), 1)
        else:
            rating = 0
        form = Review(request.form)
        if session['user_id'] in tutorobject.reviews:
            form.rating.data = str(tutorobject.reviews[session['user_id']][0])
            form.comment.data = tutorobject.reviews[session['user_id']][1]
            print(tutorobject.reviews)

    return render_template('viewtutor.html',tutorobject=tutorobject,userobject=userobject ,coursesarray=coursesarray, form=form, rating = rating)

@app.route('/viewavailableslots/<tutor_id>/<course_id>', methods=['GET',"POST"])
def viewavailableslots(tutor_id,course_id):
    return render_template('viewavailableslots.html',tutor_id=tutor_id,course_id=course_id)

#Institution User here
@app.route("/InstitutionUser/AllInstitutions")
def AllInstitutions():
    return render_template('InstitutionUser/AllInstitutions.html')

@app.route("/InstitutionUser/InstitutionPage")
def InstitutionPage():
    return render_template('InstitutionUser/InstitutionPage.html')

@app.route("/InstitutionAdmin/AllInstitutionCourses_admin")
def AllInstitutionCourses_admin():
    db = shelve.open('databases/Institution.db')
    name = 'Nanyang_Polytechnic'
    print(db[name])
    user = db[name]
    bannerlist = user.get_banner()
    print(bannerlist)
    db.close()
    return render_template('InstitutionAdmin/AllInstitutionCourses_admin.html', bannerarray=bannerlist)

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
                InstitutionObj = PendingInstitution(institution_name, institution_address, postal_code, institution_email, website, office_no, License)
                db = shelve.open('databases/PendingInstitution.db', 'w')
                name = institution_name

                if len(db) == 0:
                    db[name.replace(' ','_')] = InstitutionObj
                else:
                    for insName in db:
                        print("here")
                        print(insName)
                        print(name)
                        if insName.lower() == name.lower().replace(' ','_'):
                            error = 'This institution has been registered already'
                            return render_template('InstitutionAdmin/RegisterInstitution.html', form=form, error=error)
                        else:
                            db[name.replace(' ','_')] = InstitutionObj

                db.close()
                print(db)

                AdminObj = InstitutionAdmin(admin_firstname, admin_lastname, admin_contact, admin_email, name.replace(' ','_'))
                db = shelve.open('databases/InstitutionAdmin.db', 'w')
                db[AdminObj.get_admin_id()] = AdminObj
                db.close()
                # print(InstitutionObj)
                # redirect
                return redirect(url_for('FinishedRegistration'))


    return render_template('InstitutionAdmin/RegisterInstitution.html', form=form)


app.config["SOCIALMEDIA_UPLOAD"] = "static/images/Institutionpictures" #initializiing path for future references

@app.route("/InstitutionAdmin/<name>", methods=["GET", "POST"])
def AllInstitutions_admin(name):
    db = shelve.open('databases/Institution.db')
    print(name)
    user = db[name]
    bannerlist = user.get_banner()
    smdict = user.get_smurl()
    print(smdict)
    institutiontutordict = user.get_institutiontutor()
    seminardict = user.get_seminar()
    smform = socialmediaform(request.form)
    insform = institutiontutorform(request.form)
    semform = seminarsform(request.form)
    db.close()
    # semform.seminardescription.data = "hi"
    return render_template('InstitutionAdmin/InstitutionPage_admin.html', bannerarray=bannerlist, smarray=smdict, institutetarray=institutiontutordict, seminararray=seminardict,smform=smform, insform=insform, semform=semform)

app.config["BANNER_UPLOAD"] = "static/images/Institutionpictures/banner"
app.config["SOCIALMEDIA_UPLOAD"] = "static/images/Institutionpictures/socialmedia"
app.config["INSTITUTIONTUTOR_UPLOAD"] = "static/images/Institutionpictures/tutor"
app.config["SEMINAR_UPLOAD"] = "static/images/Institutionpictures/seminar"

#================ CRUD FOR BANNER ===================================================

#create banner function --------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/addbanner/<name>", methods=["GET", "POST"])
def addbanner(name):
    if request.files['Uploadaddbanner'].filename != "":
        image = request.files[
            "Uploadaddbanner"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
        if not allowed_image(image.filename):
            extensionerror = "That image extension is not allowed"
            print(extensionerror)
            return redirect(url_for('AllInstitutions_admin', name=session['institution']))
        else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["BANNER_UPLOAD"], filename))
            banner = filename

            db = shelve.open('databases/Institution.db', 'w')
            user = db[name]
            bannerlist = user.get_banner()
            if banner not in bannerlist:
                bannerlist.append(banner)
                user.set_banner(bannerlist)
                db[name] = user
            print(bannerlist)
            db.close()
    return redirect(url_for('AllInstitutions_admin', name=session['institution']))
    # return redirect(url_for('AllInstitutions_admin'))

#delete banner -----------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/deletebanner/<name>", methods=["GET", "POST"])
def deletebanner(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    bannerlist = user.get_banner()
    if request.form['bannerdelete']:
        print(request.form['bannerdelete'])
        print(bannerlist)
        bannerlist.remove(request.form['bannerdelete'])
        user.set_banner(bannerlist)
        db[name] = user
    db.close()
    return redirect(url_for('AllInstitutions_admin', name=session['institution']))
    # return redirect(url_for('AllInstitutions_admin'))
#================ END OF CRUD FOR BANNER ============================================

#================ CRUD FOR SOCIAL MEDIA =============================================

#create social media --------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/addsm/<name>", methods=["GET", "POST"])
def addsm(name):
    form = socialmediaform(request.form)
    if request.method == 'POST' and form.validate():
        smwebsite = request.form['smwebsite']
        print(smwebsite)
        if request.files['uploadaddsm'].filename != "":
            image = request.files["uploadaddsm"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return redirect(url_for('AllInstitutions_admin', form=form, name=session['institution']))
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["SOCIALMEDIA_UPLOAD"], filename))
                sm = filename

                db = shelve.open('databases/Institution.db', 'w')
                user = db[name]
                smdict = user.get_smurl()
                smdict[sm] = smwebsite
                user.set_smurl(smdict)
                print(smdict)
                db[name] = user
                db.close()

                return redirect(url_for('AllInstitutions_admin', name=session['institution'], form=form))
    # return redirect(url_for('AllInstitutions_admin'))

#update social media ----------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/updatesm/<name>", methods=["GET", "POST"])
def updatesm(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    smdict = user.get_smurl()
    form = socialmediaform(request.form)
    if request.method == 'POST' and form.validate():
        smwebsite = request.form['smwebsite']
        if request.files['uploadaddsm'].filename != "":  # if user uploads an image -> will update smdict[smimage] = smwebsite
            image = request.files["uploadaddsm"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return redirect(url_for('AllInstitutions_admin', form=form, name=session['institution']))
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["SOCIALMEDIA_UPLOAD"], filename))
                smimage = filename

                smdict[smimage] = smwebsite
                if request.form['smpics']:
                    smpic = request.form['smpics']
                    smdict.pop(smpic)

                socialmedia = smdict
                socialmedia[smimage] = smwebsite
                user.set_smurl(socialmedia)
                db[name] = user
        else:  # if user does not upload a file but still input edit website link
            # the problem is that the key is the image filename, but to update the link, will need the image filename...
            print("if they wan change url")
            if request.form['smpics']:
                print("this is request form")
                print(request.form['smpics'])
                smpic = request.form['smpics']
                print(smwebsite)
                print(smpic)
                smdict[smpic] = smwebsite
                user.set_smurl(smdict)
                print(user.get_smurl())
                db[name] = user

        return redirect(url_for('AllInstitutions_admin', name=session['institution'], form=form))
    # return redirect(url_for('AllInstitutions_admin'))

#delete social media ---------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/deletesm/<name>", methods=["GET", "POST"])
def deletesm(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    smdict = user.get_smurl()
    if request.form['smdelete']:
        print(request.form['smdelete'])
        print(smdict)
        smdict.pop(request.form['smdelete'])
        user.set_smurl(smdict)
        db[name] = user
    db.close()
    return redirect(url_for('AllInstitutions_admin', name=session['institution']))
    # return redirect(url_for('AllInstitutions_admin'))
#================ END OF CRUD FOR SOCIAL MEDIA ======================================

#================ CRUD FOR TUTOR ====================================================

#create tutor -----------------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/addtutor/<name>", methods=["GET", "POST"])
def addtutor(name):
    form = institutiontutorform(request.form)
    if request.method == 'POST' and form.validate():
        institutiontutor = request.form['institutiontutor']
        print(institutiontutor)
        if request.files['uploadaddtutor'].filename != "":
            image = request.files[
                "uploadaddtutor"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return redirect(url_for('AllInstitutions_admin', form=form, name=session['institution']))
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["INSTITUTIONTUTOR_UPLOAD"], filename))
                institutet = filename

                db = shelve.open('databases/Institution.db', 'w')
                user = db[name]
                institutiontutordict = user.get_institutiontutor()
                institutiontutordict[institutet] = institutiontutor
                user.set_institutiontutor(institutiontutordict)
                print(institutiontutordict)
                db[name] = user
                db.close()

        return redirect(url_for('AllInstitutions_admin', name=session['institution'], form=form))
    # return redirect(url_for('AllInstitutions_admin'))

#update tutor ----------------------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/updatetutor/<name>", methods=["GET", "POST"])
def updatetutor(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    institutiontutordict = user.get_institutiontutor()
    form = institutiontutorform(request.form)
    if request.method == 'POST' and form.validate():
        institutiontutor = request.form['institutiontutor']
        print(institutiontutor)
        if request.files['uploadupdateinstitutet'].filename != "":  # if user uploads an image -> it will update  institutiontutordict[itimage] = institutiontutor
            image = request.files["uploadupdateinstitutet"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return redirect(url_for('AllInstitutions_admin', name=session['institution']))
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["INSTITUTIONTUTOR_UPLOAD"], filename))
                itimage = filename

                institutiontutordict[itimage] = institutiontutor
                if request.form['institutiontutorpics']:
                    institutiontutorpic = request.form['institutiontutorpics']
                    institutiontutordict.pop(institutiontutorpic)

                schooltutor = institutiontutordict
                schooltutor[itimage] = institutiontutor
                user.set_institutiontutor(schooltutor)
                db[name] = user
        else:  # if user does not upload a file but still input edit tutor name
            institutiontutorpic = request.form['institutiontutorpics']
            institutiontutordict[institutiontutorpic] = institutiontutor
            user.set_institutiontutor(institutiontutordict)
            db[name] = user
        db.close()
        return redirect(url_for('AllInstitutions_admin', name=session['institution'], form=form))
    # return redirect(url_for('AllInstitutions_admin'))

#delete tutor -------------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/deletetutor/<name>", methods=["GET", "POST"])
def deletetutor(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    institutiontutordict = user.get_institutiontutor()
    if request.form['institutiontutordelete']:
        print(request.form['institutiontutordelete'])
        print(institutiontutordict)
        institutiontutordict.pop(request.form['institutiontutordelete'])
        user.set_institutiontutor(institutiontutordict)
        db[name] = user
    db.close()
    return redirect(url_for('AllInstitutions_admin', name=session['institution']))
    # return redirect(url_for('AllInstitutions_admin'))
#================ END OF CRUD FOR TUTOR =============================================

#================ CRUD FOR TOP COURSES ==============================================

#create top courses ----------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/addtopcourses", methods=["GET", "POST"])
def addtopcourses():
    pass
    # return redirect(url_for('AllInstitutions_admin'))
#delete top courses ----------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/deletetopcourses", methods=["GET", "POST"])
def deletetopcourses():
    pass
    # return redirect(url_for('AllInstitutions_admin'))
#================ END OF CRUD FOR TOP COURSES =======================================

#================ CRUD FOR SEMINARS =================================================
#create seminars
@app.route("/InstitutionAdmin/InstitutionPage_admin/addseminars/<name>", methods=["GET", "POST"])
def addseminars(name):
    print('hello')
    form = seminarsform(request.form)
    if request.method == 'POST' and form.validate():
        print('?')
        seminartitle = request.form['seminartitle']
        print('!')
        seminardescription = request.form['seminardescription']
        seminarwebsite = request.form['seminarwebsite']
        print(seminartitle)
        print(seminardescription)
        print(seminarwebsite)
        if request.files['uploadaddseminars'].filename != "":
            print('yay')
            image = request.files[
                "uploadaddseminars"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return redirect(url_for('AllInstitutions_admin', form=form, name=session['institution']))
            else:
                print('nay')
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["SEMINAR_UPLOAD"], filename))
                semin = filename

                print('why r u not working')
                db = shelve.open('databases/Institution.db', 'w')
                user = db[name]
                seminardict = user.get_seminar()
                seminardict[semin] = [seminartitle, seminardescription, seminarwebsite]
                user.set_seminar(seminardict)
                print(seminardict)
                db[name] = user
                db.close()

        return redirect(url_for('AllInstitutions_admin', name=session['institution'], form=form))
    # return redirect(url_for('AllInstitutions_admin'))

#update seminars
@app.route("/InstitutionAdmin/InstitutionPage_admin/updateseminars/<name>", methods=["GET", "POST"])
def updateseminars(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    seminardict = user.get_seminar()
    form = seminarsform(request.form)
    if request.method == "POST" and form.validate():
        seminartitle = request.form['seminartitle']
        seminardescription = request.form['seminardescription']
        seminarwebsite = request.form['seminarwebsite']
        if request.files['uploadupdateseminar'].filename != "":
            image = request.files["uploadupdateseminar"]
            if not allowed_image(image.filename):
                extensionerror = "THe image extension is not allowed"
                print(extensionerror)
                return redirect(url_for('AllInstitutions_admin', form=form, name=session['institution']))
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["SEMINAR_UPLOAD"], filename))
                seminarimage = filename

                seminardict[seminarimage] = [seminartitle, seminardescription, seminarwebsite]
                print("before popping")
                print(seminardict)
                if request.form['seminarpics']:
                    seminarpic = request.form['seminarpics']
                    seminardict.pop(seminarpic)
                    print("after popping")
                    print(seminardict)

                seminar = seminardict
                seminar[seminarimage] = [seminartitle, seminardescription, seminarwebsite]
                user.set_seminar(seminar)
                db[name] = user
        else:
            seminarpic = request.form['seminarpics']
            seminardict[seminarpic] = [seminartitle, seminardescription, seminarwebsite]
            user.set_seminar(seminardict)
            db[name] = user

        db.close()

        return redirect(url_for('AllInstitutions_admin', name=session['institution'], form=form))

# return redirect(url_for('AllInstitutions_admin'))

#delete seminars -------------------------------------------------------------------
@app.route("/InstitutionAdmin/InstitutionPage_admin/deleteseminars/<name>", methods=["GET", "POST"])
def deleteseminars(name):
    db = shelve.open('databases/Institution.db', 'w')
    user = db[name]
    print(user.get_smurl())
    seminardict = user.get_seminar()
    if request.form['seminardelete']:
        print(request.form['seminardelete'])
        print(seminardict)
        seminardict.pop(request.form['seminardelete'])
        user.set_seminar(seminardict)
        db[name] = user

    db.close()
    return redirect(url_for('AllInstitutions_admin', name=session['institution']))
    # return redirect(url_for('AllInstitutions_admin'))

#================ END OF CRUD FOR SEMINARS ==========================================
@app.route("/InstitutionAdmin/viewInstitutionPage/<name>", methods=["GET","POST"])
def viewInstitutionPage(name):
    db = shelve.open('databases/Institution.db')
    print(db[name])
    user = db[name]
    bannerlist = user.get_banner()
    smdict = user.get_smurl()
    institutiontutordict = user.get_institutiontutor()
    seminardict = user.get_seminar()
    print(bannerlist)
    print(smdict)
    print(institutiontutordict)
    print(seminardict)
    db.close()
    return render_template('InstitutionAdmin/viewInstitutionPage.html', bannerarray=bannerlist, smarray=smdict, institutetarray=institutiontutordict, seminararray=seminardict)

app.config["INSTITUTIONADMINTUTOR_UPLOAD"] = "static/images/Institutiontutor" #initializiing path for future references

@app.route("/InstitutionAdmin/RegisterInstituteTutor", methods=["GET","POST"])
def RegisterInstituteTutor():
    print("testing part 1")
    form = Registerinstitutiontutorform(request.form)
    if request.method == 'POST' and form.validate():
        print("testing part 2")
        occupation = request.form['occupation']
        fromyear = request.form['fromyear']
        toyear = request.form['toyear']
        college_country = request.form['college_country']
        college_name = request.form['college_name']
        major = request.form['major']
        graduateyear = request.form['graduateyear']
        dob = request.form['dob']
        nric = request.form['nric']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']


        if request.files['cert'].filename != "":
            image = request.files["cert"]
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return render_template("/InstitutionAdmin/RegisterInstituteTutor.html", form=form, extensionerror=extensionerror)
            else:
                print("testing part 3")
                db = shelve.open('databases/Institution.db')
                userObj = db[session['institution']]
                print(userObj)
                db.close()
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["INSTITUTIONADMINTUTOR_UPLOAD"], filename))
                schooltutor = filename
                print("Testing part 4")
                institutiontutorobj = PendingTutor(occupation, fromyear, toyear, college_country, college_name, major, graduateyear, dob, nric, schooltutor)
                itdb = shelve.open('databases/PendingInstitutionTutor.db', 'w')
                itdb[userObj.get_institution_name()] = institutiontutorobj
                print(itdb)
                itdb.close()

                #sending email to tutor for username and password
                port = 587 #for SSL
                smtp_server = "smtp.gmail.com"
                sender_email = "Iamtestingtutorhub2021@gmail.com"
                Email = email
                print(sender_email)
                password = "1@mt35t1ngTut0rHub2021"
                subject = "Your Account is Ready!"
                text = "Dear " + form.username.data  + ",\n" +"\nYour Account has officially been " \
                                                                                     "created! Do login and change your password immediately. \n" + "\nUsername: "+ form.first_name.data + form.last_name.data +"\n" + "\n Password: " + form.password.data + "\n" + "\nBest Regards,\n" + "TutorHub"
                message = "Subject: {}\n\n{}".format(subject, text)

                context = ssl.create_default_context()
                try:
                    with smtplib.SMTP(smtp_server, port) as server:
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(sender_email, password)
                        server.sendmail(sender_email, Email, message)
                except:
                    print("fail")
                print(message)

                return redirect(url_for('Complete'))

    return render_template("InstitutionAdmin/RegisterInstituteTutor.html", form=form)

@app.route("/InstitutionAdmin/Complete")
def Complete():
    return render_template("InstitutionAdmin/Complete.html")

@app.route("/InstitutionAdmin/tutorprofile")
def tutorprofile():
    return render_template("InstitutionAdmin/tutorprofile.html")

app.config["TUTORPROFILEEDIT_UPLOAD"] = "static/images/Institutiontutor" #initializiing path for future references

@app.route("/InstitutionAdmin/tutorprofileedit/", methods=["GET","POST"])
def edittutorprofile():
    print("adminprofile here")
    db = shelve.open('databases/InstitutionAdmin.db', 'r')
    userObj = db[session['admin_id']]
    print(userObj)
    db.close()

    form = InstitutionTutorProfileEditForm(request.form)

    if request.method == 'POST':
        print("admin profileedit")
        print("posting")
        username = request.form['admin_username']
        userObj.set_username(username)
        session['username'] = username
        print(username)

        admin_firstname = request.form['admin_firstname']
        userObj.set_admin_firstname(admin_firstname)
        session['admin_firstname'] = admin_firstname
        print(admin_firstname)

        admin_lastname = request.form['admin_lastname']
        userObj.set_admin_lastname(admin_lastname)
        session['admin_lastname'] = admin_lastname
        print(admin_lastname)

        admin_email = request.form['admin_email']
        userObj.set_admin_email(admin_email)
        print(admin_email)

        password = request.form['password']
        userObj.set_password(password)
        session['password'] = password

        print("maybe im here?")
        if request.files['image'].filename != "":
            print("am i here?")
            image = request.files["image"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
            if not allowed_image(image.filename):
                extensionerror = "That image extension is not allowed"
                print(extensionerror)
                return render_template('/InstitutionAdmin/tutorprofileedit.html', form=form, extensionerror=extensionerror)
            else:
                print("are you here")
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["TUTORPROFILEEDIT_UPLOAD"], filename))
                tutor_profile_pic = filename
                session['profilepic'] = tutor_profile_pic
                db = shelve.open('databases/InstitutionAdmin.db', 'r')
                userObj = db[session['admin_id']]
                userObj.set_profilepic(tutor_profile_pic)
                db.close()

        print("am i saving it?")
        db = shelve.open('databases/InstitutionAdmin.db', 'w')
        db[session['admin_id']] = userObj

        db.close()
        flash('Changes Saved')
        print("Changes saved")
        return (redirect(url_for('edittutorprofile')))


    return render_template("InstitutionAdmin/tutorprofileedit.html", form=form)

@app.route("/InstitutionAdmin/viewallinstitutiontutor/<name>")
def viewallinstitutiontutor(name):
    institutiontutordict = {}
    db = shelve.open('databases/PendingInstitutionTutor.db','r')
    institutiontutordict = db[name]
    db.close()

    institutiontutorlist = []
    for key in institutiontutordict:
        institution_tutor = institutiontutordict.get(key)
        institutiontutorlist.append(institution_tutor)

    print("institutiontutorlist")
    return render_template("InstitutionAdmin/viewallinstitutiontutor.html", institutiontutorlist = institutiontutorlist)

# @app.route("/InstitutionAdmin/InstitutionPage_admin/delete_tutor", methods=["GET", "POST"])
# def deletetutor():
#     db = shelve.open('databases/Institution.db', 'w')
#     user = db[name]
#     institutiontutordict = user.get_institutiontutor()
#     if request.form['institutiontutordelete']:
#         print(request.form['institutiontutordelete'])
#         print(institutiontutordict)
#         institutiontutordict.pop(request.form['institutiontutordelete'])
#         user.set_institutiontutor(institutiontutordict)
#         db[name] = user
#
#     return redirect(url_for('AllInstitutions_admin', institutetarray=institutiontutordict))

@app.route('/admin')
def adminHome():
    if session.get('admin_login'):
        return render_template('admin/adminHome.html')
    else:
        return redirect(url_for('home'))

@app.route('/adminProfile')
def adminProfile():
    if session.get('admin_login'):
        return render_template('admin/adminProfile.html')
    else:
        return redirect(url_for('home'))

@app.route('/adminContact')
def adminContact():
    admindb = shelve.open("databases/admin.db")
    adminarray = []
    for admins in admindb:
        admin = admindb[admins]
        adminarray.append([admin.get_admin_fullname(), admin.get_admin_role(), admin.get_admin_department()])
    return render_template('admin/adminContact.html', adminarray=adminarray)

@app.route('/adminCertificate', methods=['GET', 'POST'])
def adminCertificate():
    pendingtutordb = shelve.open("databases/pendingtutor.db")
    pendinginstitutiondb = shelve.open("databases/PendingInstitution.db")
    userdb = shelve.open("databases/user.db")
    pendingtutorarray = []
    pendinginstitutionarray = []
    userNamearray = []
    for tutorid in pendingtutordb:
        pendingtutorarray.append(pendingtutordb[tutorid])
        for userid in userdb:
            if tutorid == userid:
                userNamearray.append(userdb[userid])

    for institutionname in pendinginstitutiondb:
        pendinginstitutionarray.append(pendinginstitutiondb[institutionname])

    pendingtutordb.close()
    pendinginstitutiondb.close()
    userdb.close()

    return render_template('admin/adminCertificate.html', pendingtutorarray=pendingtutorarray, userNamearray=userNamearray, pendinginstitutionarray=pendinginstitutionarray)

@app.route('/deletePendingTutor/<id>', methods=['POST'])
def delete_tutor(id):
    pendingtutordb = shelve.open('databases/pendingtutor.db', 'w')
    pendingtutordb.pop(id)
    pendingtutordb.close()

    return redirect(url_for('adminCertificate'))

@app.route('/approvePendingTutor/<id>', methods=['POST'])
def approve_tutor(id):
    pendingtutordb = shelve.open('databases/pendingtutor.db', 'w')
    tutordb = shelve.open('databases/tutor.db', 'w')
    pendingtutor = pendingtutordb[id]
    #making tutor object from pending tutor object and update cert
    Tx = Tutor(pendingtutor)
    Tx.update_certified()
    tutordb[id] = Tx

    #popping tutor from pendingtutordb
    pendingtutordb.pop(id)
    pendingtutordb.close()
    tutordb.close()

    return redirect(url_for('adminCertificate'))

@app.route('/ViewPendingTutor/<id>', methods=['POST', 'GET'])
def view_tutor(id):
    pendingtutordb = shelve.open('databases/pendingtutor.db')
    userdb = shelve.open("databases/user.db")
    username = userdb[id]
    pendingtutor = pendingtutordb[id]
    selected = []
    selected.append([username.get_username(), pendingtutor])
    userdb.close()
    pendingtutordb.close()

    pendingtutordb = shelve.open("databases/pendingtutor.db")
    pendinginstitutiondb = shelve.open("databases/PendingInstitution.db")
    userdb = shelve.open("databases/user.db")
    pendingtutorarray = []
    pendinginstitutionarray = []
    userNamearray = []
    for tutorid in pendingtutordb:
        pendingtutorarray.append(pendingtutordb[tutorid])
        for userid in userdb:
            if tutorid == userid:
                userNamearray.append(userdb[userid])

    for institutionname in pendinginstitutiondb:
        pendinginstitutionarray.append(pendinginstitutiondb[institutionname])

    pendingtutordb.close()
    pendinginstitutiondb.close()
    userdb.close()

    return render_template('admin/adminCertificate.html', pendingtutorarray=pendingtutorarray, userNamearray=userNamearray, pendinginstitutionarray=pendinginstitutionarray, selected=selected)

@app.route('/ViewPendingInstitution/<id>', methods=['POST', 'GET'])
def view_institution(id):
    pendinginstitutiondb = shelve.open('databases/PendingInstitution.db')
    pendinginstitution = pendinginstitutiondb[id]
    iselected = []
    iselected.append([id, pendinginstitution])
    pendinginstitutiondb.close()

    pendingtutordb = shelve.open("databases/pendingtutor.db")
    pendinginstitutiondb = shelve.open("databases/PendingInstitution.db")
    userdb = shelve.open("databases/user.db")
    pendingtutorarray = []
    pendinginstitutionarray = []
    userNamearray = []
    for tutorid in pendingtutordb:
        pendingtutorarray.append(pendingtutordb[tutorid])
        for userid in userdb:
            if tutorid == userid:
                userNamearray.append(userdb[userid])

    for institutionname in pendinginstitutiondb:
        pendinginstitutionarray.append(pendinginstitutiondb[institutionname])

    pendingtutordb.close()
    pendinginstitutiondb.close()
    userdb.close()

    return render_template('admin/adminCertificate.html', pendingtutorarray=pendingtutorarray, userNamearray=userNamearray, pendinginstitutionarray=pendinginstitutionarray, iselected=iselected)

@app.route('/deletePendingInstitution/<id>', methods=['POST'])
def delete_institution(id):
    pendinginstitutiondb = shelve.open("databases/PendingInstitution.db", 'w')
    pendinginstitutiondb.pop(id)
    pendinginstitutiondb.close()

    return redirect(url_for('adminCertificate'))

@app.route('/approvePendingInstitution/<id>', methods=['POST'])
def approve_institution(id):
    pendinginstitutiondb = shelve.open("databases/PendingInstitution.db", 'w')
    institutiondb = shelve.open('databases/Institution.db', 'w')
    pendinginstitution = pendinginstitutiondb[id]

    Inst = Institution(pendinginstitution)
    Inst.update_approved()
    institutiondb[id] = Inst

    pendinginstitutiondb.pop(id)
    institutiondb.close()
    pendinginstitutiondb.close()

    return redirect(url_for('adminCertificate'))

@app.route('/adminEditProfile', methods=['POST', 'GET'])
def adminEditProfile():

    app.config["ADMIN_CERTIFICATE"] = "static/images/admin_img/admin_certificate"  # initializiing path for future references

    editAdminForm = EditAdminForm(request.form)
    if request.method == 'POST' and editAdminForm.validate():
        print("posting")

        if request.form['email'] == "":
            email = session['admin_email']
        else:
            email = request.form['email']

        if request.form['username'] == "":
            username = session['admin_username']
        else:
            username = request.form['username']

        if request.form['first_name'] == "":
            firstname = session['admin_firstname']
        else:
            firstname = request.form['first_name']

        if request.form['last_name'] == "":
            lastname = session['admin_lastname']
        else:
            lastname = request.form['last_name']

        if request.form['language'] == "":
            language = session['admin_language']
        else:
            language = request.form['language']

        if request.form['region'] == "":
            region = session['admin_region']
        else:
            region = request.form['region']

        if request.form['description'] == "":
            description = session['admin_description']
        else:
            description = request.form['description']

        if request.form['phonenumber'] == "":
            phonenumber = session['admin_phonenumber']
        else:
            phonenumber = request.form['phonenumber']

        print('opening db')
        admindb = shelve.open('databases/admin.db')
        print('successfully opened db')

        if len(admindb) == 0:
            admindb.close()
            return redirect(url_for("adminProfile"))
        else:
            availableids = []
            for admins in admindb:
                admin = admindb[admins]
                if admin.get_admin_username() == '':
                    availableids.append(admin.get_admin_id())

            for admins in admindb:
                admin = admindb[admins]
                if admin.get_admin_email() == email and admin.get_admin_email() != session['admin_email']:
                    print('email error')
                    emailerror = 'This email is in use, please enter another email.'
                    return render_template('admin/adminEditProfile.html', form=editAdminForm, emailerror=emailerror)
                elif admin.get_admin_username() == username and admin.get_admin_username() != session['admin_username']:
                    print('no username error')
                    usernameerror = 'This username is in use, please enter another username.'
                    return render_template('admin/adminEditProfile.html', form=editAdminForm,  usernameerror=usernameerror)
            admindb.close()

            if request.files['image'].filename != "":
                image = request.files["image"]  # our name attribute inside our input form field.  this will return a file object in this case should be image/png
                if not allowed_image(image.filename):
                    extensionerror = "That image extension is not allowed"
                    print(extensionerror)
                    return render_template('/admin/adminEditProfile.html', form=editAdminForm, extensionerror=extensionerror)
                else:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["ADMIN_CERTIFICATE"], filename))
                    certificate = filename
                    session['admin_certificate'].append(certificate)
                    admindb = shelve.open('databases/admin.db')
                    adminObj = admindb[session['admin_id']]
                    adminObj.add_admin_certificate(certificate)
                    admindb.close()

            admindb = shelve.open('databases/admin.db')
            for admins in admindb:
                if admins == session['admin_id']:
                    admin = admindb[admins]
                    admin.set_admin_email(email)
                    session['admin_email'] = email
                    admin.set_admin_username(username)
                    session['admin_username'] = username
                    admin.set_admin_firstname(firstname)
                    session['admin_firstname'] = firstname
                    admin.set_admin_lastname(lastname)
                    session['admin_lastname'] = lastname
                    admin.set_admin_language(language)
                    session['admin_language'] = language
                    admin.set_admin_region(region)
                    session['admin_region'] = region
                    admin.set_admin_description(description)
                    session['admin_description'] = description
                    admin.set_admin_phonenumber(phonenumber)
                    session['admin_phonenumber'] = phonenumber
                    admindb[session['admin_id']] = admin
                    return redirect(url_for('adminProfile'))
            admindb.close()

    return render_template('admin/adminEditProfile.html', form=editAdminForm)

@app.route('/adminAccount', methods=['POST', 'GET'])
def adminAccount():
    admindb = shelve.open('databases/admin.db')
    availableidarray = []
    adminrolearray = []
    for admins in admindb:
        admin = admindb[admins]
        if admin.get_admin_username() == '':
            availableidarray.append([admin.get_admin_id(), admin.get_admin_dategenerated()])
        else:
            adminrolearray.append([admin.get_admin_username(), admin.get_admin_id(), admin.get_admin_datecreated(), admin.get_admin_department(), admin.get_admin_role()])
    if len(availableidarray) != 0:
        latest_id = availableidarray[-1][0]
    else:
        latest_id = ''
    admindb.close()

    return render_template('admin/adminAccount.html', availableidarray=availableidarray, latest_id=latest_id, adminrolearray=adminrolearray)

@app.route('/adminAccountCreate', methods=['POST'])
def adminCreate():
    admin_id = uuid.uuid4().hex
    todaygenerated = datetime.now()
    admin_dategenerated = todaygenerated.strftime("%d/%m/%Y %H:%M:%S")
    admindb = shelve.open('databases/admin.db')
    admin = Admin(admin_id, admin_dategenerated)
    admindb[admin.get_admin_id()] = admin
    admindb.close()

    return redirect(url_for('adminAccount'))

@app.route('/deleteGeneratedAdmin/<id>', methods=['POST'])
def delete_generated_admin(id):
    admindb = shelve.open('databases/admin.db', 'w')
    admindb.pop(id)
    admindb.close()

    return redirect(url_for('adminAccount'))

@app.route('/clearGeneratedAdmin', methods=['POST'])
def clear_generated_admin():
    admindb = shelve.open('databases/admin.db', 'w')
    for admins in admindb:
        admin = admindb[admins]
        if admin.get_admin_username() == '':
            admindb.pop(admins)
    admindb.close()

    return redirect(url_for('adminAccount'))

@app.route('/adminAssignAdmin', methods=['POST', 'GET'])
def assign_admin():
    if request.method == 'POST':
        req = request.get_json()
        dict = json.loads(req)
        admindb = shelve.open('databases/admin.db', 'w')
        for admins in admindb:
            admin = admindb[admins]
            if admin.get_admin_id() == dict["id"]:
                admin.set_admin_role(dict["role"])
                if dict["department"] == None:
                    admin.set_admin_department("")
                else:
                    admin.set_admin_department(dict["department"])
                admindb[dict["id"]] = admin
        admindb.close()

    return redirect(url_for('adminAccount'))

@app.route('/adminPrelogin')
def adminPrelogin():
    return render_template('admin/adminPrelogin.html')

@app.route('/adminRegister', methods=['POST', 'GET'])
def adminRegister():
    createAdminForm = CreateAdminForm(request.form)
    if request.method == 'POST' and createAdminForm.validate():
        print("posting")
        email = request.form['email']
        username = request.form['username']
        confirm = request.form['confirm']
        password = request.form['password']
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        code = request.form['code']
        if confirm != password:
            sameerror = 'password does not match'
            return render_template('admin/adminRegister.html', form=createAdminForm,sameerror=sameerror)
        #Validating form(if similar)
        if username == password:
            print('similar error')
            similarerror = 'Username and password cannot be the same'
            return render_template('admin/adminRegister.html', form=createAdminForm, similarerror=similarerror)

        print('opening db')
        admindb = shelve.open('databases/admin.db')
        print('successfully opened db')

        if len(admindb) == 0:
            admindb.close()
            return redirect(url_for("adminPrelogin"))
        else:
            availableids = []
            for admins in admindb:
                admin = admindb[admins]
                if admin.get_admin_username() == '':
                    availableids.append(admin.get_admin_id())

            for admins in admindb:
                admin = admindb[admins]
                if code not in availableids:
                    print('code error')
                    codeerror = 'This code is invalid, please enter another code.'
                    return render_template('admin/adminRegister.html', form=createAdminForm, codeerror=codeerror)
                elif admin.get_admin_email() == email:
                    print('email error')
                    emailerror = 'This email is in use, please enter another email.'
                    return render_template('admin/adminRegister.html', form=createAdminForm, emailerror=emailerror)
                elif admin.get_admin_username() == username:
                    print('no username error')
                    usernameerror = 'This username is in use, please enter another username.'
                    return render_template('admin/adminRegister.html', form=createAdminForm, usernameerror=usernameerror)
            admindb.close()

            admindb = shelve.open('databases/admin.db')
            todaycreated = datetime.now()
            admin_datecreated = todaycreated.strftime("%d/%m/%Y %H:%M:%S")
            for adminids in admindb:
                if adminids == code:
                    adminobject = admindb[code]
                    adminobject.set_admin_email(email)
                    adminobject.set_admin_username(username)
                    adminobject.set_admin_firstname(firstname)
                    adminobject.set_admin_lastname(lastname)
                    adminobject.set_admin_password(password)
                    adminobject.set_admin_datecreated(admin_datecreated)
                    admindb[code] = adminobject
                    return redirect(url_for("adminPrelogin"))
            admindb.close()

    return render_template('admin/adminRegister.html', form=createAdminForm)

@app.route('/adminLogin', methods=['POST', 'GET'])
def adminLogin():
    form = AdminLoginForm(request.form)
    if request.method == 'POST' and form.validate():
        print("posting")
        admindb = shelve.open('databases/admin.db', 'r')
        username = request.form['username']
        password = request.form['password']

        # for loop to check every users in db whether they have the same username and password
        for admins in admindb:
            adminobject = admindb[admins]
            if adminobject.get_admin_username() == username and password == adminobject.get_admin_password():
                print('successfully login')
                session['admin_id'] = adminobject.get_admin_id()
                session['admin_username'] = adminobject.get_admin_username()
                session['admin_email'] = adminobject.get_admin_email()
                session['admin_firstname'] = adminobject.get_admin_firstname()
                session['admin_lastname'] = adminobject.get_admin_lastname()
                session['admin_profile_pic'] = adminobject.get_admin_profile_pic()
                session['admin_datecreated'] = adminobject.get_admin_datecreated()
                session['admin_role'] = adminobject.get_admin_role()
                session['admin_department'] = adminobject.get_admin_department()
                session['admin_description'] = adminobject.get_admin_description()
                session['admin_phonenumber'] = adminobject.get_admin_phonenumber()
                session['admin_region'] = adminobject.get_admin_region()
                session['admin_language'] = adminobject.get_admin_language()
                session['admin_certificate'] = adminobject.get_admin_certificate()
                session['admin_login'] = True
                return redirect(url_for('adminHome'))

    return render_template('admin/adminLogin.html', form=form)

@app.route('/adminLogout', methods=['GET', 'POST'])
def adminLogout():
    session.clear()
    return redirect(url_for("adminPrelogin"))


if __name__ =='__main__':
    app.run(port=5555,debug=True)


#Nuzul Firdaly