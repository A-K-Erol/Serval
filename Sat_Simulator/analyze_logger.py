from src.image import Image, ImagePipeline, ImageLogger
from src.utils import Time
from collections import defaultdict
imageLogger = ImageLogger()

print("read")
imageLogger.read("images.pkl")

# average delay between all events

# {'captured' : 0, 
#                        'prioritized_low' : 0, 
#                        'put_in_compute_queue' : 0, 
#                        'pop_from_compute_queue' : 0,
#                        'prioritized_high' : 0, 
#                        'transmitted' : 0}

for image in imageLogger.images:
    pipeline_events = image.pipeline
    sat_id = image.satellite
    
    # for each pair of events, calculate the time difference if it is not 0, else report Null
    # if the event is not present, report Null
    # if the event is present, report the time difference
    # if the event is present, report the time difference
    # Initialize dictionaries to store total delays and counts for each event pair
    total_delays = defaultdict(lambda: defaultdict(int))
    counts = defaultdict(lambda: defaultdict(int))

    # Initialize dictionaries to store total delays and counts for each event pair per satellite
    satellite_delays = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    satellite_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # Define the event pairs
    event_pairs = [
        ('captured', 'prioritized_low'),
        ('prioritized_low', 'transmitted'),
        ('put_in_compute_queue', 'pop_from_compute_queue'),
        ('pop_from_compute_queue', 'prioritized_high'),
        ('prioritized_high', 'transmitted')
    ]

    for image in imageLogger.images:
        pipeline_events = image.pipeline
        sat_id = image.satellite
        
        for event1, event2 in event_pairs:
            if event1 in pipeline_events and event2 in pipeline_events:
                time_diff = pipeline_events[event2] - pipeline_events[event1]
                if time_diff > 0:
                    total_delays[event1][event2] += time_diff
                    counts[event1][event2] += 1
                    satellite_delays[sat_id][event1][event2] += time_diff
                    satellite_counts[sat_id][event1][event2] += 1

    # Calculate average delays for all pairs of events
    average_delays = {event1: {event2: (total_delays[event1][event2] / counts[event1][event2])
                               for event2 in total_delays[event1] if counts[event1][event2] > 0}
                      for event1 in total_delays}

    # Calculate average delays for each satellite
    average_satellite_delays = {sat_id: {event1: {event2: (satellite_delays[sat_id][event1][event2] / satellite_counts[sat_id][event1][event2])
                                                  for event2 in satellite_delays[sat_id][event1] if satellite_counts[sat_id][event1][event2] > 0}
                                         for event1 in satellite_delays[sat_id]}
                                for sat_id in satellite_delays}
    


    print("all images")
    print("Average Delays:", average_delays)
    print("Average Satellite Delays:", average_satellite_delays)

print("hi pri only")
for image in imageLogger.images:
    if image.descriptor != "Pass Dynamic":
        continue

    pipeline_events = image.pipeline
    sat_id = image.satellite
    
    # for each pair of events, calculate the time difference if it is not 0, else report Null
    # if the event is not present, report Null
    # if the event is present, report the time difference
    # if the event is present, report the time difference
    # Initialize dictionaries to store total delays and counts for each event pair
    total_delays = defaultdict(lambda: defaultdict(int))
    counts = defaultdict(lambda: defaultdict(int))

    # Initialize dictionaries to store total delays and counts for each event pair per satellite
    satellite_delays = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    satellite_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # Define the event pairs
    event_pairs = [
        ('captured', 'prioritized_low'),
        ('prioritized_low', 'put_in_compute_queue'),
        ('put_in_compute_queue', 'pop_from_compute_queue'),
        ('pop_from_compute_queue', 'prioritized_high'),
        ('prioritized_high', 'transmitted')
    ]

    for image in imageLogger.images:
        pipeline_events = image.pipeline
        sat_id = image.satellite
        
        for event1, event2 in event_pairs:
            if event1 in pipeline_events and event2 in pipeline_events:
                time_diff = pipeline_events[event2] - pipeline_events[event1]
                if time_diff > 0:
                    total_delays[event1][event2] += time_diff
                    counts[event1][event2] += 1
                    satellite_delays[sat_id][event1][event2] += time_diff
                    satellite_counts[sat_id][event1][event2] += 1

    # Calculate average delays for all pairs of events
    average_delays = {event1: {event2: (total_delays[event1][event2] / counts[event1][event2])
                               for event2 in total_delays[event1] if counts[event1][event2] > 0}
                      for event1 in total_delays}

    # Calculate average delays for each satellite
    average_satellite_delays = {sat_id: {event1: {event2: (satellite_delays[sat_id][event1][event2] / satellite_counts[sat_id][event1][event2])
                                                  for event2 in satellite_delays[sat_id][event1] if satellite_counts[sat_id][event1][event2] > 0}
                                         for event1 in satellite_delays[sat_id]}
                                for sat_id in satellite_delays}
    



    print("Average Delays:", average_delays)
    print("Average Satellite Delays:", average_satellite_delays)
