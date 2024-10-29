print("Imports")
from typing import List
import pandas as pd #type: ignore
import random

import const
from src.Metrics import Metrics
from src.station import Station
from src.satellite import Satellite
from src.iotDevice import IotDevice
from src.recieveGS import RecieveGS
from src.utils import Print, Time, Location
from src.iotSatellite import IoTSatellite
from src.routing import Routing
from src.links import Link
from src.simulator import Simulator
from src.iotSatellite import IoTSatellite
from src.planetSatellite import PlanetSatellite
from src.imageSamplingSatellite import ImageSamplingSatellite
from src.image import Image
from matplotlib.patches import Polygon
from src.filter_graph import FilterGraph, Filter
import src.log as log
print("Starting to run code")
if __name__ == "__main__":
    im = Image(100, 
               Polygon([(41.85, -87.85), (41.85, -87.85), (41.85, -87.85)]), 
               Time().from_str("2022-07-10 12:00:00"), 
               filter_result={"filter_1": [1, 5], "filter_2": [1, 5], "filter_3": [1, 5], "filter_4": [1, 5], "filter_5": [1, 5], "filter_6": [1, 5]},
               name="test")
    stations = pd.read_json("referenceData/stations.json")

    groundStations: 'List[Station]' = []
    cnt = 0
    for id, row in stations.iterrows():
        ##Randomly assign gs, make 1/4 recieve only, 3/4 transmit only
        num = random.random()
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        if num < .25:
            groundStations.append(RecieveGS(s))
        else:
            cnt += 1
            groundStations.append(IotDevice(s, row["location"][0], row["location"][1]))

    print("number of stations:" , len(stations))

    california_polygon = Polygon([
        (41.8, -124.0),  # Northwest Point near Crescent City
        (41.9, -120.0),  # Northeast Point near Alturas
        (34.8, -114.6),  # Southeast Point near Needles
        (32.5, -117.1),  # Southwest Point near San Diego
        (36.6, -121.9)   # Central Coastal Point near Monterey
    ])

    const.LOGGING_FILE = "log0.txt"

    satellites = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [ImageSamplingSatellite(i, targets=[california_polygon]) for i in satellites]
    print("number of satellites:", len(satellites))

    startTime = Time().from_str("2022-07-15 13:00:00")
    endTime = Time().from_str("2022-07-15 23:00:00")


    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    filterGraph = FilterGraph(application_list=[['filter_1', 'filter_2', 'filter_3'],  # First list of filters
    ['filter_4', 'filter_5'],              # Second list of filters
    ['filter_6']])

    for filter in ['filter_1', 'filter_2', 'filter_3', 'filter_4', 'filter_5', 'filter_6']:
        Filter.build_filter(filter, runtime=1)
    #sim.load_topology("top.txt") ##You can compute these topology maps once, save them, and load them instead of computing them every runtime
    #sim.calculate_topologys()  ##To precomute the topology maps. If they aren't precomuted, it will happen at runtime
    #sim.save_topology("top.txt") ##You can save these for any of the topologyLogging - take a look in the folder 
    Metrics.metr()
    sim.run()
    Metrics.metr().print()
    Metrics.metr().image_logger.pretty_save("images.txt")

    with open("log_15.txt", "w") as f:
        for satellite in satellites:
            f.write(str(satellite) + "\n")
            f.write("\n")
            f.write("mem%, time-cache, pow, len-data, len-low, len-med, len-hi, num-proc\n")
            for analytic in satellite.analytics:
                f.write(str(analytic) + "\n")
    with open("log_16.txt", "w") as f:
        analytics = Metrics.metr().image_logger.create_analytics()
        for sat, data in analytics.items():
            f.write(str(sat) + "\n")
            f.write(str(data))
            f.write("\n")
    
    Metrics.metr().image_logger.save("images.pkl")
    ## sim.save_objects(".tmp") ## this will pickle and load all the objects until needed again
    ## sim.load_objects(".tmp") ## this will load all the objects that were pickled ##
    