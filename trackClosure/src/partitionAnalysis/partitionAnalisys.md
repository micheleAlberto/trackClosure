#A module to perform single, blind, partition analysis

##Use cases:
1)  estimate reprojection error
2)  give insight into view-graph structure
3)  give insight into view-graph reliability ( 3 = 1 + 2 )
4)  provide a list of probable wrong tracks

#Use case: estimate reprojection error
## 1.1 atomic model
e(i,j,track_id)=
    distance from epiline projected from Ti in image i to image j and point Tj
    Ti is the centroid of track T in image i in homogeneous coordinates
    Tj is the centroid of track T in image j in homogeneous coordinates
    Fji is the fundamental matrix from image j to image i
    Ti Fji Tj^t
``` python
from collections import namedtuple
import numpy as np
Err=namedtuple('reprojectionError','i j t e')
npErr=[
    ('i','u4'),
    ('j','u4'),
    ('t','u4'),
    ('e','f4')]
Deg=namedtuple('trackData','t v kp')
npDeg=[
    ('t','u4'),
    ('v','u4'),
    ('kp','u4')]
errors=
[
    Err(
        i,
        j,
        t_id
        e(i,j,T.id))
    for i in T.views
    for j in T.views
    if i is not j
    if (j,i) in EpipolarGeometries
    for T in PARTITION.points.values()
]
npErrors=np.rec.array(errors,npErr)

```
## 1.2 with global aggregation
histogram,mean, variance of reprojection error
``` python
import seaborn as sns
sns.set(rc={"figure.figsize": (8, 4)})
from scipy.stats import cauchy, norm
sns_plot = sns.distplot(npErrors.e,
    fit=norm, 
    kde=True)
sns_plot.savefig('output.png')
```

## 1.3 with image aggregation
``` python
image_errors= 
    {I: 
        [ e(i,j,T.id) 
            for i in T.views
            for j in T.views
            if i is not j
            if (j,i) in EpipolarGeometries
            for T in PARTITION.points
        ]
    }
```

bar plot : for each image the average reprojection error on that image
###scatter plot
a data point for each image describe:
*   average reprojection error on that image
*   number of tracks observed
*   number of tracks with at least 3 views observed
*   number of tracks with at least 4 views observed
``` python
max_k=5
trackCounter={(i,k):0 for i in images for k in range(2,max_k)}
for t in partition.points.values():
    for i in t.views.keys():
        for k in range(2,min(max_k,len(t.views))):
            trackCounter[i,k]+=1

np.sum(np.where(np.logical_or(npE['i']==images,npE['j']==images),[npE['e'],0.]))
npImageAggregatedData=[
    ('I','u4'),
    ('e','f4'),
    ('t2','u4'),
    ('t3','u4'),
    ('t4','f4')]
I=np.array(images)
error_by_image=np.dot(
    np.logical_or(
        npE['i'][:,np.newaxis] == I ,
        npE['j'][:,np.newaxis] == I),
    npE['e'])]
pd.DataFrame({
    'I':images,
    'e':error_by_image,
    'tracks2':[trackCounter[i,2] for i in images],
    'tracks3':[trackCounter[i,3] for i in images],
    'tracks4':[trackCounter[i,4] for i in images],
    'tracks5':[trackCounter[i,5] for i in images]
    })

sns.pairplot(, diag_kind="kde",kind="reg")

## 1.4 with image pair aggregation
scatter plot of 
*   average reprojection error on that pair
*   number of tracks that are observed in both images
https://stanford.edu/~mwaskom/software/seaborn/examples/scatterplot_matrix.html

``` python
pair_errors:=
{(i,j): 
    [ e(i,j,T.id) 
        for T in PARTITION.points
    ] 
    if (j,i) in EpipolarGeometries
    if i is not j
    for i in T.views
    for j in T.views
}
```
## 1.5 with track lenght aggregation

