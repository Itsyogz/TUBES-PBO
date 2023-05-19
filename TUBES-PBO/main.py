import pygame
from pygame.locals import *
from pygame import mixer
import random

mixer.init()
pygame.init()

screen_w = 864
screen_h = 720

screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('Challenge Car')

#sound
backsound = pygame.mixer.Sound('music/backsound1.mp3')
backsound.set_volume(0.8)
move_car = pygame.mixer.Sound('music/car1.mp3')
move_car.set_volume(0.4)
backward = pygame.mixer.Sound('music/car2.mp3')
backward.set_volume(0.4)
crash = pygame.mixer.Sound('music/crash.wav')
crash.set_volume(0.2)

#images
bg = pygame.image.load('img/bg1.png')
button_img = pygame.image.load('img/restart.png')


#define
fps = 30
scroll_speed = 20
wall_gap = 110
clock = pygame.time.Clock()
wall_frequency = 1000 #dalam miliseconds
last_wall = pygame.time.get_ticks() - wall_frequency
game_over = False
score = 0
pass_wall = False
car_move = False

#fonts
font = pygame.font.SysFont('Bauhaus 93', 60)

#colors
white = (255, 255, 255)


def drawtext(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def restart():
    wall_group.empty()
    crash.stop()
    backsound.play()
    mobil.rect.x = 80
    mobil.rect.y = int(screen_h/1.87)
    score = 0
    return score

backsound.play()

class Car(pygame.sprite.Sprite):
    def __init__ (self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):
            img = pygame.image.load(f'img/car{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.x = x
        self.y = y
        self.velX = 0
        self.velY = 0
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.speed = 10

    def update(self):

        #buat movement
        if car_move == True:
            self.velX = 0
            self.velY = 0
        
            if self.left_pressed and not self.right_pressed and self.x > 0:
                self.velX = -self.speed
            if self.right_pressed and not self.left_pressed and self.x < 740:
                self.velX = self.speed + 5
            if self.up_pressed and not self.down_pressed and self.y > 270:
                self.velY = -self.speed
            if self.down_pressed and not self.up_pressed and self.y < 500:
                self.velY = self.speed

        self.x += self.velX
        self.y += self.velY

        self.rect = pygame.Rect(self.x - 5, self.y - 38, 32, 32)

        #buat nge handle animasi
        self.counter += 1
        cooldown = 15

        if self.counter > cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]

        #rotate car
        self.image = pygame.transform.rotate(self.images[self.index],  self.velY * -2)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/wall.png')
        self.rect = self.image.get_rect()
        #posisi: 1 untuk inisialisasi top, dan -1 untuk bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(wall_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(wall_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        #pos
        pos = pygame.mouse.get_pos()

        #check ketika mouse berada di button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #menampilkan button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

wall_group = pygame.sprite.Group()
car_group = pygame.sprite.Group()

mobil = Car(80, int(screen_h/1.87))

car_group.add(mobil)

#instance
button = Button(screen_w // 2 - 50, screen_h // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)
    pygame.time.delay(10)

    #update background
    screen.blit(bg, (0,0))

    car_group.draw(screen)
    car_group.update()
    wall_group.draw(screen)

    #cek collision
    if pygame.sprite.groupcollide(car_group, wall_group, False, False) or mobil.rect.top < 230:
        game_over = True

    #untuk nge cek apakah mobil melewati jalan atau tidak
    if mobil.rect.bottom > 480:
        game_over = True
        car_move = False

    #check score
    if len(wall_group) > 0:
        if car_group.sprites()[0].rect.left > wall_group.sprites()[0].rect.left\
            and car_group.sprites()[0].rect.right < wall_group.sprites()[0].rect.right\
            and pass_wall == False:
            pass_wall = True
        if pass_wall == True:
            if car_group.sprites()[0].rect.left > wall_group.sprites()[0].rect.right:
                score += 1
                pass_wall = False


    if game_over == False and car_move == True:
        time_now = pygame.time.get_ticks()
        if time_now - last_wall > wall_frequency:
            wall_height = random.randint(-100, 100)
            top_wall = Wall(screen_w, int(screen_h / 2) + wall_height, 1)
            btm_wall = Wall(750, int(screen_h / 2) + wall_height, -1)
            wall_group.add(top_wall)
            wall_group.add(btm_wall)
            last_wall = time_now

        wall_group.update()

    drawtext(str(score), font, white, int(screen_w / 2), 60)

    #check game over dan restart button
    if game_over == True:
        car_move = False
        crash.play(-1)
        backsound.stop()
        if button.draw() == True:
            game_over = False
            score = restart()

    #event handler quit and pressed key
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and car_move == False and game_over == False:
            car_move = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                mobil.left_pressed = True
                backward.play()
            if event.key == pygame.K_d:
                mobil.right_pressed = True
                move_car.play()
            if event.key == pygame.K_w:
                mobil.up_pressed = True
                move_car.play()
            if event.key == pygame.K_s:
                mobil.down_pressed = True
                move_car.play()

        if game_over == True:
            backward.stop()
            move_car.stop()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                mobil.left_pressed = False
                backward.stop()
            if event.key == pygame.K_d:
                mobil.right_pressed = False
                move_car.stop()
            if event.key == pygame.K_w:
                mobil.up_pressed = False
                move_car.stop()
            if event.key == pygame.K_s:
                mobil.down_pressed = False
                move_car.stop()

    pygame.display.update()

pygame.quit()