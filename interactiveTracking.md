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
 
##MergeOutcome.py
Implement a class to model failures of a generic merge operation.
```
mo=MergeOutcome(track_x,track_y,tracks_Z,gEpG,oracle)
```
*   track_x,track_y are operands
*   tracks_Z is the list of results (may contain 0,1 or 2 tracks)
*   gEpG are the epipolar geometries 
*   oracle is an oracle partition

implement :

*   is_merge()
*   is_split()
*   has_correct_operands()
*   has_known_correct_operands()
*   has_mutually_correct_operands()
*   has_correct_results()
*   has_known_correct_results()
*   is_correct()
*   is_known_correct()
*   is_recover()
*   is_known_recover()
*   is_complete()
*   get_spilled()
*   get_spilled_oracles()
*   dominant_x()
*   dominant_y()
*   dominant_results()
*   is_roughly_correct()

##printOperation.py
Provide implementations for function that display a merge operation to inspect it against an oracle.
A print function is a functon takes as arguments operands and results of the operation.
```
print_foo(track_x,track_y,result) -> str
```
to generate such function use:
```
print_foo = make_print_operation(epipolar_geometries,oracle_partition)
```

##partitionTransfer.py : partition mapping utilities

*   fetch(partition,track) -> track_ids

    extract from partition identifiers of tracks that match the track

*   soft_fetch(partition,track)-> track_ids

    extract from partition identifiers of tracks that match the track or end up near a matched keypoint

*   soft_fetch_views(partition,views) -> track_ids
    
    extract from partition identifiers of tracks that match the keypoints in the list views or end up near one of those keypoint (no further than 10. pixels)

*   nearest_view(v0,partition) -> v_nearest:
    
    select the nearest view to v0 in partition

*   partition_transfer(part_x,part_y,track_ids_y) -> track_ids_x

    extract from partition x identifiers of tracks that match the tracks identified by a vector of track identifiers in partition y


*   soft_partition_transfer(part_x,part_y,track_ids_y) -> track_ids_x

    extract from partition x identifiers of tracks that match the tracks identified by a vector of track identifiers in partition y
    
*   track_is_wrong(track_x,oracle) -> bool:

*   dominant(list_of_indexes) -> dominant_oracle
 
