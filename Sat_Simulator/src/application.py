import json
import random
from matplotlib.patches import Polygon

class Application:
    def __init__(self, jfile):
        with open(jfile) as f:
            self.apps = json.load(f)

        self.avg_time = 0
        for app, data in self.apps.items():
            points = data["polygon"]
            self.apps[app]["polygon"] = Polygon(points).get_path()
            self.avg_time += data["eval_time"]
        self.avg_time /= len(self.apps)
            

    def get_candidate_applications(self, coord):
        out = []
        for app, data in self.apps.items():
            polygon, static_prob = data["polygon"], data["static_probability"]
            if polygon.contains_point(coord) and random.random() <= static_prob:
                out.append(app)
        return out
    
    def is_high_priority(self, app_list, fixed_time=False):
        time = 0

        for app in app_list:
            time += self.apps[app]["eval_time"]
            if random.random() <= self.apps[app]["dynamic_probability"]:
                return True, time if not fixed_time else self.avg_time
        return False, time if not fixed_time else self.avg_time

    