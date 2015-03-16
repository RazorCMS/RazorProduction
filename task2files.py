#!/usr/bin/env python

import os
from db import db

class task2files:
    def __init__(self, localdir=None, eos=False):

        self.localdir = localdir
        self.redirector = 'cms-xrd-global.cern.ch'
        self.d = db()
        self.eos = eos

    def localize_all(self, label, version, force=False):
        ts = self.d.tasks(label=label,version=version)
        for t in ts: 
            if t['status'] in ['registered','done']:
                self.localize(t['_id'], force)        

    def localize(self, task, force=False):
        if not self.localdir: return
        l = self.d.filelist( task )
        for location in l:
            if os.path.isfile('%s/%s'%(self.localdir, location)) and (not force):
                print "%s already exist in %s" %( location, self.localdir )
            else:
                self.copy_a_file_( location )

    def copy_a_file_(self, lfn):
        if self.eos:
            ## need to put it in a local dir then put it back to eos
            temp_localdir = '/tmp/'
            print "Copying %s over the WAN into %s" %( lfn,  temp_localdir )
            os.system('mkdir -p %s/%s'%(temp_localdir, lfn.rsplit('/',1)[0]))
            os.system('xrdcp root://%s/%s %s/%s'%( self.redirector, lfn,
                                                   temp_localdir, lfn ))
            ## create the hierarchy in eos
            print "Copying %s into eos: %s" %( lfn,  self.localdir )
            os.system('cmsMkdir %s/%s'%(self.localdir, lfn.rsplit('/',1)[0]))
            os.system('cmsStage -f %s/%s %s/%s'%( temp_localdir, lfn,
                                                  self.localdir, lfn ))
            ## then remove the local tmporary file
            os.system('rm -f %s/%s'%(temp_localdir, lfn ))
        else:
            print "Copying %s over the WAN into %s" %( lfn,  self.localdir )
            os.system('mkdir -p %s/%s'%(self.localdir, lfn.rsplit('/',1)[0]))
            os.system('xrdcp root://%s/%s %s/%s'%( self.redirector, lfn,
                                                   self.localdir, lfn ))
    def check_file_(self, path ):
        if self.eos:
            if os.system('cmsLs %s'%(path))==0:
                return True
            else:
                return False
        else:
            return os.path.isfile(path)

    def list(self, task, force=False):
        r=[]
        l = self.d.filelist( task )
        for location in l:
            if self.localdir:
                if self.check_file_('%s/%s'%(self.localdir, location)):
                    r.append('%s/%s'%( self.localdir, location))
                else:
                    if force:
                        self.copy_a_file_( location )
                        r.append('%s/%s'%( self.localdir, location))
                    else:
                        print "%s is absent in %s" %( location ,self.localdir)
            else:
                r.append('root://%s/%s' % (self.redirector, location ))

        if self.eos:
            r = map(lambda lfn : 'root://eoscms//eos/cms'+lfn, r)

        return r


if __name__ == "__main__":
    import sys
    ld = sys.argv[1]
    t2f = task2files(localdir=ld)
    tn = sys.argv[2]
    t2f.localize(tn)

    
