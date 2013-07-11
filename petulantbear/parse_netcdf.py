from netCDF4 import Dataset
from netCDF4 import Group
from netCDF4 import Variable
from netCDF4 import Dimension

import cStringIO

import numpy

NETCDF      = 'netcdf'
VARIABLE    = 'variable'
DIMENSION   = 'dimension'
ATTRIBUTE   = 'attribute'
GROUP       = 'group'
NAME        = 'name'
LENGTH      = 'length'
VALUE       = 'value'
TYPE        = 'type'
LOCATION    = 'location'
XMLNS       = 'xmlns'
NAMESPACE   = 'http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2'
HEADER      = '''<?xml version="1.0" encoding="UTF-8"?>'''

# common types...
type_map = {
    numpy.int32 : 'int',
    numpy.int64 : 'long',
    numpy.float32 : 'float',
    numpy.float64 : 'double',
    }

def parse_dim(output, dim):
    output.write('''<{dimension} {name}="{dimname}" {length}="{dimlen}"/>\n'''.format(
        dimension=DIMENSION,
        name=NAME,
        dimname=dim._name,
        length=LENGTH,
        dimlen=len(dim)
        )
    )

def parse_att(output, att):
    if isinstance(att[1],(str,unicode)):
        output.write('''<{attribute} {name}="{attname}" {value}="{attvalue}"/>\n'''.format(
            attribute=ATTRIBUTE,
            name=NAME,
            attname=att[0],
            value=VALUE,
            attvalue=att[1]
            )
        )
    else :
    
        att_type = type_map.get(type(att[1]), 'unknown')
        output.write('''<{attribute} {name}="{attname}" {type}="{att_type}" {value}="{attvalue}"/>\n'''.format(
            attribute=ATTRIBUTE,
            name=NAME,
            attname=att[0],
            type=TYPE,
            att_type = att_type,
            value=VALUE,
            attvalue=att[1]
            )
        )
        


def parse_var(output, var):

    for attname in var.ncattrs():
        parse_att(output,(attname,var.getncattr(attname)))

def parse_group(output, group):

    for dim in root.dimensions.values():
        parse_dim(output, dim)

    for attname in group.ncattrs():
        parse_att(output,(attname,group.getncattr(attname)))

    
    for var in group.variables.values():
        parse_var(output, var)


def parse_dataset(dataset, url="file:/unknown"):

    #output = cStringIO.StringIO()
    output = open('test.xml','w')
    
    output.write('''{header}\n<{netcdf} {xmlns}="{namespace}" {location}="{url}">\n'''.format(
            header=HEADER,
            netcdf=NETCDF, 
            xmlns=XMLNS,
            namespace=NAMESPACE,
            location=LOCATION,
            url = url
            )
        )
    
    for dim in dataset.dimensions.values():
        parse_dim(output, dim)
    
    for attname in dataset.ncattrs():
        parse_att(output,(attname,dataset.getncattr(attname)))
    
    
    for group in dataset.groups.values():
        parse_group(output,group)
    
    
    for var in dataset.variables.values():
        parse_var(output, var)
    
    
    output.write('''</{}>\n'''.format(NETCDF))
    
    #retval = output.getvalue()
    
    output.close()
    
    #return retval
    
    