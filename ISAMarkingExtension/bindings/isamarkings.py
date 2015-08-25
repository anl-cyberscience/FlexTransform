# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated Thu Apr 11 15:07:50 2013 by generateDS.py version 2.9a.
#

import sys
from stix.bindings import *
from stix.bindings import _cast
import stix.bindings.data_marking as data_marking_binding

XML_NS = "http://data-marking.mitre.org/extensions/MarkingStructure#EDH2Cyber-1"
XML_NS_Assertion = "http://data-marking.mitre.org/extensions/MarkingAssertion#EDH2Cyber-1"
XML_NS_EDH2 = "urn:edm:edh:v2"

#
# Data representation classes.
#

class ISAMarkingStructureType(data_marking_binding.MarkingStructureType):
    '''
    This marking extension was created to apply the SD-EDH Cyber Profile to ISA shared documents. 
    This is one of two extensions used to apply the SD-EDH Cyber profile: the ISA Markings Extension and the 
    ISA Markings Assertions Extension.
    '''
    subclass = None
    superclass = data_marking_binding.MarkingStructureType
    def __init__(self, marking_model_ref=None, marking_model_name=None, isam_version=None, identifier=None, 
                 createdatetime=None, responsibleentity=None, authref=None):
        super(ISAMarkingStructureType, self).__init__(marking_model_ref=marking_model_ref, marking_model_name=marking_model_name)
        self.xmlns          = XML_NS
        self.xmlns_prefix   = "edh2cyberMarking"
        self.xml_type       = "ISAMarkingsType"
        
        # Attributes
        self.isam_version = isam_version
        
        # Children
        self.identifier = identifier
        self.createdatetime = createdatetime
        self.responsibleentity = responsibleentity
        self.authref = authref

    def factory(*args_, **kwargs_):
        if ISAMarkingStructureType.subclass:
            return ISAMarkingStructureType.subclass(*args_, **kwargs_)
        else:
            return ISAMarkingStructureType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_isam_version(self): return self.isam_version
    def set_isam_version(self, isam_version): self.isam_version = isam_version
    def get_identifier(self): return self.identifier
    def set_identifier(self, identifier): self.identifier = identifier
    def get_createdatetime(self): return self.createdatetime
    def set_createdatetime(self, createdatetime): self.createdatetime = createdatetime
    def get_responsibleentity(self): return self.responsibleentity
    def set_responsibleentity(self, responsibleentity): self.responsibleentity = responsibleentity
    def get_authref(self): return self.authref
    def set_authref(self, authref): self.authref = authref
    def hasContent_(self):
        if (
            self.identifier is not None or
            self.createdatetime is not None or
            self.responsibleentity is not None or
            self.authref is not None or
            super(ISAMarkingStructureType, self).hasContent_()
            ):
            return True
        else:
            return False
    def export(self, lwrite, level, nsmap, namespace_=XML_NS, name_='ISAMarkingStructureType', namespacedef_='', pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(lwrite, level, pretty_print)
        lwrite('<%s:%s%s' % (nsmap[namespace_], name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self.exportAttributes(lwrite, level, already_processed, namespace_, name_='ISAMarkingStructureType')
        if self.hasContent_():
            lwrite('>%s' % (eol_, ))
            self.exportChildren(lwrite, level + 1, nsmap, XML_NS, name_, pretty_print=pretty_print)
            showIndent(lwrite, level, pretty_print)
            lwrite('</%s:%s>%s' % (nsmap[namespace_], name_, eol_))
        else:
            lwrite('/>%s' % (eol_, ))
    def exportAttributes(self, lwrite, level, already_processed, namespace_='edh2cyberMarking:', name_='ISAMarkingStructureType'):
        super(ISAMarkingStructureType, self).exportAttributes(lwrite, level, already_processed, namespace_, name_='ISAMarkingStructureType')
        if 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            xsi_type = " xsi:type='%s:%s'" % (self.xmlns_prefix, self.xml_type)
            lwrite(xsi_type)
        if self.isam_version is not None and 'isam_version' not in already_processed:
            already_processed.add('isam_version')
            lwrite(' isam_version=%s' % (quote_attrib(self.isam_version), ))
    def exportChildren(self, lwrite, level, nsmap, namespace_=XML_NS, name_='ISAMarkingStructureType', fromsubclass_=False, pretty_print=True):
        super(ISAMarkingStructureType, self).exportChildren(lwrite, level, nsmap, namespace_, name_, True, pretty_print=pretty_print)
        if self.identifier.valueOf_ is not None:
            self.identifier.export(lwrite, level, nsmap, XML_NS_EDH2, name_='Identifier', pretty_print=pretty_print)
        if self.createdatetime.valueOf_ is not None:
            self.createdatetime.export(lwrite, level, nsmap, XML_NS_EDH2, name_='CreateDateTime', pretty_print=pretty_print)
        if self.responsibleentity.valueOf_ is not None:
            self.responsibleentity.export(lwrite, level, nsmap, XML_NS_EDH2, name_='ResponsibleEntity', pretty_print=pretty_print)
        if self.authref.valueOf_ is not None:
            self.authref.export(lwrite, level, nsmap, XML_NS_EDH2, name_='AuthRef', pretty_print=pretty_print)
    def build(self, node):
        already_processed = set()
        self.buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
    def buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('isam_version', node)
        if value is not None and 'isam_version' not in already_processed:
            already_processed.add('isam_version')
            self.isam_version = value
        super(ISAMarkingStructureType, self).buildAttributes(node, attrs, already_processed)
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        super(ISAMarkingStructureType, self).buildChildren(child_, node, nodeName_, True)
        if nodeName_ == 'Identifier':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_identifier(obj_)
        if nodeName_ == 'CreateDateTime':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_createdatetime(obj_)
        if nodeName_ == 'ResponsibleEntity':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_responsibleentity(obj_)
        if nodeName_ == 'AuthRef':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_authref(obj_)
# end class ISAMarkingStructureType

class ISAMarkingAssertionsStructureType(data_marking_binding.MarkingStructureType):
    '''
    This marking extension was created to apply the SD-EDH Cyber Profile to ISA shared documents. 
    This is one of two extensions used to apply the SD-EDH Cyber profile: the ISA Markings Extension and 
    the ISA Markings Assertions Extension.
    '''
    subclass = None
    superclass = data_marking_binding.MarkingStructureType
    def __init__(self, marking_model_ref=None, marking_model_name=None, isam_version=None, default_marking=None, 
                 most_restrictive=None, policyref=None, accessprivilege=None, resourcedisposition=None, 
                 controlset=None, originalclassification=None, derivativeclassification=None, declassification=None, 
                 publicrelease=None, addlreference=None):
        super(ISAMarkingAssertionsStructureType, self).__init__(marking_model_ref=marking_model_ref, marking_model_name=marking_model_name)
        self.xmlns          = XML_NS_Assertion
        self.xmlns_prefix   = "edh2cyberMarkingAssert"
        self.xml_type       = "ISAMarkingsAssertionType"
        
        # Attributes
        self.isam_version = isam_version
        self.default_marking = _cast(bool, default_marking)
        self.most_restrictive = _cast(bool, most_restrictive)
        
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
        
    def factory(*args_, **kwargs_):
        if ISAMarkingAssertionsStructureType.subclass:
            return ISAMarkingAssertionsStructureType.subclass(*args_, **kwargs_)
        else:
            return ISAMarkingAssertionsStructureType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_isam_version(self): return self.isam_version
    def set_isam_version(self, isam_version): self.isam_version = isam_version
    def get_default_marking(self): return self.default_marking
    def set_default_marking(self, default_marking): self.default_marking = default_marking
    def get_most_restrictive(self): return self.most_restrictive
    def set_most_restrictive(self, most_restrictive): self.most_restrictive = most_restrictive
    def get_policyref(self): return self.policyref
    def set_policyref(self, policyref): self.policyref = policyref
    def get_accessprivilege(self): return self.accessprivilege
    def set_accessprivilege(self, accessprivilege): self.accessprivilege = accessprivilege
    def get_resourcedisposition(self): return self.resourcedisposition
    def set_resourcedisposition(self, resourcedisposition): self.resourcedisposition = resourcedisposition
    def get_controlset(self): return self.controlset
    def set_controlset(self, controlset): self.controlset = controlset
    def get_originalclassification(self): return self.originalclassification
    def set_originalclassification(self, originalclassification): self.originalclassification = originalclassification
    def get_derivativeclassification(self): return self.derivativeclassification
    def set_derivativeclassification(self, derivativeclassification): self.derivativeclassification = derivativeclassification
    def get_declassification(self): return self.declassification
    def set_declassification(self, declassification): self.declassification = declassification
    def get_publicrelease(self): return self.publicrelease
    def set_publicrelease(self, publicrelease): self.publicrelease = publicrelease
    def get_addlreference(self): return self.addlreference
    def set_addlreference(self, addlreference): self.addlreference = addlreference
    def hasContent_(self):
        if (
            self.policyref is not None or
            self.accessprivilege is not None or
            self.resourcedisposition is not None or
            self.controlset is not None or
            self.originalclassification is not None or
            self.derivativeclassification is not None or
            self.declassification is not None or
            self.publicrelease is not None or
            self.addlreference is not None or
            super(ISAMarkingAssertionsStructureType, self).hasContent_()
            ):
            return True
        else:
            return False
    def export(self, lwrite, level, nsmap, namespace_=XML_NS_Assertion, name_='ISAMarkingAssertionsStructureType', namespacedef_='', pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(lwrite, level, pretty_print)
        lwrite('<%s:%s%s' % (nsmap[namespace_], name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self.exportAttributes(lwrite, level, already_processed, namespace_, name_='ISAMarkingAssertionsStructureType')
        if self.hasContent_():
            lwrite('>%s' % (eol_, ))
            self.exportChildren(lwrite, level + 1, nsmap, XML_NS_Assertion, name_, pretty_print=pretty_print)
            showIndent(lwrite, level, pretty_print)
            lwrite('</%s:%s>%s' % (nsmap[namespace_], name_, eol_))
        else:
            lwrite('/>%s' % (eol_, ))
    def exportAttributes(self, lwrite, level, already_processed, namespace_='edh2cyberMarking:', name_='ISAMarkingAssertionsStructureType'):
        super(ISAMarkingAssertionsStructureType, self).exportAttributes(lwrite, level, already_processed, namespace_, name_='ISAMarkingAssertionsStructureType')
        if 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            xsi_type = " xsi:type='%s:%s'" % (self.xmlns_prefix, self.xml_type)
            lwrite(xsi_type)
        if self.isam_version is not None and 'isam_version' not in already_processed:
            already_processed.add('isam_version')
            lwrite(' isam_version=%s' % (quote_attrib(self.isam_version), ))
        if self.default_marking is not None and 'default_marking' not in already_processed:
            already_processed.add('default_marking')
            lwrite(' default_marking="%s"' % self.gds_format_boolean(self.default_marking, input_name='default_marking'))
        if self.most_restrictive is not None and 'most_restrictive' not in already_processed:
            already_processed.add('most_restrictive')
            lwrite(' most_restrictive="%s"' % self.gds_format_boolean(self.most_restrictive, input_name='most_restrictive'))
    def exportChildren(self, lwrite, level, nsmap, namespace_=XML_NS_Assertion, name_='ISAMarkingAssertionsStructureType', fromsubclass_=False, pretty_print=True):
        super(ISAMarkingAssertionsStructureType, self).exportChildren(lwrite, level, nsmap, namespace_, name_, True, pretty_print=pretty_print)
        if self.policyref.valueOf_ is not None:
            self.policyref.export(lwrite, level, nsmap, XML_NS_EDH2, name_='PolicyRef', pretty_print=pretty_print)
        if self.accessprivilege.valueOf_ is not None:
            self.accessprivilege.export(lwrite, level, nsmap, XML_NS_EDH2, name_='AccessPrivilege', pretty_print=pretty_print)
        if self.resourcedisposition.valueOf_ is not None:
            self.resourcedisposition.export(lwrite, level, nsmap, XML_NS_EDH2, name_='ResourceDisposition', pretty_print=pretty_print)
        if self.controlset.valueOf_ is not None:
            self.controlset.export(lwrite, level, nsmap, XML_NS_EDH2, name_='ControlSet', pretty_print=pretty_print)
        if self.originalclassification.valueOf_ is not None:
            self.originalclassification.export(lwrite, level, nsmap, XML_NS_EDH2, name_='OriginalClassification', pretty_print=pretty_print)
        if self.derivativeclassification.valueOf_ is not None:
            self.derivativeclassification.export(lwrite, level, nsmap, XML_NS_EDH2, name_='DerivativeClassification', pretty_print=pretty_print)
        if self.declassification.valueOf_ is not None:
            self.declassification.export(lwrite, level, nsmap, XML_NS_EDH2, name_='Declassification', pretty_print=pretty_print)
        if self.publicrelease.valueOf_ is not None:
            self.publicrelease.export(lwrite, level, nsmap, XML_NS_EDH2, name_='PublicRelease', pretty_print=pretty_print)
        if self.addlreference is not None and ( self.addlreference.url is not None or self.addlreference.comment is not None ):
            self.addlreference.export(lwrite, level, nsmap, namespace_, name_='AddlReference', pretty_print=pretty_print)
    def build(self, node):
        already_processed = set()
        self.buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
    def buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('isam_version', node)
        if value is not None and 'isam_version' not in already_processed:
            already_processed.add('isam_version')
            self.isam_version = value
        value = find_attr_value_('default_marking', node)
        if value is not None and 'default_marking' not in already_processed:
            already_processed.add('default_marking')
            if value in ('true', '1'):
                self.default_marking = True
            elif value in ('false', '0'):
                self.default_marking = False
            else:
                raise_parse_error(node, 'Bad boolean attribute')
        value = find_attr_value_('most_restrictive', node)
        if value is not None and 'most_restrictive' not in already_processed:
            already_processed.add('most_restrictive')
            if value in ('true', '1'):
                self.most_restrictive = True
            elif value in ('false', '0'):
                self.most_restrictive = False
            else:
                raise_parse_error(node, 'Bad boolean attribute')
        super(ISAMarkingAssertionsStructureType, self).buildAttributes(node, attrs, already_processed)
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        super(ISAMarkingAssertionsStructureType, self).buildChildren(child_, node, nodeName_, True)
        if nodeName_ == 'PolicyRef':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_policyref(obj_)
        if nodeName_ == 'AccessPrivilege':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_accessprivilege(obj_)
        if nodeName_ == 'ResourceDisposition':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_resourcedisposition(obj_)
        if nodeName_ == 'ControlSet':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_controlset(obj_)
        if nodeName_ == 'OriginalClassification':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_originalclassification(obj_)
        if nodeName_ == 'DerivativeClassification':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_derivativeclassification(obj_)
        if nodeName_ == 'Declassification':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_declassification(obj_)
        if nodeName_ == 'PublicRelease':
            obj_ = EDH2TextType.factory()
            obj_.build(child_)
            self.set_publicrelease(obj_)
        if nodeName_ == 'AddlReference':
            obj_ = AddlReferenceType.factory()
            obj_.build(child_)
            self.set_addlreference(obj_)
# end class ISAMarkingStructureType

class EDH2TextType(GeneratedsSuper):
    """ """
    subclass = None
    superclass = None
    def __init__(self, valueOf_=None):
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if EDH2TextType.subclass:
            return EDH2TextType.subclass(*args_, **kwargs_)
        else:
            return EDH2TextType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def hasContent_(self):
        if (
            self.valueOf_
            ):
            return True
        else:
            return False
    def export(self, lwrite, level, nsmap, namespace_=XML_NS_EDH2, name_='EDH2TextType', namespacedef_='', pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(lwrite, level, pretty_print)
        lwrite('<%s:%s%s' % (nsmap[namespace_], name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        if self.hasContent_():
            lwrite('>')
            lwrite(str(quote_xml(self.valueOf_)))
            lwrite('</%s:%s>%s' % (nsmap[namespace_], name_, eol_))
        else:
            lwrite('/>%s' % (eol_, ))
    def exportAttributes(self, lwrite, level, already_processed, namespace_='edh2:', name_='EDH2TextType'):
        pass
    def exportChildren(self, lwrite, level, nsmap, namespace_=XML_NS_EDH2, name_='EDH2TextType', fromsubclass_=False, pretty_print=True):
        pass
    def build(self, node):
        already_processed = set()
        self.buildAttributes(node, node.attrib, already_processed)
        self.valueOf_ = get_all_text_(node)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        pass
# end class EDH2TextType

class AddlReferenceType(GeneratedsSuper):
    """ """
    subclass = None
    superclass = None
    def __init__(self, url=None, comment=None):
        self.url = url
        self.comment = comment
    def factory(*args_, **kwargs_):
        if AddlReferenceType.subclass:
            return AddlReferenceType.subclass(*args_, **kwargs_)
        else:
            return AddlReferenceType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_url(self): return self.url
    def set_url(self, url): self.url = url
    def get_comment(self): return self.comment
    def set_comment(self, comment): self.comment = comment
    def hasContent_(self):
        if (
            self.url is not None or
            self.comment is not None
            ):
            return True
        else:
            return False
    def export(self, lwrite, level, nsmap, namespace_=XML_NS_Assertion, name_='AddlReference', namespacedef_='', pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(lwrite, level, pretty_print)
        lwrite('<%s:%s%s' % (nsmap[namespace_], name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        if self.hasContent_():
            lwrite('>%s' % (eol_, ))
            self.exportChildren(lwrite, level + 1, nsmap, XML_NS_Assertion, name_, pretty_print=pretty_print)
            showIndent(lwrite, level, pretty_print)
            lwrite('</%s:%s>%s' % (nsmap[namespace_], name_, eol_))
        else:
            lwrite('/>%s' % (eol_, ))
    def exportAttributes(self, lwrite, level, already_processed, namespace_='edh2cyberMarkingAssert:', name_='AddlReferenceType'):
        pass
    def exportChildren(self, lwrite, level, nsmap, namespace_=XML_NS_Assertion, name_='AddlReferenceType', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.url is not None:
            showIndent(lwrite, level, pretty_print)
            lwrite('<%s:URL>%s</%s:URL>%s' % (nsmap[namespace_], self.gds_format_string(quote_xml(self.url), input_name='URL'), nsmap[namespace_], eol_))
        if self.comment is not None:
            showIndent(lwrite, level, pretty_print)
            lwrite('<%s:Comment>%s</%s:Comment>%s' % (nsmap[namespace_], self.gds_format_string(quote_xml(self.comment), input_name='Comment'), nsmap[namespace_], eol_))
    def build(self, node):
        already_processed = set()
        self.buildAttributes(node, node.attrib, already_processed)
        self.valueOf_ = get_all_text_(node)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        if nodeName_ == 'URL':
            URL = child_.text
            URL = self.gds_validate_string(URL, node, 'URL')
            self.url = URL
        if nodeName_ == 'Comment':
            Comment = child_.text
            Comment = self.gds_validate_string(Comment, node, 'Comment')
            self.comment = Comment
# end class AddlReferenceType

GDSClassesMapping = {}

USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
"""

def usage():
    print(USAGE_TEXT)
    sys.exit(1)

def get_root_tag(node):
    tag = Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = GDSClassesMapping.get(tag)
    if rootClass is None:
        rootClass = globals().get(tag)
    return tag, rootClass

def parse(inFileName):
    doc = parsexml_(inFileName)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ISAMarkingStructureType'
        rootClass = ISAMarkingStructureType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    # sys.stdout.write('<?xml version="1.0" ?>\n')
    # rootObj.export(sys.stdout, 0, name_=rootTag,
    #     namespacedef_='',
    #     pretty_print=True)
    return rootObj

def parseEtree(inFileName):
    doc = parsexml_(inFileName)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ISAMarkingStructureType'
        rootClass = ISAMarkingStructureType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    rootElement = rootObj.to_etree(None, name_=rootTag)
    content = etree_.tostring(rootElement, pretty_print=True,
        xml_declaration=True, encoding="utf-8")
    sys.stdout.write(content)
    sys.stdout.write('\n')
    return rootObj, rootElement

def parseString(inString):
    from io import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ISAMarkingStructureType'
        rootClass = ISAMarkingStructureType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    # sys.stdout.write('<?xml version="1.0" ?>\n')
    # rootObj.export(sys.stdout, 0, name_="ISAMarkingStructureType",
    #     namespacedef_='')
    return rootObj

def main():
    args = sys.argv[1:]
    if len(args) == 1:
        parse(args[0])
    else:
        usage()

if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()

__all__ = [
    "ISAMarkingStructureType",
    "ISAMarkingAssertionsStructureType",
    "EDH2TextType",
    "AddlReferenceType"
    ]
