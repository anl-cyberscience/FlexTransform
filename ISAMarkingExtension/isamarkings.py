import ISAMarkingExtension.bindings.isamarkings as isa_binding
import stix.data_marking
from stix.data_marking import MarkingStructure

class ISAMarkingStructure(MarkingStructure):
    '''
    This marking extension was created to apply the SD-EDH Cyber Profile to ISA shared documents. 
    This is one of two extensions used to apply the SD-EDH Cyber profile: the ISA Markings Extension and the 
    ISA Markings Assertions Extension.
    '''
    _binding = isa_binding
    _binding_class = isa_binding.ISAMarkingStructureType
    _namespace = 'http://www.us-cert.gov/essa/Markings/ISAMarkings'
    _namespace_xsd = 'ISAMarkingsType.xsd'
    _XSI_TYPE = "edh2cyberMarking:ISAMarkingsType"

    def __init__(self, isam_version=None, identifier=None, createdatetime=None,
                 responsibleentity=None, authref=None):
        super(ISAMarkingStructure, self).__init__()
        self.isam_version = isam_version
        self.identifier = identifier
        self.createdatetime = createdatetime
        self.responsibleentity = responsibleentity
        self.authref = authref
        
    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        if identifier is None:
            self._identifier = None
        if isinstance(identifier, EDH2Text):
            self._identifier = identifier
        else:
            self._identifier = EDH2Text(value=identifier)
            
    @property
    def createdatetime(self):
        return self._createdatetime

    @createdatetime.setter
    def createdatetime(self, createdatetime):
        if createdatetime is None:
            self._createdatetime = None
        if isinstance(createdatetime, EDH2Text):
            self._createdatetime = createdatetime
        else:
            self._createdatetime = EDH2Text(value=createdatetime)
            
    @property
    def responsibleentity(self):
        return self._responsibleentity

    @responsibleentity.setter
    def responsibleentity(self, responsibleentity):
        if responsibleentity is None:
            self._responsibleentity = None
        if isinstance(responsibleentity, EDH2Text):
            self._responsibleentity = responsibleentity
        else:
            self._responsibleentity = EDH2Text(value=responsibleentity)
            
    @property
    def authref(self):
        return self._authref

    @authref.setter
    def authref(self, authref):
        if authref is None:
            self._authref = None
        if isinstance(authref, EDH2Text):
            self._authref = authref
        else:
            self._authref = EDH2Text(value=authref)

    def to_obj(self, return_obj=None, ns_info=None):
        super(ISAMarkingStructure, self).to_obj(return_obj=return_obj, ns_info=ns_info)
        
        ns_info.input_schemalocs.update({self._namespace: self._namespace_xsd})

        obj = self._binding_class()

        MarkingStructure.to_obj(self, return_obj=obj, ns_info=ns_info)

        obj.isam_version = self.isam_version
        
        if (self.identifier):
            obj.identifier = self.identifier.to_obj(ns_info=ns_info)
            
        if (self.createdatetime):
            obj.createdatetime = self.createdatetime.to_obj(ns_info=ns_info)
            
        if (self.responsibleentity):
            obj.responsibleentity = self.responsibleentity.to_obj(ns_info=ns_info)
        
        if (self.authref):
            obj.authref = self.authref.to_obj(ns_info=ns_info)

        return obj

    def to_dict(self):
        d = MarkingStructure.to_dict(self)
        if self.isam_version:
            d['isam_version'] = self.isam_version
            
        if self.identifier:
            d['identifier'] = self.identifier.to_dict()
            
        if self.createdatetime:
            d['createdatetime'] = self.createdatetime.to_dict()
            
        if self.responsibleentity:
            d['responsibleentity'] = self.responsibleentity.to_dict()
            
        if self.authref:
            d['authref'] = self.authref.to_dict()

        return d

    @staticmethod
    def from_obj(obj):
        if not obj:
            return None

        m = ISAMarkingStructure()
        MarkingStructure.from_obj(obj, m)
        m.isam_version = obj.isam_version
        m.identifier = EDH2Text.from_obj(obj.identifier)
        m.createdatetime = EDH2Text.from_obj(obj.createdatetime)
        m.responsibleentity = EDH2Text.from_obj(obj.responsibleentity)
        m.authref = EDH2Text.from_obj(obj.authref)

        return m

    @staticmethod
    def from_dict(marking_dict):
        if not marking_dict:
            return None

        m = ISAMarkingStructure()
        MarkingStructure.from_dict(marking_dict, m)
        m.isam_version = marking_dict.get('isam_version')
        
        if ('identifier' in marking_dict):
            m.identifier = EDH2Text.from_dict(marking_dict.get('identifier'))
        
        if ('createdatetime' in marking_dict):
            m.createdatetime = EDH2Text.from_dict(marking_dict.get('createdatetime'))
        
        if ('responsibleentity' in marking_dict):
            m.responsibleentity = EDH2Text.from_dict(marking_dict.get('responsibleentity'))
        
        if ('authref' in marking_dict):
            m.authref = EDH2Text.from_dict(marking_dict.get('authref'))

        return m

