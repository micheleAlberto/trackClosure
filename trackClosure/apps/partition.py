"""
A module to perform single, blind, partition analysis
##Use cases:
1)  estimate reprojection error
2)  give insight into view-graph structure
3)  give insight into view-graph reliability ( 3 = 1 + 2 )
4)  provide a list of probable wrong tracks

"""

"""
##Use cases:
1)  estimate reprojection error
"""

from ..src.closure.transclosure import transitiveclosure as Partition
from ..src.closure.transclosure import load_tracks
from ..src.geometry.epipolarGeometry import EpipolarGeometry
from ..src.partitionAnalysis.partitionAnalisys import most_k_tracks
    #(partition,n, key=lambda t:len(t.views)):
from ..src.partitionAnalysis.partitionAnalisys import make_EpipolarError 
    # (partition,gEpG)
from ..src.partitionAnalysis.partitionAnalisys import reprojectionErrorDataFrame 
    # (partition,epipolar_error_functor)
from ..src.partitionAnalysis.partitionAnalisys import trackDataFrame
    # (partition)
from ..src.partitionAnalysis.partitionAnalisys import  plot_GlobalErrorDistribution
    # (dfErrors,outfile='GlobalErrorDistribution.png')
from ..src.partitionAnalysis.partitionAnalisys import plot_image_aggregation
    # (dfErrors,dfNodes,outfile='ImageAggregation'):
from ..src.partitionAnalysis.partitionAnalisys import plot_image_pair_aggregation
    # (dfErrors,dfNodes,outfile='ImagePairAggregation'):
from ..src.partitionAnalysis.partitionAnalisys import  plot_track_lenght_aggregation
    # (dfErrors,dfNodes,outfile='TrackLenghtAggregation'):

from sys import argv
import os

def main():
    if len(argv) < 3:
        print """
    First argument:     partition file
    Second argument:    epipolar geometry file
    [Third argument]:   folder to store ouput files
    """
        assert(len(argv)>=3)
    cc_track_file = argv[1]
    print 'load partition file: ', cc_track_file
    CC = load_tracks(cc_track_file)
    gepg_file = argv[2]
    print 'load epipolar geometry file: ', gepg_file
    gEpG = EpipolarGeometry.load(gepg_file)
    out_folder = argv[3] if len(argv) > 3 else '/data/partitionAnalisys/'
    if os.path.isdir(out_folder):
        print 'make folder: ', out_folder
        os.makedirs(out_folder)
    longest_track_ids=most_k_tracks(CC,50)
    print "50 longest tracks:"
    for i,t_id in enumerate(longest_track_ids):
        print '#{}:\t {}'.format(i,t_id)
    for i,t_id in enumerate(longest_track_ids):
        print '#{}:\t {}'.format(i,t_id)
        print CC.points[t_id]
    err = make_EpipolarError(CC, gEpG)
    print 'build reprojection error DataFrame'
    rpj_df = reprojectionErrorDataFrame(CC, err)
    print 'build track node DataFrame'
    trk_df = trackDataFrame(CC)
    print 'plot global reprojection error distribution'
    plot_GlobalErrorDistribution(rpj_df, 
        outfile= out_folder + 'GlobalErrorDistribution')
    print 'plot image aggregations'
    plot_image_aggregation(rpj_df, trk_df, 
        outfile= out_folder +'ImageAggregation')
    print 'plot image pair aggregations'
    plot_image_pair_aggregation(rpj_df, trk_df, 
        outfile= out_folder +'ImagePairAggregation')
    print 'plot track lenght aggregations'
    plot_track_lenght_aggregation(rpj_df, trk_df, outfile= 
        out_folder +'TrackLenghtAggregation')

if __name__ == "__main__":
    main()
    
