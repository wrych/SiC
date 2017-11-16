import collectorobject
import logging


class Template(collectorobject.Resource):

    def set_test_1(self, value):
        self.log(logging.DEBUG, 'setting test1 to {0}'.format(value))

    def set_test_2(self, value):
        self.log(logging.DEBUG, 'setting test2 to {0}'.format(value))

    def get_test_1(self):
        return(self.get_child('test_1').get_set_point())

    def get_test_2(self):
        return(self.get_child('test_2').get_set_point())
