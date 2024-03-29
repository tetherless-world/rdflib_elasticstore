
"""
Code for tying SPARQL Engine into RDFLib

These should be automatically registered with RDFLib

"""

from six import string_types

from rdflib.query import Processor, Result, UpdateProcessor

from .sparql import Query

from .parser import parseQuery, parseUpdate
from .algebra import translateQuery, translateUpdate

from .evaluate import evalQuery
from .update import evalUpdate


def prepareQuery(queryString, initNs={}, base=None):
    """
    Parse and translate a SPARQL Query
    """
    ret = translateQuery(parseQuery(queryString), base, initNs)
    ret._original_args = (queryString, initNs, base)
    return ret


def processUpdate(graph, updateString, initBindings={}, initNs={}, base=None):
    """
    Process a SPARQL Update Request
    returns Nothing on success or raises Exceptions on error
    """
    evalUpdate(graph, translateUpdate(
        parseUpdate(updateString), base, initNs), initBindings)


class SPARQLResult(Result):

    def __init__(self, res):
        Result.__init__(self, res["type_"])
        self.vars = res.get("vars_")
        self.bindings = res.get("bindings")
        self.askAnswer = res.get("askAnswer")
        self.graph = res.get("graph")


class SPARQLUpdateProcessor(UpdateProcessor):
    def __init__(self, graph):
        self.graph = graph

    def update(self, strOrQuery, initBindings={}, initNs={}):
        if isinstance(strOrQuery, string_types):
            strOrQuery = translateUpdate(parseUpdate(strOrQuery), initNs=initNs)

        return evalUpdate(self.graph, strOrQuery, initBindings)


class SPARQLProcessor(Processor):

    def __init__(self, graph):
        self.graph = graph

    def query(
            self, strOrQuery, initBindings={},
            initNs={}, base=None, DEBUG=False):
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """

        if not isinstance(strOrQuery, Query):
            parsetree = parseQuery(strOrQuery)
            query = translateQuery(parsetree, base, initNs)
        else:
            query = strOrQuery

        return evalQuery(self.graph, query, initBindings, base)
