from pygamejr import game
from random import randint

screen = game.start("game",screen_width=1024, screen_height=768, screen_color="black")

x = 0
n = 0
planet_num = randint(3, 5)
planet_y_ = 100
planet_x_ = 100
planet_y = [planet_y_ + (i * randint(50,110)) for i in range(planet_num)]
planet_x = [planet_x_ + (i * randint(1,150)) for i in range(planet_num)]

for i in range(100):
    x = 
    n = n + 1
    if int(planet_x[n])+n == planet_x[n+1]:
        planet_x.remove(planet_x[n+1])
        planet_x.insert(n+1, planet_x[n]+n)


for i in range(planet_num):

    planet = game.create_ellipse(100, 100, planet_x[i], planet_y[i], color=(randint(50,255),randint(50,255),randint(50,255)))

game.keep_running()