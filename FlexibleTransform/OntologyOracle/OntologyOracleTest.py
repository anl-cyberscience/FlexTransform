'''
Created on Aug 27, 2014

@author: cstras

TODO:
  * Load the RDF file, treat as a 'TBOX'
  * Build an 'ABOX' from a JSON schema file
  * For a given concept, determine if there is a satisfying super / sub concept that will work.
'''
import unittest
from OntologyOracle.OntologyOracle import Oracle


class Test(unittest.TestCase):

    def setUp(self):
        self.myOracle = Oracle("../resources/transform.rdf")

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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()