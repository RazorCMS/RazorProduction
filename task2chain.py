from ROOT import *
import numpy as np
from task2files import task2files
import pickle

class task2chain(TChain):
    def __init__(self, task,
                 localdir='/data/vlimant',
                 struct=['configurableAnalysis/razorv','configurableAnalysis/razor']):
        TChain.__init__(self,struct[0])
        self.friends = []
        for t in struct[1:]:
            self.friends.append( TChain("configurableAnalysis/razor"))

        for f in task2files(localdir=localdir).list(task):
            self.AddFile( f )
            for fr in self.friends:
                fr.AddFile( f )

        self.leaves_=map(lambda l : l.GetName(), self.GetListOfLeaves())
        for fr in self.friends:
            self.AddFriend( fr )
            self.leaves_.extend(map(lambda l : l.GetName(), fr.GetListOfLeaves()))

    def leaves(self):
        return self.leaves_

    def tonp(self, leaves=[], maxN=None):
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
        if maxN:
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
        return data

if __name__ == "__main__":
    task='cat_v1_DYJetsToLL_M-50_HT-400to600_Tune4C_13TeV-madgraph-tauola_PU20bx25_POSTLS170_V5'
    tree = task2chain(task)
    data = tree.tonp(['jets_phi:0','jets_pt:0','jets_pt:4','razor_MR','razor_R2'])
    pickle.dump( data , open(task+'.pkl','w') )