class ISAMarkingAssertionsStructure(MarkingStructure):
    '''
    This marking extension was created to apply the SD-EDH Cyber Profile to ISA shared documents. 
    This is one of two extensions used to apply the SD-EDH Cyber profile: the ISA Markings Extension and 
    the ISA Markings Assertions Extension.
    '''
    _binding = isa_binding
    _binding_class = isa_binding.ISAMarkingAssertionsStructureType
    _namespace = 'http://www.us-cert.gov/essa/Markings/ISAMarkingAssertions'
    _namespace_xsd = 'ISAMarkingsAssertionsType.xsd'
    _XSI_TYPE = "edh2cyberMarkingAssert:ISAMarkingsAssertionType"

    def __init__(self, isam_version=None, default_marking=None, most_restrictive=None, policyref=None,
                 accessprivilege=None, resourcedisposition=None, controlset=None, originalclassification=None,
                 derivativeclassification=None, declassification=None, publicrelease=None, addlreference=None):
        super(ISAMarkingAssertionsStructure, self).__init__()
        
        # Attributes
        self.isam_version = isam_version
        self.default_marking = default_marking
        self.most_restrictive = most_restrictive
        
        # Children
        self.policyref = policyref
        self.accessprivilege = accessprivilege
        self.resourcedisposition = resourcedisposition
        self.controlset = controlset
        self.originalclassification = originalclassification
        self.derivativeclassification = derivativeclassification
        self.declassification = declassification
        self.publicrelease = publicrelease
        self.addlreference = addlreference
        
    @property
    def policyref(self):
        return self._policyref

    @policyref.setter
    def policyref(self, policyref):
        if policyref is None:
            self._policyref = None
        if isinstance(policyref, EDH2Text):
            self._policyref = policyref
        else:
            self._policyref = EDH2Text(value=policyref)
            
    @property
    def accessprivilege(self):
        return self._accessprivilege

    @accessprivilege.setter
    def accessprivilege(self, accessprivilege):
        if accessprivilege is None:
            self._accessprivilege = None
        if isinstance(accessprivilege, EDH2Text):
            self._accessprivilege = accessprivilege
        else:
            self._accessprivilege = EDH2Text(value=accessprivilege)
            
    @property
    def resourcedisposition(self):
        return self._resourcedisposition

    @resourcedisposition.setter
    def resourcedisposition(self, resourcedisposition):
        if resourcedisposition is None:
            self._resourcedisposition = None
        if isinstance(resourcedisposition, EDH2Text):
            self._resourcedisposition = resourcedisposition
        else:
            self._resourcedisposition = EDH2Text(value=resourcedisposition)
            
    @property
    def controlset(self):
        return self._controlset

    @controlset.setter
    def controlset(self, controlset):
        if controlset is None:
            self._controlset = None
        if isinstance(controlset, EDH2Text):
            self._controlset = controlset
        else:
            self._controlset = EDH2Text(value=controlset)
            
    @property
    def originalclassification(self):
        return self._originalclassification

    @originalclassification.setter
    def originalclassification(self, originalclassification):
        if originalclassification is None:
            self._originalclassification = None
        if isinstance(originalclassification, EDH2Text):
            self._originalclassification = originalclassification
        else:
            self._originalclassification = EDH2Text(value=originalclassification)
                 
    @property
    def derivativeclassification(self):
        return self._derivativeclassification

    @derivativeclassification.setter
    def derivativeclassification(self, derivativeclassification):
        if derivativeclassification is None:
            self._derivativeclassification = None
        if isinstance(derivativeclassification, EDH2Text):
            self._derivativeclassification = derivativeclassification
        else:
            self._derivativeclassification = EDH2Text(value=derivativeclassification)
            
    @property
    def declassification(self):
        return self._declassification

    @declassification.setter
    def declassification(self, declassification):
        if declassification is None:
            self._declassification = None
        if isinstance(declassification, EDH2Text):
            self._declassification = declassification
        else:
            self._declassification = EDH2Text(value=declassification)
            
    @property
    def publicrelease(self):
        return self._publicrelease

    @publicrelease.setter
    def publicrelease(self, publicrelease):
        if publicrelease is None:
            self._publicrelease = None
        if isinstance(publicrelease, EDH2Text):
            self._publicrelease = publicrelease
        else:
            self._publicrelease = EDH2Text(value=publicrelease)
            
    @property
    def addlreference(self):
        return self._addlreference

    @addlreference.setter
    def addlreference(self, addlreference):
        if addlreference is None:
            self._addlreference = None
        elif isinstance(addlreference, AddlReference):
            self._addlreference = addlreference
        else:
            raise ValueError("addlreference must be of type AddlReference")

    def to_obj(self, return_obj=None, ns_info=None):
        super(ISAMarkingAssertionsStructure, self).to_obj(return_obj=return_obj, ns_info=ns_info)

        ns_info.input_schemalocs.update({self._namespace: self._namespace_xsd})
        
        obj = self._binding_class()

        MarkingStructure.to_obj(self, return_obj=obj, ns_info=ns_info)

        obj.isam_version = self.isam_version
        obj.default_marking = self.default_marking
        obj.most_restrictive = self.most_restrictive
        
        if (self.policyref):
            obj.policyref = self.policyref.to_obj(ns_info=ns_info)
            
        if (self.accessprivilege):
            obj.accessprivilege = self.accessprivilege.to_obj(ns_info=ns_info)
            
        if (self.resourcedisposition):
            obj.resourcedisposition = self.resourcedisposition.to_obj(ns_info=ns_info)
        
        if (self.controlset):
            obj.controlset = self.controlset.to_obj(ns_info=ns_info)
            
        if (self.originalclassification):
            obj.originalclassification = self.originalclassification.to_obj(ns_info=ns_info)
            
        if (self.derivativeclassification):
            obj.derivativeclassification = self.derivativeclassification.to_obj(ns_info=ns_info)
            
        if (self.declassification):
            obj.declassification = self.declassification.to_obj(ns_info=ns_info)
        
        if (self.publicrelease):
            obj.publicrelease = self.publicrelease.to_obj(ns_info=ns_info)

        if (self.addlreference):
            obj.addlreference = self.addlreference.to_obj(ns_info=ns_info)

        return obj

    def to_dict(self):
        d = MarkingStructure.to_dict(self)
        if self.isam_version:
            d['isam_version'] = self.isam_version

        if self.default_marking:
            d['default_marking'] = self.default_marking
            
        if self.most_restrictive:
            d['most_restrictive'] = self.most_restrictive
            
        if self.policyref:
            d['policyref'] = self.policyref.to_dict()
            
        if self.accessprivilege:
            d['accessprivilege'] = self.accessprivilege.to_dict()
            
        if self.resourcedisposition:
            d['resourcedisposition'] = self.resourcedisposition.to_dict()
            
        if self.controlset:
            d['controlset'] = self.controlset.to_dict()
            
        if self.originalclassification:
            d['originalclassification'] = self.originalclassification.to_dict()
            
        if self.derivativeclassification:
            d['derivativeclassification'] = self.derivativeclassification.to_dict()
            
        if self.declassification:
            d['declassification'] = self.declassification.to_dict()
            
        if self.publicrelease:
            d['publicrelease'] = self.publicrelease.to_dict()

        if self.addlreference:
            d['addlreference'] = self.addlreference.to_dict()
            
        return d

    @staticmethod
    def from_obj(obj):
        if not obj:
            return None

        m = ISAMarkingAssertionsStructure()
        MarkingStructure.from_obj(obj, m)
        m.isam_version = obj.isam_version
        m.default_marking = obj.default_marking
        m.most_restrictive = obj.most_restrictive
        
        m.policyref = EDH2Text.from_obj(obj.policyref)
        m.accessprivilege = EDH2Text.from_obj(obj.accessprivilege)
        m.resourcedisposition = EDH2Text.from_obj(obj.resourcedisposition)
        m.controlset = EDH2Text.from_obj(obj.controlset)
        m.originalclassification = EDH2Text.from_obj(obj.originalclassification)
        m.derivativeclassification = EDH2Text.from_obj(obj.derivativeclassification)
        m.declassification = EDH2Text.from_obj(obj.declassification)
        m.publicrelease = EDH2Text.from_obj(obj.publicrelease)
        
        m.addlreference = AddlReference.from_obj(obj.addlreference)

        return m

    @staticmethod
    def from_dict(marking_dict):
        if not marking_dict:
            return None

        m = ISAMarkingAssertionsStructure()
        MarkingStructure.from_dict(marking_dict, m)
        m.isam_version = marking_dict.get('isam_version')
        m.default_marking = marking_dict.get('default_marking')
        m.most_restrictive = marking_dict.get('most_restrictive')
        
        if ('policyref' in marking_dict):
            m.policyref = EDH2Text.from_dict(marking_dict.get('policyref'))
        
        if ('accessprivilege' in marking_dict):
            m.accessprivilege = EDH2Text.from_dict(marking_dict.get('accessprivilege'))
        
        if ('resourcedisposition' in marking_dict):
            m.resourcedisposition = EDH2Text.from_dict(marking_dict.get('resourcedisposition'))
        
        if ('controlset' in marking_dict):
            m.controlset = EDH2Text.from_dict(marking_dict.get('controlset'))
            
        if ('originalclassification' in marking_dict):
            m.originalclassification = EDH2Text.from_dict(marking_dict.get('originalclassification'))
        
        if ('derivativeclassification' in marking_dict):
            m.derivativeclassification = EDH2Text.from_dict(marking_dict.get('derivativeclassification'))
        
        if ('declassification' in marking_dict):
            m.declassification = EDH2Text.from_dict(marking_dict.get('declassification'))
        
        if ('publicrelease' in marking_dict):
            m.publicrelease = EDH2Text.from_dict(marking_dict.get('publicrelease'))
            
        if ('addlreference' in marking_dict):
            m.addlreference = AddlReference.from_dict(marking_dict.get('addlreference'))

        return m

