from pygamejr import game

game.show_mouse_coordinates = True
game.start(screen_title="Mario Animation", screen_image_path="background.jpg",
           gravity=-500)

game.create_screen_walls(bottom=112, friction=0.5)

mario = game.create_image(image_path=["mario1.png", "mario2.png", "mario3.png"],
                          bottom_left=(100,200), scale_xy=(0.5, 0.5),
                          density=1, elasticity=0.6, friction=0.1)
mario.start_animation(frame_time_s=0.2)



def mario_keyboard(mario, keys):
    if "left" in keys:
        mario.apply_impulse((-10000, 0))
    elif "right" in keys:
        mario.apply_impulse((10000, 0))
    elif "up" in keys:
        mario.apply_impulse((0, 200000))
    elif "down" in keys:
        mario.apply_impulse((0, -1000))
game.handle(mario.on_keypress, mario_keyboard)

game.keep_running()