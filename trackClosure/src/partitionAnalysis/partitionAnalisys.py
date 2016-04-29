"""
A module to perform single, blind, partition analysis
##Use cases:
1)  estimate reprojection error
2)  give insight into view-graph structure
3)  give insight into view-graph reliability ( 3 = 1 + 2 )
4)  provide a list of probable wrong tracks

"""
from collections import namedtuple
import numpy as np
import pandas as pd
from ..closure.transclosure import transitiveclosure as Partition
from scipy.stats import cauchy, norm
from tqdm import tqdm

def most_k_tracks(partition,n, key=lambda t:-len(t.views)):
    func=lambda track_id:key(partition.points[track_id])
    L=sorted(partition.points.keys(),key=func)
    L=L[:n]
    return L


Err=namedtuple('reprojectionError','i j t e')
npErr=[
    ('i','u4'),
    ('j','u4'),
    ('t','u4'),
    ('e','f4')]
npNode=[
    ('t','u4'),
    ('v','u4'),
    ('kp','u4')]

def centroid(views):
    if len(views)==1:
        return views[0]
    U,V=0.,0. 
    for view_point in views:
        U+=view_point.u
        V+=view_point.v
    U=U/len(views)
    V=V/len(views)
    best_sample=min(views, key=lambda view_point: pow((view_point.u-U),2)+pow((view_point.v-V),2) )
    return best_sample

def make_EpipolarError(partition,gEpG):
    def foo(i,j,t_id):
        hi=centroid(partition.views[i]).hpt()
        hj=centroid(partition.views[j]).hpt()
        return np.dot(hi,np.dot(gEpG[j,i],hj.T))
    return foo
        
def reprojectionErrorDataFrame(partition,epipolar_error_functor):
    errors=[
            Err(
                i,
                j,
                T.id,
                epipolar_error_functor(i,j,T.id))
            for i in T.views
            for j in T.views
            if i is not j
            if (j,i) in EpipolarGeometries
            for T in tqdm(PARTITION.points.values())
        ]
    npErrors=np.rec.array(errors,npErr)
    dfErrors=pd.DataFrame.from_records(npErrors)
    return dfErrors

def trackDataFrame(partition):
    nodes=[
        (
            T.id,
            len(T.views),
            sum([
                len(v) 
                for v in T.views.values()])
            )
        for T in tqdm(PARTITION.points.values())
        ]
    npNodes=np.rec.array(nodes,npNode)
    dfNodes=pd.DataFrame.from_records(npNodes)
    return dfNodes

def plot_GlobalErrorDistribution(dfErrors,outfile='GlobalErrorDistribution'):
    sns.set(rc={"figure.figsize": (8, 4)})
    sns_plot = sns.distplot(dfErrors.e,
        fit=norm, 
        kde=True)
    sns_plot.savefig(outfile+'.png')

def plot_image_aggregation(dfErrors,dfNodes,outfile='ImageAggregation'):
    joined=pd.merge(dfErrors, dfNodes, on='t')
    by_image=joined.groupby(['i'])['e','v']
    aggregated_by_image=by_image.agg({
        'mean error' : lambda e_v: np.mean(e_v['e']),
        'mean error3+' : lambda e_v: np.mean(e_v[ e_v['v']]>2) ,
        'tracks' : len,
        'tracks3+': lambda e_v: len(e_v[ e_v['v']]>2) 
    })
    sns_plot=sns.pairplot(aggregated_by_image, diag_kind="kde",kind="reg")
    sns_plot.savefig(outfile+'.png')
    aggregated_by_image.to_csv(outfile+'.csv')

def plot_image_pair_aggregation(dfErrors,dfNodes,outfile='ImagePairAggregation'):
    joined=pd.merge(dfErrors, dfNodes, on='t')
    by_image_pair=joined.groupby(['i','j'])['e','v']
    aggregated_by_image_pair=by_image_pair.agg({
        'mean error' : lambda e_v: np.mean(e_v['e']),
        'mean error3+' : lambda e_v: np.mean(e_v[ e_v['v']]>2),
        'tracks' : len,
        'tracks3+': lambda e_v: len(e_v[ e_v['v']]>2) 
    })
    sns_plot=sns.pairplot(aggregated_by_image_pair, diag_kind="kde",kind="reg")
    sns_plot.savefig(outfile+'.png')
    aggregated_by_image_pair.to_csv(outfile+'.csv')


def plot_track_lenght_aggregation(dfErrors,dfNodes,outfile='TrackLenghtAggregation'):
    joined=pd.merge(dfErrors, dfNodes, on='t')
    by_track_lenght=joined.groupby(['v'])['e','kp']
    aggregated_by_track_lenght=by_track_lenght.agg({
        'mean error' : lambda e_kp: np.mean(e_kp['e']),
        'median error' : lambda e_kp: np.median(e_kp['e']),
        'mean keypoints': lambda e_kp : np.mean(e_kp['kp']),
        'tracks' : len})
    sns_plot=sns.pairplot(aggregated_by_track_lenght, diag_kind="kde",kind="reg")
    sns_plot.savefig(outfile+'.png')
    aggregated_by_track_lenght.to_csv(outfile+'.csv')


###

def quantifyKeypointsViewsPerTrack(part):
    return [
        (len(track.allViews()),
         len(track.views))
        for track in part.points.values]
    
    


