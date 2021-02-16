#here we store all classes of the different users, easy access to make objects later
import uuid
import shelve
from passlib.hash import pbkdf2_sha256
import string
import random

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
        self.certificate = "avatar1.jpg"
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
        self.overallrating = 0
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
        self.reviews = {}
        self.overallrating = 0
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
    def __init__(self, institution_name, institution_address, postal_code, institution_email, website, office_no, license):
        self.institution_name = institution_name
        self.institution_address = institution_address
        self.postal_code = postal_code
        self.institution_email = institution_email
        self.website = website
        self.office_no = office_no
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
    def set_license(self, license):
        self.license = license

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
    def get_license(self):
        return self.__license

    def get_approved(self):
        return self.__approved
    def update_approved(self):
        self.__approved = True

class Institution(PendingInstitution):
    def __init__(self, PendingInstitutionObj):
        super().__init__(PendingInstitutionObj.institution_name, PendingInstitutionObj.institution_address, PendingInstitutionObj.postal_code, PendingInstitutionObj.institution_email, PendingInstitutionObj.website, PendingInstitutionObj.office_no, PendingInstitutionObj.get_license())
        self.__banner = ['1.jpg']
        self.__smurl = {'2.jpg':'https://www.nyp.edu.sg/'}
        self.__institutiontutor = {'2.jpg':'Mr Wilson'}
        self.__seminar = {'2.jpg':['EAE workshop','Hi just some random text lololol','https://www.nyp.edu.sg/']}


    def get_banner(self):
        return self.__banner
    def set_banner(self, banner):
        self.__banner = banner

    def get_smurl(self):
        return self.__smurl
    def set_smurl(self, smurl):
        self.__smurl = smurl

    def get_institutiontutor(self):
        return self.__institutiontutor
    def set_institutiontutor(self, institutiontutor):
        self.__institutiontutor = institutiontutor

    def get_seminar(self):
        return self.__seminar
    def set_seminar(self, seminar):
        self.__seminar = seminar

class Essentials():
    def __init__(self, name, price, picture):
        self.__name = name
        self.__price = price
        self.__picture = picture

    def get_name(self):
        return self.__name
    def set_name(self, name):
        self.__name = name

    def get_price(self):
        return self.__price
    def set_price(self, price):
        self.__price = price

    def get_picture(self):
        return self.__picture
    def set_picture(self, picture):
        self.__picture = picture

#for institution tutor
class InstituteTutor(PendingTutor):
    def __init__(self, pending_tutor_object, tutorinstitution):
        super().__init__(pending_tutor_object.occupation, pending_tutor_object.fromyear, pending_tutor_object.toyear, pending_tutor_object.college_country, pending_tutor_object.college_name, pending_tutor_object.major, pending_tutor_object.year ,pending_tutor_object.dob, pending_tutor_object.nric)
        self.__certified = True
        self.reviews = {}
        self.overallrating = 0
        self.subjects = []
        self.courses = []
        self.__tutorinstitution = tutorinstitution

    def set_tutorinstitution(self, tutorinstitution):
        self.__tutorinstitution = tutorinstitution
    def get_tutorinstitution(self):
        return self.__tutorinstitution

    def __str__(self):
        return 'user_id:{} \n occupation:{} from:{} to:{} \n college:{} from {} \n major: {} year:{} \n cert file:{} \n dob:{} nric:{} \n certified? {} \n institution: {}'.format(
            self.user_id, self.occupation, self.fromyear, self.toyear, self.college_name, self.college_country,
            self.major, self.year, self.certificate, self.dob, self.nric, self.__certified, self.__tutorinstitution)

class InstitutionAdmin():
    def __init__(self, admin_firstname, admin_lastname, admin_contact, admin_email, institution):
        self.__admin_id = uuid.uuid4().hex
        self.__admin_firstname = admin_firstname
        self.__admin_lastname = admin_lastname
        self.__admin_contact = admin_contact
        self.__admin_email = admin_email
        self.__institution = institution
        self.__password = self.passwordcreation()
        self.__username = self.__admin_firstname + self.__admin_lastname
        self.__profilepic = '1.jpg'

    def set_profilepic(self, profilepic):
        self.__profilepic = profilepic
    def get_profilepic(self):
        return self.__profilepic

    def set_username(self, username):
        self.__username = username

    def get_username(self):
        return self.__username

    def set_password(self, password):
        self.__password = password
    def get_password(self):
        return self.__password

    def set_admin_firstname(self, admin_firstname):
        self.__admin_firstname = admin_firstname

    def get_admin_firstname(self):
        return self.__admin_firstname

    def set_admin_lastname(self, admin_lastname):
        self.__admin_lastname = admin_lastname

    def get_admin_lastname(self):
        return self.__admin_lastname

    def set_admin_contact(self, admin_contact):
        self.__admin_contact = admin_contact

    def get_admin_contact(self):
        return self.__admin_contact

    def set_admin_email(self, admin_email):
        self.__admin_email = admin_email

    def get_admin_email(self):
        return self.__admin_email

    def set_institution(self, institution):
        self.__institution = institution

    def get_institution(self):
        return self.__institution

    def get_admin_id(self):
        return self.__admin_id

    def set_admin_id(self, admin_id):
        self.__admin_id = admin_id

    def passwordcreation(self):
        password = ''
        for i in range(11):
            password += random.choice(string.ascii_letters + string.digits)

        return password

