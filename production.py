#!/usr/bin/env python                                                                                                                                                                                                                                                                                                       
import os
from optparse import OptionParser
from collections import defaultdict
from db import db
import random
import sys
import pprint 
import httplib,urllib2
import json
import copy
import hashlib

import ssl                                                                                                                                                                                             
ssl.match_hostname = lambda cert, hostname: hostname == cert['subjectAltName'][0][1]

try:
    from CRABAPI.RawCommand import crabCommand
except:
    print "source the crab3 env before"
    sys.exit(1)

#def get_from_log( log, field):
#    interest=filter(lambda l : l.startswith(field),log)
#    if len(interest):
#        value = interest[-1].split()[-1]
#        return value
#    return None

class X509CertAuth(httplib.HTTPSConnection):
    def __init__(self, host, *args, **kwargs):
        #x509_path = os.getenv("X509_USER_PROXY", None)
        x509_path = self.proxy
        #print "Proxy for cmsweb auth",x509_path
        key_file = cert_file = x509_path
        httplib.HTTPSConnection.__init__(self, host,key_file = key_file,cert_file = cert_file,**kwargs)

class X509CertOpen(urllib2.AbstractHTTPHandler):
    def default_open(self, req):
        return self.do_open(X509CertAuth, req)

def generic_call(url,header=None, load=True, data=None, delete=False):
    opener=urllib2.build_opener(X509CertOpen())
    datareq = urllib2.Request(url)

    if data:
        datareq.add_data( data )
    if delete:
        datareq.get_method = lambda: 'DELETE'

    if header:
        for (k,v) in header.items():
            datareq.add_header(k,v)
    try:
        requests_list_str=opener.open(datareq).read()
        if load:
            return json.loads(requests_list_str)
        else:
            return requests_list_str
    except:
        import traceback
        print "generic_call %s failed for %s"%( datareq.get_method(), url)
        if data:
            print json.dumps( data )
        print traceback.format_exc()
        return None

def getReport( task_object ):
    certPrivilege()

    task_name = task_object['taskname']
    res = crabCommand('report', 
                      dir = task_object['taskdir'], 
                      proxy = os.getenv('X509_USER_PROXY'))

    print "Showing the report but reporting nothing"
    print json.dumps(res, indent=2)

    ## need to massage lumis from res
    return None,None

    """
    data = '&'.join(["workflow=%s"%(task_name) , "limit=-1", "subresource=report" ])
    outputs = generic_call('https://cmsweb.cern.ch/crabserver/prod/workflow/?'+data, header={"User-agent":"CRABClient/3.3.9","Accept": "*/*"})

    input_mask = outputs['result'][0]['lumiMask']
    #pprint.pprint( input_mask )

    poolInOnlyRes = {}
    for jn, val in outputs['result'][0]['runsAndLumis'].iteritems():
        poolInOnlyRes[jn] = [f for f in val if f['type'] == 'POOLIN']


    #mergedLumis = set()
    #doubleLumis = set()

    dLumisDict = defaultdict( set )
    mLumisDict = defaultdict( set )

    for reports in poolInOnlyRes.values():
        for report in reports:
            rep = eval( report['runlumi'] )
            for run, lumis in rep.iteritems():
                run=int(run)
                for lumi in map(int,lumis):
                    #if (run,lumi) in mergedLumis:
                    #    doubleLumis.add((run,lumi))
                    #mergedLumis.add((run,lumi))
                    if lumi in mLumisDict:
                        dLumisDict[run].add( lumi )
                    mLumisDict[run].add( lumi )

    def compact( lumis ):
        #return a compact list of pairs
        ret=[]
        firstLumi=None
        lastLumi=None
        for lumi in lumis:
            if firstLumi==None:
                firstLumi=lumi
                lastLumi=lumi
            else:
                if lastLumi==None or lumi == lastLumi+1:
                    ## still in the range
                    lastLumi = lumi
                else:
                    ret.append([firstLumi,lastLumi])
                    lastLumi=None
                    firstLumi=lumi
                    
        if firstLumi:
            if lastLumi:
                ret.append([firstLumi,lastLumi])
            else:
                ret.append([firstLumi,firstLumi])
        return ret

    #pprint.pprint( len(mergedLumis) )
    #pprint.pprint( doubleLumis )


    for r,lumis in mLumisDict.iteritems():
        mLumisDict[r] = compact( lumis )

    for r,lumis in dLumisDict.iteritems():
        dLumisDict[r] = compact( lumis )

    return dict( mLumisDict ),dict( dLumisDict )
    """

