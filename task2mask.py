#!/usr/bin/env python

from db import db
import sys

class task2mask:
    def __init__(self):
        self.db = db()
        
    def mask(self, taskname):
        return self.db.lumimask( taskname )

if __name__ == "__main__":
    t2m = task2mask( )
    lm = t2m.mask( sys.argv[1] )
    print len(lm)
    print lm

