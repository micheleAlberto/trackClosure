import numpy as np
from IPython import embed
from ..src.functionalClosure.closureBenchmark.roc import *


benchmark_file='data/bench0.be'
epipolar_geometry_file='data/matches.epg'
image_dir='nave/'
omvg_dir='data/'
omvg=OpenMVG()
omvg.set_image_dir(image_dir)
omvg.set_feature_dir(omvg_dir)
image_id2name,name2image_id = omvg.loadImageMap()
gEpG=EpipolarGeometry.load(epipolar_geometry_file)
print "[live] benchmark file: ",benchmark_file
bm=load_benchmark(benchmark_file)
print "[ROC] ",bm.label , ' with {} connected components '.format(len(bm.CC.points))
synth = make_synthPoints(hard_merge)
add_point = make_add_point(synth)

cc_id=1
cc=bm.CC.points[cc_id]
roc=ROC_Tester(cc,gEpG,bm.oracle)
refiner_tuner=decomposition_tuner(gEpG,cc)

def mk_partition(tr):
    part=Partition()
    for track in refiner_tuner.build_tracks(tr):
        add_point(part,track)
    return part

def merge_tracks(t,i,j):
    t[i]=t[i]+t[j]
    del t[j]
    return t

def precision(r):
    return float(r.TP)/(r.TP+r.FP)
def accuracy(r):
    return float(r.TP)/(r.TP+r.FN)

embed()



results=[]
for R in [100.,200.,300.,400.]:
    n=30
    tr=refiner_tuner.solve_for(R)
    for minsup in [100,150,200,300,400,500,700]:
        tr2=tr.copy()
        min_supp=100
        try:
            for i in range(n):
                ti,tj=refiner_tuner.get_track_twin_pair(tr2,min_supp)
                print ti,tj
                tr2=merge_tracks(tr2,ti,tj)
                part=mk_partition(tr2)
                res=roc.testPartition(part)
                results+=[res]
        except :
            print minsup,precision(res),accuracy(res)
