'''
Created on Aug 27, 2014

@author: cstras
'''

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from collections import namedtuple
import uuid
import logging
from uuid import uuid4

class Oracle(object):
    '''
    classdocs
    '''
    BASEIRI = "http://www.anl.gov/cfm/transform.owl"
    XFORMNS = Namespace("%s#"%(BASEIRI))

    ''' Define Class Names '''
    SEMANTICCOMPONENT = URIRef("%s#%s"%(BASEIRI,"SemanticComponent"))
    
    ''' Define Properties '''
    HASSEMANTICCONCEPT = XFORMNS.hasSemanticConcept
    HASSEMANTICVALUE = XFORMNS.hasSemanticValue
    
    ''' Definie Data Elements '''
    GENERALIZATION = 1
    SPECIALIZATION = 2
    EXACTMATCH = 3

    def __init__(self, tboxLoc, schemaIRI):
        '''
        Constructor
        '''
        self.bmap = {"xform": self.XFORMNS,
                     "rdfs" : RDFS }
        self.g = Graph()
        self.g.load(tboxLoc)
        for k in self.bmap:
            self.g.bind(k, self.bmap[k])
        self.schemaReference = schemaIRI
        logging.getLogger("FlexTransform")
        
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
        
    def buildABOX(self, sourceData):
        '''
        Given a data structure of the form:
        
        Will add individuals to support the transformation.
        '''
        # First, add simple mapping types:
        for category in sourceData.keys():
            if isinstance(sourceData[category], dict):
                dictList = [sourceData[category]]
            else:
                dictList = sourceData[category]
            for d in dictList:
                for schema_element_name in d:
                    # Look for specific fields now:
                    current_fragment = d[schema_element_name]
                    if type(current_fragment) == dict and \
                       "ontologyMapping" in current_fragment.keys() and \
                       "ontologyMappingType" in current_fragment.keys() and \
                       current_fragment["ontologyMappingType"] == "simple": 
                        ## Add an individual to the ontology in the given class
                        parentClass = URIRef(current_fragment["ontologyMapping"])
                        individual = URIRef("%s-ind-%s"%(parentClass,uuid4().__str__()))
                        self.g.add((individual, RDF.type, parentClass))

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
        preference order as a tuple (list(IRI,semantic loss type,distance)) .  The current preference ordering 
        is according to:
        * Exact match > Generalization(n) > Specialization(n) 
        If none can be found, will return an empty list
        
        To determine what concepts are compatible, the ABOX needs to represent:
        1) The source schema elements that are present
            This is covered by the call to 'buildABOX' made with the mapped data as an argument.
        2) The target schema elements that are required, and what semantic concepts they map to
            This is represented by the relations "supportsSemanticComponent" and "requiresSemanticComponent"
        '''
        returnValue = list()
        ourResult = namedtuple("ourResult", ["IRI", "stype", "distance"])
        ## Determine the class hierarchy of the OntologyReference - get this as a list in order from most to least
        ## specific.
        
        ## Determine which 'required' and 'supported' semantic component class hierarchies are indicated by
        ## the target schema.
        
        # Make sure the ontology knows about this concept.  If not, print a warning and return.
        sanityQuery = """SELECT ?parent WHERE {
    <%s> rdfs:subClassOf ?parent .
}"""%(OntologyReference)
        resList = self.g.query(sanityQuery, initNs = self.bmap)
        if len(resList) == 0:
            ## Uh-oh!
            raise Exception("SemanticMapping not present in ontology (%s)"%OntologyReference)
        
        # First check to see if we have an exact match:
        #
        # SELECT ?required
        # WHERE {
        #     this.schemaReference cfm:requiresComponent ?required .
        # }
        #
        xQuery = """ASK WHERE {
<%s> <%s> <%s> .
}"""%(self.schemaReference, self.XFORMNS.requiresComponent, OntologyReference)

        resList = self.g.query(xQuery, initNs = self.bmap)
        if resList:
            ## Found an exact match!
            returnValue.append(ourResult(OntologyReference, self.EXACTMATCH, 0))
        else:
            # SELECT ?supported
            # WHERE {
            #     this.schemaReference cfm:supportsSemanticComponent ?supported .
            # }
            xQuery = """ASK WHERE {
<%s> <%s> <%s> .
}"""%(self.schemaReference, self.XFORMNS.supportsSemanticComponent, OntologyReference)
            resList = self.g.query(xQuery, initNs = self.bmap)
            if resList:
                ## Found an exact match!
                returnValue.append(ourResult(OntologyReference, self.EXACTMATCH, 0))

        ## Now start the hierarchy search
        parent = OntologyReference
        distance = 0
        stillLooking = True
        ceiling = self.XFORMNS.SemanticComponent
        relation = self.XFORMNS.requiresComponent
        childList = list()
        childList.append(OntologyReference)

        while stillLooking:
            stillLooking = False
            distance = distance + 1
            if not parent == ceiling and parent is not None:
                # Continue looking:
                stillLooking = True
                result = self.stepUpHierarchy(parent, relation, self.schemaReference)
                parent = result.individual
                if result.matchValue:
                    # We've found one, add it!
                    returnValue.append(ourResult(result.individual,self.GENERALIZATION,distance))
            if len(childList) > 0:
                stillLooking = True
                newChildList = list()
                for child in childList:
                    resList = self.stepDownHierarchy(child, relation, self.schemaReference)
                    for resultElement in resList:
                        newChildList.append(resultElement.individual)
                        if resultElement.matchValue:
                            # We found a result!
                            returnValue.append(ourResult(resultElement.individual,self.SPECIALIZATION,distance))
                childList = newChildList
        return returnValue
    
    def stepUpHierarchy(self,start,relation,subject):
        '''
        Returns a tuple giving the parent IRI of 'start' as the first argument, and
        whether it bears 'relation' to 'object' as the second argument.
        '''
        query = """SELECT ?parent
WHERE {
    <%s> rdfs:subClassOf ?parent .
}"""%start
        parent = None
        resultValue = None

        # There should be only a single result; warn if more:
        qres = self.g.query(query, initNs = self.bmap)
        wrongRowCount = -1
        for row in qres:
            parent = row[0]
            wrongRowCount = wrongRowCount + 1
            query2 = """ ASK WHERE { <%s> <%s> <%s> . } """%(subject, relation, parent)
            qres2 = self.g.query(query2, initNs = self.bmap)
            for row in qres2:
                resultValue = row
                
        # if wrongRowCount != 0:
        #     log an error?
        Result = namedtuple("Result", ["individual", "matchValue"])
        return Result(parent, resultValue)


    def stepDownHierarchy(self,start,relation,subject):
        '''
        Returns a list of tuples giving a child IRIs of 'start' as the first argument, and
        whether it bears 'relation' to 'object' as the second argument.
        '''
        query = """SELECT ?child
WHERE {
    ?child rdfs:subClassOf <%s> .
}"""%start
        child = None
        resultValue = None
        returnValue = list()
        Result = namedtuple("Result", ["individual", "matchValue"])

        # There may be any number of results
        qres = self.g.query(query, initNs = self.bmap)
        for row in qres:
            child = row[0]
            query2 = """ ASK WHERE { <%s> <%s> <%s> } """%(subject, relation, child)
            qres2 = self.g.query(query2, initNs = self.bmap)
            for row in qres2:
                resultValue = row
            returnValue.append(Result(child, resultValue))
                
        # if wrongRowCount != 0:
        #     log an error?
        return returnValue
       
    def dumpGraph(self):
        print (self.g.serialize(format="n3"))
