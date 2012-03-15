#!/usr/bin/python
#-*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This project is licensed under the GPLv3 License or any later version.

Copyright (c) 2012, Pierre-Yves Chibon

All rights reserved.
"""

"""
Unit-tests file for pySemon.
"""

import os
import rdflib
import sys
import unittest

sys.path.insert(0, os.path.abspath('../'))
import semon

if os.path.dirname(__file__):
    folder = os.path.dirname(__file__)
else:
    folder = '.'

ONTOFILE = '%s/test.onto' % folder


class SemanticOntologyTests(unittest.TestCase):
    """ SemanticOntology tests. """

    def __init__(self, methodName='runTest'):
        """ Constructor. """
        unittest.TestCase.__init__(self, methodName)

    #def tearDownClass(self):
        #""" Remove file created by running the tests. """
        #if os.path.exists('FedDoap.owl'):
            #os.remove('FedDoap.owl')
        #if os.path.exists('FedDoap.onto'):
            #os.remove('FedDoap.onto')

    def test_load_text(self):
        """ Test the load_text function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')

    def test_to_text(self):
        """ Test the to_text function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        so.to_text(False)

    def test_to_owl(self):
        """ Test the to_text function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        so.to_owl()

    def test_load_owl(self):
        """ Test the load_owl function. """
        so = semon.SemanticOntology()
        so.load_owl('FedDoap', 'FedDoap.owl')

    def test_remove_load_owl(self):
        """ Test the load_owl function to a remote ontology. """
        so = semon.SemanticOntology()
        so.load_owl('doap', 
            'https://raw.github.com/edumbill/doap/master/schema/doap.rdf')

    def test_get_class_name(self):
        """ Test the get_class_names function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        self.assertEqual(['feddoap:Package'], so.get_class_names())

    def test_get_property_name(self):
        """ Test the get_class_names function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        self.assertEqual(['feddoap:PackageMaintainer'],
            so.get_property_names())

    def test_get_classes(self):
        """ Test the get_classes function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        classes = so.get_classes()
        self.assertEqual(['"Package"@en'],
            classes['feddoap:Package']['rdfs:label'])
        self.assertEqual(['"A package is a pre-built, distributable, project."@en'],
            classes['feddoap:Package']['rdfs:comment'])

    def test_get_properties(self):
        """ Test the get_properties function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        properties = so.get_properties()
        self.assertEqual(['"Package maintainer"@en'],
            properties['feddoap:PackageMaintainer']['rdfs:label'])
        self.assertEqual(['"The maintainer of a packager."@en'],
            properties['feddoap:PackageMaintainer']['rdfs:comment'])

    def test_get_ontology_info(self):
        """ Test the get_ontology_info function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        infos = so.get_ontology_info()
        self.assertEqual({}, infos)

    def test_get_info(self):
        """ Test the get_info function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        uri = rdflib.term.URIRef(
            'http://fedoraproject.org/ontologies/feddoap#Package')
        infos = so.get_info(uri)
        self.assertEqual(['"Package"@en'],
            infos['rdfs:label'])
        self.assertEqual(['"A package is a pre-built, distributable, project."@en'],
            infos['rdfs:comment'])

    def test_get_uri(self):
        """ Test the get_uri function. """
        so = semon.SemanticOntology()
        so.load_text('FedDoap', 'test.onto')
        self.assertEqual(None, so.get_uri())


suite = unittest.TestLoader().loadTestsFromTestCase(SemanticOntologyTests)
unittest.TextTestRunner(verbosity=2).run(suite)
