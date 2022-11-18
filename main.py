import pygame
import neat
import time
import os
import random
pygame.font.init()

WIDTH = 540
HEIGHT = 800
FLOOR = 730
DRAW_LINES = False

TRIES = 0

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Flappy Bird")

# Increase the size of images
BIRD = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))]
PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")).convert_alpha())
BASE = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "base.png")).convert_alpha())
BG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bg.png")).convert_alpha())

STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)


class Bird:
    """
    Bird class represents the Flappy bird, the main character of game
    """
    IMGS = BIRD
    MAX_ROTATION = 25       # Tilt of Bird
    ROT_VEL = 20            # Rotate in each frame
    ANIMATION_TIME = 5      # Time

    def __init__(self, a, b):
        """
        __init__ function:-
        Initialization of object
        param a: starting x position
        param b: starting b position
        return: None
        """
        self.a = a
        self.b = b
        self.tilt = 0   # how much image tilted
        self.tick_count = 0
        self.vel = 0
        self.height = self.a
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        jump function:-
        Jump the bird
        return: None
        """
        self.vel = -10.5
        self.tick_count = 0     # Count for last jump
        self.height = self.b

    def move(self):
        """
        move function:-
        move the bird
        return: None
        """
        self.tick_count += 1

        dist = self.vel*self.tick_count + 1.5*self.tick_count**2        # Displacement

        # Terminal Velocity
        if dist >= 16:
            dist = (dist/abs(dist)) * 16

        if dist < 0:
            dist -= 2           # Jump

        self.b = self.b + dist

        if dist < 0 or self.b < self.height + 50:       # Tilting the bird upward
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:                         # Tilting the bird downward
                self.tilt -= self.ROT_VEL

    # Win = Window
    def draw(self, win):
        """
        draw function:-
        draw the bird
        param win: pygame window
        return: None
        """

        self.img_count += 1

        # For animation

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:                # When bird is going down it isn't flapping
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # This is how to rotate image in pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.a, self.b)).center)
        win.blit(rotated_image, new_rect.topleft)

# Mask can detect pixel, it returns list
    def get_mask(self):
        """
        get_mask function:-
        get the mask
        return: return the mask of current image
        """
        return pygame.mask.from_surface(self.img)

# Blit means draw


class Pipe:
    """
    Pipe class represents a pipe
    """
    GAP = 200
    VEL = 5

    def __init__(self, a):
        """
        initialization of pipe object
        param a: The x position of object : int
        return: None
        """
        self.a = a
        self.height = 0

        # Top and bottom of pipe
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE, False, True)
        self.PIPE_BOTTOM = PIPE

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        The top of the screen -> set the height of the pipe
        param: None
        return: None
        """
        self.height = random.randrange(40, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        Movement of pipe
        param: None
        return: None
        """
        self.a -= self.VEL

    def draw(self, win):
        """
        Draw the pipes (Top and bottom)
        param win: pygame window
        return: None
        """

        win.blit(self.PIPE_TOP, (self.a, self.top))         # Top pipe

        win.blit(self.PIPE_BOTTOM, (self.a, self.bottom))       # Bottom pipe

    def collide(self, bird):
        """
        Checks if a point of bird is colliding with pipe.
        param bird: Flappy Bird
        return: If collision happened: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.a - bird.a, self.top - round(bird.b))
        bottom_offset = (self.a - bird.a, self.bottom - round(bird.b))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)  # Returns none if doesn't collide
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    """
    Represent the base/floor of game
    """
    VEL = 5     # Always same as PIPE
    WIDTH = BASE.get_width()
    IMG = BASE

    def __init__(self, b):
        """
        Initialization of the object
        param b: Y-axis position: int
        return: None
        """
        self.b = b
        self.a1 = 0
        self.a2 = self.WIDTH

    def move(self):
        """
        move function-
        Use two images so base looks continuous. First image on screen and second image behind it.
        Param : None
        Return : None
        """
        self.a1 -= self.VEL
        self.a2 -= self.VEL

        if self.a1 + self.WIDTH < 0:
            self.a1 = self.a2 + self.WIDTH

        if self.a2 + self.WIDTH < 0:
            self.a2 = self.a1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor
        param win: pygame window
        return : None
        """
        win.blit(self.IMG, (self.a1, self.b))
        win.blit(self.IMG, (self.a2, self.b))


def draw_window(win, birds, pipes, base, score, tries):
    """
    draw_window function-
    draws the windows for the main game
    param win: pygame window
    param bird: a Flappy Bird object
    param pipes: List of pipes
    param score: score of the game: int
    param base: base of game
    param tries: current generation
    param pipe_ind: index of closest pipe
    return: None
    """
    if tries == 0:
        tries = 1
    win.blit(BG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    # Current score
    label_sco = STAT_FONT.render("Score: " + str(score), True, (255, 255, 255))
    win.blit(label_sco, (WIDTH - 10 - label_sco.get_width(), 50))

    # Current Generation
    label_sco = STAT_FONT.render("Generation No:  " + str(tries), True, (255, 255, 255))
    win.blit(label_sco, (10, 10))

    # Alive birds
    label_sco = STAT_FONT.render("Alive: " + str(len(birds)), True, (255, 255, 255))
    win.blit(label_sco, (10, 50))

    pygame.display.update()


def main(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the score and how many
    pipe it clears in game
    """

    global WIN, TRIES
    win = WIN
    TRIES += 1
    nets = []       # Netword that bird uses to play
    ge = []     # Genomes
    birds = []

    for genome_id, genome in genomes:            # Genome id, Genome object
        genome.fitness = 0          # Starting fitness
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run and len(birds) > 0:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        # bird.move()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].a > pipes[0].a + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        for a, bird in enumerate(birds):
            bird.move()
            ge[a].fitness += 0.1

            # Flappy bird location, top pipe location and bottom pipe location to determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.b, abs(bird.b - pipes[pipe_ind].height), abs(bird.b - pipes[pipe_ind].bottom)))

            # tanh function always value between -1 and 1.
            if output[0] > 0.5:
                bird.jump()

        base.move()

        add_pipe = False
        rem = []
        for pipe in pipes:

            pipe.move()

            for a, bird in enumerate(birds):
                # Check the collision with bird
                if pipe.collide(bird):
                    ge[a].fitness -= 1
                    birds.pop(a)
                    nets.pop(a)
                    ge.pop(a)

                # Check if we have pass the pipe
                if not pipe.passed and pipe.a < bird.a:
                    pipe.passed = True
                    add_pipe = True

            # Check if pipe is visible on screen
            if pipe.a + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

        if add_pipe:
            score += 1

            # gets reward for passing pipe
            for g in ge:
                g.fitness += 7
            pipes.append(Pipe(WIDTH))

        for r in rem:
            pipes.remove(r)

        for a, bird in enumerate(birds):
            if bird.b + bird.img.get_height() >= 730 or bird.b < 0:
                birds.pop(a)
                nets.pop(a)
                ge.pop(a)

        draw_window(win, birds, pipes, base, score, TRIES)


def run(config_path):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    param config_file: location of config file
    return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # Top level object of NEAT run
    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

# Call main function 50 times
    winner = population.run(main, 50)     # Fitness function - fitness of

    print('\nBest Bird:\n{!s}'.format(winner))


if __name__ == "__main__":
    """
    Determine path to configuration file. This path manipulation is
    here so that the script will run successfully regardless of the
    current working directory.
    """
    local_dir = os.path.dirname(__file__)               # Directory path of current folder
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
