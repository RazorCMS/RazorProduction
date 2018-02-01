import cherrypy
import os
import urllib2
import json

class RestIndex(object):
    def __init__(self):
        pass
    def index(self):
        return "alive"
    def GET(self):
        text="<h1>REST API</h1>"
        text+="<table border='1'><thead><tr><th>Path</th><th>Function name</th><th>Doc</th></tr></thead><tbody>"

        keys = self.__dict__.keys()
        keys.sort()
        for key in keys:
            o = getattr(self, key)
            text+="<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%( key,
                                                                 o.__class__.__name__,
                                                                 getattr(getattr(o,'GET',None),'__doc__',''))
        text+="</tbody></table>\n"
        return text
    
    @cherrypy.expose
    def default(self, *vpath, **params):
        method = getattr(self, cherrypy.request.method, None)
        if not method:
            raise cherrypy.HTTPError(405, "Method not implemented.")
        return method(*vpath, **params); 

#class Header(RestIndex):
#    def GET(self):
#        d={}
#        for (key,value) in cherrypy.request.headers.iteritems():
#            d[key] = value
#        return json.dumps(d)

class GetDocs(RestIndex):
    def GET(self, *args,**argd):
        """
        Get all docs given label= version=
        """
        if not 'label' in argd and not 'version' in argd:
            return "missing arguments"

        label = argd['label']
        version = int(argd['version'])
        f =urllib2.urlopen('http://cms-caltech-db.cern.ch:5984/tasks/_design/tasks/_view/label-version?key=["%s",%d]&include_docs=true'%(label,version))

        return f.read()

class GetMain(RestIndex):
    def GET(self):
        """
        Get the main on-going production
        """
        f = urllib2.urlopen('http://cms-caltech-db.cern.ch:5984/main/_all_docs?include_docs=true')
        return f.read()

class Production(object):
    file_location = os.path.dirname(__file__)

    rest = RestIndex()
    rest.getdocs = GetDocs()
    rest.getmain = GetMain()
    #rest.header = Header()

    @cherrypy.expose
    def index(self, *args, **kwargs):
        #return json.dumps( kwargs )
        return open(os.path.join(self.file_location,'html','index.html'))
    
    

if __name__ == '__main__':
    cherrypy.quickstart(Production(), config='cherrypy.conf')
