#!/usr/bin/env python

from db import db
import sys
import json

class task2mask:
    def __init__(self):
        self.db = db()
        
    def mask(self, taskname):
        return self.db.lumimask( taskname )

if __name__ == "__main__":
    t2m = task2mask( )
    lm = t2m.mask( sys.argv[1] )
    #print len(lm)
    if len(sys.argv)>1:
        print "mask written in",sys.argv[2]
        open(sys.argv[2],'w').write(json.dumps(lm))
    else:
        print json.dumps(lm)
        
