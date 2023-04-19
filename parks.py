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
def library_table(curr, conn):
   curr.execute("CREATE TABLE IF NOT EXISTS library (library_id INTEGER PRIMARY KEY, libraryname TEXT,  zipcode INTEGER)")
   conn.commit()
   #created the library table but have not filled it yet
def fill_library(curr, conn, add):
   start = 0 + add
   limit = 25 + add
   library_response = requests.get("https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Public_Library_Facilities/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json")
   items = library_response.json()
   #iterate through the park info and add to dictionary
   for item in items["features"][start:limit]:
       library_id = item["attributes"]["ObjectId"]
       #print(library_id)
       library_name = item["attributes"]["Library_Name"]
       #city = item["attributes"]["City"]
       zipcode = item["attributes"]["Zip_Code"]
       #year = item["attributes"]["Year_Built"]
       curr.execute("""INSERT OR IGNORE INTO library (library_id, libraryname, zipcode) VALUES (?, ?, ?)""", (library_id, library_name, zipcode))
   conn.commit()

#create a statement to join the tables where the zipcodes are equal  
# maybe I also need to create a table that for each zip code has the number of parks and libraries, that would be good to turn into a visualisation as well 
def sum_parks(parks): 
    #calauclate the total amounts of park in each zip code
    conn = sqlite3.connect(parks)
    curr = conn.cursor()
    #exexute the query to get zipcode data and count from parks table 
    curr.execute("SELECT zipcode, COUNT(*) FROM park_table GROUP BY zipcode")
    info = curr.fetchall()
    #create a dictionary to store the counts for each zip code 
    counts = {}
    for park in info: 
        zipcode = park[0]
        count = park[1]
        counts[zipcode] = count 
    conn.close()
    print(counts)
    return counts
#now get the counts of each library in the park 
def library_counts(parks): 
    conn = sqlite3.connect(parks)
    curr = conn.cursor()
    #exexute the query to get zipcode data and count from parks table 
    curr.execute("SELECT zipcode, COUNT(*) FROM library GROUP BY zipcode")
    info = curr.fetchall()
    #create a dictionary to store the counts for each zip code 
    counts = {}
    for library in info: 
        zipcode = library[0]
        count = library[1]
        counts[zipcode] = count 
    conn.close()
    print(counts)
    return counts

def zip_table(curr, conn):
    pass 
    #I want this table to have two columns, zipcode id and then the zipcode that goes with this id. 
    # Eventually I believe the join table will have zipcode id as primary key, number of parks in that zipcode, and number of libraries 
    # (maybe I make this my calculation)

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
#call the libary table and make sure it only adds 25 in at a time 
    library_table(curr, conn)
    curr.execute("SELECT COUNT(library_id) FROM library")
    conn.commit()
    linfo = curr.fetchall()
    length = linfo[0][0]
    if length < 25:
       fill_library(curr, conn, 0)
    elif 25 <= length < 50:
       fill_library(curr, conn, 25)
    elif 50 <= length < 75:
       fill_library(curr, conn, 50)
    elif 75 <= length < 100:
       fill_library(curr, conn, 75)
    elif 100 <= length < 125:
       fill_library(curr, conn, 100)
    elif 125 <= length <150:
       fill_library(curr, conn, 125)
#call the park counts by zipcode function 
    park_counts = sum_parks("parks.db")
#call the library counts by zipcode function  
    lib_counts = library_counts("parks.db")
    
    
if __name__ == "__main__":
    main()
    