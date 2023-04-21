#SI206 Final Project
#Team Name: Emma and Sibora's Park Analysis
#Team members: Emma Moore and Sibora Berisha 
import sqlite3
import requests
import json 
import os
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd 
import matplotlib.pyplot as plt 
from wordcloud import WordCloud
#opening a database

#Function one: Create a databse to store the park api info 
def set_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    curr = conn.cursor()
    return curr, conn
#This function creates a table with zipcodes from the library api and gives them an id 
def create_zips(curr, conn): 
    curr.execute("CREATE TABLE IF NOT EXISTS zipcodes (zipcode_id INTEGER PRIMARY KEY, zipcode INTEGER)")
    conn.commit()

def zip_table(curr, conn):
    # fetch zipcodes from API 1
    libraries = requests.get("https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Public_Library_Facilities/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json")
    zipcodesl = libraries.json()
    l_lst = []
   
    for item in zipcodesl["features"]: 
        zipcode = item["attributes"]["Zip_Code"]
        l_lst.append(zipcode)
    # fetch zipcodes from API 2: parks 
    parks = requests.get("https://maps.lacity.org/lahub/rest/services/Recreation_and_Parks_Department/MapServer/4/query?outFields=*&where=1%3D1&f=geojson")
    zipcodesp = parks.json()
    p_lst = []
    for item in zipcodesp["features"]: 
        zipcode = item["properties"]["ZIP"]
        p_lst.append(zipcode)
    #make a lst with both zipcode lists
    zip_lst = p_lst + l_lst
    # create a dictionary to keep track of existing zipcodes and their ids
    zip_dict = {}
    # add each unique zipcode to the zipcodes table
    for zipcode in zip_lst:
        if zipcode in zip_dict:
            # zipcode already exists, retrieve its id
            zipcode_id = zip_dict[zipcode]
        else:
            # zipcode is new, assign a new id and add to dictionary
            zipcode_id = len(zip_dict) + 1
            zip_dict[zipcode] = zipcode_id
            # insert the zipcode and its id into the zipcodes table
        curr.execute("INSERT OR IGNORE INTO zipcodes (zipcode_id, zipcode) VALUES (?,?)", (zipcode_id, zipcode))
    #print(zip_dict)
    conn.commit()

#Function 2: creates empty park table 
def create_table(curr, conn): 
    curr.execute("CREATE TABLE IF NOT EXISTS parks (park_id INTEGER PRIMARY KEY, park_name TEXT, zipcode_id INTEGER, park_type TEXT, amenities TEXT, FOREIGN KEY (zipcode_id) REFERENCES zipcodes(zipcode_id))")
    conn.commit()
#Function 3: calls api and extracts info, adds to the table 25 items at a time 
def update_table(curr, conn, add): 
    start = 0 + add 
    limit = 25 + add
    park_response = requests.get( "https://maps.lacity.org/lahub/rest/services/Recreation_and_Parks_Department/MapServer/4/query?outFields=*&where=1%3D1&f=geojson")
    items = park_response.json()
    # iterate through the park info and add to dictionary
    for item in items["features"][start:limit]: 
        park_id = item["properties"]["OBJECTID_1"]
        park_name = item["properties"]["FACNAME_1"]
        zipcode = item["properties"]["ZIP"]
        park_type = item["properties"]["CATEGORY"]
        amenities = item["properties"]["DESCRIP"]
        # get the corresponding zipcode_id from the 'zipcodes' table
        zip_id = int(curr.execute("SELECT zipcode_id FROM zipcodes WHERE CAST(zipcode AS INTEGER) = ?", (zipcode,)).fetchone()[0])
        print(zip_id)
        #print(zip_id)
        # insert the park record into the 'parks' table
        curr.execute("INSERT OR IGNORE INTO parks (park_id, park_name, zipcode_id, park_type, amenities) VALUES (?, ?, ?, ?, ?)", (park_id, park_name, zip_id, park_type, amenities))
    conn.commit() 

#Function 4: creates the empty library table 
def library_table(curr, conn):
   curr.execute("CREATE TABLE IF NOT EXISTS library (library_id INTEGER PRIMARY KEY, libraryname TEXT,  zipcode_id INTEGER)")
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
       zipcode = item["attributes"]["Zip_Code"]
       zip_id = int(curr.execute("SELECT zipcode_id FROM zipcodes WHERE CAST(zipcode AS INTEGER) = ?", (zipcode,)).fetchone()[0])
       curr.execute("""INSERT OR IGNORE INTO library (library_id, libraryname, zipcode_id) VALUES (?, ?, ?)""", (library_id, library_name, zip_id))
   conn.commit()
