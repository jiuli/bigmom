#-*- coding:utf-8 -*-
# Author : lijunsong
# Date: 2017-12-1 16:14:00

import contextlib
import logging
from multiprocessing import pool
import threading

from pymysql.connections import Connection
from pymysql.cursors import DictCursor, Cursor

from base.pool import PoolContainer, PoolIsEmptyException, PoolIsFullException


logger = logging.getLogger("MySQLConnectionPool")

class MySQLConnectionPool(object):
    def __init__(self,pool_name,host=None,username=None,
                 password="", database=None,port=3306,
                 charset='utf8',use_dict_cursor=True,
                 max_pool_size=30,enable_auto_resize=True,
                 auto_resize_scale=1.5,pool_resize_boundary=48,
                 defer_connect_pool=False, **kwargs):
        
        
        self._host = host
        self._username = username
        self._password = password
        self._database = database
        self._port = port
        self._charset = charset
        self._cursor_class = DictCursor if use_dict_cursor else Cursor
        self._other_kwargs = kwargs
        self._pool_name = pool_name
        self._max_pool_size = max_pool_size if max_pool_size < pool_resize_boundary else pool_resize_boundary
        self._enable_auto_resize = enable_auto_resize
        self._pool_resize_boundary = pool_resize_boundary
        if auto_resize_scale < 1:
            raise ValueError("Invalid scale {},must be bigger than 1.".formart(auto_resize_scale))
        self._auto_resize_scale = int(round(auto_resize_scale, 0))
        self._pool_container = PoolContainer(self._max_pool_size)
        
        self.__safe_lock = threading.RLock()
        self.__is_killed = False
        self.__is_connected = False
        
        if not defer_connect_pool:
            self.connect()
        
    
    def __repr__(self, *args, **kwargs):
        ''' __str__()用于显示给用户，而__repr__()用于显示给开发人员
        '''
        return '<MySQLConnectionPool name={!r}, size={!r}'.format(self.pool_name,self.size)
    
    def __del__(self):
        self.close()
        
    def __iter__(self):
        ''' Iterate each connection item '''
        return iter(self._pool_container)
    
    @property
    def pool_name(self):
        return self._pool_name
    
    @property
    def pool_size(self):
        return self._pool_container.pool_size
    
    @property
    def free_size(self):
        return self._pool_container.free_size
    
    @property
    def size(self):
        return '<boundary={},max={},current={},free={}>'.format(self._pool_resize_boundary,
                                                                self._max_pool_size,
                                                                self.pool_size,
                                                                self.free_size)
    def _borrow(self, block):
        try:
            connection = self._pool_container.get(block, None)
        except PoolIsEmptyException:
            return None
        else:
            # check if the connection is alive or not
            connection.ping(reconnect=True)
            return connection
    
    def return_connection(self, connection):
        return self._pool_container.return_(connection)
    
    def _create_connection(self):
        ''' Create a pymysql connection object
        '''
        return Connection(host=self._host,
                          user=self._username,
                          passwd=self._password,
                          db=self._database,
                          port=self._port,
                          charset=self._charset,
                          cursorclass=self._cursor_class,
                          **self._other_kwargs)
    
    def connect(self):
        ''' Connect to this connection pool
        '''
        if self.__is_connected:
            return
        logger.info('"{}" Connect to connection pool'.format(self))
        
        test_conn = self._create_connection()
        try:
            test_conn.ping()
        except Exception as e:
            raise e
        else:
            with self.__safe_lock:
                self.__is_connected = True
            self._adjust_connection_pool()
        finally:
            test_conn.close()
    
    def _free(self):
        ''' Release all the connections in the pool
        '''
        for connection in self:
            try:
                connection.close()
            except Exception as e:
                _ = e
                
                
    def close(self):
        ''' close this connection pool'''
        try:
            logger.info('"{}" Close connection pool'.format(self))
        except Exception:
            pass
        
        with self.__safe_lock:
            if self.__is_killed is True:
                return True
        self._free()
        
        with self.__safe_lock:
            self.__is_killed = True
    
    def _adjust_max_pool_size(self):
        with self.__safe_lock:
            self._max_pool_size *= self._auto_resize_scale
            if self._max_pool_size > self._pool_resize_boundary:
                self._max_pool_size = self._pool_resize_boundary
            
            logger.debug('"{}" Max pool size ')
    
    def _adjust_connection_pool(self):
        logger.debug('"{}" Adjust connection pool, current size is "{}"'.format(
                    self, self.size))
        
        if self.pool_size >= self._max_pool_size:
            if self._enable_auto_resize:
                self._adj()
                
        try:
            connection = self._create_connection()
        except Exception as e:
            logger.error(e)
            return False
        else:
            try:
                self._pool_container.add(connection)
            except PoolIsFullException:
                return False
            else:
                return True
            
    def borrow_connection(self):
        ''' Get a free connection item from current pool.
            It's a little confused here, but it works as expected now.
        '''
        block = False
        
        while True:
            conn = self._borrow(block)
            if conn is None:
                block = not self._adjust_connection_pool()
            else:
                return conn
        
        
    @contextlib.contextmanager
    def connection(self, autocommit=False):
        conn = self.borrow_connection()
        assert isinstance(conn, Connection)
        
        old_value = conn.get_autocommit()
        conn.autocommit(autocommit)
        try:
            yield conn
        except Exception as e:
            raise e
        finally:
            conn.autocommit(old_value)
            self.return_connection(conn)
        
    @contextlib.contextmanager
    def cursor(self, cursor=None):
        with self.connection(True) as conn:
            assert isinstance(conn, Connection)
            
            cursor = conn.cursor(cursor)
            
            try:
                yield cursor
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()