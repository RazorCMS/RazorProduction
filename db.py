import os
import json
import pprint
import copy 
import couchdb

class db:
    def __init__(self):
        self.couch = couchdb.Server('http://cms-caltech-db:5984/')
        self.rdb = self.couch['tasks']
        self.cdb = self.couch['prods']
        self.odb = self.couch['outputs']
        self.main = self.couch['main']

    def register(self, out):
        if not out in self.odb:
            doc = { "datasetname" : out,
                    "filenames" : [],
                    "locations" : [],
                    "status" : "new",
                    "_id" : out
                    }
            self.odb.save( doc )

    def set_main(self, label, version):
        doc = self.main['main']
        doc['label'] = label
        doc['version'] =version
        self.main.save( doc )
        
    def get_label(self):
        doc = self.main['main']
        return doc['label']#'leopard'

    def get_version(self):
        doc = self.main['main']
        return doc['version']#1

    def show(self):
        print "all campaigns"
        for cid in self.cdb:
            print cid

        print "all requests"
        for rid in self.rdb:
            print rid

    def get_campaigns( self ):
        print "available productions"
        for d in self.cdb:
            if d.startswith('_'): continue
            c = self.cdb[d]
            print '\t',c['label'],c['version']

    def get_campaign( self, label, version=None,status=None):
        ##until we have a view
        v=0
        latest_v=None
        for cid in self.cdb:
            if cid.startswith('_'): continue
            c= self.cdb[cid]
            if c['label'] != label: continue
            if version and c['version'] != version: continue
            if status and c['status'] != status: continue
            if c['version'] > v:
                v=c['version']
                latest_v = c 
            if version: return c
        if latest_v: return latest_v
        return None
    def save_campaign(self, doc ):
        #if doc['_id'] in self.cdb:
        #    print doc['_id'],"already present"
        #    return False
        (i,r)=self.cdb.save( doc )
        doc = self.cdb[i]

    def save_task(self, doc):
        (i,r)=self.rdb.save( doc )
        doc = self.rdb[i]

    def exists(self, d):
        i = self.doc_id( d )
        if i in self.rdb:
            return True
        else:
            ## a fall back from the initially created docs
            i = '%s_v%d_%s_v%d' % ( d['label'],
                                    d['version'],
                                    d['id'],
                                    d['subversion']
                                    )
            return i in self.rdb

        #for rn in self.rdb:
        #    r = self.rdb[rn]
        #    if any(map( lambda k : d[k]!=r[k], ['version','label','id'])): continue
        #    return True
        #return False

    def doc_id( self, doc):
        return '%s_v%d_%s' % ( doc['label'], 
                               doc['version'],
                               doc['id'],
                               )
    def getA(self, docid, what):
        if what in self.couch:
            if docid in self.couch[what]:
                return self.couch[what][docid]
            else:
                print docid,"does not exist in",what
                return None
        else:
            print what,"is not a db"
            return None

    def updateA(self, doc, what):
        if not '_id' in doc:
            print "No document id present"
            return False
        if not what in self.couch:
            print what,"is not a db"                
            return False
        if doc['_id'] not in self.couch[what]:
            print "cannot update inexisting",doc['_id']
            return False
        (i,r) = self.couch[what].save( doc )
        doc = self.couch[what][i]
        return True

    def add (self, d):
        if not self.doc_id(d) in self.rdb:
            d['_id'] = self.doc_id(d)
            self.rdb.save(d)
            return True
        else:
            return False

    def get(self,label,version):
        for cn  in self.cdb:
            c = self.cdb[cn]
            if c['label'] != label: continue
            if c['version'] != version: continue
            return c
        return None

    def current(self,label,status='started',version=None):
        return self.get_campaign(label,version=version,status=status)

    def tasks(self,label,version,rstatus=None,user=None,status='started'):
        c=self.current(label=label,status=status,version=version)
        if not c:
            return []
        this=[]
        for rn in self.rdb:
            if rn.startswith('_'):continue
            r = self.rdb[rn]
            if all(map( lambda k : r[k]==c[k], ['version','label'])):
                if user and r['assignee'] != user: continue
                if rstatus and r['status'] != rstatus: continue
                this.append(r)
                
        this.sort(key = lambda d : d['id'])
        return this
    def __del__(self):

        import random
        if random.random()<0.05:
            ## comapatc on output, from time to time
            print "#####"
            print "Compacting the DB"
            print "#####"
            self.main.compact()
            self.cdb.compact()
            self.rdb.compact()


if __name__ == "__main__":
    #d = db()
    #d.show()
    #tasks=d.tasks()
    #pprint.pprint(tasks)
    pass