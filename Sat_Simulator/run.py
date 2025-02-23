print("Beginning Imports...")
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

print("Imports Complete")
if __name__ == "__main__":
    stations = pd.read_json("referenceData/stations.json")

    groundStations: 'List[Station]' = []
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))

    application = Application(jfile="apps/onlycal.json")
    satellites = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [ImageSamplingSatellite2(i, application=application) for i in satellites]


    print("number of stations:" , len(stations))
    print("number of satellites:", len(satellites))

    startTime = Time().from_str("2022-07-15 14:00:00")
    endTime = Time().from_str("2022-07-16 2:00:00")


    sim = Simulator(60, startTime, endTime, satellites, groundStations)

    Metrics.metr()
    sim.run()

    satellite_log_file = "satellite_logs.txt"
    image_logger_log_file = "image_logger.txt"
    analytics_log_file = "analytics_logs.txt"

    # Logging satellite analytics
    with open(satellite_log_file, "w") as log_file:
        log_file.write("Logs Saving\n")
        for satellite in satellites:
            log_file.write(str(satellite) + "\n")
            log_file.write("len-data, len-low, len-med, len-hi, mem%, time-cache, pow, num-proc\n")
            for analytic in satellite.analytics:
                log_file.write(str(analytic) + "\n")


    # Logging image logger data
    Metrics.metr().image_logger.pretty_save(image_logger_log_file)


    # Logging analytics data
    with open(analytics_log_file, "w") as log_file:
        analytics = Metrics.metr().image_logger.create_analytics()
        for sat, data in analytics.items():
            log_file.write(str(sat) + "\n")
            log_file.write(str(data) + "\n")

    Metrics.metr().print()