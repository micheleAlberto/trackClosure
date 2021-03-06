from partitionTransfer import dominant
from itertools import combinations
from ...closure.validation.compactRepresentation import compactPoint
from ...closure.view import view as view_type
#view_type = closure.view.view
print_conv = {
    type(None): lambda x: 'None',
    type(str): lambda x: x,
    type(1): str,
    type(True): str,
    type(1.): lambda x: "{:4.2f}".format(x),
    type(view_type): lambda x: 'kp' + str(x.id_keypoint)
    }


def fillLeft(_s, l):
    s = print_conv[s](s)
    sl = len(s)
    if sl <= l:
        return (' ' * (l - sl)) + s
    else:
        return s[0:l]


def line(cells):
    return ' '.join(
        [
            fillLeft(cells[0], 4),
            fillLeft(cells[1], 4)
        ] +
        map(fillLeft, cells[2:])) + '\n'


def print_list_epipolar_constraints(images, gEpG):
    return ('epipolar geometries:\n' +
           ', '.join([
                '<{},{}>'.format(ij[0], ij[1])
                for ij in combinations(range(9), 2)])
            + '\n')


def make_print_operation(gEpG, oracle):
    def print_operation(track_x, track_y, result):
        return print_merge_operation(track_x, track_y, result, gEpG, oracle)
    return print_operation


def print_merge_operation(track_x, track_y, result, gEpG, oracle):
        """
        arguments:
        track_x,track_y :   track operands
        result          :   list resulting from merging operands
        gEpG            :   epipolar geometries
        oracle          :   oracle partition

        print to a string a table with columns:
        Im      : image identifier
        -       : header identifier or keypoint oracle
        P       : point P
        Q       : point Q
        Z1,Z2   : results

        for each image in the merge problem an header made of 3 lines is printed
        O       : oracle header, for each track the dominant oracle
        X/Y     : coordinates for the each track on the image

        for each keypoint observed in the image a line will display
        keypoint oracle identifier
        keypoint identifier in the column of every track that referece it
        """
        tracks = [track_x, track_y] + results
        labels = ['Im', '', 'P', 'Q', 'Z1', 'Z2']
        s = ""
        Tc = map(compactPoint, tracks)
        # {image_id:(image_id,homogeneus_keypoint,keypoint_radius)}
        # Tc is a list of compacted tracks
        images = set(track_x.views.keys() + track_y.views.keys())
        keypoints = {
            im_id:
            set(sum(
                    [t.getKeypointsIds(im_id) for t in tracks],
                    []  # sum with lists as argument
                        #catenate the lists, [] is initial
               ))
            for im_id in images}
        s += line(labels)
        for im_id in sorted(images):
            keypoints_im = [
                set([
                    v.id_keypoint
                    for v in t.views[im_id]]
                ) for t in tracks]
            # image header:
            # 1-oracle header
            image_oracles = [
                dominant(soft_fetch_views(t.views[im]))
                for t in tracks]
            s += line([im_id, 'O'] + image_oracles)
            # 2-X header
            xs = [tc[im_id][1][0] for tc in Tc]
            s += line([im_id, 'X'] + xs)
            # 3-Y header
            ys = [tc[im_id][1][1] for tc in Tc]
            s += line([im_id, 'Y'] + ys)
            for kp_id in keypoints[im_id]:
                o = oracle.views[im_id].get(kp_id)
                track_has_kp = [
                    kp_id if (kp_id in kp_set) else ' '
                    for kp_set in keypoints_im]
                if o:
                    s += line([im_id, o] + track_has_kp)
                else:
                    s += line([im_id, o] + track_has_kp)
            s += '\n'
        s += print_list_epipolar_constraints(images, gEpG)
        return s


