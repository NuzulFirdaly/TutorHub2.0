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
        self.__user_recent = []

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

    def get_user_recent(self):
        return self.__user_recent

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

    def set_user_recent(self, recent):
        self.__user_recent = recent

    def __str__(self):
        return ' user_id:{} \n username: {} \n email: {} \n password:{} \n firstname:{} \n lastname:{} \n fullname:{} \n languages:{} \n description:{} '.format(
            self.get_user_id(),self.get_username(), self.get_user_email(), self.get_user_pw(), self.get_user_firstname(),
            self.get_user_lastname(), self.get_user_fullname(),
            self.get_user_language(), self.get_user_description())

    def __eq__(self, other):
        return self.__user_id == other.get_user_id()

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
    def __str__(self):
        return 'user_id:{} \n occupation:{} from:{} to:{} \n college:{} from {} \n major: {} year:{} \n cert file:{} \n dob:{} nric:{} \n certified? {}'.format(
            self.user_id, self.occupation, self.fromyear, self.toyear, self.college_name, self.college_country,
            self.major, self.year, self.certificate, self.dob, self.nric, self.__certified)

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
        self.hourlyrate = 1
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
#reminder for myself: documents thingy submit
class PendingInstitution():
    def __init__(self, institution_name, institution_address, postal_code, institution_email, website, office_no, admin_firstname, admin_lastname, admin_contact, admin_email, license):
        self.institution_name = institution_name
        self.institution_address = institution_address
        self.postal_code = postal_code
        self.institution_email = institution_email
        self.website = website
        self.office_no = office_no
        self.__admin_firstname = admin_firstname
        self.__admin_lastname = admin_lastname
        self.__admin_contact = admin_contact
        self.__admin_email = admin_email
        self.__license = license
        self.__approved = False

    def set_institution_name(self, institution_name):
        self.institution_name = institution_name
    def set_institution_address(self, institution_address):
        self.institution_address = institution_address
    def set_institution_email(self, institution_email):
        self.institution_email = institution_email
    def set_website(self, website):
        self.website = website
    def set_office_no(self, office_no):
        self.office_no = office_no
    def set_admin_firstname(self, admin_firstname):
        self.__admin_firstname = admin_firstname
    def set_admin_lastname(self, admin_lastname):
        self.__admin_lastname = admin_lastname
    def set_admin_email(self, admin_email):
        self.__admin_email = admin_email
    def set_license(self, license):
        self.license = license
    def set_admin_contact(self, admin_contact):
        self.__admin_contact = admin_contact
    def set_postal_code(self, postal_code):
        self.postal_code = postal_code

    def get_postal_code(self):
        return self.postal_code
    def get_institution_name(self):
        return self.institution_name
    def get_institution_address(self):
        return self.institution_address
    def get_instituion_email(self):
        return self.institution_email
    def get_website(self):
        return self.website
    def get_office_no(self):
        return self.office_no
    def get_admin_firstname(self):
        return self.__admin_firstname
    def get_admin_lastname(self):
        return self.__admin_lastname
    def get_admin_email(self):
        return self.__admin_email
    def get_license(self):
        return self.__license
    def get_admin_contact(self):
        return self.__admin_contact

    def get_approved(self):
        return self.__approved
    def update_approved(self):
        self.__approved = True

class Institution(PendingInstitution):
    def __init__(self, PendingInstitutionObj):
        super().__init__(PendingInstitutionObj.institution_name, PendingInstitutionObj.institution_address, PendingInstitutionObj.postal_code, PendingInstitutionObj.institution_email, PendingInstitutionObj.website, PendingInstitutionObj.office_no, PendingInstitutionObj.get_admin_firstname(), PendingInstitutionObj.get_admin_lastname(), PendingInstitutionObj.get_admin_contact(), PendingInstitutionObj.get_admin_email(), PendingInstitutionObj.get_license())
        self.__banner = ['1.jpg']
        self.__sm = ['2.jpg']

    def get_banner(self):
        return self.__banner
    def set_banner(self, banner):
        self.__banner = banner

    def get_sm(self):
        return self.__sm
    def set_sm(self, sm):
        self.__sm = sm