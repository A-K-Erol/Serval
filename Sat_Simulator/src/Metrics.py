from src.image import Image, ImageLogger
metr = None

class Metrics(object):
    """
    Class that holds the metrics for the simulation
    """
    metr = None

    def metr():
        """
        Returns the metrics object
        """
        global metr
        if not metr:
            metr = Metrics()
        return metr

    def __init__(self) -> None:
        self.images_captured = 0
        self.pri_captured = 0
        self.hipri_captured = 0
        self.hipri_computed = 0
        self.hipri_sent = 0
        self.cmpt_delay = [0,1E-32]
        self.transmit_delay = [0,1E-32]
        self.image_logger = ImageLogger()


    def print(self) -> None:
        """
        Prints the metrics
        """
        print("Images Captured: ", self.images_captured)
        print("Images not computed ", self.pri_captured)
        print("High Priority Images Captured: ", self.hipri_captured)
        print("High Priority Images Computed: ", self.hipri_computed)
        print("High Priority Images Sent: ", self.hipri_sent)
        print("Computation Delay: ", self.cmpt_delay[0]/self.cmpt_delay[1])
        print("Transmit Delay: ", self.transmit_delay[0]/self.transmit_delay[1])


