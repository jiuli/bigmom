#-*- coding:utf-8 -*-
# Author : lijunsong
# Date: 2017-12-6 16:30:00

import logging

from DBUtils.PooledDB import PooledDB
import pymysql
from pymysql.cursors import DictCursor, Cursor

from base import mysql_configs


logger = logging.getLogger("MySQLPool")

class MySQLPool():
    
    __pool = None
    def __init__(self,creator=pymysql,mincached=1, maxcached=20,
                 host=None,username=None, password="", database=None,
                 port=3306, charset='utf8',use_dict_cursor=True,**kwargs):
        
        self._host = host
        self._port = port
        self._creator = creator
        self._charset = charset
        self._username = username
        self._password = password
        self._database = database
        self._other_kwargs = kwargs
        self._mincached = mincached
        self._mincached = maxcached
        self._cursor_class = DictCursor if use_dict_cursor else Cursor
        
        self._conn = MySQLPool.__getConnection(self)
        self._cursor = self._conn.cursor()
        
    @staticmethod
    def __getConnection(self):
        if MySQLPool.__pool is None:
            __pool = PooledDB(creator=self._creator,mincached=self._mincached,
                              maxcached=self._mincached,host=self._host,port=self._port,
                              user=self._username,passwd=self._password,db=self._database,
                              charset=self._charset,cursorclass=self._cursor_class
                            )
            
            return __pool.connection()
        
    def queryAll(self,sql,param=None):
        
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        
        return result
    
    def queryOne(self,sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        
        return result

    def queryMany(self,sql,num,param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        
        return result
    
    def __getInsertId(self):
        self._cursor.execute('select @@IDENTITY AS id')
        result = self._cursor.fetchall()
        return result[0]['id']
    
    def insertOne(self,sql,value):
        
        self._cursor.execute(sql,value)
        return self.__getInsertId()
    
    def insertMany(self,sql,values):
        count = self._cursor.executemany(sql,values)
        return count
    
    def __query(self,sql,param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        
        return count
    
    def update(self,sql,param=None):
        
        return self.__query(sql, param)
    
    def delete(self,sql,param=None):
        
        return self.__query(sql, param)
    
    def begin(self):
        '''
        @summary: 开启事务
        '''
        self._conn.autocommit(0)  # execute()之后不自动提交
    
    def end(self, option='commit'):
        '''
        @summary: 结束事务
        '''
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()
            
    def dispose(self,isEnd=1):
        '''
        @summary: 释放连接池资源
        '''
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        
        self._cursor.close()
        self._conn.close()

if __name__ == '__main__':
    mySQLPool = MySQLPool(**mysql_configs.jason_local)
    sql = 'select * from sys_user where login_name like "%{}%"'.format('123')
    
    result = mySQLPool.queryAll(sql)
    if result == False:
        pass
    for res in result:
        print(res)
        print('\n')
    
    mySQLPool.dispose()
    
    