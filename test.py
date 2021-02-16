from Models import  *
import shelve

#creating a function which automatically makes the users, a certified tutor.
def make_certified(userobject):
    userobject.update_certified()
    return userobject

def auto_certify_all():
    try:
        db = shelve.open('databases/pendingtutor.db','c')
        for users in db:
            print(db[users])
        userdb = shelve.open('databases/user.db')
        for users in db:
            #certifying all users in our pending tutor.db
            certified_user = make_certified(db[users])
            userobject = userdb[db[users].user_id]
            print(f"=========== Pending DB Certifying =================\n {userobject.get_username()}\n {certified_user}")
            #posting back to db
            db[certified_user.user_id] = certified_user
        db.close()
    except IOError:
        print("Error opening user.db")

#creating a function that loops through the pending tutor database to put certified tutors inside the tutor db
def move_tutors():
    def check_certified(user):
        if user.get_certified() == True:
            return True
        else:
            return False
    try:
        db = shelve.open('databases/pendingtutor.db', 'c')
        tutordb = shelve.open('databases/tutor.db','c')
        for users in db:
            print(db[users])
            if check_certified(db[users]) == True:
                #making tutor object from the pending tutorobject
                certified_tutor_object = Tutor(db[users])
                certified_tutor_object.update_certified()
                tutordb[certified_tutor_object.user_id] = certified_tutor_object
                print("This is the just assigned tutor \n",certified_tutor_object.user_id)
                #hmm for some reason since i use inheritance, and the pending tutor object always initialize __certified as false,
                # when we make our Tutor object, it will also initialize .__certified as false even if in pending tutor the attribute was changed to true.
                #Aiya, i'll just do a update_certified() on the tutor object again. sry m'lords
        db.close()
        for tutors in tutordb:
            print("=========== THIS IS TUTOR.DB ==============")
            print(tutordb[tutors])
        tutordb.close()
    except IOError:
        print("Error opening user.db")


def see_sessions():
    coursesdb = shelve.open("databases/courses.db")
    for courses in coursesdb:
        course_object = coursesdb[courses]
        for sessions in course_object.sessions:
            print(sessions)
def delete_courses():
    db = shelve.open('databases/courses.db')
    db.clear()
    db.close()

def delete_users():
    db = shelve.open('databases/user.db')
    db.clear()
    db.close()