class Essentials():
    def __init__(self, name, price, picture, user_id, username, userpic):
        self.__name = name
        self.__price = price
        self.__picture = picture
        self.__user_id = user_id
        self.__username = username
        self.__userpic = userpic

    def get_name(self):
        return self.__name
    def set_name(self, name):
        self.__name = name

    def get_price(self):
        return self.__price
    def set_price(self, price):
        self.__price = price

    def get_picture(self):
        return self.__picture
    def set_picture(self, picture):
        self.__picture = picture

    def get_user_id(self):
        return self.__user_id
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def get_username(self):
        return self.__username
    def set_username(self, username):
        self.__username = username

    def get_userpic(self):
        return self.__userpic
    def set_userpic(self, userpic):
        self.__userpic = userpic

class Admin():
    def __init__(self, admin_id, admin_dategenerated):
        self.__admin_id = admin_id
        self.__admin_email = ''
        self.__admin_username = ''
        self.__admin_password = ''
        self.__admin_firstname = ''
        self.__admin_lastname = ''
        self.__admin_role = 'Unassigned'
        self.__admin_department = ''
        self.__admin_profile_pic = "avatar3.jpg"
        self.__admin_dategenerated = admin_dategenerated
        self.__admin_datecreated = ''
        self.__admin_description = ''
        self.__admin_phonenumber = ''
        self.__admin_region = ''
        self.__admin_language = ''
        self.__admin_certificate = []

    def get_admin_id(self):
        return self.__admin_id

    def get_admin_email(self):
        return self.__admin_email

    def get_admin_username(self):
        return self.__admin_username

    def get_admin_password(self):
        return self.__admin_password

    def get_admin_firstname(self):
        return self.__admin_firstname

    def get_admin_lastname(self):
        return self.__admin_lastname

    def get_admin_fullname(self):
        return self.__admin_firstname + " " + self.__admin_lastname

    def get_admin_profile_pic(self):
        return self.__admin_profile_pic

    def get_admin_dategenerated(self):
        return self.__admin_dategenerated

    def get_admin_datecreated(self):
        return self.__admin_datecreated

    def get_admin_role(self):
        return self.__admin_role

    def get_admin_description(self):
        return self.__admin_description

    def get_admin_phonenumber(self):
        return self.__admin_phonenumber

    def get_admin_region(self):
        return self.__admin_region

    def get_admin_language(self):
        return self.__admin_language

    def get_admin_certificate(self):
        return self.__admin_certificate

    def get_admin_department(self):
        return self.__admin_department

    def set_admin_email(self, email):
        self.__admin_email = email

    def set_admin_username(self, username):
        self.__admin_username = username

    def set_admin_firstname(self, firstname):
        self.__admin_firstname = firstname

    def set_admin_lastname(self, lastname):
        self.__admin_lastname = lastname

    def set_admin_profile_pic(self, profile_pic):
        self.__admin_profile_pic = profile_pic

    def set_admin_password(self, password):
        self.__admin_password = password

    def set_admin_datecreated(self, datecreated):
        self.__admin_datecreated = datecreated

    def set_admin_role(self, role):
        self.__admin_role = role

    def set_admin_description(self, description):
        self.__admin_description = description

    def set_admin_phonenumber(self, phonenumber):
        self.__admin_phonenumber = phonenumber

    def set_admin_region(self, region):
        self.__admin_region = region

    def set_admin_language(self, language):
        self.__admin_language = language

    def set_admin_department(self, department):
        self.__admin_department = department

    def __str__(self):
        return ' admin_id:{} \n username: {} \n email: {} \n password:{} \n firstname:{} \n lastname:{} \n fullname:{} \n role:{} \n certificate:{}'.format(
            self.get_admin_id(), self.get_admin_username(), self.get_admin_email(), self.get_admin_password(),
            self.get_admin_firstname(),
            self.get_admin_lastname(), self.get_admin_fullname(), self.get_admin_role(), self.get_admin_certificate())

    def __eq__(self, other):
        return self.__admin_id == other.get_user_id()

    def add_admin_certificate(self, certificate):
        self.__admin_certificate.append(certificate)

    def remove_admin_certificate(self, certificate):
        self.__admin_certificate.pop(certificate)

    def get_admin(adminid):
        try:
            admindb = shelve.open('databases/admin.db', 'r')
        except IOError:
            print("Error opening user.db")
        except:
            print("Unknown error occurred fetching admin.db")
        else:
            if adminid in admindb.keys():
                admin = admindb.get(adminid)
                admindb.close()
                return admin
            else:
                print("AdminID not found in admin.db")


    def update_user(admin_obj):
        try:
            admindb = shelve.open('databases/admin.db', 'r')
        except IOError:
            print("Error opening user.db")
        except:
            print("Unknown error occurred fetching admin.db")
        else:
            if admin_obj.get_admin_id() in admindb.keys():
                admindb[admin_obj.get_admin_id()] = admin_obj
                admindb.close()
