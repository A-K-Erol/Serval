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
class ImageSamplingSatellite(ImageSatellite):
    def __init__(
        self,
        node: "node.Node",
        energy_config: Dict[str, float] = {
            "compute_energy": 9.0,
            "transmit_energy": 5.0,
            "camera_energy": 4.0,
            "receive_energy": 1.5,
            "normal_energy": 2.0,
        },
        computation_schedule: Dict[int, bool] = {},
        priority_bw_allocation: float = 1,
        start_time: datetime = datetime(2021, 7, 1),
        targets: List[Polygon] = [],
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
        self.normalPowerConsumption = energy_config["normal_energy"]
        self.currentMWs = 25000
        self.recievePowerConsumption = 0
        self.transmitPowerConsumption = energy_config["transmit_energy"]
        self.concentrator = 0
        self.powerGeneration = energy_config["receive_energy"]
        self.maxMWs = 25000
        self.beamForming = True
        self.start_time = Time().from_datetime(start_time)
        self.targets = targets
        self.image_rate = 3 # images per minute
        self.glacial_threshold = 0.5
        self.dynamic_threshold = 0.6
        self.compute_time = 5 # seconds per image
        self.analytics = []

    def in_target(self) -> bool: 
        """
        Returns whether the satellite is in the target
        """
        a = self.node.position.to_coords()

        return any(
            [
                target.get_path().contains_point(a)
                for target in self.targets
            ]
        )

    def populate_cache(self, timeStep: float) -> None:
        """
        Populates the cache with images
        """

        # for comptuational efficiency on machine
        x, y = self.node.position.to_coords()
        if x < 10 or x > 80 or y < -140 or y > -100:
            return 0
        # bounding = Polygon([
        # (10, -100),
        # (80, -140),
        # (10, -140), 
        # (80, -100)
        # ])

        # if not bounding.get_path().contains_point(self.node.position.to_coords()):
        #     print("b", end="")
        #     return # shortcut for computational efficiency

        images_captured = int(timeStep * self.image_rate)
        self.currentMWs -= self.energy_config["camera_energy"]
        Metrics.metr().images_captured += images_captured
        a = len(self.dataQueue)
        for _ in range(images_captured):
            image = Image(
                10, Polygon([(0,0),(1,1),(1,0),(0,1)]), log.loggingCurrentTime.to_datetime(), name="Target Image", satellite = self.node.id
            )
            Metrics.metr().image_logger.add_image(image)
            filters = [["Cloud",0.8,1],["Fire",0.5,0.25]]
            image.pipeline = ImagePipeline(filters)
            image.pipeline.log_event("captured")

            
            if self.in_target() and random.random() < self.glacial_threshold:
                print("Cali image found")
                Metrics.metr().pri_captured += 1
                image.pipeline.log_event("put_in_compute_queue")
                self.primitive_high_priority_queue.put(image)
                image.descriptor = "Pass Glacial"
            else:
                image.score = 0
                image.descriptor = "Fail Glacial"
                log.Log("Image put in lo priority queue", image, self)
                image.pipeline.log_event("prioritized_low")
                self.lo_priority_queue.put(image)

            log.Log("Image captured by sat", image, self)
            self.cache_size += image.size

        print("hi", a, len(self.dataQueue))
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
            image = self.primitive_high_priority_queue.pop()
            
            if self.computation_time_cache < image.pipeline.max_filter_time:
                self.primitive_high_priority_queue.put(image)
                break

            self.images_processed_per_timestep += 1
            
            Metrics.metr().pri_captured -= 1
            log.Log(
                "Doing computation on sat", image, self, {
                    "time": self.compute_time, "cache": self.computation_time_cache}
            )

            filter_res, filter_time = image.pipeline.apply_filter()
            self.computation_time_cache -= filter_time

            if filter_res:
                Metrics.metr().cmpt_delay[1] += 1
                Metrics.metr().cmpt_delay[0] += (log.loggingCurrentTime.to_datetime() - image.time).total_seconds()
                image.descriptor = "Pass Dynamic"
                image.score = 1
                self.final_high_priority_queue.put(image)
                Metrics.metr().hipri_computed += 1
                log.Log("Setting image score on sat", image, self)
            else:
                image.descriptor = "Fail Dynamic"
                image.score = 1
                self.lo_priority_queue.put(image)
                log.Log("Setting image score on sat", image, self)

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
            if self.currentMWs > self.energy_config["compute_energy"] * timeStep:
                self.computation_time_cache += timeStep * self.priority_bw_allocation
                self.currentMWs -= self.energy_config["compute_energy"] * timeStep
        log.Log(
            "Computation time cache", self, {
                "time_cache": self.computation_time_cache}
        )
        self.do_computation()
        self.analytics.append([self.percent_of_memory_filled(), self.computation_time_cache, self.currentMWs, len(self.dataQueue), len(self.lo_priority_queue), len(self.primitive_high_priority_queue), len(self.final_high_priority_queue), self.images_processed_per_timestep, ims_captured])