def getOutput( task_object ):
    certPrivilege()
    task_name = task_object['taskname']
    ## to be fixed you want the lfns of all output files
    #res = crabCommand('data',
    #                  proxy = os.getenv('X509_USER_PROXY')
    #                  )
    return []

def registerOutput( r ):
    if r['output'] and len(r['output']):
        for out in r['output']:
            print "Registering an edm output:",out
            outs= []
            ret = fileSummary( out, 'phys03', summary=False)
            for ns in ret: 
                outs.append( ns['logical_file_name'])
            if not outs:
                print "Empty outputs for",r['taskname']
                return
            d.register( out, 
                        fns=outs,
                        locations=r['outsite'],
                        owner=r['_id'])
    else:
        print "Getting output from crab3"
        ## get a list of files
        outs = getOutput( r )
        if not outs:
            print "Empty outputs for",r['taskname']
            return
        ## use the task id as datasetname
        d.register( r['_id'],
                    fns=outs,
                    locations=r['outsite'],
                    owner=r['_id']
                    )


def fileSummary( dataset, dbs, summary=True):
    certPrivilege()
    dbs3_url='https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/'%dbs
    if summary:
        urlds="%s/filesummaries?dataset=%s"%( dbs3_url, dataset)
    else:
        urlds="%s/files?dataset=%s"%( dbs3_url, dataset)

    ret = generic_call(urlds)    
    return ret

def crabKill( task_object, user):
    task_name = task_object['taskname']
    if not certPrivilege(user):
        print os.environ.get('USER'),"cannot kill a task for",user
        return False
    
    res = crabCommand('kill', 
                      dir = task_object['taskdir'],
                      proxy = os.getenv('X509_USER_PROXY')
                      )
    if res.get("status",None) == "SUCCESS":
        print "\t task kill successfully"
        return True
    else:
        print "failed to kill"
        print json.dumps( res ,indent=2)
        return False ## for now

def crabResubmit( task_object , jobs, black_sites, user):
    task_name = task_object['taskname']
    black_sites = filter(lambda s : not s in ['Unknown'], black_sites)
    if not certPrivilege(user):
        print os.environ.get('USER'),"cannot resubmit a task for",user
        return False
    
    res = crabCommand('resubmit', 
                      dir = task_object['taskdir'],
                      jobids = ",".join(jobs),
                      siteblacklist = ",".join(black_sites),
                      proxy = os.getenv('X509_USER_PROXY')
                      )
    print json.dumps(res)
    #print "\t resubmission sucessful"
    #return True
    print "failed resubmission"
    return False

def crabStatus( task_object ):
    certPrivilege()
    task_name = task_object['taskname']

    try:
        res = crabCommand('status',
                          long=True,
                          dir = task_object['taskdir'],
                          proxy = os.getenv('X509_USER_PROXY'))
        #print json.dumps( res , indent = 2 )
        print res.keys()
        status = res['status']
        return res
    except:
        try:
            res = crabCommand('status',
                              long=False,
                              dir = task_object['taskdir'],
                              proxy = os.getenv('X509_USER_PROXY'))
            #print json.dumps( res , indent = 2 )
            print res.keys()
            status = res['status']
            return res            
        except:
            print "no status for",task_name
            return None
    

def privilege(who=['vlimant'],what=''):
    if not privilegeB(who,what):
        sys.exit(1)

