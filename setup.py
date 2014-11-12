#!/usr/bin/env python

import os
import sys
import pprint
from optparse import OptionParser
from db import db

production_schema={
    'admins': (None, "the coma separated list of username being able to make changes in the production" ,str,list),
    'dataset':("", "the list of datasets to be processed in the production",str,list) ,
    'installation': ( None, "the set of instructions to instal and compile the software for the production",str,str),
    'setup' : (None,"the list of instructions to setup the production",str,str),
    #'timing' : (None,"The average time to process an event",float,float),## NOT USED YET
    'label': (None,"the name of the production",str,str),
    'version' : (None,"the version of the production",int,int),
    'participants': ("","the coma separated list of people allow to participate in the production",str,list),
    'status' : ('new',None,str,str),
    'outpath' : ("", "specify the output location at the site",str,str),
    'outsite' : ("T2_US_Caltech", "the output storate site",str,str)
    }
    
usage="""
"""
parser = OptionParser(usage)
a_doc={}
for (key,(defv,comment,i_type,c_type)) in production_schema.items():
    if comment:
        add=""
        if defv==None:
            add="is MANDATORY"
        parser.add_option('--%s'% key, help=comment+add, default=None, type=i_type)
        #if defv!=None:
        #    parser.add_option('--%s'% key, help=comment,default=defv,type=i_type)
        #else:
        #    #make it mandatory
        #    parser.add_option('--%s'% key, help=comment,type=i_type)
    else:
        ## the ones that do not need anything
        a_doc[key] = c_type(defv)

parser.add_option('-u',help="update the information in the db",dest="update_",default=False,action="store_true")
parser.add_option('-c',help="read the information from a card",dest="card_",default=False,action="store_true")
parser.add_option('-a',help="add the provided information to the existing config",dest="add_",default=False,action='store_true')
(options,args) = parser.parse_args()

if options.add_ and not options.update_:
    print "add options only functions with updating"
    sys.exit(1)
if options.add_ and options.card_: 
    print "add option does not function with using card"
    sys.exit(2)    

d = db()
if options.update_:
    a_doc = d.get_campaign( options.label, options.version )
    
if options.card_:

    card=open("%s_v%d.card"%(options.label,options.version))
    cards=card.read().split('\n')
    key=None
    add=False
    for l in cards:
        if not l: continue
        if l.startswith('@@'):
            key=l[2:]
            add=True
            setattr(options,key,"")
        elif l.startswith('@'):
            key=l[1:]
            add=False
        else:   
            if add:    
                setattr(options,key,getattr(options,key)+'\n'+l)
            else:
                #use the specified type
                setattr(options,key, production_schema[key][2](l))
                """if l.isdigit():
                    setattr(options,key,int(l))
                elif l.replace('.','').isdigit()
                    setattr(options,key,float(l)
                else:
                    setattr(options,key,l)
                """

for (key,(defv,comment,i_type,c_type)) in production_schema.items():
    if hasattr(options,key):
        if options.update_ and getattr(options,key)==None:
            ## update whatever is really needed
            continue
        if options.update_ and key in ['version','label']:
            print "not updating",key
            continue

        if getattr(options,key)==None:
            if defv==None:
                print key,"is a mandatory member"
                sys.exit(1)            
            else:
                setattr(options,key,defv)

        if c_type==list:
            if options.add_:
                a_doc[key].extend(filter(None,getattr(options,key).split(',')))
            else:
                a_doc[key] = filter(None,getattr(options,key).split(','))
        else:
            if options.add_:
                print "add options does not function for non list member:",key
                sys.exit(3)
            a_doc[key] = c_type(getattr(options,key))
        if a_doc[key]==None:
            print key,"is a mandatory member"
            sys.exit(1)

K=raw_input("Go with %s \n ? Y/N :"%(pprint.pformat(dict(a_doc))))

if K.lower() in ['y','yes']:
    if options.update_:
        d.cdb.save( a_doc )
    else:
        a_doc['_id'] = "%s_v%d" % ( a_doc['label'] , a_doc['version'] )
        d.save_campaign( a_doc )
