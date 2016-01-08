'''
Created on Aug 27, 2014

@author: cstras

TODO:
  * Load the RDF file, treat as a 'TBOX'
  * Build an 'ABOX' from a JSON schema file
  * For a given concept, determine if there is a satisfying super / sub concept that will work.
'''
import unittest
from FlexTransform.OntologyOracle.OntologyOracle import Oracle
from rdflib import Namespace, RDF, URIRef  # @UnusedImport
import os

class OntologyOracleTests(unittest.TestCase):
    
    myOracle = None
    IRIBaseNS = None

    def setUp(self):
        self.IRIBaseNS = Namespace("http://www.anl.gov/cfm/transform.owl#")
        currentdir = os.path.dirname(__file__)
        self.myOracle = Oracle(os.path.join(currentdir,"../resources/test.owl"), self.IRIBaseNS.cfm13schema)

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

    def testStepUpHierarchy(self):

        start = self.myOracle.XFORMNS.PortNumberIndicatorValueSemanticComponent
        expectedParent = self.myOracle.XFORMNS.IndicatorValueSemanticConcept
        ceiling = self.myOracle.XFORMNS.SemanticComponent  # @UnusedVariable
        subject = self.myOracle.XFORMNS.cfm13schema
        predicate = self.myOracle.XFORMNS.containsComponent
        result = self.myOracle.stepUpHierarchy(start, predicate, subject)
        if result.matchValue:
            self.fail("Should not have matched for IRI %s!"%result.individual)
        if not result.individual == expectedParent:
            self.fail("Expected parent of %s, got %s"%(expectedParent, result.individual))

    def testStepDownHierarchy(self):

        start = self.myOracle.XFORMNS.PortNumberIndicatorValueSemanticComponent
        expectedChildList = [self.myOracle.XFORMNS.DestinationPortListIndicatorValueSemanticComponent,
                             self.myOracle.XFORMNS.DestinationPortNumberIndicatorValueSemanticComponent
                             ]
        subject = self.myOracle.XFORMNS.cfm13schema
        predicate =self.myOracle.XFORMNS.containsComponent
        expectedChildLength = 2

        resultList = self.myOracle.stepDownHierarchy(start, predicate, subject)
        if len(resultList) != expectedChildLength:
            self.fail("Expected %d elements, but got %d!"%(expectedChildLength, len(resultList)))
        for result in resultList:
            if result.matchValue:
                self.fail("Should not have matched for IRI %s!"%result.individual)
            if not result.individual in expectedChildList:
                self.fail("Unexpected child %s"%(result.individual))

    def testGetCompatibleConcepts(self):
        """
        This test will add edges to ensure that we can:
        Find and return an exact match
        Find and return a generalization
        Find and return a specialization
        """

        start = self.myOracle.XFORMNS.PortNumberIndicatorValueSemanticComponent
        specializationNode = self.myOracle.XFORMNS.DestinationPortListIndicatorValueSemanticComponent
        generalizationNode = self.myOracle.XFORMNS.IndicatorValueSemanticConcept
        supportsRelation = self.myOracle.XFORMNS.containsComponent  # @UnusedVariable
        requiresRelation = self.myOracle.XFORMNS.requiresComponent

        ## Test that we see no results by default:
        tList = self.myOracle.getCompatibleConcepts(start)
        self.assertEqual(len(tList), 0, "Expected list length of 0, but found %d!"%len(tList))

        ## Test the specialization:
        # Add the specialization
        #iquery = """INSERT DATA {
    #%s %s %s
#}"""%(self.myOracle.schemaReference, requiresRelation, specializationNode)
        #self.myOracle.g.query(iquery)
        self.myOracle.g.add( (self.myOracle.schemaReference, requiresRelation, specializationNode))
        
        # We should now see the specializationNode returned, and that should be the only result.
        tList = self.myOracle.getCompatibleConcepts(start)
        testList = [x.IRI for x in tList]
        self.assertIn(specializationNode, testList, "Results do not include %s!"%specializationNode)
        self.assertEqual(len(tList), 1, "Expected one result, but returned %d"%len(tList))

        ## Test the generalization:
        # Add the generalization
        #iquery = """INSERT DATA {
    #%s %s %s
#}"""%(self.myOracle.schemaReference, requiresRelation, generalizationNode)
        #self.myOracle.g.query(iquery)
        self.myOracle.g.add( (self.myOracle.schemaReference, requiresRelation, generalizationNode))
        
        # We should now see the generalizationNode returned first, and there should be two results.
        tList = self.myOracle.getCompatibleConcepts(start)
        testList = [x.IRI for x in tList]
        self.assertEqual(generalizationNode, tList[0].IRI, "First result is not %s!"%generalizationNode)
        self.assertIn(specializationNode, testList, "Results do not include %s!"%specializationNode)
        self.assertEqual(len(tList), 2, "Expected two results, but returned %d"%len(tList))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
