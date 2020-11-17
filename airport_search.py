import pandas as pd
import folium
from geopy import ArcGIS, distance


class Airports():

    """From an Address and radius (default 40km) creates Object containing 
    coordinates of Address, specified radius around address in kms,
    and database with info on all airports within that radius"""

    def __init__(self, location, radius=40):
        if pd.DataFrame([[location]])[0].apply(ArcGIS().geocode)[0] != None:
            airport_database = pd.read_csv("airports.csv", header=None, usecols=[0,1,2,3,4,5,6,7])
            airport_database.columns = ["ID", "Airport", "City", "Country","IATA","ICAO", "Latitude", "Longitude"]
            airport_database["Coordinates"] = airport_database.apply(lambda x: (x["Latitude"],x["Longitude"]), axis=1)

            #self.location is the tuple (lon,lat)
            self.location = pd.DataFrame([[location]])[0].apply(ArcGIS().geocode)[0].point[0:2]
            self.radius = radius
            airport_database["<xks"] = airport_database.apply(lambda x: within_x_kms(x["Coordinates"], self.location, radius), axis=1)
            self.database = airport_database[airport_database.loc[:,"<xks"]]
        
        else:
            self.location = None
            self.radius = None
            self.database = None
        
def within_x_kms(p1,p2, x):
    return distance.distance(p1,p2) < x