#top 10 graphs
def join_vis(db): 
    conn = sqlite3.connect(db)
    curr = conn.cursor()
    curr.execute("SELECT zipcodes.zipcode, COUNT(DISTINCT parks.park_id) + COUNT(DISTINCT library.library_id) AS total_count FROM zipcodes LEFT JOIN parks ON zipcodes.zipcode_id = parks.zipcode_id LEFT JOIN library ON zipcodes.zipcode_id = library.zipcode_id GROUP BY zipcodes.zipcode ORDER BY total_count DESC LIMIT 10")
    results = curr.fetchall() 
    zipcodes = [result[0] for result in results]
    total_counts = [result[1] for result in results]
# Create bar chart
    plt.bar(zipcodes, total_counts, width = 0.9)
    plt.xticks(zipcodes, rotation=90)
    plt.title('Top 10 Zipcodes by Total Parks and Libraries')
    plt.xlabel('Zipcode')
    plt.ylabel('Total Parks and Libraries')
    plt.show()
# Close database connection
    conn.close()

def count_type(parksdb): 
    #I want to calculate the percent of parks that that are each type, then I can create a pie chart with that 
    #this is in the type column of the park_table 
    conn = sqlite3.connect(parksdb)
    curr = conn.cursor()
    #query = curr.execute("SELECT type FROM park_table")
    #types = curr.fetchall()
    rquery = curr.execute("SELECT park_type FROM parks WHERE park_type = 'Recreational Centers'")
    rec_centers = curr.fetchall()
    pquery = curr.execute("SELECT park_type FROM parks WHERE park_type = 'Parks'")
    parks = curr.fetchall()
    aquery = curr.execute("SELECT park_type FROM parks WHERE park_type = 'Aquatics'")
    aquatics = curr.fetchall()
    squery = curr.execute("SELECT park_type FROM parks WHERE park_type = 'Sport Facilities'")
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
        fileout.write(f" The number of parks that are {list(type_dct.keys())[0]} is {list(type_dct.values())[0]}, the number of parks that are {list(type_dct.keys())[1]} is {list(type_dct.values())[1]}, the number of parks that are {list(type_dct.keys())[2]} is {list(type_dct.values())[2]}, the number of parks that are {list(type_dct.keys())[3]} is {list(type_dct.values())[3]}\n")
        fileout.close()

#This function creates a pie chart with the percent of parks that are each type 
def type_graph(count_dct):  
    dlabels = list(count_dct.keys())
    counts = list(count_dct.values())
    fig = go.Figure(data=[go.Pie(labels= dlabels, values= counts)])
    fig.update_layout(title="Percent of total parks as each type")
    fig.show()
#creates a word cloud with the amentity names 
def amen_cloud(parksdb): 
    conn = sqlite3.connect(parksdb)
    curr = conn.cursor()
    # Retrieve all data from all tables in the database
    table = "parks"
    column = "amenities"

    # Read the data into a DataFrame
    query = f'SELECT {column} FROM {table}'
    df = pd.read_sql_query(query, conn)

    # Select the column of interest
    text = df[column].to_string(index=False)

    # Create a word cloud object
    wordcloud = WordCloud(width=800, height=800, background_color='white', colormap='inferno', stopwords=None).generate(text)

    # Plot the word cloud
    plt.figure(figsize=(8,8))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()

    # Close the database connection

def main():
    curr,conn = set_database("parks.db")
    create_zips(curr, conn)
    curr.execute('SELECT COUNT ("zipcode_id") FROM zipcodes')
    conn.commit() 
    zips = curr.fetchall()
    count = zips[0][0]
    zip_table(curr, conn) 
    
    """if count < 25: 
        zip_table(curr, conn, 0)
    elif 25 <= count < 50: 
        zip_table(curr, conn, 25)
    elif 50 <= count < 75: 
        zip_table(curr, conn, 50)
    elif 75 <= count < 100: 
        zip_table(curr, conn, 75)
    elif 100 <= count < 125: 
        zip_table(curr, conn, 100)
    elif 125 <= count <150: 
        zip_table(curr, conn, 125)"""

    create_table(curr, conn)
    curr.execute('SELECT COUNT("park_id") FROM parks')
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

#call the count types function 
    typedct = count_type("parks.db")
    #print(typedct)
#call the function that creates a graph with counts of each type of park 
    type_graph(typedct)
#call the function that writes the results to a file 
    write_type("typefile", typedct)
#call the amentities function 
    amen_cloud("parks.db")
    #call count graph 
    join_vis("parks.db")

if __name__ == "__main__":
    main()