def certPrivilege(user=None):
    x509_path = os.getenv("X509_USER_PROXY", None)
    proxy_path = ''
    if user:
        proxy_path = '/afs/cern.ch/user/%s/%s/cert/voms_proxy.cert'%(user[0],user)
    ### a mode where vlimant copies the file o
    if options.impersonate:
        current_user = os.getenv('USER',None)
        home = os.getenv('HOME',None)
        new_proxy_path = '%s/private/cert/%s_voms_proxy.cert'%( home, user)
        copy_com = 'rm -f %s ; cp %s %s ; chmod 400 %s'%( new_proxy_path, proxy_path, new_proxy_path, new_proxy_path )
        print "Copied proxy cert over \n %s"%copy_com
        error = os.system( copy_com )
        print error
        if error!=0:
            print "Proxy file cannot be retrieved"
            return None
        proxy_path = new_proxy_path

    if os.path.isfile( proxy_path ):
        print "give",proxy_path
        X509CertAuth.proxy = proxy_path
        return proxy_path
    else:
        if user:
            if user == os.environ.get('USER'):
                X509CertAuth.proxy = x509_path
                return x509_path
        elif x509_path:
                X509CertAuth.proxy = x509_path
                return x509_path
        else:
            print "Proxy file %s not found and %s invalid"% (proxy_path,x509_path)

    X509CertAuth.proxy = None
    return None
    
def privilegeB(who=['vlimant'],what=''):
    if type(who) != list: 
        those = copy.deepcopy([who])
    else:
        those=copy.deepcopy(who)
            
    user=os.environ.get('USER')
    if user not in those:
        if what:
            print user,"cannot do ",what,", only",','.join(those),"can"
        else:
            print user,"cannot do that, only",','.join(those),"can"            
        return False
    return True


def write_crab( r, crab_py ):
    if '@' in r['dataset']:
        (dataset,dbs)=r['dataset'].split('@')
    else:
        dataset=r['dataset']
        dbs=None
    crab=open(crab_py,'w')
    nLumiPerJob = 30 ## usually ~100 events per lumi
    hash_id = hashlib.md5(r['id']).hexdigest()
    crab.write('''
from WMCore.Configuration import Configuration
config = Configuration()
config.section_("General")
config.General.requestName = "prod_%s_v%d_%s_v%d"
config.General.workArea = "crab_prod"

config.section_("JobType")
config.JobType.pluginName = "Analysis"
config.JobType.psetName = "prod.py"
config.JobType.allowUndistributedCMSSW = True

config.section_("Data")
config.Data.ignoreLocality = True
config.Data.publication    = False
config.Data.inputDataset = "%s"
config.Data.splitting = "LumiBased"
config.Data.unitsPerJob = %d
config.Data.outputDatasetTag = "%s_%s_v%d_v%d"

config.section_("Site")
config.Site.whitelist = ["T2_*"]
config.Site.storageSite = "%s"
'''%( r['label'],
      r['version'],
      hash_id, #r['id'],
      r['subversion'],
      dataset,
      nLumiPerJob,
      r['label'],
      ### add the proc_string
      dataset.split('/')[2],
      r['version'],
      r['subversion'],
      r['outsite']
      ))
    if 'USER' in dataset and not dbs:
        dbs= 'phys03'
    if dbs:
        crab.write("config.Data.dbsUrl = '%s'\n"%(dbs))
    if r['outpath']:
        outLFN = r['outpath']
        username = r['assignee']
        if not outLFN.endswith('/'):
            outLFN+='/'
        if not username in outLFN:
            outLFN+=username+'/'
        crab.write("config.Data.outLFNDirBase = '%s'\n"%(outLFN))
                
    crab.close()
    print "crab config created for",r['id']
    r['status']='created'
    d.save_task( r ) 

