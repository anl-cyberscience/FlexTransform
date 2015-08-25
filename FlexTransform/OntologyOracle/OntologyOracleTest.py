'''
Created on Aug 27, 2014

@author: cstras

TODO:
  * Load the RDF file, treat as a 'TBOX'
  * Build an 'ABOX' from a JSON schema file
  * For a given concept, determine if there is a satisfying super / sub concept that will work.
'''
import unittest
from .OntologyOracle import Oracle
from rdflib import Namespace, RDF, URIRef


class Test(unittest.TestCase):

    def setUp(self):
        self.myOracle = Oracle("../resources/transform.rdf")
        self.IRIBaseNS = Namespace("http://www.anl.gov/cfm/ontologies/transform.owl#")

    def tearDown(self):
        pass

    def testAddSemanticComponent(self):
        self.myOracle.addSemanticComponent("ToStarFileHasMore", "ToStarFalse")
        resList = self.myOracle.getSemanticComponentList()
        print ("Component\tConcept\tValue")
        if len(resList) == 0:
            self.fail("No results retrieved from the graph, expecting 1, got %d"%(len(resList)))
        for compList in resList:
            if len(compList) != 3:
                self.fail("Invalid component list element: %s"%(compList))
            print("%s\t%s\t%s"%(compList[0],compList[1],compList[2]))
        pass

    def testAddSemanticComponentIndividual(self):
        testClass = self.IRIBaseNS.TestClass
        individualValue = "testValue"
        individualName = self.IRIBaseNS.selfDefinedName
        
        ''' First try with no individual name '''
        assignedName = self.myOracle.addSemanticComponentIndividual(testClass, 
                                                     individualValue, 
                                                     None)
        
        ''' Query for individual from graph '''
        myQuery = "SELECT ?s WHERE { ?s <%s> <%s> . }"%(RDF.type, testClass)
        print("[D] Executing query %s"%(myQuery))
        result = self.myOracle.g.query(myQuery)
        tpass = False
        for row in result:
            if not str(row[0]) == assignedName:
                self.fail("Expected name %s, but got name %s"%(assignedName, row[0]))
            elif not tpass:
               tpass = True
            else:
                self.fail("Multiple rows returned after adding only a single triple:\n%s"([str(x) for x in result]))
        if not tpass:
            self.fail("Multiple rows returned after adding only a single triple:\n%s"([str(x) for x in result]))

        ''' Query for individual value '''
        myQuery = " SELECT ?o WHERE { <%s> <%s> ?o . } "%(assignedName, self.myOracle.XFORMNS.hasValue)
        result = self.myOracle.g.query(myQuery)
        tpass = False
        for row in result:
            if not str(row[0]) == individualValue:
                self.fail("Expected value %s, but got %s"%(individualValue, row[0]))
            elif not tpass:
               tpass = True
            else:
                self.fail("Multiple rows returned after adding only a single triple:\n%s"%([str(x) for x in result]))
        if not tpass:
            self.fail("Query returned no rows.\n%s"%(myQuery))

        ''' Also try with a specified individual name '''
        assignedName = self.myOracle.addSemanticComponentIndividual(testClass, 
                                                     individualValue, 
                                                     individualName)
        
        if not str(assignedName) == str(individualName):
            self.fail("Expected name %s, instead got %s.")

        ''' Query for individual from graph '''
        myQuery = "SELECT ?o WHERE { <%s> <%s> ?o . }"%(individualName, RDF.type)
        result = self.myOracle.g.query(myQuery)
        tpass = False
        for row in result:
            if not str(row[0]) == str(testClass):
                self.fail("Expected parent class %s, but got class %s"%(testClass, row[0]))
            elif not tpass:
               tpass = True
            else:
                self.fail("Multiple rows returned after adding only a single triple:\n%s"([str(x) for x in result]))
        if not tpass:
            self.fail("No rows returned for query\n\t %s \n after adding triple:\n%s"(myQuery, [str(x) for x in result]))

        ''' Query for individual value '''
        myQuery = " SELECT ?o WHERE { <%s> <%s> ?o . } "%(assignedName, self.myOracle.XFORMNS.hasValue)
        result = self.myOracle.g.query(myQuery)
        tpass = False
        for row in result:
            if not str(row[0]) == individualValue:
                self.fail("Expected value %s, but got %s"%(individualValue, row[0]))
            elif not tpass:
               tpass = True
            else:
                self.fail("Multiple rows returned after adding only a single triple:\n%s"([str(x) for x in result]))
        if not tpass:
            self.fail("No rows returned for query\n\t %s \n after adding triple:\n%s"(myQuery, [str(x) for x in result]))

    def testGeneralizeSemanticConcept(self):
            self.fail("Needs to be implemented.")

    def testSpecializeSemanticConcept(self):
            self.fail("Needs to be implemented.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()