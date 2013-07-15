"""
@TODO add NcVarAttrib class to set the name of a variable using renameVariable - nothing else can change!
@TODO add NcGrpAttrib class to prevent setting anything on a group - netCDF4 does not expose a way to do it!
"""

import cStringIO
from lxml import etree
from parse_netcdf import *

namespaces = {'ncml':NAMESPACE}

class NetcdfEtreeException(Exception):
    """
    An exception class for NetCDF etree wrappers
    """

class NcDimAttrib(etree._Attrib):
    
    def __init__(self, *args, **kwargs):
        self._nc_element = args[0]
        self._nc_obj = args[0]._nc_obj
        super(NcDimAttrib, self).__init__(*args,**kwargs)
    
    def __setitem__(self, key, value):

        nc_object = self._nc_obj
        if nc_object is None:
            raise NetcdfEtreeException('Internal Error: No nc_obj available!')  

        if key == NAME:
            # renameDimension(Old value, New Value)
            nc_object.renameDimension(self[NAME], value)
        elif key == LENGTH:
            raise NetcdfEtreeException('''The legth of the dimension "{}" can not be modified in a NetCDF4 Python Dataset'''.format(self[NAME]))
        elif key == ISUNLIMITED:
            raise NetcdfEtreeException('''The nature of the dimension "{}" can not be changed once it is created as limited or unlimited in a NetCDF4 Python Dataset'''.format(self[NAME]))
        else:
            raise NetcdfEtreeException('''The key "{}" is not part of the schema for NcML Dimensions'''.format(key))

        super(NcDimAttrib, self).__setitem__(key, value)

    def __delitem__(self, key):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be deleted from the a NetCDF4 Python Dataset''')

    def update(self, dct):
        for key, value in dct.iteritems():
            self[key] = value

    def pop(self, key, *default):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be popped from a NetCDF4 Python Dataset''')

    def clear(self):
        raise NetcdfEtreeException('''Dimensions and dimension attributes can not be cleared from a NetCDF4 Python Dataset''')


class NcAttrAttrib(etree._Attrib):
    
    def __init__(self, *args, **kwargs):
        self._nc_element = args[0]
        self._nc_obj = args[0]._nc_obj
        super(NcAttrAttrib, self).__init__(*args,**kwargs)
    
    def __setitem__(self, key, value):

        nc_object = self._nc_obj
        if nc_object is None:
            raise NetcdfEtreeException('Internal Error: No nc_obj available!')  

        current_attr_name = self[NAME]

        if key == NAME:
            # change the name of an existing attribute
            new_attr_name = value
            current_attr_value = nc_object.getncattr(current_attr_name)
            nc_object.setncattr(new_attr_name, current_attr_value)
            nc_object.delncattr(current_attr_name)
        elif key == VALUE:
            # Set the value of an existing attribute without changing its type
            current_type = type(nc_object.getncattr(current_attr_name))
            try:
                new_value = current_type(value)
            except ValueError, TypeError:
                raise NetcdfEtreeException('''Can not cast the new value "{}" (type: {}) of the attribute "{}" to the current type "{}"'''.format(value, type(value), current_attr_name, current_type))
            nc_object.setncattr(current_attr_name, new_value)
        elif key == TYPE:
            current_value = nc_object.getncattr(current_attr_name)
            try:
                new_type = inverse_type_map[value]
            except KeyError:
                raise NetcdfEtreeException('''Unknown new type "{}" specified for attribute "{}"'''.format(value, current_attr_name))
            
            try:
                new_value = new_type(current_value)
            except ValueError, TypeError:
                raise NetcdfEtreeException('''Can not cast the current value "{}" (type: {}) of the attribute "{}" to the new type "{}"'''.format(current_value, type(current_value), current_attr_name, new_type))
                
            nc_object.setncattr(current_attr_name, new_value)
            
            # Make sure to change the representation of the value to be consistent with the new type
            super(NcAttrAttrib, self).__setitem__(VALUE, unicode(new_value))
            
        else:
            raise NetcdfEtreeException('''The key "{}" is not part of the schema for NcML Attributes'''.format(key))

        super(NcAttrAttrib, self).__setitem__(key, value)
        

    def __delitem__(self, key):
        raise NetcdfEtreeException('''NcML Attribute attributes can not be deleted from a NetCDF4 Python Dataset''')

    def update(self, dct):
        for key, value in dct.iteritems():
            self[key] = value

    def pop(self, key, *default):
        raise NetcdfEtreeException('''NcML Attribute attributes can not be popped from a NetCDF4 Python Dataset''')

    def clear(self):
        raise NetcdfEtreeException('''NcML Attribute attributes can not be cleared from a NetCDF4 Python Dataset''')




class NetcdfElement(etree.ElementBase):
    """
    Must define a Python class extending from etree cython so that we can set attributes 
    """
                
class VariableElement(etree.ElementBase):
    def _init(self):
        name_att = self.attrib['name']
        pobj = self.getparent()._nc_obj
        var = pobj.variables[name_att]
        self._nc_obj = var
        
class GroupElement(etree.ElementBase):
    def _init(self):
        name_att = self.attrib['name']
        pobj = self.getparent()._nc_obj
        grp = pobj.groups[name_att]
        self._nc_obj = grp

class DimensionElement(etree.ElementBase):
    def _init(self):
        parent = self.getparent()
        self._nc_obj = parent._nc_obj

    @property 
    def attrib(self):
        return NcDimAttrib(self)
        
    def set(self,key,value):
        self.attrib[key] = value
                
        
class AttributeElement(etree.ElementBase):
    def _init(self):
        parent = self.getparent()
        self._nc_obj = parent._nc_obj

    @property 
    def attrib(self):
        return NcAttrAttrib(self)
        
    def set(self,key,value):
        self.attrib[key] = value



class NetCDFLookup(etree.CustomElementClassLookup):

    _lookup = {
        NETCDF      : NetcdfElement,
        VARIABLE    : VariableElement,
        DIMENSION   : DimensionElement,
        ATTRIBUTE   : AttributeElement,
        GROUP       : GroupElement,
        }


    def lookup(self, node_type, document, namespace, name):
        print "Looking up:",node_type,document,namespace,name
        
        return NetCDFLookup._lookup.get(name)
        
        
def my_parser(dataset):

    parser = etree.XMLParser()
    parser.set_element_class_lookup(NetCDFLookup())

    xml_etree = None
    output = cStringIO.StringIO()
    try:
        parse_dataset_buffer(dataset,output)
        output.reset()
        xml_etree = etree.parse(output, parser)
    finally:
        output.close()

    root = xml_etree.getroot()
    
    root._nc_obj = dataset
    
    return root
    
    
    