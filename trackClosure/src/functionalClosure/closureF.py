from ..closure.transclosure import transitiveclosure as Partition


def make_closure(add_pt_functor):
    def closure_functor(partition_1, partition_2):
        for p2Id in partition_2.points.keys():
            p2 = partition_2.points[p2Id]
            assert(p2Id > 0)
            add_pt_functor(partition_1, p2)
        return partition_1
    return closure_functor


def make_closure_on_copy(closure_functor):
    def copy_closure_functor(partition_1, partition_2):
        new_partition = Partition()
        new_partition = closure_functor(new_partition, partition_1)
        new_partition = closure_functor(new_partition, partition_2)
        return new_partition
    return copy_closure_functor


def make_closure_assertive(closure_functor):
    def assertive_closure_function(partition_1, partition_2):
        result = closure_functor(partition_1, partition_2)
        #from view to points
        #assert inclusion of the view in the point
        for I in result.views:
            for kp in result.views[I]:
                t_id = result.views[I][kp]
                T = result.points[t_id]
                assert I in T.views, (
                    "scene point " + str(t_id) +
                    " lacks view " + str(I))
                assert kp in T.views[I].keys(), (
                    "scene point " + str(t_id) +
                    " lacks view point " + str((I, kp)))
        #from points to view
        #assert existence and reference to the point
        for t_id in result.points:
            T = result.points[t_id]
            for I in T.views:
                assert I in result.views, (
                    "view {} is in scene point {}".format(I, t_id) +
                    ", but it is not in the view index")
                for kp in [v.id_keypoint for v in T.views[I]]:
                    assert kp in result.views[I], (
                        "view point {}".format((I, kp)) +
                        " is in scene point {}".format(t_id) +
                        ", but not in view index")
                    assert t_id == result.views[I][kp], (
                        "view point {} is in scene point {}".format(
                            (I, kp), t_id
                        ) +
                        ", but point to {}".format(result.views[I][kp])
                        )
        return result
    return assertive_closure_function



