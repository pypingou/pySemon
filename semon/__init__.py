#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Reads in an ontology file and play with it.
"""

import ConfigParser
import rdflib

RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
OWL = rdflib.Namespace('http://www.w3.org/2002/07/owl#')
VS = rdflib.Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')

DC = rdflib.Namespace('http://purl.org/dc/elements/1.1/')
FOAF = rdflib.Namespace('http://xmlns.com/foaf/0.1/')

NS = {RDF: 'rdf', RDFS: 'rdfs', OWL: 'owl', VS: 'vs', DC: 'dc',
        FOAF: 'foaf'}


def parse_config(filename):
    """ For a given filename, parse its content and return the
    dictionnary of all the values in it.

    :arg filename, path to the configuration file to read.
    """
    options = {}
    f = open(filename)
    for line in f:
        if not line.startswith("#") and not line.startswith(';') \
            and line.strip() != "":
            line = line.strip()
            if line.startswith("["):
                section = line[1:-1]
                options[section] = {}
            else:
                parts = line.split("=", 1)
                options[section][parts[0].strip()] = parts[1].strip()
    f.close()
    return options


def _get_full_name(uri):
    """ From a partial URI return its complete version using the already
    known ontologies.

    arg uri, Unique Resource Identifier in its short version (onto:name)
    to expand to its complete version (http://url/to/onto#name).
    """
    onto, name = uri.split(':')
    for val in NS:
        if NS[val] == onto:
            onto = val
    return onto + name


def _get_key(uri):
    """ For a given uri, split on #, check if it is present in the lsit
    of namespace already defined and if so return the abbreviated
    version otherwise, return the full uri.

    :arg uri, Unique Resource Identifier for which to check if the base
    URI is already present in the list of defined namespaces.
    """
    if '#' in uri:
        base_uri, name = uri.split('#')
        base_uri = rdflib.Namespace(base_uri + '#')
    else:
        base_uri, name = uri.rsplit('/', 1)
        base_uri = rdflib.Namespace(base_uri + '/')
    key = uri
    if base_uri in NS:
        key = '%s:%s' % (NS[base_uri], name)
    return key


def _load_namespace(config):
    """ From a configuration file provided by ConfigParser, load the
    section containing the Namespaces and add them to the list of known
    namespaces.

    :arg config, the configuration object to parse as obtained by
    ConfigParser
    """
    if 'Namespace' in config:
        for option in config['Namespace']:
            ns = base_uri = rdflib.Namespace(config['Namespace'][option])
            if ns not in NS:
                NS[ns] = option


class SemanticOntology(object):
    """ This class will contain graph of the semantic ontology and
    provide acess to its content.
    """

    def __init__(self):
        """ Constructor.
        Instanciate the default attributes.
        """
        self.name = None
        self.graph = rdflib.Graph()

    def _load_section(self, config, section):
        """ Load a given section into the graph.
        :arg config, the configuration file containing our ontology as
        provided by ConfigParser.
        :arg section, the name of the section to load from the
        configuration.
        """
        subject = rdflib.term.URIRef(_get_full_name(section))
        for option in config[section]:
            predicate = rdflib.term.URIRef(_get_full_name(option))
            object = config[section][option]
            if object.startswith('<'):
                object = object.replace('>', '').replace('<', '')
                object = rdflib.term.URIRef(object)
            else:
                object = rdflib.term.Literal(object)
            #print subject, predicate, object
            self.graph.add((subject, predicate, object))

    def load_text(self, name, filename):
        """ Load a semantic ontology from a text file.

        :arg ontology, url or path to the file containing the ontology
        to load.
        """
        self.name = name
        config = parse_config(filename)
        _load_namespace(config)
        for section in config:
            if section != 'Namespace':
                self._load_section(config, section)

    def load_owl(self, name, ontology):
        """ Load a semantic ontology owl file.

        :arg ontology, url or path to the file containing the ontology
        to load.
        """
        self.name = name
        self.graph.parse(ontology, format='xml')
        NS[rdflib.Namespace(self.get_uri())] = self.name

    def __add_entries(self, entries, config, all_lang=True):
        """ Add a sections and their content from a dict or dict as
        would be returned by the get_classes or get_properties
        functions.

        :arg entries, dict of dict containing the section and their
        content to be added to the configuration.
        :arg config, the configuration object as obtained by
        ConfigParser
        :arg all_lang, a boolean specifying if the configuration should
        contain all the language available or just english.
        """
        for entry in entries:
            config.add_section(entry)
            for key in entries[entry]:
                value = entries[entry][key]
                if type(value) == list:
                    values = []
                    for val in value:
                        lang = None
                        if type(val) == rdflib.Literal and val.language:
                            lang = val.language
                        if all_lang or lang is None or lang == 'en':
                            values.append(val.n3())
                    value = values
                if len(value) == 1:
                    value = value[0]
                if value:
                    config.set(entry, key, value)
        return config

    def get_uri(self):
        """ Return the URI of the ontology.
        """
        return self.graph.value(predicate=RDF['type'], object=OWL['Ontology'])

    def get_ontology_info(self):
        """ Return all the information known about the ontology.
        """
        return self.get_info(self.get_uri())

    def get_info(self, subject):
        """ Return as a dictionnary all the information known about a
        given subject.

        :arg subject, URI used to query the graph and generate the dict
        of information.
        """
        infos = {}
        for pred, obj in self.graph.predicate_objects(subject):
            key = _get_key(pred)
            if key in infos:
                infos[key].append(obj)
            else:
                infos[key] = [obj]
        return infos

    def get_class_names(self):
        """ Return all the classes found in this ontology.
        """
        classes = []
        for subject in self.graph.subjects(predicate=RDF['type'],
            object=RDFS['Class']):
            key = _get_key(subject)
            classes.append(key)
        return classes

    def get_classes(self):
        """ Return the classes found in this ontology with all their
        information.
        """
        classes = {}
        for subject in self.graph.subjects(predicate=RDF['type'],
            object=RDFS['Class']):
            key = _get_key(subject)
            infos = self.get_info(subject)
            classes[key] = infos
        return classes

    def get_property_names(self):
        """ Return all the property found in this ontology.
        """
        properties = []
        for subject in self.graph.subjects(predicate=RDF['type'],
            object=RDF['Property']):
            key = _get_key(subject)
            properties.append(key)
        return properties

    def get_properties(self):
        """ Return the properties found in this ontology with all their
        information.
        """
        properties = {}
        for subject in self.graph.subjects(predicate=RDF['type'],
            object=RDF['Property']):
            key = _get_key(subject)
            infos = self.get_info(subject)
            properties[key] = infos
        return properties

    def to_owl(self):
        """ Generate a owl version of the ontology.
        """
        stream = open('%s.owl' % self.name, 'w')
        stream.write(self.graph.serialize(format='xml'))
        stream.close()

    def to_text(self, all_lang=True):
        """ Generate a text version of the ontology.

        :arg all_lang, a boolean specifying if the configuration should
        contain all the language available or just english.
        """
        config = ConfigParser.RawConfigParser()
        # First we dump the Namespace
        config.add_section('Namespaces')
        for ns in NS:
            config.set('Namespaces', NS[ns], ns)
        # Then we dump all the classes
        classes = self.get_classes()
        config = self.__add_entries(classes, config, all_lang=all_lang)
        # Then we dump all the properties
        classes = self.get_properties()
        config = self.__add_entries(classes, config, all_lang=all_lang)
        stream = open('%s.onto' % self.name, 'w')
        config.write(stream)
        stream.close()


if __name__ == '__main__':
    so = SemanticOntology()
    #so.load_owl('doap', 'https://raw.github.com/edumbill/doap/master/schema/doap.rdf')
    so.load_text('FedDoap', 'test.onto')
    #print so.get_ontology_info()
    for c in so.get_class_names():
        print c
    #for c in so.get_property_names():
        #print c
    #so.to_text()
    #so.to_text(False)
    so.to_owl()
