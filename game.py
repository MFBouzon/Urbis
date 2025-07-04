import random
import math

WIDTH = 576
HEIGHT = 544
TILE_SIZE = 32

MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3

items_collected = 0

#Controle de teclas pressionadas
keys_pressed = {
    "left": False,
    "right": False,
    "up": False,
    "down": False
}

#Classe base para representar os personagens do jogo
class Character:
    def __init__(self, x, y, sprites, speed=1.5, tilemap=None):
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
        self.tilemap = tilemap


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
        
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if self.tilemap is None or self.can_move(new_x, new_y+7):
            self.x = new_x
            self.y = new_y

    def can_move(self, x, y):
        col, row = self.tilemap.world_to_tile(x, y)
        return self.tilemap.is_walkable(col, row)

#Classe do Hero derivada da classe Character para representar o protagonista do jogo
class Hero(Character):
    def __init__(self, x, y, sprites=None, speed=1.5, tilemap=None):
        sprites = {
            "up": [Actor("hero_up_1"), Actor("hero_up_2"), Actor("hero_up_3")],
            "down": [Actor("hero_down_1"), Actor("hero_down_2"), Actor("hero_down_3")],
            "left": [Actor("hero_left_1"), Actor("hero_left_2"), Actor("hero_left_3")],
            "right": [Actor("hero_right_1"), Actor("hero_right_2"), Actor("hero_right_3")]
        }
        super().__init__(x, y, sprites, tilemap=tilemap)
        self.health = 100

    def update(self, dt):
        super().update(dt)

    def move(self, dx, dy):
        moving_now = dx != 0 or dy != 0
        super().move(dx, dy)
            


#Classe do inimigo derivada da classe Character
class Enemy(Character):
    def __init__(self, patrol_area):
        self.patrol_area = patrol_area  # Rect
        sprites = {
            "up": [Actor("enemy2_up_1"), Actor("enemy2_up_2"), Actor("enemy2_up_3")],
            "down": [Actor("enemy2_down_1"), Actor("enemy2_down_2"), Actor("enemy2_down_3")],
            "left": [Actor("enemy2_left_1"), Actor("enemy2_left_2"), Actor("enemy2_left_3")],
            "right": [Actor("enemy2_right_1"), Actor("enemy2_right_2"), Actor("enemy2_right_3")]
        }

        super().__init__(self.patrol_area.left, self.patrol_area.top, sprites, speed=1)
        self.targets= [
            (self.patrol_area.right, self.patrol_area.top),   
            (self.patrol_area.right, self.patrol_area.bottom), 
            (self.patrol_area.left, self.patrol_area.bottom), 
            (self.patrol_area.left, self.patrol_area.top)
        ]
        print(self.targets)
        self.current_target = 0  
        self.target_x, self.target_y = self.targets[self.current_target]
        self.item = Actor("item", 
                         center=(self.patrol_area.centerx, 
                                self.patrol_area.centery))
        self.item_collected = False

    def update(self, dt):
        super().update(dt)
        
        if math.dist((self.x, self.y), (self.target_x, self.target_y)) == 0:
            self.current_target = (self.current_target + 1) % 4
            self.target_x, self.target_y = self.targets[self.current_target]
        
        dx = 0
        dy = 0
        if abs(self.x - self.target_x) > 0:
            if self.target_x > self.x:
                dx = 1  
            else: 
                dx = -1
        if abs(self.y - self.target_y) > 0:
            if self.target_y > self.y:
                dy = 1  
            else: 
                dy = -1
        
        self.move(dx, dy)

    def draw(self):
        super().draw()
        if not self.item_collected:
            self.item.draw()

