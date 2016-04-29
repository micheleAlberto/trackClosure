BLUE=   (255, 0,   0  )
GREEN=  (0,   255, 0  )
RED=    (0,   0,   255)
YELLOW= (0,   128, 128)
PURPLE= (128, 0,   128)
PURPLO= (128, 128, 0  )
PURPLO= (128, 128, 0  )
COLORS=[BLUE,GREEN,RED,YELLOW,PURPLE,PURPLO]
import rainbowboa
COLORS=[(int(c[0,0,0]),
         int(c[0,0,1]),
         int(c[0,0,2])) 
    for c in rainbowboa.colors]
