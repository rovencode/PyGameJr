from pygamejr import game

game.start("Realistic Baking Simulation", 1024, 768, screen_image_path='x1.png')

game.create_image("x3.png", center=(512, 384), scale_xy=(2.5, 2.5))

game.keep_running()