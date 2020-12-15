 
# --- Importer les bibliothèques utilisées pour ce programme
 
import math
import pygame
import neat 
from neat import nn, population, statistics #, visualize
import random
from random import randint

 
# Définition de quelques couleurs
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 200, 255)
 
# Taille des blocs de séparation

brick_width = 23
brick_height = 15
 
 
class Brick(pygame.sprite.Sprite):
    # Nous utilisons cette classe pour créer un bloc qui est detruit par la balle. Nous utilisons la classe "Sprite" dans Pygame.
 
    def __init__(self, color, x, y):
        # Constructor. 
 
        # Call parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.Surface([brick_width, brick_height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
 
 
class Ball(pygame.sprite.Sprite):
    # Cette classe est la balle, On utilise encore la class "Sprite" dans Pygame  
 
    speed = 10.0
    x = 0.0
    y = 180.0
    direction = 200
    width = 10
    height = 10
 
    # Constructor 
    def __init__(self):
        super().__init__()
 
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()
 
    def bounce(self, diff):
        
        self.direction = (180 - self.direction) % 360
        self.direction -= diff
 
    def update(self):
        # position de la balle 
        # Sin et Cos sont en degrees, on fait la conversion 
        direction_rad = math.radians(self.direction)
 
        self.x += self.speed * math.sin(direction_rad)
        self.y -= self.speed * math.cos(direction_rad)
 
        self.rect.x = self.x
        self.rect.y = self.y
 
        if self.y <= 0:
            self.bounce(0)
            self.y = 1
 
        if self.x <= 0:
            self.direction = (360 - self.direction) % 360
            self.x = 1
 
        if self.x > self.screenwidth - self.width:
            self.direction = (360 - self.direction) % 360
            self.x = self.screenwidth - self.width - 1
 
        if self.y > 600:
            return True
        else:
            return False
 
 
class Player(pygame.sprite.Sprite):
#cette classe est la bare horisital controlle par le joueur  
    def __init__(self):
        super().__init__()
 
        self.width = 75
        self.height = 15
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((white))

        self.rect = self.image.get_rect()
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()
 
        self.rect.x = 0
        self.rect.y = self.screenheight-self.height
 
    def update(self):

        # On va chercher la position de la sourie, Cette partie Doit etre changer pour NEAT 
        pos = pygame.mouse.get_pos()

        self.rect.x = pos[0]
        # Je met les limites pour que le joeur depasse pas lecran du jeu 
        if self.rect.x > self.screenwidth - self.width:
            self.rect.x = self.screenwidth - self.width
 
pygame.init()
screen = pygame.display.set_mode([800, 600])
pygame.display.set_caption('Break Out By Ouss')
pygame.mouse.set_visible(0)

font = pygame.font.Font(None, 36)
background = pygame.Surface(screen.get_size())
bricks = pygame.sprite.Group()
balls = pygame.sprite.Group()
allsprites = pygame.sprite.Group()
 
player = Player()
allsprites.add(player)
 
ball = Ball()
allsprites.add(ball)
balls.add(ball)
 
# pisition y de la premiere brick
top = 80
brickcount = 32
 
# --- Creation des bricks 
for row in range(5):
    
    for column in range(0, brickcount):
        
        brick = Brick(blue, column * (brick_width + 2) + 1, top)
        bricks.add(brick)
        allsprites.add(brick)
    
    top += brick_height + 2
 
clock = pygame.time.Clock()
 
game_over = False
exit_program = False
 
# Main
while not exit_program:
    clock.tick(30)
    screen.fill(black)
    gameScore = (brickcount *5  - len(bricks)) * 50
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program = True

    if not game_over:
        # update la position de la  balle et du joueur 
        player.update()
        game_over = ball.update()
        score = font.render('Score = %d' %gameScore, True, white)
        scorepos = score.get_rect(centerx=background.get_width() / 10)
        scorepos.top = 10
        screen.blit(score, scorepos)
 
    # Game over 
    if game_over:
        text = font.render("Game Over", True, white)
        textpos = text.get_rect(centerx=background.get_width()/2)
        textpos.top = 300
        screen.blit(text, textpos)
        score = font.render('Score = %d' %gameScore, True, white)
        scorepos = score.get_rect(centerx=background.get_width() / 10)
        scorepos.top = 10
        screen.blit(score, scorepos)
 
    # si la balle touche le joeur 
    if pygame.sprite.spritecollide(player, balls, False):
        diff = (player.rect.x + player.width/2) - (ball.rect.x+ball.width/2)
 
        ball.rect.y = screen.get_height() - player.rect.height - ball.rect.height - 1
        ball.bounce(diff)
 
    # collisions entre la balle et bricks 
    deadbricks = pygame.sprite.spritecollide(ball, bricks, True)
 
    if len(deadbricks) > 0:
        ball.bounce(0)
 
        if len(bricks) == 0:
            game_over = True
 
    allsprites.draw(screen)
    pygame.display.flip()
 
pygame.quit()