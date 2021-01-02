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

def check_user():
    db = shelve.open('databases/user.db')
    for i in db.values():
        i.get_language