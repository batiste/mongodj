import datetime
import sys

import pymongo
from pymongo.objectid import ObjectId
from pymongo.errors import InvalidId

from django.db import models
from django.db.models.sql import aggregates as sqlaggregates
from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql import aggregates as sqlaggregates
from django.db.models.sql.constants import LOOKUP_SEP, MULTI, SINGLE
from django.db.models.sql.where import AND, OR
from django.db.utils import DatabaseError, IntegrityError
from django.utils.tree import Node
from django.db.models.sql.where import WhereNode
import re

from django.conf import settings

TYPE_MAPPING = {
    'unicode':  lambda val: unicode(val),
    # mongodb doesn't handle number anyway
    #'int':      lambda val: int(val),
    'float':    lambda val: float(val),
    'bool':     lambda val: bool(val),
    'objectid': lambda val: val,
}

OPERATORS_MAP = {
    'exact':    lambda val: val,
    'iexact':    lambda val: re.compile(r'^%s$' % val, re.IGNORECASE),
    'startswith':    lambda val: re.compile(r'%s' % val),
    'istartswith':    lambda val: re.compile(r'^%s' % val, re.IGNORECASE),
    'endswith':    lambda val: re.compile(r'%s$' % val),
    'iendswith':    lambda val: re.compile(r'%s$' % val, re.IGNORECASE),
    'contains':    lambda val: re.compile(r'%s' % val),
    'icontains':    lambda val: re.compile(r'%s' % val, re.IGNORECASE),
    'regex':    lambda val: re.compile(val),
    'iregex':    lambda val: re.compile(val, re.IGNORECASE),
    'gt':       lambda val: {"$gt": val},
    'gte':      lambda val: {"$gte": val},
    'lt':       lambda val: {"$lt": val},
    'lte':      lambda val: {"$lte": val},
    'in':       lambda val: {"$in": val},
}

def _get_mapping(db_type, value):
    # TODO - comments. lotsa comments
    if db_type in TYPE_MAPPING:
        _func = TYPE_MAPPING[db_type]
    else:
        _func = lambda val: val
    # TODO - what if the data is represented as list on the python side?
    if isinstance(value, list):
        return map(_func, value)
    return _func(value)
    
def python2db(db_type, value):
    # mongodb only handle 8 bit number
    if isinstance(value, (int, float, long)):
        return str(value)
    return _get_mapping(db_type, value)
    
def db2python(db_type, value):
    return _get_mapping(db_type, value)
    
def _parse_constraint(where_child, connection):
    _constraint, lookup_type, _annotation, value = where_child
    (table_alias, column, db_type), value = _constraint.process(lookup_type, value, connection)
    if lookup_type not in ('in', 'range') and isinstance(value, (tuple, list)):
        # Django fields always return a list (see Field.get_db_prep_lookup)
        # except if get_db_prep_lookup got overridden by a subclass
        if len(value) > 1:
            # TODO... - when can we get here?
            raise Exception("blah!")
        if lookup_type == 'isnull':
            value = annotation
        else:
            value = value[0]
    #fix managing of some specific "string manipulation in standard sql field" 
    # line 287 in where.py  params = self.field.get_db_prep_lookup(lookup_type, value, connection=connection, prepared=True)
    if lookup_type in ['startswith', 'istartswith']:
        if value.endswith(u"%"):
            value = value[:-1]
    elif lookup_type in ['endswith', 'iendswith']:
        if value.startswith(u"%"):
            value = value[1:]
    elif lookup_type in ['icontains', 'contains']:
        value = value[1:-1]

    return (lookup_type, table_alias, column, db_type, value)

