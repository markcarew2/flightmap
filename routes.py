import pandas as pd
from airport_search import Airports

class Routes():

    """From two Airports objects, creates a dataframe of all routes between
       all airports in that Airports object, also keeps the departure and 
       arrival locations as elements"""

    def __init__(self, departure_Airports, arrival_Airports):
        routes_dataframe = pd.read_csv("routes.csv")
        
        self.dLocation = departure_Airports.location
        self.aLocation = arrival_Airports.location

        routes_dataframe.loc[:,"Source airport ID"] = routes_dataframe.loc[:,"Source airport ID"].apply(lambda x: convert_to_int(x))
        routes_dataframe.loc[:,"Destination airport ID"] = routes_dataframe.loc[:,"Destination airport ID"].apply(lambda x: convert_to_int(x))

        routes_dataframe.loc[:,"Flyout"] = routes_dataframe.loc[:,"Source airport ID"].isin(departure_Airports.database.loc[:,"ID"])
        helpdataframe = routes_dataframe[routes_dataframe.loc[:,"Flyout"]].copy()
        
        #Check that there are routes leaving departure airports and going to arrival airports
        #if not, makes the routedataframe empty
        if(helpdataframe.size!=0):
            helpdataframe.loc[:,"Flyin"] = helpdataframe.loc[:,"Destination airport ID"].isin(arrival_Airports.database.loc[:,"ID"])
            self.routedataframe = helpdataframe[helpdataframe.loc[:,"Flyin"]].copy()

            if(self.routedataframe.size!=0):
                self.routedataframe.loc[:,"Departure Coordinates"] = self.routedataframe.loc[:,"Source airport ID"].apply(lambda x: extract_route_coordinates(departure_Airports.database, x))
                self.routedataframe.loc[:,"Arrival Coordinates"] = self.routedataframe.loc[:,"Destination airport ID"].apply(lambda x: extract_route_coordinates(arrival_Airports.database, x))
            
            else:
                self.routedataframe = pd.DataFrame()
        
        else:
            self.routedataframe = pd.DataFrame()

#To convert aiport ID to ints
def convert_to_int(x):
    if x!=r"\N":
        return int(x)
    else:
        return 0

#To help extract coordinates of airport to copy to relevant route
#This isolates the correct airport's coordinates
def extract_route_coordinates(airports, AirportID):
    airport = airports[airports.loc[:,"ID"] == AirportID].copy()
    return airport.iloc[-1,-2]
