#fromOpenMVG.wrapper
Use class OpenMVG from wrapper module
``` python
from fromOpenMVG.wrapper import OpenMVG
```
other modules:
* getMatches
* parseFeat
* parseImages
* parseMatches
* putMatches
* trackCentroid
* export.export

#trackvis
drawing functions
#functionalClosure

#geometry
``` python
from geometry.epipolarGeometry import EpipolarGeometry

epg=EpipolarGeometry()
for ij in matches:
    pt_i=[]
    pt_j=[]
    for m in matches[ij]:
        pt_i.append(m[1][0:2])
        pt_j.append(m[3][0:2])
    pt_i=np.array(pt_i)
    pt_j=np.array(pt_j)
    # fundamental matrix estimation
    epg[ij]=pt_i,pt_j
    ji=ij[1],ij[0]
    print 'fundamental matrix of ',ij ,'is:\n',epg[ij]
    print 'fundamental matrix of ',ji ,'is:\n',epg[ji]
epg.save('geometry.epg')
```
#benchmark
``` python
from benchmark.benchmark import Benchmark
from benchmark.benchmark import save_benchmark
from benchmark.benchmark import load_benchmark
from benchmark.OracleGui import oracle_gui

image_id2name={1:'a.jpg',2:'b.jpg',3:'c.jpg'}
be=load_benchmark('benchmark.be')
cc=be.cc
gui=oracle_gui(lambda i:image_dir+image_id2name[i],gEpG,cc)
gui.play()
save_benchmark(be,'benchmark.be')
```
#closure
##closure.validation

#Apps
##tracking
