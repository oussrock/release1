import gym
import os
import neat



environment = gym.make('CartPole-v1')
environment.reset()
steps = 1000



def eval_genomes(genomes, config):

    for genome_id, genome in genomes:
        # NEAT initialization
        observation = [0, 0, 0, 0]  
        gameover = False
        net = neat.nn.FeedForwardNetwork.create(genome, config) #Creat net for genome with configs
        genome.fitness = 0  #Starting fitness at  0

        # Game initialization

        while not gameover:
            #environment.render()     uncomment if we want to see the game running 
            
            output = net.activate(observation)  
            action = max(output)

            if output[0] == action:
                action = 1
            else:
                action = 0

            observation, reward, gameover, info = environment.step(action)  #Performs action
            if observation[3] > 0.5 or observation[3] < -0.5:   
                gameover = True
                reward = -5
                environment.reset()
            genome.fitness += reward    #Rewards genome for each action 
        environment.reset()

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    Population = neat.Population(config)

    # Reporter 
    Population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    Population.add_reporter(stats)

    # NEAT
    winnerGenome = Population.run(eval_genomes, 50)

    # Print the best Genome stats 
    print('\nBest genome:\n{!s}'.format(winnerGenome))

    #test winner 100 times and prints the score over 100 tries 
    winner_net = neat.nn.FeedForwardNetwork.create(winnerGenome, config)
    test_model(winner_net)  

def test_model(winnerGenome):
    
    observation = [0, 0, 0, 0]
    score = 0
    reward = 0
    #testing 100 times the genome and keeping score to see if he could solve the problem 
    for i in range(100):
        done = False
        observation = [0, 0, 0, 0]
        while not done:
            #environment.render()   #Render game uncomment if you want to see the 100 tries it takes some time    
            output = winnerGenome.activate(observation)
            action = max(output)
            if output[0] == action:
                action = 1
            else:
                action = 0

            observation, reward, done, info = environment.step(action)
            if observation[3] > 0.5 or observation[3] < -0.5:
                done = True
                environment.reset()
            score += reward
        environment.reset()

    print("Score Over 100 tries:")
    print(score/100)



if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_feedforward_cartpole.txt')
    run(config_path)
