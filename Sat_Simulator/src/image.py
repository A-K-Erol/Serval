import random
from typing import Dict, List
from shapely.geometry import Polygon

from src.data import Data
from src.utils import Time
from . import log
import pickle

class ImageLogger(object):
    def __init__(self):
        self.images = []
    
    def add_image(self, image):
        self.images.append(image)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.images, f)
    
    def read(self, filename):
        with open(filename, 'rb') as f:
            self.images = pickle.load(f)
    
    def __str__(self):
        out = []
        for image in self.images:
            out.append(f'Id: {image.id}, Satellite: {image.satellite}, Pipeline: {str(image.pipeline)}')
        return '\n'.join(out)
    
    def pretty_save(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self))
    
    def create_analytics(self):
        satellite_images = {}
        satellite_analytics = {}
        for image in self.images:
            if image.satellite not in satellite_images:
                satellite_images[image.satellite] = []
            satellite_images[image.satellite].append(image)

        for satellite, images in satellite_images.items():
            total = len(images)
            percent_hi_num = 0
            percent_hi_den = 1E-32
            capture_to_compute = 0
            capture_to_compute_den = 1E-32
            compute_to_prioritize = 0
            compute_to_prioritize_den = 1E-32
            capture_to_transmit = 0
            capture_to_transmit_den = 1E-32
            hi_prioritize_to_transmit = 0
            hi_prioritize_to_transmit_den = 1E-32

            filter_0 = 0
            filter_1 = 0

            for image in images:
                if image.pipeline.events['captured'] and image.pipeline.events['pop_from_compute_queue']:
                    capture_to_compute -= Time.difference_in_seconds(image.pipeline.events['captured'], image.pipeline.events['pop_from_compute_queue'])
                    capture_to_compute_den += 1
                if image.pipeline.events['captured'] and image.pipeline.events['transmitted']:
                    capture_to_transmit -= Time.difference_in_seconds(image.pipeline.events['captured'], image.pipeline.events['transmitted'])
                    capture_to_transmit_den += 1
                if image.pipeline.events['pop_from_compute_queue'] and image.pipeline.events['prioritized_high']:
                    compute_to_prioritize -= Time.difference_in_seconds(image.pipeline.events['pop_from_compute_queue'], image.pipeline.events['prioritized_high'])
                    compute_to_prioritize_den += 1
                if image.pipeline.events['prioritized_high'] and image.pipeline.events['transmitted']:
                    hi_prioritize_to_transmit -= Time.difference_in_seconds(image.pipeline.events['prioritized_high'], image.pipeline.events['transmitted'])
                    hi_prioritize_to_transmit_den += 1


                if image.pipeline.events['prioritized_high']:
                    percent_hi_num += 1
                if image.pipeline.events['captured']:
                    percent_hi_den += 1

                # for filter in image.pipeline.filters:
                #     if image.pipeline.events[filter[0][0]]:
                #         filter_0 += 1
                #     if image.pipeline.events[filter[1][0]]:
                #         filter_1 += 1
            
            satellite_analytics[satellite] = {"num hi": percent_hi_num, "percent hi": percent_hi_num / percent_hi_den, "avg capture to compute": capture_to_compute / capture_to_compute_den, "avg compute to prioritize": compute_to_prioritize / compute_to_prioritize_den, "avg capture to transmit": capture_to_transmit / capture_to_compute_den, "avg hi pri to transmit": hi_prioritize_to_transmit / hi_prioritize_to_transmit_den, "filter_0": filter_0 / total, "filter_1": filter_1 / total}
        return satellite_analytics
            






class ImagePipeline(object):
    def __init__(self, filters: List[str] = []):
        self.filters = filters
        self.events = {'captured' : 0, 
                       'prioritized_low' : 0, 
                       'put_in_compute_queue' : 0, 
                       'pop_from_compute_queue' : 0,
                       'prioritized_high' : 0, 
                       'transmitted' : 0}
        
        self.max_filter_time = 0
        for filter, probability, time in filters:
            self.events[filter] = 0
            self.max_filter_time += time

    def log_event(self, event, time = None):
        if event not in self.events:
            print("Event not found")
        if time:
            self.events[event] = time
        else:
            self.events[event] = log.get_logging_time()

    def apply_filter(self):
        self.log_event("pop_from_compute_queue")
        curr_time = log.get_logging_time().copy()
        for filter_name, filter_pass_rate, filter_time in self.filters:
            curr_time.add_seconds(filter_time)
            self.log_event(filter_name, curr_time)
            if filter_pass_rate < random.random():
                self.log_event("prioritized_low", curr_time)
                return False, Time.difference_in_seconds(curr_time, log.get_logging_time())
        self.log_event("prioritized_high", curr_time)
        return True, Time.difference_in_seconds(curr_time, log.get_logging_time())
    
    def __str__(self):
        event_pairs = [
        ('captured', 'prioritized_low'),
        ('prioritized_low', 'transmitted'),
        ('put_in_compute_queue', 'pop_from_compute_queue'),
        ('pop_from_compute_queue', 'prioritized_high'),
        ('prioritized_high', 'transmitted')
    ]
        out = []
        for event1, event2 in event_pairs:
            if self.events[event1] and self.events[event2]:
                out.append(f'{event1} -> {event2}: {Time.difference_in_seconds(self.events[event1], self.events[event2])}')
        return '        '.join(out)   
    


class Image(Data):
    id = 0

    def __init__(self, size: int, region: 'Polygon', time: 'Time', 
                 filter_result: Dict[str, List[float]] = {}, 
                 side_channel_info: Dict[str, float] = {},
                 name="", Pipeline: 'ImagePipeline' = None, satellite = None):
        
        """
        Arguments:
                size (float) - size of image in m
                region (Polygon) - region of image
                time (datetime) - time of image
                mask (np.ndarray) - mask of image
                filter_result  - filter result of image, {name:[score, computation_time]}
                name: name of the image
        """
        super().__init__(size)
        self.satellite = satellite
        self.time = time
        self.region = region
        self.size = size
        self.filter_result = filter_result
        self.id = Image.id
        self.compute_storage = None
        self.score = None
        Image.id += 1
        self.name = name
        self.side_channel_info = side_channel_info
        self.descriptor = ""
        self.pipeline = Pipeline

    def set_score(self, value):
        self.score = value

    @classmethod
    def set_id(cls, value):
        cls.id = value

    @staticmethod
    def from_dict(data):
        min_x, min_y, max_x, max_y = data['region']
        region = Polygon([(min_x, min_y), (max_x, min_y),
                         (max_x, max_y), (min_x, max_y)])
        return Image(
            **data,
            region=region
        )

    # To implement custom comparator (on the score) for the priority queue in the detector
    def __lt__(self, obj):
        """self < obj."""
        # Priority queue is a min heap while we want to put the highest score first
        # So we reverse the comparison
        return self.score > obj.score if not self.score == obj.score else self.time < obj.time

    def __le__(self, obj):
        """self <= obj."""
        return self < obj or self == obj

    def __eq__(self, obj):
        """self == obj."""
        return self.score == obj.score and self.time == obj.time

    def __ne__(self, obj):
        """self != obj."""
        return not self == obj

    def __gt__(self, obj):
        """self > obj."""
        return not self <= obj

    def __ge__(self, obj):
        """self >= obj."""
        return not self < obj

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return "{{imageId: {}, imageSize: {}, imageScore: {}, imageName: {}}}".format(self.id, self.size, self.score, self.name)
