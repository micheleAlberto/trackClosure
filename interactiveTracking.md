# TODO: live benchmark - interactiveClosure.py
--live *benchmark_file* *epipolar_file* ?
interactively debug robust closure of partitions of benchmark file
implementa funzioni per realizzare una chiusura robusta controllando ad ogni inserimento di punto
##interactiveClosure.py

### make_merge_with_validation(radius,gEpG)

provide an implementation of a merge function usign multiview validation

(float) radius is the threshold of the validation filter

gEpG={(i,j):Fij}  is a dictionary that maps pair of images (by index) to fundamental matrices

return a merge function:

robust_merge: (trackA,trackB)->result_tracks

###make_merge_interactive
Arguments:
*   merge_functor
*   oracle_partition
*   interrupt_if_not_correct=True
*   interrupt_if_not_complete=True

provide an interactive implementation of the given merge operator both input and output are merge functions in the form

merge_functor:(trackA,trackB)->result_tracks

### make_synthPoints(merge_points_functor)
provide an implementation of synth points using merge_points_functor as a merge operation.
        
merge_points_functor(trackA,trackB) -> new_tracks
    
where new_tracks is a list of at most 2 tracks
    
Return a synthPoints function:
        
synthPoints(leader,list_of_followers) -> new_tracks
    
examples:
*   make_synthPoints(hard_merge)
*   make_synthPoints(merge_with_validation)
##interactiveMerge.py
 
##mergeException.py
##printOperation.py
##partitionTransfer.py