class EDH2Text(stix.Entity):
    _binding = isa_binding
    _binding_class = isa_binding.EDH2TextType
    _namespace = 'urn:edm:edh:v2'
    _namespace_xsd = 'SD-EDH_Profile_Cyber.xsd'
    _XSI_NS = "edh2"

    def __init__(self, value=None):
        self.value = value

    def to_obj(self, return_obj=None, ns_info=None):
        super(EDH2Text, self).to_obj(return_obj=return_obj, ns_info=ns_info)

        ns_info.input_schemalocs.update({self._namespace: self._namespace_xsd})
        
        text_obj = self._binding_class()

        text_obj.valueOf_ = self.value
        return text_obj

    def to_dict(self):
        # Return a plain string if there is no format specified.
        return self.value

    @classmethod
    def from_obj(cls, text_obj):
        if not text_obj:
            return None

        text = EDH2Text()

        text.value = text_obj.valueOf_

        return text

    @classmethod
    def from_dict(cls, text_dict):
        if text_dict is None:
            return None

        text = EDH2Text()

        if not isinstance(text_dict, dict):
            text.value = text_dict
        else:
            text.value = text_dict.get('value')

        return text
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")

    def __unicode__(self):
        return str(self.value)

class AddlReference(stix.Entity):
    _namespace = 'http://www.us-cert.gov/essa/Markings/ISAMarkingAssertions'
    _binding = isa_binding
    _binding_class = isa_binding.AddlReferenceType

    def __init__(self, url=None, comment=None):
        self.url = url
        self.comment = comment

    def to_obj(self, return_obj=None, ns_info=None):
        super(AddlReference, self).to_obj(return_obj=return_obj, ns_info=ns_info)

        obj = self._binding_class()

        if self.url:
            obj.url = self.url
        if self.comment:
            obj.comment = self.comment

        return obj

    def to_dict(self):
        d = {}
        if self.url:
            d['url'] = self.url
        if self.comment:
            d['coment'] = self.comment
            
        return d

    @staticmethod
    def from_obj(obj):       
        if not obj:
            return None
        a = AddlReference()

        a.url = obj.url
        a.comment = obj.comment

        return a

    @staticmethod
    def from_dict(dict_):       
        if dict_ is None:
            return None
        a = AddlReference()

        a.url = dict_.get('url')
        a.comment = dict_.get('comment')

        return a

stix.data_marking.add_extension(ISAMarkingStructure)
stix.data_marking.add_extension(ISAMarkingAssertionsStructure)

