from lxml import etree

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

namespaces = {'ncml':"http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"}

class netcdfElement(etree.ElementBase):
    def _init(self):
        print 'netcdfElement _init', self.getparent()
        
class variableElement(etree.ElementBase):
    def _init(self):
        print 'variableElement _init', self.getparent().tag 
        self._foo = self.getparent()._foo + '/var'
        
class groupElement(etree.ElementBase):
    def _init(self):
        print 'groupElement _init', self.getparent().tag 
        self._foo = self.getparent()._foo + '/grp'

class dimensionElement(etree.ElementBase):
    def _init(self):
        print 'dimensionElement _init', self.getparent().tag 
        self._foo = self.getparent()._foo + '/dim'
        
class attributeElement(etree.ElementBase):
    def _init(self):
        print 'attributeElement _init', self.getparent().tag 
        self._foo = self.getparent()._foo + '/att'

class NetCDFLookup(etree.CustomElementClassLookup):

    _lookup = {
        NETCDF      : netcdfElement,
        VARIABLE    : variableElement,
        DIMENSION   : dimensionElement,
        ATTRIBUTE   : attributeElement,
        GROUP       : groupElement,
        }


    def lookup(self, node_type, document, namespace, name):
        print "Looking up:",node_type,document,namespace,name
        
        return NetCDFLookup._lookup.get(name)
        
        
def my_parser(fname):

    

    parser = etree.XMLParser()

    parser.set_element_class_lookup(NetCDFLookup())

    xml_etree = etree.parse(fname, parser)
    
    root = xml_etree.getroot()
    
    root._foo = fname
    
    return root
    
    
root = my_parser('profile_shore.ncml')
    
    
    