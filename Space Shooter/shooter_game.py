import pygame
from time import sleep
from random import randint
import os

pygame.init()
pygame.font.init()

display_info = pygame.display.Info()

screen_width = display_info.current_w
screen_height = display_info.current_h

developer_screen_width = 2560
developer_screen_height = 1440

delta_x = screen_width / developer_screen_width
delta_y = screen_height / developer_screen_height

screen_title = "Маладёжний шутир"
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(screen_title)
screen_bg = pygame.transform.scale(pygame.image.load(os.path.join(os.getcwd(), "sprites", "galaxy.jpg")), (screen_width, screen_height))
clock = pygame.time.Clock()
tickrate = 60

class Hitbox():

    def __init__(self, screen, x, y, width, height, color, weight):
        self.screen = screen

        self.x = x
        self.y = y
        self.width = width 
        self.height = height
        self.color = color

        if weight < 1:
            weight = 1
        self.weight = weight  

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw_hitbox(self):
        pygame.draw.rect(self.screen, self.color, self.rect, self.weight)

class Picture(Hitbox):
    def __init__(self, screen, x, y, width, height, color, weight, path):
        Hitbox.__init__(self, screen, x, y, width, height, color, weight)
        self.path = path
        self.image = pygame.transform.scale(pygame.image.load(self.path).convert_alpha(), (self.width, self.height))

    def draw_picture(self):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(Picture):
    def __init__(self, screen, x, y, width, height, color, weight, path, speed, player_id):
        Picture.__init__(self, screen, x, y, width, height, color, weight, path)

        self.speed = speed
        self.player_id = player_id

        self.dx = 0
        self.delta = 1
    
    def move(self):
        self.rect.x += int(self.speed * self.dx * self.delta)


    def contoller(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and not keys[pygame.K_d]:
            self.dx = -1
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            self.dx = 1
        else:
            self.dx = 0
        self.move()

class Enemy(Picture):
    def __init__(self, screen, x, y, width, height, color, weight, path, speed):
        Picture.__init__(self, screen, x, y, width, height, color, weight, path)

        self.speed = speed
        self.dy = 1
        self.dx = 1
        self.counter = 0
        self.move_delay = 1

    def move(self, tickrate):
        self.rect.y += int(self.speed * self.dy)
        
        if self.counter >= tickrate * self.move_delay:
            self.counter = 0 
            if self.dx == 1:
                self.dx = -1
            else:
                self.dx = 1
        else:
            self.counter += randint(0, 1)


        self.rect.x += int(self.speed * self.dx)
        
class Wall(Hitbox):
    def __init__(self, screen, x, y, width, height, color, weight):
        Hitbox.__init__(self, screen, x, y, width, height, color, weight)

class Bullet(Picture):
    def __init__(self, screen, x, y, width, height, color, weight, path, speed):
        Picture.__init__(self, screen, x, y, width, height, color, weight, path)

        self.speed = speed
        self.dy = 1

    def bullet_move(self):
        self.rect.y -= int(self.speed * self.dy)


font = pygame.font.Font(None, 36)
print(delta_x)
print(delta_y)
score = 0
miss = 0

font_2 = pygame.font.Font(None, 72)

Win_text = font_2.render("Вы победили!", True, (0, 255, 50))
Lose_text = font_2.render("Поражение :(", True, (255, 0, 0))

enemies_rects = []

pygame.mixer.music.load(os.path.join(os.getcwd(), "sounds", "space.ogg"))
pygame.mixer.music.set_volume(0.000001)
pygame.mixer.music.play()

player = Player(screen, screen_width / 2, screen_height - 250, 250 * delta_x, 250 * delta_y, (0, 0, 0), 10, os.path.join(os.getcwd(), "sprites", "player.png"), 15 * delta_x, 1)
enemies= []
for i in range(6):
    enemy = Enemy(screen, randint(100, screen_width - 100), 200 * delta_y, 150 * delta_y, 50 * delta_y, (0, 0, 0), 10, os.path.join(os.getcwd(), "sprites", "enemy" + str(randint(1,2)) + ".png"), randint(1, 2) * delta_y)
    enemies.append(enemy)
    enemies_rects.append(enemy.rect)


fire = pygame.mixer.Sound(os.path.join(os.getcwd(), "sounds", "fire.ogg"))
fire.set_volume(0.1)



bullets = []

is_working = True
while is_working:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_working = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(screen, player.rect.x + 118, player.rect.y, 15 * delta_x, 30 * delta_y, (0, 0, 0), 10, os.path.join(os.getcwd(),"sprites", "bullet.png"), 10 * delta_y)
                bullets.append(bullet)
                fire.play()
                
    screen.blit(screen_bg, (0, 0))

    player.draw_picture()
    player.contoller()

    for bullet in bullets:
        bullet.draw_picture()
        bullet.bullet_move()
        if bullet.rect.y < 0:
            bullets.remove(bullet)
        i = bullet.rect.collidelist(enemies_rects)
        if i != -1:
            enemies_rects.pop(i)
            print(i)
            enemies.pop(i)
            bullets.remove(bullet)
            score += 1

    if score == 10:
        screen.blit(Win_text, (1100 * delta_x, 600 * delta_y))
        score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))
        pygame.display.update()
        sleep(2)
        is_working = False
    
    if miss == 10:
        screen.blit(Lose_text, (1100 * delta_x, 600 * delta_y))
        pygame.display.update()
        miss_text = font.render(f"Пропущено: {miss}", True, (255, 255, 255))
        sleep(2)
        is_working = False

    for enemy in enemies:
        enemy.draw_picture()
        enemy.move(tickrate)

        if enemy.rect.y > screen_height:
            enemies.remove(enemy)
            miss += 1
            enemies_rects.remove(enemy.rect)

    if len(enemies) < 6:
        enemy = Enemy(screen, randint(100, screen_width - 100), 200 * delta_y, 150 * delta_y, 50 * delta_y, (0, 0, 0), 10, os.path.join(os.getcwd(), "sprites", "enemy" + str(randint(1,2)) + ".png"), randint(1, 2) * delta_y)
        enemies_rects.append(enemy.rect)
        enemies.append(enemy)

    index = player.rect.collidelist(enemies_rects)
    if index != -1:
        screen.blit(Lose_text, (150, 150))
        pygame.display.update()
        miss_text = font.render(f"Пропущено: {miss}", True, (255, 255, 255))
        sleep(2)
        is_working = False

    score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))
    miss_text = font.render(f"Пропущено: {miss}", True, (255, 255, 255))

    screen.blit(score_text, (40, 120))
    screen.blit(miss_text, (10, 60))





    pygame.display.update()
    clock.tick(tickrate)