from pygamejr import game, DrawOptions

game.set_camera_controls(True)
game.start()

score = 0
health = 100
inventory = 10

hud = game.create_hud()
score_label = hud.add_text(f"Score: {score}", (10, 10), font_size=30, color="red")
health_label = hud.add_text(f"Health: {health}", (800, 10), font_size=30, color="blue")
inventory_label = hud.add_text(f"Inventory: {inventory}", (10, 40), font_size=20, color="purple")
hud.draw_options = DrawOptions(fps_pos = (800, 40))

ball1 = game.create_circle(radius=100, color="red",
                           image_path="ball.gif",
                           center=(200,200),
                           scale_xy=(1., 1.), border=0)

while game.is_running():
    ball1.turn_by(1)
    game.update()