def submit(d, r, crab_py, user):
    ## write the crab config in case not there yet
    if not os.path.isfile(crab_py):
        write_crab( r, crab_py )

    ## check if you can impersonate
    if not certPrivilege(user):
        print os.environ.get('USER'),"cannot submit a task for",user
        return False

    c = d.get_campaign(label=r['label'], version=r['version'])
    if not c:
        print "could not find",r['label']
        return False

    test = os.system(c['setup'])
    if test!=0:
        print "The setup command failed %d \n %s. You probably need to install the production" %( test, c['setup'])
        return False

    retry = True
    while retry:
        res = crabCommand('submit', config = crab_py , proxy = os.getenv('X509_USER_PROXY'))
        taskname = res.get('uniquerequestname', None)
        reqname = res.get('requestname', None)
        if taskname and reqname:
            r['taskname'] = taskname
            r['status']='submitted'
            ## or adjust the directory
            r['taskdir']=os.getenv('PWD')+'/crab_prod/'+reqname
            retry=False
        else:
            retry=False
            ## try to remove the directory
            print json.dumps(res, indent=2)
            print "could not submit with",crab_py

    d.save_task( r ) 
    return True

def resubmit(r, do=True):
    failed= set()
    failed_sites = set()
    
    if 'jobs' in r['taskinfo']:
        for (jid,jst) in r['taskinfo']['jobs'].items():
            if jst['State'] == 'failed':
                failed.add(jid)
                if 'SiteHistory' in jst:
                    failed_sites.update(jst['SiteHistory'])
    #print failed,failed_sites
    print len(failed),"failed jobs at",len(failed_sites),"sites"

    if failed:
        print "Resubmitting for",r['id']
        return crabResubmit( r, failed , failed_sites, r['assignee'])
    else:
        print "No failed jobs to resubmit"
    return False

option_usage={
    'setup' : 
    'Sets up a new production campaign from a file <label>_<version>.card or add the provided coma sperated dataset names to the list to be processed',
    'start' :
        'Start the processing campaign by creating the tasks, and counting statistics',
    'assign' :
        'Assign randomly the tasks to the provided coma separated list of users',
    'list' :
        'List the tasks assigned to you or --args @user (@all), or the task --args n, or the task containing --args string',
    'install' :
        'Use the production recipe to install the software and production configurations',
    'create' :
        'Create the crab configuration for the task --args n, or the task containing --args string',
    'submit' :
        'Doest the explicit submission of the task --args n, or the task containing --args string',
    'reset' : 
        'Does reset the task --args n, or the task containing --args string',
    'acquire' :
        'Allows to assign to oneself a task of someone else',
    'collect' : 
        'Retrieve the crab status and operated resubmissions, reset if necessary of the task --args n, or the task containing --args string',
    'clean' : 
        'Remove all documents pertaining a given production'
    }
do_choices=['setup','start','assign','list','install','create','submit','reset', 'acquire','collect','clean']

usage='''./production.py --do <actions> [--args <arguments>]
'''
for c in do_choices:
    usage+="\t %s\n"%c
    usage+=option_usage[c]
    usage+='\n'
d=db()

default_label=d.get_label()
default_version=d.get_version()

parser = OptionParser(usage)

parser.add_option("--do",help="The action to be done %s"%do_choices,choices=do_choices,default='list')
parser.add_option("--label",help="The production to participate in (default=%s)"%default_label, default=default_label)
parser.add_option("--version",help="The version of the production to participate in (default=%d)"%default_version,default=default_version)
parser.add_option("--args",help="The arguments to be passed",default=None)
parser.add_option("--unlimited",help="limits the collect action",default=False,action='store_true')
parser.add_option("--impersonate",help="allow one to impersonate the others", default=False,action='store_true')
(options,args) = parser.parse_args()


if options.version:
    options.version = int(options.version)

print "####################################################"
print "Currently working on %s version %d"%( options.label, options.version )
print "####################################################"

