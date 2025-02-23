import json
class Schedule:
    def __init__(self) -> None:
        self.schedule = []

    def add(self, task) -> None:
        self.schedule.append(task)

    def serialize(self) -> str:
        return json.dumps(self.schedule)
    
    def deserialize(self, schedule: str) -> None:
        self.schedule = json.loads(schedule)




