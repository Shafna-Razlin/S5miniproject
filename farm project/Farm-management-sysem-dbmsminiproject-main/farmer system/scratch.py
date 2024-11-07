import mysql.connector

connection = mysql.connector.connect(host="localhost" , user="root", password="", database="farmers")

if connection.is_connected():
    print('connected succesfully')

else:
    print('failed to connect')

connection.close()