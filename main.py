from airport_search import Airports
from airport_mapping import AirportMap

dAddress = "Toronto"
aAddress = "New York"
kms = 80

dAirports = Airports(dAddress, kms)
aAirports = Airports(aAddress, kms)

a = AirportMap(dAirports, aAirports)