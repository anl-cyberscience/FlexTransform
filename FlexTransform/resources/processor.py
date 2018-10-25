
class Processor:
    """
    Base class for pre/post processing objects
    """

    def preprocess(self, source_file):
        raise NotImplementedError

    def postprocess(self, transformed_file):
        raise NotImplementedError
