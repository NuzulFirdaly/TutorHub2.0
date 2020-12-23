import shelve
try:
    shelve.open('databases/user.db','c')
except IOError:
    print("Error opening user.db")