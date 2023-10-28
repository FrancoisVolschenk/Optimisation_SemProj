"""
Author: F Volschenk - 219030964
This file contains code for visualizing the wumpus world. It can be played by a human, or a trained agent can be loaded in to solve the world.
"""

from World import World, Player
from Constants import *
import pickle
from time import sleep

class Visualizer:
    """ This class is in charge of displaying the state of the world and the position of the player """
    def __init__(self, rows, cols, num_pits, num_gold, num_wumpi, shroud):
        self.FONT = pygame.font.SysFont("Arial", TOKEN_SIZE, bold = True)
        self.rows = rows
        self.cols = cols
        self.screen = None
        self.clock = None
        self.agent = None
        self.shroud = shroud

        self.world = World(rows, cols, num_pits, num_gold, num_wumpi)

    def draw_grid(self):
        """ This method is used to update the display at every iteration of the game world """
        for r in range(self.rows):
            for c in range(self.cols):
                self.screen.blit(COLOURS[SAFE], (c * TOKEN_SIZE, r * TOKEN_SIZE))
                if self.shroud and (r, c) not in self.world.player.seen: # if the shroud is activated, draw darkness over unexplored spots
                    colour = COLOURS[SHROUD]
                else: 
                    colour = COLOURS[self.world.cpy_world[r][c][-1]]

                self.screen.blit(colour, (c * TOKEN_SIZE, r * TOKEN_SIZE))
                pygame.draw.rect(self.screen, (0, 0, 0), (c * TOKEN_SIZE, r * TOKEN_SIZE, TOKEN_SIZE, TOKEN_SIZE), 1)
        self.screen.blit(COLOURS[PLAYER], (self.world.player.x * TOKEN_SIZE, self.world.player.y * TOKEN_SIZE)) # The player is drawn last

    def _draw_text(self, text, colour, x, y):
        """ Place text at a specified position on the screen """
        img = self.FONT.render(text, True, colour)
        self.screen.blit(img, (x, y))

    def Visualize(self):
        """ Allow the player to navigate the world, or display the agent solving the world """
        if self.world.tile_grid is None: # if there is no world yet, create one
            self.world.set_map()
        if self.world.player is None: # If there is no player yet, create one
            x, y = 1, 1
            self.world.player = Player(self.rows, self.cols, x, y)

        if self.screen is None:
            # Create the display
            self.screen = pygame.display.set_mode((self.cols * TOKEN_SIZE, self.rows * TOKEN_SIZE))
            pygame.display.set_caption("Wumpus World")
        if self.clock is None:
            self.clock = pygame.time.Clock()

        run = True
        action_ptr = -1
        sleep(5) # give enough time to move to new screen
        while run: # Run the game loop until a terminal state is reached or the agent runs out of energy
            self.clock.tick(5)
            action_ptr += 1
            if self.agent is not None and action_ptr >= len(self.agent):
                run = False
                continue

            # If the user closes the window, exit the game 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            # Display any senses of the current square in the top left corner
            lstState = self.world.cpy_world[self.world.player.y][self.world.player.x]
            DisplayText = ""
            for s in lstState:
                DisplayText += SENSES_TRANSLATION[s] + " "
            if self.agent is None: # This means that a user is playing the game
                keys = pygame.key.get_pressed()

                action = None
                # Move the player
                if keys[pygame.K_LEFT]:
                    action = "L"
                if keys[pygame.K_RIGHT]:
                    action = "R"
                if keys[pygame.K_UP]:
                    action = "U"
                if keys[pygame.K_DOWN]:
                    action = "D"

                self.world.player.move(action)

            else: # get the action from the agent 
                action = self.agent[action_ptr]
                pygame.display.set_caption(f"A: {ACTIONS_TRANSLATION[action]}")
                self.world.player.move(action)

            self.world.eval_position()  # determine if the player has collected gold           

            state = self.world.check_state() # determine if a terminal state has been reached 
            if self.world.player.energy <= 0:
                run = False
            if state != ENDSTATES["NOT_DONE"]:
                run = False
                if state == ENDSTATES["WON"]:
                    print("You Won")
                if state == ENDSTATES["WUMPUS"]:
                    print("You were eaten by a wumpus")
                if state == ENDSTATES["PIT"]:
                    print("You fell into a pit")

            self.screen.fill((0, 0, 0))  # Clear the screen
            self.draw_grid()  # Draw the grid and player
            self._draw_text(DisplayText, (255, 0, 0), 50, 50) # display the senses of the current space
            pygame.display.flip()  # Update the display

        pygame.quit()

if __name__ == "__main__":
    chPlay = input("Choose an option:\n(1) play the game\n(2)load a trained agent\n:")
    chMode = input("Would you like to turn on the shroud?(y/n)\n:")[0].upper() == "Y"
    if chPlay == "1":
        vis = Visualizer(rows = 20, cols = 15, num_pits = 2, num_gold = 3, num_wumpi = 3, shroud = chMode)
        vis.Visualize()
    else:
        world = None
        with open("World.bin", "rb") as fp:
            world = pickle.load(fp)
        world.reset()
        vis = Visualizer(world.rows, world.cols, world.num_pits, world.num_gold, world.num_wumpi, shroud = chMode)
        vis.world = world

        agent = []
        with open("Player.txt", "r") as fp:
            for action in fp:
                agent.append(action.strip())
        vis.agent = agent
        vis.Visualize()
