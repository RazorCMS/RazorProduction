from db import db
d=db()
l1=d.filelist('leopard_v1_RSGluonToTT_M-4000_Tune4C_13TeV-pythia8')
print l1
l2=d.filelist('tiger_v1_QCD_Pt-470to600_Tune4C_13TeV_pythia8')
print l2

