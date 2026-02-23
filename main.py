import math
import random
from pygame import Rect

# --- Configuracoes ---
WIDTH = 800
HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -13 
SPEED = 5

game_state = "menu"
frame_count = 0
sound_enabled = True
music_started = False
mouse_pos = (0, 0)

# Botões do Menu
btn_start_rect = Rect(300, 220, 200, 50)
btn_sound_rect = Rect(300, 300, 200, 50)
btn_quit_rect  = Rect(300, 380, 200, 50)

class Animator:
    def __init__(self, frames, delay):
        self.frames = frames
        self.delay = delay
        self.current_frame = 0
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer >= self.delay:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_frame(self):
        return self.frames[self.current_frame]

class Hero:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 40, 50)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_left = False
        
        # Animações para a Direita
        self.idle_r = Animator(["hero_idle1", "hero_idle2"], 20)
        self.run_r = Animator(["hero_run1", "hero_run2"], 8)
        
        # Animações para a Esquerda
        self.idle_l = Animator(["hero_idle1", "hero_idle2"], 20)
        self.run_l = Animator(["hero_run_l1", "hero_run_l2"], 8)
        
        self.thoughts = ["Vou chegar la", "Cuidado!", "Quase..."]
        self.current_thought = ""

    def update(self, platforms):
        self.vy += GRAVITY
        self.rect.y += self.vy
        self.on_ground = False
        
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.bottom
                    self.vy = 0

        if self.vx < 0: self.facing_left = True
        elif self.vx > 0: self.facing_left = False

        self.rect.x += self.vx
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0: self.rect.right = p.left
                elif self.vx < 0: self.rect.left = p.right

        if self.facing_left:
            if self.vx != 0: self.run_l.update()
            else: self.idle_l.update()
        else:
            if self.vx != 0: self.run_r.update()
            else: self.idle_r.update()

        if random.randint(1, 150) == 1:
            self.current_thought = random.choice(self.thoughts)

    def draw(self):
        breath = math.sin(frame_count * 0.1) * 2 if self.vx == 0 else 0
        
        if self.facing_left:
            img = self.run_l.get_frame() if self.vx != 0 else self.idle_l.get_frame()
        else:
            img = self.run_r.get_frame() if self.vx != 0 else self.idle_r.get_frame()
            
        screen.blit(img, (self.rect.x, self.rect.y + breath))
        
        if self.current_thought and self.vx == 0:
            screen.draw.text(self.current_thought, (self.rect.x - 20, self.rect.y - 30), color="white", fontsize=20)

class Enemy:
    def __init__(self, platform):
        self.platform = platform
        self.rect = Rect(platform.x, platform.y - 45, 35, 45)
        self.vx = 2
        self.anim = Animator(["enemy_walk1", "enemy_walk2"], 10)

    def update(self):
        self.rect.x += self.vx
        if self.rect.right > self.platform.right or self.rect.left < self.platform.left:
            self.vx *= -1
        self.anim.update()

    def draw(self):
        screen.blit(self.anim.get_frame(), self.rect.topleft)


p_ground = Rect(0, 550, 800, 50)
p1 = Rect(150, 430, 200, 40)
p2 = Rect(450, 310, 200, 40)
p3 = Rect(100, 190, 200, 40)
p_final = Rect(500, 120, 250, 40)

platforms = [p_ground, p1, p2, p3, p_final]
enemies = [Enemy(p1), Enemy(p2), Enemy(p3)]
goal = Rect(650, 70, 40, 50)
hero = Hero(50, 500)

def reset_game():
    global hero, game_state
    hero.rect.topleft = (50, 500)
    hero.vy = 0
    hero.vx = 0
    game_state = "play"

def draw_styled_button(rect, text, base_color=(50, 50, 200)):
    color = (80, 80, 255) if rect.collidepoint(mouse_pos) else base_color
    screen.draw.filled_rect(Rect(rect.x + 4, rect.y + 4, rect.width, rect.height), (20, 20, 20))
    screen.draw.filled_rect(rect, color)
    screen.draw.rect(rect, (255, 255, 255))
    screen.draw.text(text, center=rect.center, color="white", fontsize=30)

def update():
    global frame_count, game_state, music_started
    frame_count += 1

    if sound_enabled:
        if not music_started:
            music.play("background")
            music_started = True
    else:
        if music_started:
            music.stop()
            music_started = False

    if game_state == "play":
        if keyboard.left:
            hero.vx = -SPEED
        elif keyboard.right:
            hero.vx = SPEED
        else:
            hero.vx = 0

        hero.update(platforms)

        for e in enemies:
            e.update()
            if hero.rect.colliderect(e.rect):
                if sound_enabled:
                    sounds.hit.play()
                game_state = "gameover"

        if hero.rect.colliderect(goal):
            game_state = "win"

        if hero.rect.top > HEIGHT:
            game_state = "gameover"

def draw():
    screen.clear()
    screen.blit("background", (0, 0))
    
    if game_state == "menu":
        screen.draw.text("Jogo Plataforma, center=(400, 100), fontsize=60, color="white")
        draw_styled_button(btn_start_rect, "INICIAR")
        
        txt_som = "SOM: LIGADO" if sound_enabled else "SOM: DESLIGADO"
        cor_som = (50, 200, 50) if sound_enabled else (200, 50, 50)
        draw_styled_button(btn_sound_rect, txt_som, cor_som)
        
        draw_styled_button(btn_quit_rect, "SAIR", (100, 100, 100))
        
    elif game_state == "play":
        for p in platforms:
            for x in range(p.left, p.right, 32):
                screen.blit("platform", (x, p.top))
        screen.blit("flag_image", (goal.x, goal.y))
        hero.draw()
        for e in enemies: e.draw()
        
    elif game_state == "gameover":
        screen.draw.text("GAME OVER", center=(400, 300), fontsize=80, color="red")
        screen.draw.text("Pressione R para recomecar", center=(400, 400), fontsize=30, color="white")
        
    elif game_state == "win":
        screen.draw.text("VOCE VENCEU!", center=(400, 300), fontsize=80, color="green")
        screen.draw.text("Pressione R para o Menu", center=(400, 400), fontsize=30, color="white")

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos

def on_mouse_down(pos):
    global game_state, sound_enabled, music_started
    if game_state == "menu":
        if btn_start_rect.collidepoint(pos):
            reset_game()
        elif btn_sound_rect.collidepoint(pos):
            sound_enabled = not sound_enabled
            if sound_enabled:
                if not music_started:
                    music.play("background")
                    music_started = True
            else:
                if music_started:
                    music.stop()
                    music_started = False
        elif btn_quit_rect.collidepoint(pos):
            quit()

def on_key_down(key):
    global game_state  # Resolve o erro de UnboundLocalError
    if game_state == "play":
        if (key == keys.SPACE or key == keys.UP) and hero.on_ground:
            hero.vy = JUMP_STRENGTH
            if sound_enabled: sounds.jump.play()
    elif game_state in ["gameover", "win"] and key == keys.R:
        game_state = "menu"