if options.do == 'setup':
    ##  does it already exist ?
    c=d.get(label=options.label,version=options.version)
    if c:
        privilege(c['admins'])

        ##maybe just include things to it
        if options.args:
            ds=options.args.split(',')
            c['dataset']=list(set(c['dataset']+ds))
            d.save_campaign( c )
            print c['dataset']
        else:
            print "nothing to be done for existing",c['label'],c['version']

    else:
        ##read in a card for setting something up
        card=open("%s_v%d.card"%(options.label,options.version))
        cards=card.read().split('\n')
        key=None
        data={}
        add=False
        check_schema = {'admins':[],
                        'dataset':[],
                        'installation':None,
                        'setup' : None,
                        'label':None,
                        'version' : None,
                        'participants':[],
                        'status' : 'new',
                        'outpath' : "", ## specify the output location
                        'outsite' : 'T2_US_Caltech',
                        }
        for l in cards:
            if not l: continue
            if l.startswith('@@'):
                key=l[2:]
                add=True
                data[key]=""
            elif l.startswith('@'):
                key=l[1:]
                add=False
            else:   
                if add:    
                    data[key]+='\n'+l
                else:
                    if l.isdigit():
                        data[key]=int(l)
                    elif ',' in l or type(check_schema[key]) == list:
                        data[key] = l.split(',')
                    else:
                        data[key]=l

        print data.keys()
        data['status']='new'

        for (key, value) in  check_schema.items():
            if not key in data and value==None:
                print key,"is a mandatory entry"
                sys.exit(13)
            elif not key in data:
                print key,"is missing and added as",value
                data[key] = value
        if data['label'] != options.label:
            print "inconsistent label"
            sys.exit(12)
        if data['version'] != options.version:
            print "inconsistent version"
            sys.exit(12)
        privilege(data['admins'])

        K=raw_input("Go with %s \n ? Y/N :"%(pprint.pformat(data)))
        if K.lower() in ['y','yes']:
            data['_id'] = "%s_v%d" % ( data['label'] ,data['version'] )
            d.save_campaign( data )


    sys.exit(0)
    

if options.do == 'start':
    c=d.get(label=options.label,version=options.version)
    if c:
        privilege(c['admins'])
        if c['status'] != 'started' or True:
            ## build all tasks
            for ds in c['dataset']:
                ## how to name the task from the dataset
                #this_id='_'.join([ds.split('/')[1],ds.split('/')[2].split('-')[1]])
                this_id='_'.join(ds.split('/')[1:3])
                print this_id
                newtask={
                    "label" : c['label'],
                    "version" : c['version'],
                    "subversion" : 1,
                    "nevents" : 0,
                    "dataset" : ds,
                    "assignee" : None,
                    "status" : "new",
                    "id" : this_id,
                    "taskname" : None,
                    "taskdir" : None,
                    "outpath" : c['outpath'],
                    "outsite" : c['outsite'],
                    }

                if d.exists( newtask ): 
                    print newtask['id'],"exists"
                    continue
                ## sum up the size
                dbs='global'
                dataset=ds
                if 'USER' in dataset:
                    dbs='phys03'
                if '@' in dataset:
                    (dataset,dbs) = dataset.split('@')
                ret = fileSummary( dataset,dbs )
                for r in ret: 
                    newtask['nevents']+=r['num_event']
                print newtask['dataset'],newtask['nevents']
                ## find out whether it's there already
                if d.add( newtask ):
                    print pprint.pformat(newtask),"was added"


            c['status'] = 'started'
            print c,"started"
            d.save_campaign( c )
        ## set as current main production on-going for everyone to retrieve from the same label/version
        d.set_main(options.label,version=options.version)
        sys.exit(0)
    else:
        print "could not find",options.label,"to be started"
        sys.exit(1)
        


## assign to a bunch a people
if options.do == 'assign':
    c = d.get_campaign(label=options.label, version=options.version)
    privilege(c['admins'])
    users=c['participants']
    if options.args:
        users=options.args.split(',')

    rs = d.tasks(label=options.label,version=options.version)
    for r in rs:
        if not r['assignee']:
            r['assignee'] = random.choice( users )
            d.save_task( r ) 
        print r['id'],'assigned to',r['assignee']
    sys.exit(0)

