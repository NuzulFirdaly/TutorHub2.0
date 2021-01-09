#here we store all classes of the different users, easy access to make objects later
import uuid
import shelve
from passlib.hash import pbkdf2_sha256

class User():
    def __init__(self,user_email,username,user_pw,user_firstname,user_lastname):
        self.__user_id = uuid.uuid4().hex
        self.__user_email=user_email
        self.__username=username
        #encrypts user password
        self.__user_pw=pbkdf2_sha256.hash(user_pw)
        self.__user_firstname =user_firstname
        self.__user_lastname =user_lastname
        self.__user_profile_pic = "avatar3.jpg"
        self.__user_description = ""
        self.__user_language = 'English'
        self.__user_language_proficiency = 'Basic'

    # User_Model Accessor
    def get_user_email(self):
        return self.__user_email

    def get_username(self):
        return self.__username

    def get_user_pw(self):
        return self.__user_pw

    def get_user_firstname(self):
        return self.__user_firstname

    def get_user_lastname(self):
        return self.__user_lastname

    def get_user_fullname(self):
        return self.__user_firstname + " " + self.__user_lastname

    def get_user_id(self):
        return self.__user_id

    def get_user_profile_pic(self):
        return self.__user_profile_pic

    def get_user_description(self):
        return self.__user_description

    def get_user_language(self):
        # languagelist = []
        # for languages in self.__user_language:
        #     languagelist.append(languages)
        # liststring = ','.join(languagelist)
        return self.__user_language

    def get_user_language_proficiency(self):
        return self.__user_language_proficiency

    #Set methods, i actually dont know why we didnt just make this a public data attribute
    def set_user_email(self, email):
        self.__user_email = email

    def set_user_username(self, username):
        self.__username = username

    def set_user_firstname(self, firstname):
        self.__user_firstname = firstname

    def set_user_lastname(self, lastname):
        self.__user_lastname = lastname

    def set_user_profile_pic(self, profile_pic):
        self.__user_profile_pic = profile_pic

    def set_user_description(self, description):
        self.__user_description = description

    def set_user_language(self, language):
        self.__user_language = language

    def set_user_language_proficiency(self, proficiency):
        self.__user_language_proficiency = proficiency

    def __str__(self):
        return ' user_id:{} \n username: {} \n email: {} \n password:{} \n firstname:{} \n lastname:{} \n fullname:{} \n languages:{} \n description:{} '.format(
            self.get_user_id(),self.get_username(), self.get_user_email(), self.get_user_pw(), self.get_user_firstname(),
            self.get_user_lastname(), self.get_user_fullname(),
            self.get_user_language(), self.get_user_description())

def get_user(userid):
    try:
        db = shelve.open('databases/user.db', 'r')
    except IOError:
        print("Error opening user.db")
    except:
        print("Unknown error occurred fetching user.db")
    else:
        if userid in db.keys():
            user = db.get(userid)
            db.close()
            return user
        else:
            print("Userid not found in user.db")

def update_user(user_obj):
    try:
        db = shelve.open('databases/user.db', 'r')
    except IOError:
        print("Error opening user.db")
    except:
        print("Unknown error occurred fetching user.db")
    else:
        if user_obj.get_user_id() in db.keys():
            db[user_obj.get_user_id()] = user_obj
            db.close()


class PendingTutor():
    def __init__(self, user_id, occupation,fromyear,toyear,college_country,college_name,major, year ,dob,nric):
        self.user_id = user_id
        self.occupation = occupation
        self.fromyear = fromyear
        self.toyear = toyear
        self.college_country = college_country
        self.college_name = college_name
        self.major = major
        self.year = year
        self.certificate = ""
        self.dob = dob
        self.nric = nric
        self.__certified = False
    def get_certified(self):
        return self.__certified
    def update_certified(self):
        self.__certified = True
    def __str__(self):
        return 'user_id:{} \n occupation:{} from:{} to:{} \n college:{} from {} \n major: {} year:{} \n cert file:{} \n dob:{} nric:{} \n certified? {}'.format(
            self.user_id,self.occupation,self.fromyear,self.toyear,self.college_name,self.college_country,self.major,self.year,self.certificate,self.dob,self.nric,self.__certified)

#our Tutor class inherites pending tutor class, so i dont need to initialize everything again
class Tutor(PendingTutor):
    def __init__(self, pending_tutor_object):
        super().__init__(pending_tutor_object.user_id, pending_tutor_object.occupation, pending_tutor_object.fromyear, pending_tutor_object.toyear, pending_tutor_object.college_country, pending_tutor_object.college_name, pending_tutor_object.major, pending_tutor_object.year ,pending_tutor_object.dob, pending_tutor_object.nric)
        self.__certified = True
        self.reviews = {}
        self.subjects = []
        self.courses = []

class Courses():
    def __init__(self,course_title,category,subcategory,description,tutor,short_description):
        self.course_id = uuid.uuid4().hex
        self.course_title = course_title
        self.category = category
        self.subcategory = subcategory
        self.short_description = short_description
        self.description =description
        #tutor id/ userid
        self.tutor = tutor
        self.course_thumbnail = "default.jpg"
        self.sessions = [Session()]
        self.hourlyrate = 0
        self.maximumdays = 0
        self.maximumhoursperssion = 0
        self.minimumdays = 0
    def __str__(self):
        return 'Course ID:{} \n Course Title:{} \n Category:{} Subcategory: {} \n ' \
               'Description:{} \n Tutor ID: {} ' \
               '\n Course Filename: {} '.format(self.course_id,self.course_title,self.category,self.subcategory,self.description,self.tutor,self.course_thumbnail)
def put_default_session(course_object):
    s1 = Session()
    course_object.sessions.append(s1)

class Session():

    def __init__(self):
        self.session_no = 1
        self.session_title = 'Introductory Session'
        self.session_description = "blah blah blah"
        self.session_materials = []
        self.time_approx = 4
    def __str__(self):
        return '++++++++++++++++++++++++++++\n' \
               ' Session No: {} \n Title:{} \n Description: {} \n time: {}'.format(self.session_no,self.session_title,self.session_description,self.time_approx)
