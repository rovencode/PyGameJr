from pygamejr import game

game.start(screen_title="Mario Animation",
           screen_image_path="background.jpg",)

mario = game.create_image(image_path=["mario1.png", "mario2.png", "mario3.png"],
                          bottom_left=(100,100),
                          scale_xy=(0.5, 0.5))

mario.start_animation(frame_time_s=0.2)

game.keep_running()