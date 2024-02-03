
TODOs
- actor.xy()
- actor.center()
- remove(actor)
- remove_all_actors


https://github.com/viblo/pymunk/blob/master/pymunk/examples/using_sprites.py
https://github.com/viblo/pymunk/blob/master/pymunk/examples/platformer.py
https://github.com/YushanWang9801/pygame_mario/tree/main
https://github.com/mx0c/super-mario-python/blob/master/classes/Sprites.py

## Algo

1. Take points with body centeroid to zero
Coordinate systems:
-	b_local_0  Body local without rotation
-	b_local  Body local with rotation
-	b_global  Global of b_local
-	camera_global  Camera view of b_global


1.	Take points centered at (0,0), + z=(0,0)
2.	Rotate by body angle
3.	Add body pos
4.	Apply camera scale, angle, translate to points
5.	Find box, x_min, y_min
6.	Top_left = x_min, y_max
7.	Normalize shape using x_min, y_min so bottom_left is zero
8.	Find y_max
9.	Invert y=y_max-y
10.	zs = centroid in surface coordinates
11.	Create surface x_max-x_min, y_max-y_min
12.	Draw on surface at top left = 0,0
13.	 Draw image at zs – (w,h)/2 for draw mode = center
14.	Draw surface on screen at top_left

     For tiling:
1.	Take points centered at (0,0
2.	Apply camera scale
3.	Calculate box
4.	Create surface of same size
5.	Scale image by given factor * camera factor
6.	Tile or center on surface
7.	Rotate by body angle + camera angle

