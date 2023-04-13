#SI206 Final Project
#Team Name: Emma and Sibora's Park Analysis
#Team members: Emma Moore and Sibora Berisha 
import sqlite3
import requests
import json 


#Function one: Create a databse to store the park api info 
def create_db():
    conn = sqlite3.connect("park.db")
    print("Database created successfully")
    conn.close()

#Function two: acess data from the api and load it into the database 
def load_db(): 
    #make a request to the park api key to get data 
    park_response = requests.get("https://maps.lacity.org/lahub/rest/services/Recreation_and_Parks_Department/MapServer/4/query?outFields=*&where=1%3D1&f=geojson")
    
    #extract the park data from the request 
    park_data = park_response.text
    park_json = json.loads(park_data)
    #print(park_json)
    #Connect the api data to the database 
    conn = sqlite3.connect("park.db")
    #Create a cursor object to execute sql queries 
    cursor = conn.cursor()
#still need to make sure it only adds 25 items at a time with a total of at least 100 items 
#call the function 
    #Function part 3: create a table with some of the data from the api: 
    #first create the table 
    cursor.execute("CREATE TABLE IF NOT EXISTS park_table (id INTEGER PRIMARY KEY, parkname TEXT, zipcode INTEGER, city TEXT, region TEXT, type TEXT, amentities TEXT)")
    #second fill the table with selected park data 
    for park in park_json["features"]: 
        park_id = park["properties"]["OBJECTID_1"]
        #print(park_id)
        park_name = park["properties"]["FACNAME_1"]
        #print(park_name)
        zipcode = park["properties"]["ZIP"]
        city = park["properties"]["CITY"]
        region = park["properties"]["REGNAME"]
        type = park["properties"]["CATEGORY"]
        amentities = park["properties"]["DESCRIP"]
        cursor.execute("""INSERT OR IGNORE INTO park_table (id, parkname, zipcode, city, region, type, amentities) VALUES (?, ?, ?, ?, ?, ?, ?)""", (park_id, park_name, zipcode, city, region, type, amentities))
    conn.commit()
load_db()
