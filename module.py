"""
Objects for accessing a set of I/O modules.
"""

from .dom import (ElementAccess, ElementDict, AttributeDescriptor)

class CatalogNumber(AttributeDescriptor):
    """Descriptor class for accessing catalog numbers."""
    def __init__(self):
        """Executes superclass's initializer with attribute name."""
        super(CatalogNumber, self).__init__('CatalogNumber')

class SafetyNetworkNumber(AttributeDescriptor):
    """Descriptor class for accessing safety network numbers."""
    def __init__(self):
        """Executes superclass's initializer with attribute name."""
        super(SafetyNetworkNumber, self).__init__('SafetyNetwork')

    def from_xml(self, value):
        """Removes the leading radix and unused 16 most significant bits."""
        fields = value.split('_')
        return str(''.join(fields[1:]))

    def to_xml(self, value):
        """Custom converter for setting a new value.

        Allows the given string to omit underscores, expands to a 32-bit
        value, and adds a radix prefix.
        """
        if not isinstance(value, str):
            raise TypeError('Safety network number must be a hex string')
        new = value.replace('_', '')

        # Ensure valid hex string.
        try:
            x = int(new, 16)
        except ValueError:
            raise ValueError('Safety network number must be a hex string')

        # Generate a zero-padded string and enforce 24-bit limit.
        padded = "{0:012X}".format(x)
        if not len(padded) == 12:
            raise ValueError('Value must be 24-bit, 12 hex characters')

        # Add radix prefix and insert underscores for the final output string.
        fields = ['16#0000']
        for word in range(3):
            start = word * 4
            end = start + 4
            fields.append(padded[start:end])
        return '_'.join(fields)


class Module(ElementAccess):
    """Accessor object for a communication module."""
    snn = SafetyNetworkNumber()

    def __init__(self, element):
        ElementAccess.__init__(self, element)
        
        ports_element = self.get_child_element('Ports')
        self.ports = ElementDict(ports_element, key_attr='Id', types=Port, key_type=int)

    @classmethod
    def createController(cls, prj):
        element = prj._create_append_element(prj.element, 'Module', {'CatalogNumber' : '',
                                                 'Inhibited' : 'false',
                                                 'Major' : '',
                                                 'MajorFault' : 'true',
                                                 'Minor' : '',
                                                 'Name' : 'Local',
                                                 'ParentModPortId' : '1',
                                                 'ParentModule' : 'Local',
                                                 'ProductCode' : '96',
                                                 'ProductType' : '14',
                                                 'Vendor' : '1'})      
        ekey = prj._create_append_element(prj.element, 'EKey', {'State' : 'ExactMatch'})    
        ports = prj._create_append_element(prj.element, 'Ports') 
        port = prj._create_append_element(prj.element, 'Port', {'Address' : '',\
                                            'Id' : '1',
                                            'Type' : 'ICP',
                                            'Upstream' : 'false'}) 
        bus = prj._create_append_element(prj.element, 'Bus', {'Size' : '10'})
        port.appendChild(bus)
        ports.appendChild(port)
        element.appendChild(ekey)
        element.appendChild(ports)
        
        #append module to the xml structure
        prj.controller.element.getElementsByTagName("Modules")[0].appendChild(element)
        #Add Module to modules dictionary
        prj.modules.append('Local', element)  
        

class Port(ElementAccess):
    """Accessor object for a module's port."""
    address = AttributeDescriptor('Address')
    type = AttributeDescriptor('Type', True)
