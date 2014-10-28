import os
from db import db

#d=db()
#l1=d.filelist('leopard_v1_RSGluonToTT_M-4000_Tune4C_13TeV-pythia8')
#print l1
#l2=d.filelist('tiger_v1_QCD_Pt-470to600_Tune4C_13TeV_pythia8')
#print l2
#ts = d.tasks(label='cat',version=1)
#for t in ts:
#    l3=d.filelist(t['_id'])
#    if l3:
#        ## replicate it over here
#        redirector = 'cms-xrd-global.cern.ch'
#        localdir = '/data/vlimant'
#        for location in l3:
#            print "Copying %s over the WAN into %s" %( location, localdir )
#            os.system('mkdir -p %s/%s'%(localdir, location.rsplit('/',1)[0]))
#            os.system('xrdcp root://%s/%s %s/%s'%( redirector, location,
#                                                   localdir, location ))
            
                      
class task2files:
    def __init__(self, localdir=None):

        self.localdir = localdir
        self.redirector = 'cms-xrd-global.cern.ch'
        self.d = db()

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
        print "Copying %s over the WAN into %s" %( lfn,  self.localdir )
        os.system('mkdir -p %s/%s'%(self.localdir, lfn.rsplit('/',1)[0]))
        os.system('xrdcp root://%s/%s %s/%s'%( self.redirector, lfn,
                                               self.localdir, lfn ))

    def list(self, task, force=False):
        r=[]
        l = self.d.filelist( task )
        for location in l:
            if self.localdir:
                if os.path.isfile('%s/%s'%(self.localdir, location)):
                    r.append('%s/%s'%( self.localdir, location))
                else:
                    if force:
                        self.copy_a_file_( location )
                        r.append('%s/%s'%( self.localdir, location))
                    else:
                        print "%s is absent in %s" %( self.localdir, location)
            else:
                r.append('root://%s/%s' % (self.redirector, location ))
        return r


if __name__ == "__main__":
    t2f = task2files(localdir='/data/vlimant/')
    #t2f.localize_all(label='cat', version=1)
    t2f.localize('cat_v1_DYJetsToLL_M-50_HT-400to600_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5')


