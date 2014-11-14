from ROOT import *
import numpy as np
from task2files import task2files
import pickle

class task2chain(TChain):
    def __init__(self, task,
                 localdir='/data/vlimant',
                 struct=['configurableAnalysis/razorv','configurableAnalysis/razor'],force=False,eos=False):
        TChain.__init__(self,struct[0])
        self.friends = []
        for t in struct[1:]:
            self.friends.append( TChain("configurableAnalysis/razor"))

        self.localdir = localdir
        myfiles=task2files(localdir=localdir,eos=eos).list(task)
        if not myfiles:
            print "There are no localfiles for",task
            if force:
                myfiles=task2files(localdir=localdir,eos=eos).list(task, force=True)
            else:
                return

        for f in myfiles:
            self.AddFile( f )
            for fr in self.friends:
                fr.AddFile( f )

        self.leaves_=map(lambda l : l.GetName(), self.GetListOfLeaves())
        for fr in self.friends:
            self.AddFriend( fr )
            self.leaves_.extend(map(lambda l : l.GetName(), fr.GetListOfLeaves()))

    def leaves(self):
        return self.leaves_

    def tonp(self, leaves=[], maxN=None, write=False):
        self.SetBranchStatus('*',0)
        releave=[]
        for l in leaves:
            if ':' in l:
                (l,i) = l.split(':')
                releave.append( (l,int(i)))
            else:
                releave.append( (l, None))

            if not l in self.leaves_:
                print "leave",l,"is not allowed from",self.leaves_
                return None
            self.SetBranchStatus(l,1)
        samples=self.GetEntries()
        if maxN and samples>maxN:
            samples=maxN
        ## initialize the data
        data = np.zeros([samples, len(leaves)])

        ientry=0
        for event in self:
            if ientry>=samples: break

            for (il,l) in enumerate(releave):
                o=getattr(self,l[0])
                v=0
                if l[1]!=None:
                    if l[1]<len(o):
                        v=o[l[1]]
                else:
                    v=o
                data[ientry][il] = v
            ientry+=1            
        if write:
            d=open(self.localdir+'/'+write+'.pkl','w')
            pickle.dump( data, d)
            d.close()

        print data[-1]
        return data

if __name__ == "__main__":
    task='cat_v1_DYJetsToLL_M-50_HT-400to600_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5'
    stats=10000
    for task in [
        'cat_v1_DYJetsToLL_M-50_HT-400to600_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5',
        'cat_v1_QCD_Pt-15to30_Tune4C_13TeV_pythia8_castor_PU20bx25_POSTLS170_V5',
        'cat_v1_TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5',
        'cat_v1_WJetsToLNu_HT-400to600_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5',
        'cat_v1_ZJetsToNuNu_HT-200to400_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5'
        ]:
        print task
        tree = task2chain(task)
        data = tree.tonp(['jets_pt:0','jets_pt:1','jets_pt:2',
                          'razor_MR','razor_R2',
                          'electrons_Pt:0','electrons_Pt:1',
                          'muons_Pt:0','muons_Pt:1',
                          'jets_eta:0','jets_eta:1','jets_eta:2',
                          'jets_mass:0','jets_mass:1','jets_mass:2',
                          ],
                         maxN=stats, 
                         write=task)
        
