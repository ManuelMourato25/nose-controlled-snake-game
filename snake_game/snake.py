import pygame
import sys
import time
import random
from messaging.rabbitmq import create_queue, receive


def initialize_global_variables():
    """
    Initialize variables that are constant throughout the game
    :return:
            game_window : Pygame window
            black : black color in Pygame
            white : white color in Pygame
            red : red color in Pygame
            green: green color in Pygame
            blue: blue color in Pygame
            fps_controller: frames per second controller
            difficulty: difficulty level
            frame_size_x: frame size x
            frame_size_y: frame size y
    """

    # Difficulty settings
    # Easy      ->  5
    # Medium    ->  10
    # Hard      ->  25
    # Harder    ->  40
    # Impossible->  60
    difficulty = 10

    # Window size
    frame_size_x = 720
    frame_size_y = 480

    # Checks for errors encountered
    check_errors = pygame.init()
    # pygame.init() example output -> (6, 0)
    # second number in tuple gives number of errors
    if check_errors[1] > 0:
        print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
        sys.exit(-1)
    else:
        print('[+] Game successfully initialised')

    # Initialise game window
    pygame.display.set_caption('Snake Game')
    game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
    # Colors (R, G, B)
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    red = pygame.Color(255, 0, 0)
    green = pygame.Color(0, 255, 0)
    blue = pygame.Color(0, 0, 255)
    # FPS (frames per second) controller
    fps_controller = pygame.time.Clock()
    return game_window, black, white, red, green, blue, fps_controller, difficulty, frame_size_x, frame_size_y


class SnakeGame:
    """
    Class which implements the game logic
    """

    def __init__(self):
        # Initialize global variables
        self.game_window, self.black, self.white, \
        self.red, self.green, self.blue, self.fps_controller, self.difficulty, \
        self.frame_size_x, self.frame_size_y = initialize_global_variables()
        # Connect to message broker
        self.connection, self.channel = create_queue('localhost', 'snake_game')

    def initialize_game_variables(self):
        """
        Initialize game variables
        :return:
                snake_pos: initial snake position
                snake_body : initial snake body location
                food_pos: initial food position
                food_spawn: boolean that tells if food should be spawned
                direction: initial snake direction
                change_to: initial change to direction
                score: initial score
        """
        # Game variables
        snake_pos = [100, 50]
        snake_body = [[100, 50], [100 - 10, 50], [100 - (2 * 10), 50]]
        food_pos = [random.randrange(1, (self.frame_size_x // 10)) * 10,
                    random.randrange(1, (self.frame_size_y // 10)) * 10]
        food_spawn = True
        direction = 'RIGHT'
        change_to = direction
        score = 0
        return snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score

    def game_over(self, score):
        """
        Game over menu to be displayed and control logic for retry or quit
        :return: Initial game parameters
        """
        # Display game over menu
        my_font = pygame.font.SysFont('times new roman', 90)
        game_over_surface = my_font.render('YOU DIED', True, self.red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.frame_size_x / 2, self.frame_size_y / 4)
        self.game_window.fill(self.black)
        self.game_window.blit(game_over_surface, game_over_rect)
        self.show_score(self.red, 'times', 20, score)
        self.play_again('times', 20, self.red)
        pygame.display.flip()
        # Wait for user nose movement to decide on the next action
        # If nose goes right, game is retried
        # If nose goes left, game ends
        while True:
            change_to = receive(self.channel, 'snake_game')
            if not isinstance(change_to, str):
                change_to = change_to.decode("utf-8")
            if change_to == "RIGHT":
                break
            if change_to == 'LEFT':
                self.channel.queue_delete(queue='snake_game')
                self.connection.close()
                pygame.quit()
                sys.exit()
        return self.initialize_game_variables()

    def show_score(self, color, font, size, score):
        """
        Displays user score
        :param color: font color
        :param font: font type
        :param size: font size
        :param score: player score
        :return:
        """
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render('Score : ' + str(score), True, color)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (self.frame_size_x / 10, 15)
        self.game_window.blit(score_surface, score_rect)

    def play_again(self, font, size, color):
        """
        Displays play again message in menu
        :param self:
        :param font:
        :param size:
        :param color:
        :return:
        """
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render('Slide nose right to play again | Slide nose left to quit', True, color)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (self.frame_size_x / 2, self.frame_size_y / 2)
        self.game_window.blit(score_surface, score_rect)

    def start_game(self):
        """
        Game logic
        :return:
        """
        # Initialize game variables
        snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score = self.initialize_game_variables()
        # Send start to nose detection system
        self.channel.basic_publish(exchange='', routing_key='snake_game', body='START')

        # Delay to make sure START message is received by the tracker
        time.sleep(2)
        while True:
            # Get next movement from message broker
            change_to = receive(self.channel, 'snake_game')
            if not isinstance(change_to, str):
                change_to = change_to.decode("utf-8")
            if change_to != '':
                print(change_to)

            # Making sure the snake cannot move in the opposite direction instantaneously
            if change_to == 'UP' and direction != 'DOWN':
                direction = 'UP'
            if change_to == 'DOWN' and direction != 'UP':
                direction = 'DOWN'
            if change_to == 'LEFT' and direction != 'RIGHT':
                direction = 'LEFT'
            if change_to == 'RIGHT' and direction != 'LEFT':
                direction = 'RIGHT'

            # Moving the snake
            if direction == 'UP':
                snake_pos[1] -= 10
            if direction == 'DOWN':
                snake_pos[1] += 10
            if direction == 'LEFT':
                snake_pos[0] -= 10
            if direction == 'RIGHT':
                snake_pos[0] += 10

            # Snake body growing mechanism
            snake_body.insert(0, list(snake_pos))
            if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
                score += 1
                food_spawn = False
            else:
                snake_body.pop()

            # Spawning food on the screen
            if not food_spawn:
                food_pos = [random.randrange(1, (self.frame_size_x // 10)) * 10,
                            random.randrange(1, (self.frame_size_y // 10)) * 10]
            food_spawn = True

            # GFX
            self.game_window.fill(self.black)
            for pos in snake_body:
                pygame.draw.rect(self.game_window, self.green, pygame.Rect(pos[0], pos[1], 10, 10))

            # Snake food
            pygame.draw.rect(self.game_window, self.white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

            # Game Over conditions
            # Getting out of bounds
            if snake_pos[0] < 0 or snake_pos[0] > self.frame_size_x - 10:
                snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score = self.game_over(score)
            if snake_pos[1] < 0 or snake_pos[1] > self.frame_size_y - 10:
                snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score = self.game_over(score)
            # Touching the snake body
            for block in snake_body[1:]:
                if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                    snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score = self.game_over(score)

            self.show_score(self.white, 'consolas', 20, score)
            # Refresh game screen
            pygame.display.update()
            # Refresh rate
            self.fps_controller.tick(self.difficulty)


if __name__ == "__main__":
    SnakeGame().start_game()
