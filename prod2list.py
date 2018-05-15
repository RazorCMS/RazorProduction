#!/usr/bin/env python

import os 
import sys
from optparse import OptionParser
from db import db
import ssl
ssl.match_hostname = lambda cert, hostname: hostname == cert['subjectAltName'][0][1]

parser = OptionParser("")
parser.add_option("--label")
parser.add_option("--version",default=1,type=int)
parser.add_option("--prepend",default='root://eoscms//eos/cms/')
(options,args) = parser.parse_args()

d = db()
tasks = d.tasks(label=options.label, version=options.version)

for t in tasks:
    files = d.filelist( t['_id'] )
    filelist = open( t['_id']+'.txt','w')
    filelist.write('\n'.join([options.prepend+s for s in files]+['']))
    filelist.close()

