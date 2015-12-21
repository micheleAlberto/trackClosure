import sys
import numpy as np

from ..src.fromOpenMVG.wrapper import OpenMVG, KEYPOINT_METHODS



omvg=OpenMVG()
print 'set_feature_dir("data")'
omvg.set_feature_dir("data")
print '1'
omvg.set_image_dir(sys.argv[1])
print 'intrinsicsAnalysis'
omvg.intrinsicsAnalysis()
print 'set_image_dir('+sys.argv[1]+')'
omvg.computeFeatures(KEYPOINT_METHODS[2])
print 'computeFeatures'
omvg.computeMatches(ratio=0.9)
#omvg.computeMatches(ratio=0.7,video=14)
print '1computeMatches  '



