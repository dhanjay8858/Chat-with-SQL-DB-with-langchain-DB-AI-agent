import sqlite3

connection=sqlite3.connect("student.db")

cursor=connection.cursor()

table_info=''' CREATE TABLE STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT)
'''

cursor.execute(table_info)

cursor.execute(''' INSERT INTO STUDENT VALUES ('AMIT','Data Science','C',98)''')
cursor.execute(''' INSERT INTO STUDENT VALUES ('RAM','Data Analytic','A',92)''')
cursor.execute(''' INSERT INTO STUDENT VALUES ('SUMIT','Computer Science','B',96)''')
cursor.execute(''' INSERT INTO STUDENT VALUES ('AMAN','AI','A',88)''')
cursor.execute(''' INSERT INTO STUDENT VALUES ('KAMAl','GENAI','C',68)''')
cursor.execute(''' INSERT INTO STUDENT VALUES ('ANSHU','ML','B',99)''')

print("The inserted Record are :")

data=cursor.execute('''SELECT * FROM STUDENT''')

for row in data:
    print(row)


connection.commit()

connection.close()