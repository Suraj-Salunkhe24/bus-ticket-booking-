import sqlite3

con=sqlite3.connect("passenger.db")
cur=con.cursor()
# cur.execute("""  CREATE TABLE IF NOT EXISTS passenger_data (id INTEGER PRIMARY KEY AUTOINCREMENT ,From_Location VARCHAR(50),To_Location VARCHAR(50), Departure TEXT,Arrival TEXT )""")


# cur.execute(""" CREATE TABLE travels_info (
#          id INTEGER PRIMARY KEY AUTOINCREMENT,
#         "Travels Name" TEXT,
#         "Vehicle Number" TEXT,
#         "Front Image" TEXT,
#         "Inside Image" TEXT,
#         "Available_Scats" INTEGER,
#         From_Location TEXT,
#         To_Location TEXT,
#         Amount INTEGER
#     )
# """)

cur.execute("create table user_information(id INTEGER PRIMARY KEY AUTOINCREMENT , name text,  mobile_no int , email text)")
# cur.execute("drop table passenger_data")
# cur.execute(" DELETE FROM user_information")
con.commit()
con.close()