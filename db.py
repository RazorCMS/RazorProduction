import os
import json
import pprint
import copy 
import couchdb

class db:
    def __init__(self):
        self.couch = couchdb.Server('https://cms-caltech-db/db/')
        self.rdb = self.couch['tasks']
        self.cdb = self.couch['prods']
        self.odb = self.couch['outputs']
        self.main = self.couch['main']

    def register(self, out, fns= None, locations=None, owner=None):
        files=[]
        locs=[]
        if fns:
            files=fns
        if locations:
            locs = locations
        newid=out.replace('/','|')
        rev=None
        if newid in self.odb:
            rev= self.odb[newid]['_rev']
        if not newid in self.odb or len(self.odb[newid]['filenames'])==0:
            doc = { "datasetname" : out,
                    "filenames" : fns,
                    "locations" : locs,
                    "status" : "new",
                    "owner" : owner,
                    "_id" : newid
                    }
            if rev:
                doc['_rev'] = rev
            self.odb.save( doc )
            print out,"registered as output in",newid
        else:
            print out,"has already been registered in doc",newid

    def getoutput(self, something):
        if something in self.rdb:
            if 'output' in self.rdb[something] and self.rdb[something]['output']:
                something = self.rdb[something]['output'][0] ### only the first output !!!
            else: 
                return None
        if '/' in something:
            docid = something.replace('/','|')
        else:
            docid = something

        if not docid in self.odb:
            print "Cannot find the information about",something,"under",docid
            return None
        else:
            return self.odb[docid]

    def cleaning(self, label, version):
        ## get campaign
        campaign_doc = self.cdb["%s_v%s"%(label,version)]
        ## get all tasks
        task_docs = self.rdb.view('tasks/label-version', key=[label,version])
        outputs_docs = []
        files_to_remove = []
        ## get all ouputs
        for r in task_docs:
            #search by owner
            outputs_docs.extend( self.odb.view('outputs/owner', key=[r['id']]) )

        #print campaign_doc
        #print len( task_docs )
        #print len( outputs_docs )

        #clean the output doc
        for oid in outputs_docs:
            print oid['id']
            doc = self.odb.get( oid['id'] )
            files_to_remove = doc['filenames'] 
            self.odb.delete( doc )

        # clean the task doc
        for tid in task_docs:
            print tid['id']
            doc = self.rdb.get( tid['id'] )
            self.rdb.delete( doc )
        
        #clean the campaign document
        self.cdb.delete( campaign_doc )

    def lumimask(self, task):
        if task in self.rdb:
            r= self.rdb[task]
            if 'ranlumis' in r:
                return r['ranlumis']
        print "not mask found for",task
        return []

    def filelist(self, something):
        o = self.getoutput( something )
        if o: return o['filenames']
        else: return []
        
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
        for dn in self.cdb.view('prods/label-version'):
            print "\t",dn['key'][0],dn['key'][1]


    def get_campaign( self, label, version=None,status=None):
        ##until we have a view
        v=0
        latest_v=None
        view='prods/label'
        key =[label]
        if status:
            view+='-status'
            key.append(status)
        if version:
            view+='-version'
            key.append(version)
        print "using cdb ",view,key
        for cn in self.cdb.view(view,key=key,include_docs=True):
            c= cn['doc']
            if c['version'] > v:
                v=c['version']
                latest_v = c 
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
        print label,version
        for cn in self.cdb.view('prods/label-version',key=[label,version],include_docs=True):
            return cn['doc']
        return None

    def current(self,label,status='started',version=None):
        return self.get_campaign(label,version=version,status=status)

    def tasks(self,label,version,rstatus=None,user=None,status='started'):
        #c=self.current(label=label,status=status,version=version)
        #if not c:
        #    return []
        this=[]
        view='tasks/label-version'
        key=[label,version]
        if user:
            view+='-user'
            key.append(user)
        if rstatus:
            view+='-status'
            key.append(rstatus)
        print "using rdb ",view,key
        this = [rn['doc'] for rn in self.rdb.view(view,key=key,include_docs=True)]
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
