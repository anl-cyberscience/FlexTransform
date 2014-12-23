'''
Created on Aug 27, 2014

@author: cstras
'''

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
import uuid

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

    def __init__(self, tboxIRI):
        '''
        Constructor
        '''
        self.bmap = {"xform": self.XFORMNS}
        self.g = Graph()
        self.g.load(tboxIRI)
        for k in self.bmap:
            self.g.bind(k, self.bmap[k])
        
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
        
    def dumpGraph(self):
        print (self.g.serialize(format="n3"))