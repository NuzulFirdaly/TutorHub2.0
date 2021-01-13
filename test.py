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
            print(f"=========== Certifying =================\n {userobject.get_username()}\n {certified_user}")
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
    p1 = PendingTutor(user2.get_user_id(),'Student',2020,2023,'Singapore','Nanyang Polytechnic','Diploma in Information technology','2023','2003-12-02','T03009F')
    pendingdb[p1.user_id] = p1
    pendingdb.close()

    #auto certifying all tutors in pending tutors
    auto_certify_all()
    #moving tutor
    move_tutors()
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
    userdb = shelve.open('databases/user.db')
    userdb.clear()
    userdb.close()
    print('everything is deleted')
def delete_specific_course_from_tutor(user_id,course_id):
    tutordb = shelve.open('databases/tutor.db')
    tutorobject = tutordb[user_id]
    tutorobject.courses.remove(course_id)
    tutordb[user_id] = tutorobject
    tutordb.close()

# delete_everything()
# generate_stuff()
