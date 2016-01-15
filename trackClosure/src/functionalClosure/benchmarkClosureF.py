
from mergeF import make_merge_with_validation # (radius,gEpG)
from mergeF import make_merge_interactive 
# (merge_functor, outcome_filter,oracle_partition, gEpG, outcome_functor=None)
from synthF import make_synthPoints # (merge_points_functor)    
from addPointF import make_add_point # (SynthPoints_functor)
from closureF import make_closure # (add_pt_functor)
from closureBenchmark.closureBenchmark import make_closure_benchmark # (closure_functor)


def benchmark_test(gEpG,radius):
    smart_merge = make_merge_with_validation(radius,gEpG)
    """
    sensible_merge = make_merge_interactive(
            smart_merge,
            lambda outocome: not outcome.is_correct(),
            oracle, gEpG)
    synth = make_synthPoints(sensible_merge)
    """
    synth = make_synthPoints(smart_merge)
    add_point = make_add_point(synth)
    my_closure = make_closure(add_point)
    cbf= make_closure_benchmark(my_closure)
    return cbf




