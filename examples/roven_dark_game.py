from pygamejr import game

from random import randint

game.start(screen_color="black", screen_width=1024, screen_height=768)

shadow2 = game.create_circle(235, center=(100, 100), color=(50, 50, 50,45))

flower1=game.create_image("images__21_-removebg-preview (1).png", center=(randint(0,1024), randint(0,768)))
flower2=game.create_image("images__21_-removebg-preview (1).png", center=(randint(0,1024), randint(0,768)))
flower3=game.create_image("images__21_-removebg-preview (1).png", center=(randint(0,1024 - 128), randint(0,768 - 64)))
box = game.create_rect(100, 100, center=(randint(128, 640), randint(128,640)), color=(150, 75, 0, 2))
flower4=game.create_image("images__21_-removebg-preview (1).png", center=(box.xy()[0], box.xy()[1] + 20))
flower5=game.create_image("images__21_-removebg-preview (1).png", center=(randint(0,1024), randint(0,768)))

shadow = game.create_circle(165, center=(100, 100), color=(128, 128, 128,35))

circle = game.create_circle(100, center=(100, 100), color=(255,230,0,25))

circle2 = game.create_circle(75, center=(100, 100), color=(255,230,0,15))

box.add_costume_rect("box 75t", 75, 75, color=(150, 75, 0, 20))
box.add_costume_rect("box 100t", 75, 75, color=(150, 75, 0, 45))

firefly_g = game.create_circle(140, center=(100, 100), color=(0, 255, 150, 110))
firefly_2g = game.create_circle(140, center=(100, 100), color=(0, 255, 150, 110))
firefly = game.create_circle(50, center=(100, 100), color=(0, 255, 150, 225))
firefly2 = game.create_circle(50, center=(400, 400), color=(0, 255, 150, 225))

game_text = game.create_image("download__10_-removebg-preview.png", (350, 0))

glide_to_flower = randint(1, 5)
glide_to_flower2 = randint(1, 5)

while game.is_running():

    shadow2.move_to(((game.mouse_xy()[0])), ((game.mouse_xy()[1])))
    shadow.move_to(((game.mouse_xy()[0])+35), ((game.mouse_xy()[1])+35))
    circle.move_to(((game.mouse_xy()[0]) + 65), ((game.mouse_xy()[1]) + 65))
    circle2.move_to(((game.mouse_xy()[0]) + 78), ((game.mouse_xy()[1]) + 78))

    if box.touches(shadow2) or box.touches(firefly_g) or box.touches(firefly_2g):

        box.set_costume("box 75t")

    elif box.touches(shadow) or box.touches(firefly) or box.touches(firefly2) or box.touches(circle) or box.touches(circle2):

        box.set_costume("box 100t")

    else:

        box.set_costume("")

    if glide_to_flower == 1:

        firefly.glide_to((flower1.center(), 4))

    elif glide_to_flower == 2:

        firefly.glide_to((flower2.center(), 4))
        

    elif glide_to_flower == 3:

        firefly.glide_to((flower3.center(), 4))
        

    elif glide_to_flower == 4:

        firefly.glide_to((flower4.center(), 4))

    elif glide_to_flower == 5:

        firefly.glide_to((flower5.center(), 4))
    
    if firefly.touches(flower1) or firefly.touches(flower2) or firefly.touches(flower3) or firefly.touches(flower4) or firefly.touches(flower5):

        glide_to_flower = randint(1, 5)

    else:

        glide_to_flower = glide_to_flower

    if glide_to_flower2 == 1:

        firefly2.glide_to((flower1.center(), 4))

    elif glide_to_flower2 == 2:

        firefly2.glide_to((flower2.center(), 4))

    elif glide_to_flower2 == 3:

        firefly2.glide_to((flower3.center(), 4))

    elif glide_to_flower2 == 4:

        firefly2.glide_to((flower4.center(), 4))

    elif glide_to_flower2 == 5:

        firefly2.glide_to((flower5.center(), 4))
    
    if firefly2.touches(flower1) or firefly2.touches(flower2) or firefly2.touches(flower3) or firefly2.touches(flower4) or firefly2.touches(flower5):

        glide_to_flower2 = randint(1, 5)
        

    firefly_g.move_to(((firefly.xy()[0])-42, (firefly.xy()[1])-42))
    firefly_2g.move_to(((firefly2.xy()[0])-42, (firefly2.xy()[1])-42))

    if box.touches(circle2):
        
        box.move_to((randint(128, 640), randint(128,640)))
        flower1.move_to((randint(0,1024), randint(0,768)))
        flower2.move_to((randint(0,1024), randint(0,768)))
        flower3.move_to((randint(0,1024), randint(0,768)))
        flower4.move_to((box.xy()[0], box.xy()[1] + 20))
        flower5.move_to((randint(0,1024), randint(0,768)))

    else:

        pass

    game.update()