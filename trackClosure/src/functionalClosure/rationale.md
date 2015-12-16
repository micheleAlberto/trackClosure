#THE FUNCTIONAL SCHEMA OF CLOSURE
closure (part1,part2) -> part1
add_point(part1,track2) (-> part1?)
SynthPoints(track2,tracks1[]) -> tracks[]
merge(track1,track2) -> tracks[]

```
make_closure(gEpG,radius)
merge_f=make_merge_with_validation(gEpG,radius)
merge_i_f=make_merge_interactive(
        merge_f,
        labda merge_outcome: not merge_outcome.is_correct(),
synth_f=make_synthPoints(merge_i_f)
add_point_f=make_add_point(synth_f)
closure_f=make_closure(add_point_f)
return closure_f
```

##Merge Functions
hard_merge(p,q)
(informed_merge(vr,p,q,radius=4.))
(informed_split(vr,p,q))
make_merge_with_validation(radius,gEpG)
### validation 
make_merge_interactive
##synth point Functions
make_synthPoints(merge_points_functor)
##Add Point Functions
make_add_point(SynthPoints_functor)
##Closure funtions