class SQLCompiler(SQLCompiler):
    """
    A simple query: no joins, no distinct, etc.
    
    Internal attributes of interest:
        x connection - DatabaseWrapper instance
        x query - query object, which is to be
            executed
    """
    
    def __init__(self, *args, **kw):
        super(SQLCompiler, self).__init__(*args, **kw)
        self.cursor = self.connection._cursor
    
    """
    Private API
    """
    def _execute_aggregate_query(self, aggregates, result_type):
        if len(aggregates) == 1 and isinstance(aggregates[0], sqlaggregates.Count):
            count = self.get_count()
        if result_type is SINGLE:
            return [count]
        elif result_type is MULTI:
            return [[count]]
    
    def _get_query(self):
        query = {}
        where = self.query.where
        pk_column = self.query.get_meta().pk.column
        query = self._get_query_recursif(query=query, where=where, pk_column=pk_column)
        # if we have a _id, we need to put back the value into the pk_column
        if query.has_key(pk_column):
            query['_id'] = query[pk_column]
            del query[pk_column]
        return query

    def _get_query_recursif(self, query, where, pk_column):
        if where.connector == OR:
            raise NotImplementedError("OR queries not supported yet.")
        for child in where.children:
            if isinstance(child, (list, tuple)):
                lookup_type, collection, column, db_type, value = \
                    _parse_constraint(child, self.connection)
                if column == pk_column:
                    if lookup_type=='exact':
                        query["_id"] = value
                    elif lookup_type=='in':
                        query["_id"] = {"$in":value}
                else:
                    query[column] = OPERATORS_MAP[lookup_type](python2db(db_type, value))
            elif isinstance(child, WhereNode):
                query = self._get_query_recursif(query=query, where=child,
                    pk_column=pk_column)
        return query
    
    def _get_collection(self):
        _collection = self.query.get_meta().db_table
        return self.cursor()[_collection]
        
    """
    Public API
    """
    def get_count(self):
        return self.get_results().count()
    
    def get_results(self):
        """
        @returns: pymongo iterator over results
        defined by self.query
        """
        _high_limit = self.query.high_mark or 0
        _low_limit = self.query.low_mark or 0
        query = self._get_query()
        
        results = self._get_collection().find(query).skip(_low_limit).limit(
            _high_limit - _low_limit)

        if self.query.order_by:
            sort_list = []
            for order in self.query.order_by:
                if order.startswith('-'):
                    sort_list.append((order[1:], pymongo.DESCENDING))
                else:
                    sort_list.append((order, pymongo.ASCENDING))
            results = results.sort(sort_list)
        return results

    """
    API used by Django
    """
    def results_iter(self):
        """
        Returns an iterator over the results from executing this query.
        
        self.query - the query created by the ORM
        self.query.where - conditions imposed by the query
        """
        pk_column = str(self.query.get_meta().pk.column)
        for document in self.get_results():
            # remove the_id at the last moment if present
            if document.has_key('_id'):
                document[pk_column] = document['_id']
                del document['_id']
            result = []
            for field in self.query.get_meta().local_fields:
                result.append(db2python(field.db_type(
                    connection=self.connection), document.get(field.column, field.default)))
            yield result
            
    def execute_sql(self, result_type=MULTI):
        # let's catch aggregate call
        aggregates = self.query.aggregate_select.values()
        if aggregates:
            return self._execute_aggregate_query(aggregates, result_type)
        return
            
    def has_results(self):
        return self.get_count() > 0
                        
class SQLInsertCompiler(SQLCompiler):
    
    def execute_sql(self, return_id=False):
        """
        self.query - the data that should be inserted
        """
        dat = {}
        
        for (field, value), column in zip(self.query.values, self.query.columns):
            dat[column] = python2db(field.db_type(connection=self.connection), value)

        # every object should have a unique pk, (is it always the case in Django?)
        pk_field = self.query.get_meta().pk
        pk_name = pk_field.attname

        if pk_name in dat:
            pk = dat.pop(pk_name)
            if isinstance(pk, (str, unicode)):
                try:
                    pk = ObjectId(pk)
                except InvalidId:
                    # http://www.mongodb.org/display/DOCS/Object+IDs
                    # Users are welcome to use their own conventions
                    # for creating ids; the _id value may be of any type
                    # so long as it is a unique.
                    pass
            dat['_id'] = pk
                
        res = self.connection._cursor()[self.query.get_meta().db_table].save(dat)

        if return_id:
            return unicode(res)

class SQLUpdateCompiler(SQLCompiler):

    def execute_sql(self, return_id=False):
        """
        self.query - the data that should be inserted
        """
        dat = {}
        for (field, value), column in zip(self.query.values, self.query.columns):
            dat[column] = python2db(field.db_type(connection=self.connection), value)
        # every object should have a unique pk
        pk_field = self.query.get_meta().pk
        pk_name = pk_field.attname

        res = self.connection._cursor()[self.query.get_meta().db_table].save(dat)

        if return_id:
            return unicode(res)
        
class SQLDeleteCompiler(SQLCompiler):
    
    def execute_sql(self, result_type=MULTI):
        query = self._get_query()
        return self._get_collection().remove(query)
        