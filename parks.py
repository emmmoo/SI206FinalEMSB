#SI206 Final Project
#Team Name: Emma and Sibora's Park Analysis
#Team members: Emma Moore and Sibora Berisha 
import sqlite3
import requests
import json 
import os
import plotly.graph_objs as go
import plotly.io as pio

#opening a database

#Function one: Create a databse to store the park api info 
def set_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    curr = conn.cursor()
    return curr, conn
#Function 2: creates empty park table 
def create_table(curr, conn): 
    curr.execute("CREATE TABLE IF NOT EXISTS park_table (id INTEGER PRIMARY KEY, parkname TEXT, zipcode INTEGER, city TEXT, region TEXT, type TEXT, amentities TEXT)")
    conn.commit()
#Function 3: calls api and extracts info, adds to the table 25 items at a time 
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
#Function 4: creates the empty library table 
def library_table(curr, conn):
   curr.execute("CREATE TABLE IF NOT EXISTS library (library_id INTEGER PRIMARY KEY, libraryname TEXT,  zipcode INTEGER)")
   conn.commit()
   #created the library table but have not filled it yet

#Function 5: calls library api and extracts info, adds to the table 25 items at a time 
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
    #print(counts)
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
    #print(counts)
    return counts

def zip_table(curr, conn):
    pass 
    #I want this table to have two columns, zipcode id and then the zipcode that goes with this id. 
    # Eventually I believe the join table will have zipcode id as primary key, number of parks in that zipcode, and number of libraries 
    # (maybe I make this my calculation)
def total_counts(pcounts, lcounts): 
    total = {}
    for zipcode in pcounts: 
        if zipcode in lcounts: 
            total[zipcode] = pcounts[zipcode] + lcounts[zipcode]
        else:
            total[zipcode] = pcounts[zipcode]
    for zipcode in lcounts: 
        if zipcode not in pcounts: 
            total[zipcode] = lcounts[zipcode]
    #print(total)
    return total
def count_graph(tcounts): 
    #make a bar chart of the library and park counts by zipcode 
    x = list(tcounts.keys())
    y = list(tcounts.values())

    fig = go.Figure(data=[go.Bar(x=x, y=y)])
    fig.update_layout(xaxis_title='Zipcode', yaxis_title='Count')
    
    pio.show(fig)
def count_type(parksdb): 
    #I want to calculate the percent of parks that that are each type, then I can create a pie chart with that 
    #this is in the type column of the park_table 
    conn = sqlite3.connect(parksdb)
    curr = conn.cursor()
    #query = curr.execute("SELECT type FROM park_table")
    #types = curr.fetchall()
    rquery = curr.execute("SELECT type FROM park_table WHERE type = 'Recreational Centers'")
    rec_centers = curr.fetchall()
    pquery = curr.execute("SELECT type FROM park_table WHERE type = 'Parks'")
    parks = curr.fetchall()
    aquery = curr.execute("SELECT type FROM park_table WHERE type = 'Aquatics'")
    aquatics = curr.fetchall()
    squery = curr.execute("SELECT type FROM park_table WHERE type = 'Sport Facilities'")
    sports = curr.fetchall()

    rec_count = len(rec_centers)
    park_count = len(parks) 
    aq_count = len(aquatics)
    sport_count = len(sports)

    type_count_dct = {"Recreational Centers": rec_count, "Parks": park_count, "Aquatic Facilities": aq_count, "Sport Facilities": sport_count}
    return type_count_dct
#create a function that write the park type and counts to a file
def write_type(filename, type_dct):
    with open(filename, "w", newline="") as fileout:
        fileout.write("Number of parks that are each type")
        fileout.write(f" The number of parks that are {type_dct.keys()[0]} is {type_dct.values()[0]}, the number of parks that are {type_dct.keys()[1]} is {type_dct.values()[1]}, the number of parks that are {type_dct.keys()[2]} is {type_dct.values()[2]}, the number of parks that are {type_dct.keys()[3]} is {type_dct.values()[3]}\n")
        fileout.close()
#This function creates a pie chart with the percent of parks that are each type 
def type_graph(count_dct):  
    dlabels = list(count_dct.keys())
    counts = list(count_dct.values())
    fig = go.Figure(data=[go.Pie(labels= dlabels, values= counts)])
    fig.show()

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

    total = total_counts(park_counts, lib_counts)
    #print(total)
#call the counts bar graph function 
    #count_graph(total)
#call the count types function 
    typedct = count_type("parks.db")
    #print(typedct)
#call the function that creates a graph with counts of each type of park 
    type_graph(typedct)
#call the function that writes the results to a file 
    write_type(typedct)

if __name__ == "__main__":
    main()
    