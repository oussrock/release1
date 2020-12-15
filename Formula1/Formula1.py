import pygame
import math
import sys
import random
import os
import neat

width_gamescreen = 1500
height_gamescreen = 800
generation = 0

class Car:

    def __init__(self):

        self.surface = pygame.image.load("Ferrari.png")
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotated_surface = self.surface
        self.position = [650, 650]
        self.angle = 0
        self.speed = 0
        self.center = [self.position[0] + 50, self.position[1] + 50]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0

    def draw(self, screen):

        screen.blit(self.rotated_surface, self.position)
        self.draw_radar(screen)

    def draw_radar(self, screen):

        for r in self.radars:
            position, dist = r
            pygame.draw.line(screen, (255, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (255, 0, 0), position, 5)

    def check_collision(self, map):

        self.is_alive = True
        for points in self.four_collisions_points:
            if map.get_at((int(points[0]), int(points[1]))) == (255, 255, 255, 255):
                self.is_alive = False
                break

    def check_radar(self, degree, map):

        longeur = 0

        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * longeur)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * longeur)

        while not map.get_at((x, y)) == (255, 255, 255, 255) and longeur < 300:
            
            longeur = longeur + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * longeur)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * longeur)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, map):
        #Car speed fixed, could be changed if required to add diffuclty 
        self.speed = 15

        #check positionition
        self.rotated_surface = self.rot_center(self.surface, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed

        if self.position[0] < 20:
            self.position[0] = 20
        elif self.position[0] > width_gamescreen - 120:
            self.position[0] = width_gamescreen - 120


        self.distance += self.speed
        self.time_spent += 1
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed

        if self.position[1] < 20:
            self.position[1] = 20
        elif self.position[1] > height_gamescreen - 120:
            self.position[1] = height_gamescreen - 120

        # caculate 4 collision points
        self.center = [int(self.position[0]) + 50, int(self.position[1]) + 50]
        longeur = 40 # Estimation distance between center and corner 

        left_top_lenght = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * longeur, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * longeur]
        right_top_lenght = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * longeur, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * longeur]
        left_bottom_lenght = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * longeur, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * longeur]
        right_bottom_lenght = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * longeur, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * longeur]
        self.four_collisions_points = [left_top_lenght, right_top_lenght, left_bottom_lenght, right_bottom_lenght]

        self.check_collision(map)
        self.radars.clear()
        for degreee in range(-90, 120, 45):
            self.check_radar(degreee, map)

    def get_data(self):
        radars = self.radars
        return_value = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            return_value[i] = int(r[1] / 30)

        return return_value

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        return self.distance / 50.0

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

def run_car(genomes, config):

    # NEAT initialization
    nets = []
    cars = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

        
        cars.append(Car())

    # Game initialization 

    pygame.init()
    screen = pygame.display.set_mode((width_gamescreen, height_gamescreen))
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    car_font = pygame.font.SysFont("Arial", 30)
    map = pygame.image.load('MonacoGP.png')


    # Main loop
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)


        # Input my data and get result from network
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            i = output.index(max(output))
            if i == 0:
                car.angle += 10
            else:
                car.angle -= 10

        # Update car and fitness
        remain_cars = 0
        for i, car in enumerate(cars):
            if car.get_alive():
                remain_cars += 1
                car.update(map)
                genomes[i][1].fitness += car.get_reward()

        # check
        if remain_cars == 0:
            break

        # Drawing
        screen.blit(map, (0, 0))
        for car in cars:
            if car.get_alive():
                car.draw(screen)

        text = generation_font.render("Generation : " + str(generation), True, (0, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (width_gamescreen/1.2, 700)
        screen.blit(text, text_rect)

        text = car_font.render("remain cars : " + str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (width_gamescreen/1.2, 750)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)

if __name__ == "__main__":
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, 'config-feedforward.txt')

    Population = neat.Population(config)

    # Reporter 
    Population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    Population.add_reporter(stats)

    # NEAT
    Population.run(run_car, 1000)
