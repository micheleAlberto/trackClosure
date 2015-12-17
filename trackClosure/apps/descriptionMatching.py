import sys
import numpy as np

from ..src.fromOpenMVG.wrapper import OpenMVG, KEYPOINT_METHODS



omvg=OpenMVG()
omvg.set_feature_dir("./.openmvgData")
omvg.set_image_dir(sys.argv[1])
omvg.computeFeatures(KEYPOINT_METHODS[2])
omvg.computeMatches(ratio=0.6)