if options.do == 'clean':
    ## this is dangerous indeed !!!
    d.cleaning( options.label, options.version)


##install the production 
if options.do == 'install':
    c = d.get_campaign(label=options.label, version=options.version)
    if c:
        print "Installing production for",c['label'],"version",c['version']
        #print c['installation']
        os.system( c['installation'] )
        sys.exit(0)
    else:
        print "could not find",options.label,"started"
        sys.exit(1)

## create the tasks
if options.do in ['list','create','submit','reset','collect','acquire']:
    d.get_campaigns()
    user=os.environ.get('USER')
    if options.args and '@' in options.args:
        options.args,user=options.args.split('@')
        if user=='all': 
            user=None
        else:
            print "looking for user",user
        #print type(options.args),options.args.isdigit(),user
    status = None
    if options.args and '%' in options.args:
        options.args,status=options.args.split('%')
        print "looking for status",status


    rs = d.tasks(label=options.label,user=user,version=options.version,rstatus=status)
    l=len(rs)

    for (ri,r) in enumerate(rs):
        if options.args:
            if options.args.isdigit():
                if ri!=int(options.args): continue
            elif not options.args in r['id']: continue
        print "%d/%d]"%(ri,l)+100*"-"
        if options.do == 'list':
            for (k,v) in r.items():
                if k.startswith('_'): continue
                if k in []: continue
                if type(v) != dict:
                    print "%s : %s"%(k,v)
                else:
                    what = ['outdatasets','jobsPerStatus']
                    for w in what:
                        if w in v:
                            print "%s.%s: %s"%( k,w,v[w])
                        else:
                            print "%s.%s: N/A"%(k, w)
                    #pprint.pprint( v )

                    #jobs=defaultdict(list)
                    #for status in v['jobsPerStatus'].keys():
                            #for (jid,jst) in v['jobs'].items():
                            #if jst['State'] == status:
                            #    jobs[status].append(jid)
                    #pprint.pprint( dict( jobs))
                            #if 'failed' in jobs:
                            #print "failed",','.join(jobs['failed'])
            #pprint.pprint( r )
            outs = getOutput( r )
            print len(outs),"outputs"
            print '\n'.join(outs)
            continue
        if options.do == 'reset':
            if not privilegeB(r['assignee'],'reset'):
                continue
            ## do the hard reset of a task regardless of what is the status in crab
            K=raw_input("Go with killing task %s ? Y/N :"%( r['taskname']))
            if K.lower() in ['y','yes']:
                K=raw_input("Confirm that you want to kill all for task %s ? Y/N :"%( r['taskname']))
                if K.lower() in ['y','yes']:
                    dead = crabKill( r, r['assignee'])
                    print "Crab kill output",dead
                    if not dead:
                        print "Crab kill failed. Please retry to reset again"
                        continue
                else:
                    continue
            else:
                continue

            K=raw_input("Go with ressetting %s @ %s \n ? Y/N :"%(r['id'], r['assignee']))
            if K.lower() in ['y','yes']:
                print "ressetting",r['id']
                if r['status'] in ['submitted','done']:
                    r['subversion']+=1
                    print "bump"
                r['status'] = 'new'
                r['taskdir'] = ''
                r['taskname'] = ''
                r['taskinfo'] = {}
                d.save_task( r )
            continue

        if options.do == 'acquire':
            if r['status'] not in ['new','created']:
                print r['id'],'is',r['status']
                continue

            r['assignee'] = os.environ.get('USER')
            print r['id'],'belongs to',r['assignee']
            d.save_task( r )
            continue

        if options.do in ['create','submit','collect']:
            crab_py = 'prod_%s_v%d_%s_v%d.py'%(r['label'],r['version'],r['id'],r['subversion'])

        if options.do in  ['create']:
            if r['status']!='new':
                print r['id'],'is',r['status']
                continue
            #if not privilegeB(r['assignee'],'create'):              
            #    continue
            # others are protected if you create for them, they will be created for them too
            write_crab( r, crab_py )
            continue

        if options.do in  ['submit']: 
            if r['status'] != 'created':
                print "Cannot submit",r['id'],'in status',r['status']
                continue
            # delegate the privilege to proxy existence
            #if not privilegeB(r['assignee'],'submit'):     
            #    continue
            submit(d, r, crab_py, r['assignee'])
            continue

        if options.do in ['collect']:
            print "\tCollecting for",r['id'],'@',r['assignee']

            if r['status'] in ['registered']:
                print r['id'],'is',r['status']
                continue

            if r['status'] in ['done']:
                print r['id'],'is',r['status']
                print r['status'],"Getting report from crab3"
                (ran,twice) = getReport( r )
                r['ranlumis'] = ran
                open(r['taskdir']+'/lumiSummary.json','w').write(json.dumps(ran))
                r['duplicatelumis'] = twice

                registerOutput( r )

                r['status'] = 'registered'
                d.save_task( r )
                continue
            
            if r['status'] == 'new':
                if not options.unlimited: continue
                ## then create it !
                #if not privilegeB(r['assignee'],'create'): 
                #    continue
                write_crab( r, crab_py )
                continue
            
            if r['status'] == 'created':
                if not options.unlimited: continue
                ## then submit it !
                # delegate the privilege to proxy existence    
                #if not privilegeB(r['assignee'],'submit'):
                #    continue
                print "submitting",r['id'],'in',r['status']
                submit(d, r, crab_py, r['assignee'])
                continue

            ## get the info from crab-status
            #info=crabStatus(r['taskname'])
            info=crabStatus(r)

            if not info: 
                print "could not find anything for",r['taskname']
                continue
            if info['status'] == 'UNKNOWN':
                print "Could not get anything for",r['taskname']
                continue

            ## make a copy into the task itself
            r['taskinfo']=copy.deepcopy(info)
            if 'outdatasets' in info:
                r['output'] = copy.deepcopy(info['outdatasets'])
            else:
                r['output'] = None

            if info['status'] == 'COMPLETED':
                
                if r['status'] == 'submitted':
                    print r['id'],'is done'
                    # get the lumi mask while progressing on the processing
                    info['status'],"Getting report from crab3"
                    (ran,twice) = getReport( r  )
                    r['ranlumis'] = ran
                    r['duplicatelumis'] = twice                    

                    r['status']='done'

                    registerOutput( r )

                    d.save_task( r )
                    continue

            elif info['status'] == 'SUBMITTED':
                r['status']='submitted'
                print info['status'],"Getting report from crab3"
                # get the lumi mask while progressing on the processing
                #(ran,twice) = getReport( r['taskname'] )
                (ran,twice) = getReport( r )
                r['ranlumis'] = ran
                r['duplicatelumis'] = twice
                ## register the output as we go
                registerOutput( r )
                ## takes care of resubmitting failed jobs only
                resubmit(r)
                d.save_task( r )
                continue
            
            elif info['status'] in ['FAILED', 'RESUBMITFAILED']:
                ## try to figure out what to do. resubmit or scratch  it
                if not info.get('jobSetID',None) and options.unlimited: ### needs fixing somehow
                    ## the taskk was just never started : scratch
                    print "The task was never started. Resetting",r['id']
                    r['status'] = 'new'
                    d.save_task( r )
                    continue

                diff_status=set(info['jobsPerStatus'].keys()) - set(['failed','finished'])
                if len(diff_status)==0:
                    ## only failed of finished jobs
                    resubmit(r)
                    continue
                else:
                    print "Unknow case. report to admins"
                    print info['status']
                    print info['jobsPerStatus']
                    r['status']= info['status']
                    d.save_task( r )
                    continue

            elif info['status'] in ['RESUBMIT','QUEUED']:
                print r['id'],'is',info['status']
                r['status']= 'submitted'
                d.save_task( r )
                continue
            else:
                print "Unknow case. report to admins"
                print r['id'],'is',r['status'],info['status']
                #print info['status']
                #pprint.pprint( info )
                continue

    

