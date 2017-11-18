import unittest

import collectorobject


class Test(unittest.TestCase):

    def get_instance(self, *args, **kw_args):
        obj = collectorobject.Value(*args, **kw_args)
        return obj

    def get_attr_getter(self, obj, attr):
        return(getattr(obj, 'get_{0}'.format(attr)))

    def assertAttrEqual(self, obj, attr, value):
        return(self.assertEqual(self.get_attr_getter(obj, attr)(), value))

    def assertDTypeEqual(self, obj, dtype):
        return(self.assertAttrEqual(obj, 'dtype', dtype))

    def assertAccessModeEqual(self, obj, access_mode):
        return(self.assertAttrEqual(obj, 'access_mode', access_mode))

    def assertUnitEqual(self, obj, unit):
        return(self.assertAttrEqual(obj, 'unit', unit))

    def test_class(self):
        obj = self.get_instance()
        self.assertIsInstance(obj, collectorobject.Value)

    def test_class_dtype(self):
        dtype = 'float'
        obj = self.get_instance(dtype=dtype)
        self.assertDTypeEqual(obj, dtype)

    def test_set_dtype(self):
        dtype = 'float'
        obj = self.get_instance()
        obj.set_dtype(dtype)
        self.assertDTypeEqual(obj, dtype)

    def test_class_default_access_mode(self):
        obj = self.get_instance()
        self.assertAccessModeEqual(obj, 'rw')

    def test_class_access_mode(self):
        access_mode = 'r'
        obj = self.get_instance(access_mode=access_mode)
        self.assertAccessModeEqual(obj, access_mode)

    def test_class_access_mode_raises(self):
        access_mode = 'x'
        self.assertRaises(ValueError, self.get_instance, access_mode=access_mode)

    def test_set_access_mode(self):
        access_mode = 'w'
        obj = self.get_instance()
        obj.set_access_mode(access_mode)
        self.assertAccessModeEqual(obj, access_mode)

    def test_set_value(self):
        value = 1.0
        obj = self.get_instance()
        obj.set_value(value)
        self.assertAlmostEqual(obj.get_set_point(), value)

    def test_set_value_casting(self):
        value = 1.0
        dtype = 'float'
        obj = self.get_instance()
        obj.set_dtype(dtype)
        obj.set_value(int(value))
        self.assertEqual(type(obj.get_value()), obj.get_dtype_from_str(dtype))

    def test_get_value_not_set(self):
        obj = self.get_instance()
        self.assertRaises(RuntimeError, obj.get_set_point)

    def test_get_value(self):
        set_point = 10.0
        obj = self.get_instance()
        obj.set_value(set_point)
        value = obj.get_value()
        self.assertAlmostEqual(value, set_point)

    def test_class_default_unit(self):
        obj = self.get_instance()
        self.assertUnitEqual(obj, '')

    def test_class_unit(self):
        unit = 's'
        obj = self.get_instance(unit=unit)
        self.assertUnitEqual(obj, unit)

    def test_set_unit(self):
        unit = 'A'
        obj = self.get_instance()
        obj.set_unit(unit)
        self.assertUnitEqual(obj, unit)

    def test_class_allowed_range(self):
        allowed_range = [0, 10]
        obj = self.get_instance(dtype='float', allowed_range=allowed_range)
        self.assertAttrEqual(obj, 'allowed_range', allowed_range)

    def test_values_below_range(self):
        allowed_range = [0.0, 10.0]
        value = -1
        obj = self.get_instance(dtype='float', allowed_range=allowed_range)
        self.assertRaises(ValueError, obj.set_value, value)

    def test_values_above_range(self):
        allowed_range = [0.0, 10.0]
        value = 11
        obj = self.get_instance(dtype='float', allowed_range=allowed_range)
        self.assertRaises(ValueError, obj.set_value, value)

    def test_class_allowed_values(self):
        allowed_values = ['a', 'b', 'c']
        obj = self.get_instance(allowed_values=allowed_values)
        self.assertAttrEqual(obj, 'allowed_values', allowed_values)

    def test_values_not_in_allowed_values(self):
        allowed_values = ['a', 'b', 'c']
        value = 'd'
        obj = self.get_instance(allowed_values=allowed_values)
        self.assertRaises(ValueError, obj.set_value, value)

    def test_allowed_range_type_error(self):
        self.assertRaises(ValueError,
                          self.get_instance,
                          dtype=float,
                          allowed_values=[0,'a'])

    def test_range_only_with_numerals(self):
        self.assertRaises(TypeError,
                          self.get_instance,
                          dtype='str',
                          allowed_range=['a', 'b'])
        
    def test_value_dict(self):
        access_mode = 'r'
        dtype = 'int'
        unit = 'Ohm'
        allowed_values = [1,2,3]
        value = 3
        obj = self.get_instance(access_mode=access_mode,
                                dtype='int', 
                                unit=unit,
                                allowed_values=allowed_values)
        obj.set_value(value)
        self.assertDictEqual(obj.get_value_dict(), 
                             {
                                 'access_mode': access_mode,
                                 'allowed_values':allowed_values,
                                 'dtype': dtype,
                                 'unit':unit,
                                 'value': value
                             })