def generate_stuff():
    #generating tutee
    userdb = shelve.open('databases/user.db')
    # def __init__(self,user_email,username,user_pw,user_firstname,user_lastname):
    user1 = User('user1@mail.com','user1testing', 'password','user1','tutee')
    user2 = User('user2@mail.com','user2testing', 'password','user2','tutor')
    userdb[user1.get_user_id()] = user1
    userdb[user2.get_user_id()] = user2
    userdb.close()

    #making user 2 a pendingtutor
    #    def __init__(self, user_id, occupation,fromyear,toyear,college_country,college_name,major, year ,dob,nric):

    pendingdb = shelve.open('databases/pendingtutor.db')
    p1 = PendingTutor(user2.get_user_id(),'Student',2020,2023,'Singapore','Nanyang Polytechnic','Diploma in Information technology','2023','2003-12-02','T0137009F')
    pendingdb[p1.user_id] = p1
    pendingdb.close()

    #auto certifying all tutors in pending tutors
    auto_certify_all()
    #moving tutor
    move_tutors()
    coursesdb = shelve.open("databases/courses.db")
    #  (self,course_title,category,subcategory,description,tutor,short_description):
    # self.hourlyrate = 0
    # self.maximumdays = 0
    # self.maximumhoursperssion = 0
    # self.minimumdays = 0

    # categories = {'GRAPHICS & DESIGN': ['LOGO DESIGN', 'BRAND STYLE GUIDES', 'GAME ART', 'RESUME DESIGN'],
    #               'DIGITAL MARKETING': ['SOCIAL MEDIA ADVERTISING', 'SEO', 'PODCAST MARKETING', 'SURVEY',
    #                                     'WEB TRAFFIC'],
    #               'WRITING & TRANSLATION': ['ARTICLES & BLOG POSTS'],
    #               'PROGRAMMING & TECH': ['WEB PROGRAMMING', 'E-COMMERCE DEVELOPMENT', 'MOBILE APPLS',
    #                                      'DESKTOP APPLICATIONS', 'DATABASES', 'USER TESTING']
    #               }
    # need to add PRE-TERTIARY : ["CHEMISTRY","BIOLOGY", "MATH"]
    # MATH : MATH
    c1 = Courses('Flask App Development','PROGRAMMING & TECH', 'WEB PROGRAMMING', 'Blah Blah Blah Blah', p1.user_id, "Developing an application using Flask")
    c1.course_thumbnail = 'flasklol.png'
    c2 = Courses('NodeJS App Development','PROGRAMMING & TECH', 'WEB PROGRAMMING', 'Blah Blah Blah Blah', p1.user_id, "Developing an application using NodeJS")
    c2.course_thumbnail = 'blah.jpg'
    c3 = Courses('SQL 101','PROGRAMMING & TECH', 'DATABASES', 'Blah Blah Blah Blah', p1.user_id, "Learning the basics of SQL")
    c3.course_thumbnail = "sql.png"
    c4 = Courses('User Research Methods', 'PROGRAMMING & TECH', 'USER TESTING', 'Blah Blah Blah Blah', p1.user_id,"Understanding User Researching Methods")
    c4.course_thumbnail = "userresearch.png"

    cmath1 = Courses('Introduction To Mathematical Thinking', "MATH & LOGIC", "MATH", " Mathematical thinking is not the same as doing mathematics – at least not as mathematics is typically presented in our school system. School math typically focuses on learning procedures to solve highly stereotyped problems. Professional mathematicians think a certain way to solve real problems, problems that can arise from the everyday world, or from science, or from within mathematics itself. The key to success in school math is to learn to think inside-the-box. In contrast, a key feature of mathematical thinking is thinking outside-the-box – a valuable ability in today’s world. This course helps to develop that crucial way of thinking.",
                     p1.user_id, "Learn how to think the way mathematicians do – a powerful cognitive process developed over thousands of years. ")
    cmath1.course_thumbnail = "maththink.jfif"
    #adding the sessions
    # self.session_no = 1
    # self.session_title = 'Introductory Session'
    # self.session_description = "blah blah blah"
    # self.session_materials = []
    # self.time_approx = 4
    s1 = Session()
    s1.session_title = "Welcome Lecture"
    s1.session_description = "START with the Welcome lecture. It explains what this course is about. (It comes with a short Background Reading assignment, to read before you start the course, and a Reading Supplement on Set Theory for use later in the course, both in downloadable PDF format.) This initial orientation lecture is important, since this course is probably not like any math course you have taken before – even if in places it might look like one! AFTER THAT, Lecture 1 prepares the groundwork for the course; then in Lecture 2 we dive into the first topic. This may all look like easy stuff, but tens of thousands of former students found they had trouble later by skipping through Week 1 too quickly! Be warned. If possible, form or join a study group and discuss everything with them. BY THE WAY, the time estimates for watching the video lectures are machine generated, based on the video length. Expect to spend a lot longer going through the lectures sufficiently well to understand the material. The time estimates for completing the weekly Problem Sets (Quiz format) are a bit more reliable, but even they are just a guideline. You may find yourself taking a lot longer."
    s2 = Session()
    s2.session_no = 2
    s2.session_title = "Mathematical Proofs"
    s2.session_description = "This week we complete our brief look at mathematical proofs"
    cmath1.sessions = [s1,s2]
    coursesdb[c1.course_id] = c1
    coursesdb[c2.course_id] = c2
    coursesdb[c3.course_id] = c3
    coursesdb[c4.course_id] = c4
    coursesdb[cmath1.course_id] = cmath1
    coursesdb.close()

    #pending the courseid to the tutor courselist

    #theres a key error because when i move tutor from pending to the tutordb, they used a new user_id(since the inheritance reruns the intialization and creates a new user_id
    # to solve this issue, i believe
    #Why is the for loop for tutors not printing the objet's string method???
    tutordb = shelve.open('databases/tutor.db')
    print('These are the tutors IDs ')
    for tutors in tutordb:
        print(tutors)
    tutorobject = tutordb[p1.user_id]
    tutorobject.courses.append(c1.course_id)
    tutorobject.courses.append(c2.course_id)
    tutorobject.courses.append(c3.course_id)
    tutorobject.courses.append(c4.course_id)
    tutorobject.courses.append(cmath1.course_id)
    tutordb[p1.user_id] = tutorobject
    tutordb.close()

    # Generate shop items
    db = shelve.open('databases/itemlist.db')

    name = 'Black_Pen'
    item = Essentials('Black_Pen', '2.10', 'blackpen.jpg', user2.get_user_id(), user2.get_username(),
                      user2.get_user_profile_pic())
    db[name] = item

    name = 'Exercise_Book'
    item = Essentials('Exercise_Book', '1.80', 'Exercisebook.jpg', user2.get_user_id(), user2.get_username(),
                      user2.get_user_profile_pic())
    db[name] = item

    db.close()


