#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write see http://www.gnu.org/licenses/gpl.html
# Copyright 2012 Sebastian Herold

import os
import shutil

from bz2 import BZ2File

import createrepo
from createrepo.yumbased import CreateRepoPackage
from createrepo import MetaDataSqlite
from yum.sqlutils import executeSQL
from createrepo.utils import MDError
from yum import misc

class AppendingMetaDataSqlite(MetaDataSqlite):
    def __init__(self, destdir):
        MetaDataSqlite.__init__(self, destdir)
        
    def containsPackage(self, po):
        result = executeSQL(self.pri_cx, "SELECT count(*) FROM packages WHERE name = ? AND arch = ? AND version = ? AND epoch = ? AND release = ?;", (po.name, po.arch, po.version, po.epoch, po.release)).fetchall()
        count = result[0][0]
        if count > 0:
            return True
        
        return False
    
    def generateNewPackageNumber(self):
        result = executeSQL(self.pri_cx, 'SELECT MAX(pkgKey) FROM packages;').fetchall()
        return result[0][0] + 1
        
    def create_primary_db(self):
        self.check_or_create(self.pri_cx, 18, MetaDataSqlite.create_primary_db)
    
    def create_filelists_db(self):
        self.check_or_create(self.file_cx, 7, MetaDataSqlite.create_filelists_db)
    
    def create_other_db(self):
        self.check_or_create(self.other_cx, 6, MetaDataSqlite.create_other_db)
    
    def check_or_create(self, cursor, expected_count, create_method):
        result = executeSQL(cursor, 'select count(*) from sqlite_master;').fetchall()
        object_count = result[0][0]
        if object_count == 0:
            print 'Create db ...'
            create_method(self)
        elif object_count != expected_count:
            raise MDError('DB exists, but has wrong table count. Was ' + object_count.__str__() + ', expected: ' + expected_count.__str__())
    
def uncompressDB(from_file, to_file):
    if os.path.exists(from_file):
        orig = BZ2File(from_file)
        dest = open(to_file, 'wb')
        try: 
            shutil.copyfileobj(orig, dest)
        finally:
            dest.close()
            orig.close()
    else:
        print "DB skipped: File not found " + from_file
    
def uncompressDBs(from_dir, to_dir):
    uncompressDB(os.path.join(from_dir, 'primary.sqlite.bz2'), os.path.join(to_dir, 'primary.sqlite'))
    uncompressDB(os.path.join(from_dir, 'other.sqlite.bz2'), os.path.join(to_dir, 'other.sqlite'))
    uncompressDB(os.path.join(from_dir, 'filelists.sqlite.bz2'), os.path.join(to_dir, 'filelists.sqlite'))

def _return_primary_files(self, list_of_files=None):
    returns = {}
    if list_of_files is None:
        list_of_files = self.returnFileEntries('file')
    for item in list_of_files:
        if item is None:
            continue
        if misc.re_primary_filename(item):
            returns[item] = 1
    return returns.keys()
 
def _return_primary_dirs(self):
    returns = {}
    for item in self.returnFileEntries('dir'):
        if item is None:
            continue
        if misc.re_primary_dirname(item):
            returns[item] = 1
    return returns.keys()

# set missing functions
CreateRepoPackage._return_primary_files = _return_primary_files
CreateRepoPackage._return_primary_dirs = _return_primary_dirs

class UpdateRepo(object):
    
    def __init__(self, directory, rpm_to_add):
        self.config = createrepo.MetaDataConfig()
        self.config.directory = directory
        self.config.database_only = True
        self.output_dir = os.path.join(self.config.directory, 'repodata')
        self.temp_dir = os.path.join(self.config.directory, '.repodata')
        self.rpm = rpm_to_add

    def execute(self):
        self.reuseExistingMetadata()
        self.generateMetaData()

    def reuseExistingMetadata(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.mkdir(self.temp_dir)
        
        uncompressDBs(self.output_dir, self.temp_dir)

    def generateMetaData(self):
        generator = createrepo.MetaDataGenerator(self.config)
        
        generator.md_sqlite = AppendingMetaDataSqlite(self.temp_dir)
        
        self.addRpm(generator, self.rpm)
        
        generator.closeMetadataDocs()
        generator.doRepoMetadata()
        
    def addRpm(self, generator, rpm):
        po = generator.read_in_package(rpm)
        
        if generator.md_sqlite.containsPackage(po):
            print 'Package ' + po.__str__() + ' already included.'
        else:
            po.crp_reldir = rpm
            po.crp_packagenumber = generator.md_sqlite.generateNewPackageNumber()
            po.crp_baseurl = ''
            
            po.do_sqlite_dump(generator.md_sqlite)
            
            
            
# UpdateRepo('/Users/she/temp/repo', 'mod_python.rpm').execute()

