import pandas as pd
import folium
from geopy import ArcGIS, distance
from airport_search import Airports
from routes import Routes
import math
from geographiclib import geodesic


class AirportMap():
    
    """Takes one or two Airport objects, Creates a folium map that, 
        if one Airport object is entered, maps the airports within 
        the Airport Object's radius and, 
        if two Airport objects are entered, maps both Airport Objects 
        and the routes between them in Great Circles"""

    def __init__(self, departure_Airports, arrival_Airports=None):
        
        figure = folium.Figure(width=1000,height=500)
        
        if arrival_Airports != None and arrival_Airports.location != None and departure_Airports.location != None:
            
            #Collects all airports around departure and arrival locations
            allAirportsDataframe = departure_Airports.database.append(arrival_Airports.database)

            #Midpoint between longs and lats of the two Airport.locations, used to center the map
            midpoint = (round(((departure_Airports.location[0]+arrival_Airports.location[0])/2), 5), round(((departure_Airports.location[1]+arrival_Airports.location[1])/2),5))
            
            #Find distance between airports, use this to calc initial zoom
            distance1 = distance.distance(departure_Airports.location, arrival_Airports.location) 
            zoom = calc_zoom(distance1)


            #Begin building map
            mappy = folium.Map(location = midpoint, tiles="Stamen Terrain", 
                            zoom_start=zoom, min_zoom=2).add_to(figure)

            fga = folium.FeatureGroup(name="Airports")
            location = folium.FeatureGroup(name="Your Location")
            fgroutes = folium.FeatureGroup(name="Routes")

            #Fill out Airport feature group with labels
            for latitude, longitude, name, city, country in zip(allAirportsDataframe["Latitude"],allAirportsDataframe["Longitude"],allAirportsDataframe["Airport"],
                                                                allAirportsDataframe["City"],allAirportsDataframe["Country"]):

                if isinstance(city, float):
                    city = "None"
                else:
                    pass

                if isinstance(name, float):
                    city = "None"
                else:
                    pass

                if isinstance(country, float):
                    city = "None"
                else:
                    pass

                tooltip1 = "Airport: "+ name + "  City: " + city + "  Country: " + country

                fga.add_child(folium.CircleMarker(location=[latitude,longitude], radius=4,
                                                tooltip=tooltip1))


            #Add Routes
            routes = Routes(departure_Airports, arrival_Airports)
            if(routes.routedataframe.empty == False):
                self.routedataframe = routes.routedataframe[['Airline', 'Airline ID', 'Source airport','Destination airport','Stops']]
                
                #Create the great circles of the routes
                routes.routedataframe["Arcline Lists"] = routes.routedataframe.apply(lambda x: get_points(x["Departure Coordinates"], x["Arrival Coordinates"]), axis=1)
                routes.routedataframe["Arcline Lists"].apply(lambda x: fgroutes.add_child(folium.PolyLine(x, weight=1, color="maroon")))
            
            else:
                self.routedataframe = pd.DataFrame(columns = ['Airline', 'Airline ID', 'Source airport','Destination airport','Stops'])

            #Add departure and arrival locations
            location.add_child(folium.Marker(location=departure_Airports.location, tooltip="Your Address", 
                                            icon=folium.Icon(icon="f267", prefix="fa")))
            location.add_child(folium.Marker(location=arrival_Airports.location, tooltip="Your Destination", 
                                            icon=folium.Icon(icon="f267", prefix="fa")))

            #Draw specified radii around departure and arrival locations
            folium.Circle(departure_Airports.location, radius=departure_Airports.radius*1000, color="green", weight=2, fill=True).add_to(mappy)
            folium.Circle(arrival_Airports.location, radius=arrival_Airports.radius*1000, color="red", weight=2, fill=True).add_to(mappy)
            
            #Add Feature Groups to Map
            mappy.add_child(fga)
            mappy.add_child(location)
            mappy.add_child(fgroutes)

            mappy.add_child(folium.LayerControl())

            mappy.save("map.html")

            self.map = mappy

        elif departure_Airports != None and departure_Airports.location != None:

            self.routedataframe = None
            zoom = calc_zoom(departure_Airports.radius)
            figure = folium.Figure(width=1000,height=500)
            mappy = folium.Map(location = departure_Airports.location, tiles="Stamen Terrain", 
                            zoom_start=zoom, min_zoom=2).add_to(figure)

            fga = folium.FeatureGroup(name="Airports")
            location = folium.FeatureGroup(name="Your Location")

            for latitude, longitude, name, city, country in zip(departure_Airports.database["Latitude"],departure_Airports.database["Longitude"],departure_Airports.database["Airport"],
                                                                departure_Airports.database["City"],departure_Airports.database["Country"]):

                if isinstance(city, float):
                    city = "None"
                else:
                    pass

                if isinstance(name, float):
                    city = "None"
                else:
                    pass

                if isinstance(country, float):
                    city = "None"
                else:
                    pass

                tooltip1 = "Airport: "+ name + "  City: " + city + "  Country: " + country

                fga.add_child(folium.CircleMarker(location=[latitude,longitude], radius=4,
                                                tooltip=tooltip1))

            location.add_child(folium.Marker(location=departure_Airports.location, tooltip="Your Address", 
                                            icon=folium.Icon(icon="f267", prefix="fa")))

            folium.Circle(departure_Airports.location, radius=departure_Airports.radius*1000, color="green", weight=2, fill=True).add_to(mappy)
            mappy.add_child(fga)
            mappy.add_child(location)

            mappy.add_child(folium.LayerControl())

            mappy.save("map.html")
            self.map=mappy
            

        else:
            self.routedataframe = None
            self.map = None
            print("No Such Address")

#Used to find the right zoom for the map based on selected radius
def calc_zoom(radius):
    zooms = [27.5*(2**num) for num in range(0,10)]
    for zoom in zooms:
        if radius > 12000:
            return 0
        
        elif radius<zoom+(zoom/4):
            return 11-zooms.index(zoom)
        else:
            pass

#Get points on geodesic between two points
def get_points(dCoord, aCoord):
    
    #Variables for earth geode
    flattening = 1/298.257223563
    equ_rad = 6371000
    earth = geodesic.Geodesic(equ_rad,flattening)

    #Make Arcline object between coordinates
    geo_line = earth.InverseLine(dCoord[0], dCoord[1], aCoord[0], aCoord[1])

    #Build the list, point every 10kms along Arcline
    r = range(0, round(geo_line.s13), 10000)
    arcline_list = []
    for i in r:
        arcline_list.append(get_points_helper(geo_line, i))
    arcline_list.append(get_points_helper(geo_line, geo_line.s13))

    return arcline_list

#Returns tuple of long and lat from Geodesic Library
def get_points_helper(geo_line, dist):
    lat = geo_line.Position(dist)["lat2"]
    lon = geo_line.Position(dist)["lon2"]
    return (lat,lon)