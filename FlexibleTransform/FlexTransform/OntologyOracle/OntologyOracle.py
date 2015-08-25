'''
Created on Aug 27, 2014

@author: cstras
'''

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
import uuid
import logging

class Oracle(object):
    '''
    classdocs
    '''
    BASEIRI = "http://www.anl.gov/cfm/ontologies/transform.owl"
    XFORMNS = Namespace("%s#"%(BASEIRI))

    ''' Define Class Names '''
    SEMANTICCOMPONENT = URIRef("%s#%s"%(BASEIRI,"SemanticComponent"))
    
    ''' Define Properties '''
    HASSEMANTICCONCEPT = XFORMNS.hasSemanticConcept
    HASSEMANTICVALUE = XFORMNS.hasSemanticValue

    def __init__(self, tboxLoc):
        '''
        Constructor
        '''
        self.bmap = {"xform": self.XFORMNS}
        self.g = Graph()
        self.g.load(tboxLoc)
        for k in self.bmap:
            self.g.bind(k, self.bmap[k])
        logging.getLogger("FlexibleTransform")
        
    def addSemanticComponent(self, semanticConceptClassIRI, semanticValueClassIRI ):
        '''
        Create new components in the given semantic concept class and value class,
        and create a new semantic component with those attributes
        '''
        semValClassURIRef = URIRef("%s#%s"%(self.BASEIRI,semanticValueClassIRI))
        semConClassURIRef = URIRef("%s#%s"%(self.BASEIRI,semanticConceptClassIRI))

        ciUUID = uuid.uuid4()
        conceptIndividual = URIRef("%s#%s-%s"%(self.BASEIRI,"concept",ciUUID))
        self.g.add((conceptIndividual, RDF.type, semConClassURIRef))

        ciUUID = uuid.uuid4()
        valueIndividual = URIRef("%s#%s-%s"%(self.BASEIRI,"value",ciUUID))
        self.g.add((valueIndividual, RDF.type, semValClassURIRef))
        
        ciUUID = uuid.uuid4()
        componentIndividual = URIRef("%s#%s-%s"%(self.BASEIRI,"component",ciUUID))
        self.g.add((componentIndividual, RDF.type, self.SEMANTICCOMPONENT))
        self.g.add((componentIndividual, self.HASSEMANTICCONCEPT, conceptIndividual))
        self.g.add((componentIndividual, self.HASSEMANTICVALUE, valueIndividual))

    def getSemanticComponentList(self):
        '''
        Return a list of lists - semantic components, along with their concept and values
        '''
        toReturn = list()
        
        ''' Get all of the individuals in the component class '''
        components = self.g.subjects(RDF.type, self.SEMANTICCOMPONENT)
        for compIndividual in components:
            cTemp = list()
            cTemp.append(compIndividual)
            '''TODO: Need to deal with having multiple associated concepts/values
                     with a single semantic component.
            '''
            conGen = self.g.objects(compIndividual, self.HASSEMANTICCONCEPT)
            for conIndividual in conGen:
                cTemp.append(conIndividual)
            valGen = self.g.objects(compIndividual, self.HASSEMANTICVALUE)
            for valIndividual in valGen:
                cTemp.append(valIndividual)
            toReturn.append(cTemp)
        return toReturn
    
    def addSemanticComponentIndividual(self, classIRI, individualValue, individualName=None):
        '''
        Add the given individual value to the classIRI, which must be a subclass of SemanticComponent.
        Parameters:
          * classIRI - The direct parent class to place the individual in
          * individualValue - The value of the individual
          * individualName - The name of the individual, if desired (if not set, one will be generated)
        Returns:
          * The Individual name URI
        '''
        
        if individualName == None:
            ''' Generate a name - use ClassName-UUIDv4 '''
            individualName = "{0}-{1}".format(classIRI, str(uuid.uuid4()))
            
        ''' TODO: Check to ensure a provided individualName is absolute, and is
            prefixed with the correct IRI; if not, warn / error.
        '''
        v = Literal(individualValue)
        n = URIRef(individualName)
        c = URIRef(classIRI)
        
        ''' First, insert the individual as an element of the parent class. '''
        #triple = "{0} {1} {2} .".format(n, RDF.type, c)
        #sq = " INSERT DATA { %s } "%(triple)
        self.g.add((n, RDF.type, c))

        ''' Second, add the value to the individual.'''
        self.g.add((n, self.XFORMNS.hasValue, v))
        
        return individualName
    
    def getCompatibleConcepts(self,OntologyReference):
        '''
        Given a reference to an ontological concept, will return a list of compatible concepts in
        preference order as a tuple (list(IRIs),semantic loss type) .  The current preference ordering 
        is according to:
        * Exact match > Specialization(n) > Generalization(n)
        If none can be found, will return 'None'
        '''
        print ("Not yet implemented.")
    
    def generalizeSemanticComponent(self,individualIRI):
        '''
        '''
        print ("Not yet implemented.")

    def specializeSemanticComponent(self,individualIRI):
        '''
        '''
        print ("Not yet implemented.")
       
    def dumpGraph(self):
        print (self.g.serialize(format="n3"))