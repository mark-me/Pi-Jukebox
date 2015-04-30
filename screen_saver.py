#!/usr/bin/python
import random, pygame, time
from PIL import Image
from pygame.locals import *
from pygame.color import THECOLORS as color

# VARIABLES TO INCLUDE MATH
mat = [[0.0,0.0,0.0,0.16,0.0,0.0,0.01],
	[0.85,0.04,-0.04,0.85,0.0,1.6,0.85],
	[0.2,-0.25,0.23,0.22,0.0,1.6,0.07],
	[-0.15,0.28,0.26,0.24,0.0,0.44,0.07]]

xa = -5.5
xb = 6.5
ya = -0.5
yb = 10.5

x = 0.0
y = 0.0

imgx = 320
imgy = 240

# VARIABLES FOR CONTROL
k = 1
end = imgx*imgy / 10 * 4 # Looks like nothing is happening after this point.


# START LOOP
done = False
while not done:
    # DETECT END OF DRAWING
    if k == end:
        # ENJOY AND RESET
        time.sleep(3)
        k = 0
        screen.fill(color['black'])
    else:
        # MATH FOR THE FRACTAL
        p = random.random()
        if p <= mat[0][6]:
            i = 0
        elif p <= mat[0][6] + mat[1][6]:
            i = 1
        elif p <= mat[0][6] + mat[1][6] + mat[2][6]:
            i = 2
        else:
            i = 3
        x0 = x * mat[i][0] + y * mat[i][1] + mat[i][4]
        y = x * mat[i][2] + y * mat[i][3] + mat[i][5]
        x = x0
        jx = int((x-xa)/(xb-xa)*(imgx-1))
        jy = int(imgy-1)-int((y-ya)/(yb-ya)*imgy-1)
        # AFTER PLAYING WITH SEVERAL COLORS, WHITE ON BLACK IS THE BEST
        c = color['white']
        screen.set_at((jx, jy), c)
        pygame.display.update()
    # DETECT EVENTS TO END PYGAME
    events = pygame.event.get()
    for e in events:
        if e.type == KEYDOWN and e.key == K_ESCAPE or e.type == QUIT:
            done = True
    # CYCLE AGAIN
    k += 1

# DONE
pygame.quit()