def delete_pending():
    db = shelve.open('databases/pendingtutor.db')
    db.clear()
    db.close()


def delete_everything():
    coursedb = shelve.open('databases/courses.db')
    coursedb.clear()
    coursedb.close()
    pendingdb = shelve.open('databases/pendingtutor.db')
    pendingdb.clear()
    pendingdb.close()
    tutordb = shelve.open('databases/tutor.db')
    tutordb.clear()
    tutordb.close()
    PendingInstitution = shelve.open('databases/PendingInstitution.db')
    PendingInstitution.clear()
    PendingInstitution.close()
    Institution = shelve.open('databases/Institution.db')
    Institution.clear()
    Institution.close()
    PendingInstitutionTutor = shelve.open('databases/PendingInstitutionTutor.db')
    PendingInstitutionTutor.clear()
    PendingInstitutionTutor.close()
    userdb = shelve.open('databases/user.db')
    userdb.clear()
    userdb.close()
    reportdb = shelve.open('databases/report.db')
    reportdb.clear()
    reportdb.close()
    itemlistdb = shelve.open('databases/itemlist.db')
    itemlistdb.clear()
    itemlistdb.close()
    itemlistdb = shelve.open('databases/InstitutionAdmin.db')
    itemlistdb.clear()
    itemlistdb.close()
    admindb = shelve.open('databases/admin.db')
    admindb.clear()
    admindb.close()
    print('everything is deleted')
def delete_specific_course_from_tutor(user_id,course_id):
    tutordb = shelve.open('databases/tutor.db')
    tutorobject = tutordb[user_id]
    tutorobject.courses.remove(course_id)
    tutordb[user_id] = tutorobject
    tutordb.close()

def chris_not_mine(): #erika
    db = shelve.open('databases/PendingInstitution.db')
    for key in db:
        user = db.pop(key)
        print(user)
        print(key)

    admin = Institution(user)
    db.close()
    db = shelve.open('databases/Institution.db')
    db['Nanyang_Polytechnic'] = admin
    # print(db['Nanyang_Polytechnic'])
    admin = db['Nanyang_Polytechnic']
    admin.set_banner(['2.jpg'])
    # admin.set_sm(['2.jpg'])
    admin.set_institutiontutor({'2.jpg':'Mr Wilson'})
    admin.set_seminar({'2.jpg':['EAE workshop','Hi just some random text lololol','https://www.nyp.edu.sg/']})
    db['Nanyang_Polytechnic'] = admin

    print(db['Nanyang_Polytechnic'].get_banner())
    print(db['Nanyang_Polytechnic'].get_institutiontutor())
    print(db['Nanyang_Polytechnic'].get_seminar())
    # print(db['Nanyang_Polytechnic'].get_sm())
    db.close()

    insadmindb = shelve.open('databases/InstitutionAdmin.db')
    for padmin in insadmindb:
        print(insadmindb[padmin].get_institution())
        if insadmindb[padmin].get_institution() == 'Nanyang_Polytechnic':
            password = insadmindb[padmin].get_password()
            username = insadmindb[padmin].get_username()
            print(password)
            print(username)

    insadmindb.close()

def check_password():
    insadmindb = shelve.open('databases/InstitutionAdmin.db')
    for padmin in insadmindb:
        print(insadmindb[padmin].get_institution())
        if insadmindb[padmin].get_institution() == 'Nanyang_Polytechnic':
            password = insadmindb[padmin].get_password()
            username = insadmindb[padmin].get_username()
            print(password)
            print(username)

    insadmindb.close()
def check_ptutor_db():
    ptutordb = shelve.open("databases/pendingtutor.db")
    for ptutors in ptutordb:
        print(ptutordb[ptutors])
    ptutordb.close()

def check_pinstitution_db():
    pinstitutiondb = shelve.open("databases/pendinginstitution.db")
    for pinstitution in pinstitutiondb:
        print(pinstitutiondb[pinstitution])
    pinstitutiondb.close()

def check_institutiontutor_db():
    pinstitutiontutordb = shelve.open("databases/PendingInstitutionTutor.db")
    for institute in pinstitutiontutordb:
        print(pinstitutiontutordb[institute])
        print(institute)
    pinstitutiontutordb.close()

# check_pinstitution_db()
delete_everything()
generate_stuff()
# chris_not_mine()
# check_password()
# check_ptutor_db()
# print("")
# check_pinstitution_db()
