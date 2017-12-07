#-*- coding:utf-8 -*-
# Author : lijunsong
# Date: 2017-12-1 16:14:00
import logging
from queue import Queue, Empty
import threading


logger = logging.getLogger('pool')



class PoolIsFullException(Exception):
    pass

class PoolIsEmptyException(Exception):
    pass


class PoolContainer(object):
    def __init__(self, max_pool_size):
        self._pool_lock = threading.RLock()
        self._free_items = Queue()
        self._pool_items = set()
        self._max_pool_size = 0
        self.max_pool_size = max_pool_size
    
    def __repr__(self, *args, **kwargs):
        return '<{0.__class__.__name__} {0.size}>'.format(self)
    
    def __iter__(self):
        with self._pool_lock:
            return iter(self._pool_items)
        
    def __contains__(self, item):
        with self._pool_lock:
            return item in self._pool_items
        
    def __len__(self):
        with self._pool_lock:
            return len(self._pool_items)
    
    @property
    def max_pool_size(self):
        return self._max_pool_size
    
    @max_pool_size.setter
    def max_pool_size(self, value):
        if value > self._max_pool_size:
            self._max_pool_size = value
    
    @property
    def free_size(self):
        return self._free_items.qsize()
    
    @property
    def pool_size(self):
        return len(self)
    
    @property
    def size(self):
        return '<max={}, current={}, free={}>'.format(self.max_pool_size,
                                                      self.pool_size,self.free_size)
    def add(self, item):
        if item is None:
            return None
        
        if item in self:
            logger.debug('Duplicate item found "{}", current size is "{}"'.format(
                    item, self.size))
            return None
        
        if self.pool_size >= self.max_pool_size:
            raise PoolIsFullException
        
        self._free_items.put_nowait(item)
        
        with self._pool_lock:
            self._pool_items.add(item)
        
        logger.debug('Add item "{!r}", current size is "{}"'.format(item, self.size))
        
    def return_(self, item):
        ''' Return a item to the pool.
            Note that the item to be returned should exist in this pool '''
        if item is None:
            return False
        
        if item not in self:
            logger.error('Current pool dose not contain item:"{}"'.format(item))
            return False
        
        self._free_items.put_nowait(item)
        
        logger.debug('Return item "{!r}",current size is "{}"'.format(item, self.size))
        return True
    
    def get(self, block=True, wait_timeout=60):
        try:
            item = self._free_items.get(block, timeout=wait_timeout)
        except Empty:
            raise PoolIsEmptyException('Cannot find any available item.')
        else:
            logger.debug('Get item "{}", current size is "{}"'.format(item, self.size))
            return item
        
    