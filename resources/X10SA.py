import epicsclient

class EPICS(epicsclient.Epics):
    
    def __init__(self, logger=sys.stdout):
        super(Epics, self).__init__('X10SA', logger)