import gym
import numpy as np 
import cv2
import neat 
import pickle 

import random
import noise


env = gym.make('Breakout-v0')
#env = gym.make('VideoPinball-v0')

imagearray = []

def eval_genomes(genomes, config):
	for genome_id, genome in genomes:
		observation = env.reset()
		inputx, inputy, inputColour = env.observation_space.shape

		inputx = int (inputx / 8)
		inputy = int (inputy / 8)

		net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)

		fitness_current = 0 
		frame = 0 
		counter = 0 

		game_done = False 

		while not game_done :
			frame += 1

			factor = 0.5 
			observation = np.uint8(noise.noisy(observation,factor))

			observation = cv2.resize(observation, (inputx, inputy))
			#observation = cv2.cvtColor(observation, cv2.COLOR_RGB2GRAY)

			imagearray = np.ndarray.flatten(observation)
			nnOutput = net.activate(imagearray)

			numerical_input = nnOutput.index(max(nnOutput))
			observation, reward, game_done, info = env.step(numerical_input)


			fitness_current += reward

			if reward > 0 :
				counter = 0 
			else :
				counter += 1


			env.render()
			if game_done or counter == 300:
				game_done= True 
				print (genome_id, fitness_current, counter)
			genome.fitness = fitness_current

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, 'config3.txt')			

pop = neat.Population(config)

pop.add_reporter(neat.Checkpointer(10))

winner = pop.run(eval_genomes)

with open('winner_BreakOut123.pkl', 'wb') as output :
	pickle.dump(winner, output, 1)
