print("Imports")
from typing import List
import pandas as pd #type: ignore
import random

import const
from src.Metrics import Metrics
from src.application import Application
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
from src.imageSamplingSatellite2 import ImageSamplingSatellite2
from src.image import Image
from matplotlib.patches import Polygon
from src.filter_graph import FilterGraph, Filter
import src.log as log
print("Starting to run code")
if __name__ == "__main__":
    stations = pd.read_json("referenceData/stations.json")

    groundStations: 'List[Station]' = []
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))


    print("number of stations:" , len(stations))

    application = Application(jfile="apps/onlycal.json")

    const.LOGGING_FILE = "log0.txt"

    satellites = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [ImageSamplingSatellite2(i, application=application) for i in satellites]
    print("number of satellites:", len(satellites))

    startTime = Time().from_str("2022-07-15 14:00:00")
    endTime = Time().from_str("2022-07-18 14:30:00")


    sim = Simulator(60, startTime, endTime, satellites, groundStations)

    Metrics.metr()
    sim.run()
    Metrics.metr().print()
    # Metrics.metr().image_logger.pretty_save("images.txt")
    
    print("Logs Saving")
    print("LOGKEY")
    for satellite in satellites:
        print(str(satellite))
        print("len-data, len-low, len-med, len-hi, mem%, time-cache, pow, num-proc")
        for analytic in satellite.analytics:
            print(analytic)
    print("LOGKEY")
    print(str(Metrics.metr().image_logger))
    print("LOGKEY")
    analytics = Metrics.metr().image_logger.create_analytics()
    for sat, data in analytics.items():
        print(sat)
        print(data)
    print("LOGKEY")
    Metrics.metr().image_logger.pretty_save("xyz.txt")
    