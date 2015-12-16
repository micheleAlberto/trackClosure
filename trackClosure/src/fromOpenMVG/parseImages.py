import numpy as np
import sys
import json
"""
GOAL : parse sfmdata.json to get the 
a) mapping from image_id to imageFile
b) reverse mapping
"""


def parseImages(sfm_file_name):
    with open(sfm_file_name) as fp:
        data=json.load(fp)
    views=data['views']
    view_id2name={v['key']:v['value']['ptr_wrapper']['data']['filename'] for v in views}
    name2view_id={view_id2name[vid]:vid for vid in view_id2name}
    print "[parseImages] ",len(view_id2name)," images"
    return view_id2name,name2view_id

#TESTING:
def main():
    argv=sys.argv
    if len(argv)==1:
        d,i=parseImages('matchDir/sfm_data.json')
    else:
        d,i=parseImages(argv[1])
    for k in d:
        print "[{}]:{}".format(k,d[k])
    for n in i:
        print "{}:[{}]".format(n,i[n])
if __name__ == "__main__":
    main()