#Classe do Tilemap para representar o mapa do jogo
class TileMap:
    def __init__(self, rows=17, cols=18, tile_size=32, grass_prob=0.15):
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.grass_prob = grass_prob
        self.tile_images = {
            0: "land",
            1: "grass",   
        }
        self.map = []
        self.generate_map()
    
    def generate_map(self):
        self.map = []
        
        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                if row == 0 or row == self.rows-1 or col == 0 or col == self.cols-1:
                    current_row.append(1)
                else:
                    current_row.append(1 if random.random() < self.grass_prob else 0)
            self.map.append(current_row)
        
        
    def draw(self, screen, offset_x=0, offset_y=0):
        start_col = max(0, offset_x // self.tile_size)
        start_row = max(0, offset_y // self.tile_size)
        end_col = min(self.cols, (offset_x + WIDTH) // self.tile_size + 1)
        end_row = min(self.rows, (offset_y + HEIGHT) // self.tile_size + 1)
        
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                tile_type = self.map[row][col]
                if tile_type in self.tile_images:
                    image_name = self.tile_images[tile_type]
                    screen.blit(image_name,
                                (col * self.tile_size - offset_x, 
                                 row * self.tile_size - offset_y)
                    )

    def world_to_tile(self, x, y):
        return (
            int(x // self.tile_size),
            int(y // self.tile_size)
        )
    
    def is_walkable(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.map[row][col] == 0 

def play_music(track):
    if sound:
        music.stop()
        music.play(track)
    else:
        music.stop()

def update_music():
    if game_state == MENU:
        play_music("menu")
    elif game_state == PLAYING:
        play_music("background")
    elif game_state == GAME_OVER:
        play_music("game_over")
    elif game_state == VICTORY:
        play_music("victory")    

def draw_menu():
    screen.clear()
    screen.fill((30, 30, 50))
    
    logo = Actor("logo", center=(WIDTH//2, HEIGHT//5))
    logo.draw()
    
    screen.draw.filled_rect(start_button, (0, 200, 200))
    screen.draw.text(
        "Iniciar",
        center=start_button.center,
        fontsize=30,
        color=(255, 255, 255)
    )
    

    sound_color = (0, 150, 220) if sound else (80, 85, 90)
    screen.draw.filled_rect(sound_button, sound_color)
    sound_text = "Som: LIGADO" if sound else "Som: DESLIGADO"
    screen.draw.text(
        sound_text,
        center=sound_button.center,
        fontsize=30,
        color=(255, 255, 255)
    )
    
    screen.draw.filled_rect(exit_button, (50, 50, 50))
    screen.draw.text(
        "Sair",
        center=exit_button.center,
        fontsize=30,
        color=(255, 255, 255)
    )
    
    
    screen.draw.line(
        (WIDTH//4, HEIGHT//3 + 10), 
        (3*WIDTH//4, HEIGHT//3 + 10), 
        (80, 80, 80, 100)
    )

def draw_game_over():
    screen.clear()
    screen.fill((20, 20, 30))
    
    screen.draw.text(
        "DERROTA",
        center=(WIDTH//2, HEIGHT//3),
        fontsize=72,
        color=(200, 50, 50)
    )
    
    screen.draw.filled_rect(start_button, (70, 130, 80))
    screen.draw.text(
        "Voltar ao Menu",
        center=start_button.center,
        fontsize=30,
        color=(255, 255, 255)
    )

def draw_victory():
    screen.clear()
    screen.fill((20, 20, 30))
    
    screen.draw.text(
        "SUCESSO!",
        center=(WIDTH//2, HEIGHT//3),
        fontsize=72,
        color=(50, 200, 50)
    )
    
    screen.draw.filled_rect(start_button, (70, 130, 80))
    screen.draw.text(
        "Voltar ao Menu",
        center=start_button.center,
        fontsize=30,
        color=(255, 255, 255)
    )

def reset_game():
    global game_state, hero, enemies, items_collected
    
    game_state = MENU  # Volta para o menu
    hero = Hero(WIDTH/2, HEIGHT/2, tilemap=tilemap)
    enemies = [
        Enemy(Rect(100, 100, 150, 150)),
        Enemy(Rect(350, 350, 100, 100))
    ]
    items_collected = 0
    update_music()

game_state = MENU
sound = True


start_button = Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50)
sound_button = Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
exit_button = Rect(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50)

tilemap = TileMap(
    rows=HEIGHT//TILE_SIZE,
    cols=WIDTH//TILE_SIZE,
    tile_size=TILE_SIZE,
    grass_prob=0.0
)

reset_game()

total_items = len(enemies)

def update(dt):
    global game_state, items_collected
    if game_state == PLAYING:
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
        hero.update(dt)

        for enemy in enemies:
            enemy.update(dt)
            if math.dist((hero.x, hero.y), (enemy.x, enemy.y)) < 20:
                game_state = GAME_OVER
                if sound:
                    sounds.game_over.play()
                update_music()
            
            if (not enemy.item_collected and 
                math.dist((hero.x, hero.y), (enemy.item.x, enemy.item.y)) < 20):
                enemy.item_collected = True
                items_collected += 1
                if sound:
                    sounds.collect.play()
                
                if items_collected >= total_items:
                    game_state = VICTORY
                    update_music()


def draw():
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        screen.clear()
        tilemap.draw(screen)
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        screen.draw.text(f"Garotas salvas: {items_collected}/{total_items}", (10, 10), fontsize=20)
    elif game_state == GAME_OVER:
        draw_game_over()
    elif game_state == VICTORY:
        draw_victory()

#interação com o click do mouse
def on_mouse_down(pos):
    global game_state, sound
    
    if game_state == MENU:
        if start_button.collidepoint(pos):
            game_state = PLAYING
            if sound:
                sounds.start.play()
                update_music()
        elif sound_button.collidepoint(pos):
            sound = not sound
            if sound:
                sounds.toggle_on.play()
                music.unpause()
                if not music.is_playing("menu"):
                    update_music()
            else:
                sounds.toggle_off.play()
                music.pause()

        elif exit_button.collidepoint(pos):
            quit()

    elif game_state == GAME_OVER or game_state == VICTORY:
        if start_button.collidepoint(pos):
            if sound:
                sounds.start.play()
            reset_game()

#interação com o teclado
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

