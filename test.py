import shelve
try:
    db = shelve.open('databases/pendingtutor.db','c')
    for pendingtutors in db:
        print(db[pendingtutors])
except IOError:
    print("Error opening user.db")