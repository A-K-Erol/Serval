"""
Specific type of satellite that takes images and holds the data for transmission
"""

import numpy as np
import const

from src.image import Image
from src.packet import Packet
import src.log as log
from src.Metrics import Metrics

from src.nodeDecorator import NodeDecorator
class ImageSatellite (NodeDecorator):
    """
    Class that simulates an imaging satellite

    lastData (Data) - Normally none, however, if between time steps in simulation, the satellite is producing an object, this will be the data object. For example, if satellite takes an image every 5 seconds, but the time step is 2 seconds, it will store that data here, ik its dumb, if u have better ideas, I'm all ears
    """
    def __init__(self, node: 'Node') -> None:
        super().__init__(node)
        self.beamForming = True
        self.waitForAck = False
        

    def load_data(self, timeStep: float) -> None:
        """
        Adds proportional memory to the timeStep,

        Arguments:
            timeStep (float) - time to calculate memory
        """
        
        ##lets say that the satellite takes an image every .001 second and the size of the image is 1 kb
        for i in np.arange(0, timeStep, 1):
            img = Image(const.DATA_SIZE, None, log.loggingCurrentTime.to_datetime())
            #print("Created image", img)
            self.dataQueue.appendleft(img)
       
    def load_packet_buffer(self) -> None:
        """
        Loads the packet buffer with data
        """
        if len(self.transmitPacketQueue) < 600 and len(self.dataQueue) > 0:
            while len(self.transmitPacketQueue) < 600 and len(self.dataQueue) > 0:
                dataObj = self.dataQueue.pop()    
                if type(dataObj) == Image:
                    dataObj.pipeline.log_event("transmitted")  

                if dataObj.size == const.DATA_SIZE:
                    packets = dataObj.to_packets()
                else:
                    packets = dataObj.to_packets(dataObj.size)
                
                packets[0].image = dataObj                
                for packet in packets:
                    self.transmitPacketQueue.appendleft((packet, dataObj))

    
    def recieve_packet(self, pck: Packet) -> None:
        # Do nothing
        self.generate_ack(pck)
        pass
