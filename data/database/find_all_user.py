import sqlite3

#path accords with the .bat file with invokes this .py file
print(sqlite3.connect('./data/database/ji_ke_pan.db').cursor().execute('select * from students').fetchall())