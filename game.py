WIDTH = 320
HEIGHT = 160
TILE_SIZE = 16

MENU = 0
PLAYING = 1
game_state = MENU

sound = True

#Controle de teclas pressionadas
keys_pressed = {
    "left": False,
    "right": False,
    "up": False,
    "down": False
}

#Classe base de personagem
class Character:
    def __init__(self, x, y, sprites, speed=1):
        self.x = x
        self.y = y
        self.sprites = sprites
        self.current = 0
        self.animation_movement_speed = 0.1
        self.animation_idle_speed = 0.5
        self.time_since_last_frame = 0
        self.speed = speed
        self.direction = "down"
        self.moving = False


    def update(self, dt):
        self.time_since_last_frame += dt
        
        if not self.moving:
            if self.time_since_last_frame >= self.animation_idle_speed:
                self.time_since_last_frame = 0
                self.current = (self.current + 1) % 2
        
        else:
            if self.time_since_last_frame >= self.animation_movement_speed:
                self.time_since_last_frame = 0
                self.current = (self.current + 1) % len(self.sprites[self.direction])
        

    def draw(self):
        sprite = self.sprites[self.direction][self.current]
        screen.blit(sprite.image, (self.x - sprite.width/2, self.y - sprite.height/2))
    
    def move(self, dx, dy):
        moving_now = dx != 0 or dy != 0

        if self.moving and not moving_now:
            self.current = 0
        
        self.moving = moving_now

        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
        
        self.x += dx * self.speed
        self.y += dy * self.speed

#Classe do Hero derivada da classe Character
class Hero(Character):
    def __init__(self, x, y):
        sprites = {
            "up": [Actor("hero_up_1"), Actor("hero_up_2"), Actor("hero_up_3")],
            "down": [Actor("hero_down_1"), Actor("hero_down_2"), Actor("hero_down_3")],
            "left": [Actor("hero_left_1"), Actor("hero_left_2"), Actor("hero_left_3")],
            "right": [Actor("hero_right_1"), Actor("hero_right_2"), Actor("hero_right_3")]
        }
        super().__init__(x, y, sprites)
        self.health = 100

    def update(self, dt):
        super().update(dt)


hero = Hero(WIDTH/2, HEIGHT/2)

def update(dt):
    hero.update(dt)

    dx, dy = 0, 0
    if keys_pressed["left"]:
        dx -= 1
    if keys_pressed["right"]:
        dx += 1
    if keys_pressed["up"]:
        dy -= 1
    if keys_pressed["down"]:
        dy += 1
    
    hero.move(dx, dy)

def draw():
    screen.clear()
    
    screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (20, 20, 30))
    
    for x in range(0, WIDTH, TILE_SIZE):
        screen.draw.line((x, 0), (x, HEIGHT), (40, 40, 40))
    for y in range(0, HEIGHT, TILE_SIZE):
        screen.draw.line((0, y), (WIDTH, y), (40, 40, 40))
    
    hero.draw()
    
    screen.draw.text(f"Health: {hero.health}", (10, 10), fontsize=16)


def on_key_down(key):
    if key == keys.LEFT:
        keys_pressed["left"] = True
    elif key == keys.RIGHT:
        keys_pressed["right"] = True
    elif key == keys.UP:
        keys_pressed["up"] = True
    elif key == keys.DOWN:
        keys_pressed["down"] = True

def on_key_up(key):
    if key == keys.LEFT:
        keys_pressed["left"] = False
    elif key == keys.RIGHT:
        keys_pressed["right"] = False
    elif key == keys.UP:
        keys_pressed["up"] = False
    elif key == keys.DOWN:
        keys_pressed["down"] = False

