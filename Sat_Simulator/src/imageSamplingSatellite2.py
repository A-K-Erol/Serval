from datetime import datetime
import random
from typing import Dict, List
from src.image import Image, ImageLogger, ImagePipeline
from . import node
from .imageSatellite import ImageSatellite
from .filter_graph import FilterGraph, FilterStatus
from . import log
from .utils import FusedQueue, MyQueue, Time
from matplotlib.patches import Polygon
from src.Metrics import Metrics
from src.application import Application
class ImageSamplingSatellite2(ImageSatellite):
    def __init__(
        self,
        node: "node.Node",
        energy_config: Dict[str, float] = {},
        computation_schedule: Dict[int, bool] = {},
        priority_bw_allocation: float = 1,
        start_time: datetime = datetime(2025, 1, 1),
        application: Application = None
    ) -> None:
        """
        Energy config:
        - compute_energy: energy to compute in a time step
        - transmit_energy: energy to transmit in a time step
        - camera_energy: energy to take a picture in a time step
        - receive_energy: energy to receive in a time step
        """
        super(ImageSatellite, self).__init__(node)
        self.node = self.get_node()
        self.cache_size = 0
        self.energy_config = energy_config
        self.computation_schedule = computation_schedule
        self.computation_time_cache = 0
        (
            self.lo_priority_queue,
            self.primitive_high_priority_queue,
            self.final_high_priority_queue,
        ) = (MyQueue(), MyQueue(), MyQueue())
        self.dataQueue: "FusedQueue" = FusedQueue(
            [
                self.final_high_priority_queue,
                self.primitive_high_priority_queue,
                self.lo_priority_queue,
            ],
            priority_bw_allocation=priority_bw_allocation,
            # callback=lambda data, method: log.Log(f"Data accessed in the data queue", self, data, {"method": method})
        )
        self.priority_bw_allocation = priority_bw_allocation
        self.normalPowerConsumption = 1.13 * 1000 # 1.13W
        self.currentMWs = 300000
        self.compute_power = 10 * 1000 # 10 W
        self.recievePowerConsumption = 1 * 1000 # 2 W
        self.transmitPowerConsumption = 5 * 1000 # 50 W
        self.camera_power = 4.5 * 1000 # 4.5 W
        self.concentrator = 0
        self.powerGeneration = 7 * 1000 # 7 W
        self.maxMWs = 400000
        self.beamForming = True
        self.start_time = Time().from_datetime(start_time)
        self.application = application
        self.image_rate = .75 # images per second
        self.glacial_threshold = .4
        self.analytics = []
        self.coords = self.node.position.to_coords()



    def populate_cache(self, timeStep: float) -> None:
        """
        Populates the cache with images
        """
        coords = self.node.position.to_coords()
        images_captured = int(timeStep * self.image_rate)
        self.currentMWs -= self.camera_power * timeStep
        Metrics.metr().images_captured += images_captured



        for _ in range(images_captured):
            # print("Capturing Image")
            image = Image(10, time = log.loggingCurrentTime, coord = coords, satellite = self.node.id, name = "Target Image")
            app_list = self.application.get_candidate_applications(coords)
            image.pipeline = ImagePipeline(application=self.application, filters=None, candidate_applications=app_list)
            image.pipeline.log_event("captured")

            if app_list:
                Metrics.metr().hipri_captured += 1
                image.score, image.compute_time = self.application.is_high_priority() # Simulate Priority Determination -- time will be deducted only after true compute
                image.pipeline.log_event("put_in_compute_queue")
                self.primitive_high_priority_queue.put(image)
            else:
                image.score, image.compute_time = 0, 0
                image.pipeline.log_event("prioritized_low")
                self.lo_priority_queue.put(image)

            Metrics.metr().image_logger.add_image(image)
            self.cache_size += image.size

        return images_captured

    def get_cache_size(self) -> int:
        """
        Returns the size of the cache
        """
        return self.cache_size

    def do_computation(self) -> None:
        """
        Does the computation
        """
        while (len(self.primitive_high_priority_queue) > 0):
            if self.computation_time_cache <= 0:
                break
            
            image = self.primitive_high_priority_queue.pop()
            image.pipeline.log_event("pop_from_compute_queue")
            self.computation_time_cache -= image.compute_time

            self.images_processed_per_timestep += 1
            
            if image.score == 1:
                image.pipeline.log_event("prioritized_high")
                self.final_high_priority_queue.put(image)
            else:
                image.pipeline.log_event("prioritized_low")
                self.lo_priority_queue.put(image)

    def percent_of_memory_filled(self) -> float:
        return len(self.dataQueue) / 10000000

    def load_data(self, timeStep: float) -> None:
        """
        Loads data from the cache into the node
        """
        self.images_processed_per_timestep = 0
        self.time = log.loggingCurrentTime
        ims_captured = self.populate_cache(timeStep)
        # Do computation
        if self.computation_time_cache < timeStep:
            if self.currentMWs > self.compute_power * timeStep:
                self.computation_time_cache += timeStep
                self.currentMWs -= self.compute_power * timeStep
        log.Log(
            "Computation time cache", self, {
                "time_cache": self.computation_time_cache}
        )
        self.do_computation()
        self.analytics.append([len(self.dataQueue), len(self.lo_priority_queue), len(self.primitive_high_priority_queue), len(self.final_high_priority_queue), self.percent_of_memory_filled(), self.computation_time_cache, self.currentMWs, self.images_processed_per_timestep, ims_captured])
