#SI206 Final Project
#Team Name: Emma and Sibora's Park Analysis
#Team members: Emma Moore and Sibora Berisha 
import sqlite3
import requests
import json 
import os

#opening a database

#Function one: Create a databse to store the park api info 
def set_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    curr = conn.cursor()
    return curr, conn
def create_table(curr, conn): 
    #create a table for parks
    curr.execute("CREATE TABLE IF NOT EXISTS park_table (id INTEGER PRIMARY KEY, parkname TEXT, zipcode INTEGER, city TEXT, region TEXT, type TEXT, amentities TEXT)")
    conn.commit()

def update_table(curr, conn, add): 
    start = 0 + add 
    limit = 25 + add
    park_response = requests.get( "https://maps.lacity.org/lahub/rest/services/Recreation_and_Parks_Department/MapServer/4/query?outFields=*&where=1%3D1&f=geojson")
    items = park_response.json()
    #iterate through the park info and add to dictionary
    for item in items["features"][start:limit]: 
        park_id = item["properties"]["OBJECTID_1"]
         #print(park_id)
        park_name = item["properties"]["FACNAME_1"]
        #print(park_name)
        zipcode = item["properties"]["ZIP"]
        city = item["properties"]["CITY"]
        region = item["properties"]["REGNAME"]
        type  = item["properties"]["CATEGORY"]
        amentities = item["properties"]["DESCRIP"]
        curr.execute("""INSERT OR IGNORE INTO park_table (id, parkname, zipcode, city, region, type, amentities) VALUES (?, ?, ?, ?, ?, ?, ?)""", (park_id, park_name, zipcode, city, region, type, amentities))
    conn.commit()


def main():
    curr,conn = set_database("parks.db")
    create_table(curr, conn)
    curr.execute('SELECT COUNT("park_id") FROM park_table')
    conn.commit()
    data = curr.fetchall()
    length = data[0][0]

    if length < 25: 
        update_table(curr, conn, 0)
    elif 25 <= length < 50: 
        update_table(curr, conn, 25)
    elif 50 <= length < 75: 
        update_table(curr, conn, 50)
    elif 75 <= length < 100: 
        update_table(curr, conn, 75)
    elif 100 <= length < 125: 
        update_table(curr, conn, 100)
    elif 125 <= length <150: 
        update_table(curr, conn, 125)


    
if __name__ == "__main__":
    main()
    