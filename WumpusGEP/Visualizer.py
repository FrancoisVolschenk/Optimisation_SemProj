
from World import World, Player
from Constants import *
import pickle
from time import sleep
from Genes import Gene
import random

class Visualizer:
    def __init__(self, rows, cols, num_pits, num_gold, num_wumpi):
        self.FONT = pygame.font.SysFont("Arial", TOKEN_SIZE, bold = True)
        self.rows = rows
        self.cols = cols
        self.screen = None
        self.clock = None
        self.agent = None

        self.world = World(rows, cols, num_pits, num_gold, num_wumpi)

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.screen.blit(COLOURS[SAFE], (c * TOKEN_SIZE, r * TOKEN_SIZE))
                # if (r, c) not in self.world.player.seen:
                #     colour = COLOURS[SHROUD]
                # else: 
                colour = COLOURS[self.world.cpy_world[r][c][-1]]

                self.screen.blit(colour, (c * TOKEN_SIZE, r * TOKEN_SIZE))
                pygame.draw.rect(self.screen, (0, 0, 0), (c * TOKEN_SIZE, r * TOKEN_SIZE, TOKEN_SIZE, TOKEN_SIZE), 1)
        self.screen.blit(COLOURS[PLAYER], (self.world.player.x * TOKEN_SIZE, self.world.player.y * TOKEN_SIZE))

    def _draw_text(self, text, colour, x, y):
        img = self.FONT.render(text, True, colour)
        self.screen.blit(img, (x, y))

    def Visualize(self):
        if self.world.tile_grid is None:
            self.world.set_map()
        if self.world.player is None:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            while SAFE not in self.world.cpy_world[y][x]:
                x = random.randint(0, self.cols - 1)
                y = random.randint(0, self.rows - 1)
            self.world.player = Player(self.rows, self.cols, x, y)

        if self.screen is None:
            # Create the display
            self.screen = pygame.display.set_mode((self.cols * TOKEN_SIZE, self.rows * TOKEN_SIZE))
            pygame.display.set_caption("Wumpus World")
        if self.clock is None:
            self.clock = pygame.time.Clock()

        run = True
        if self.agent is not None:
            gene_ptr = 0
            action_ptr = self.agent.express_tree(self.agent.chromosome[gene_ptr])
        sleep(5) # give enough time to move to new screen
        while run:
            self.clock.tick(5)
            # sleep(1)
            if self.world.player.energy <= 0:
                run = False
                print("You ran out of energy")
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            lstState = self.world.cpy_world[self.world.player.y][self.world.player.x]
            DisplayText = ""
            for s in lstState:
                DisplayText += SENSES_TRANSLATION[s] + " "
            if self.agent is None:
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

                self.world.player.move(action, lstState)

            else:
                action = action_ptr[0]
                pygame.display.set_caption(f"A: {ACTIONS_TRANSLATION.get(action, 'Sensing')}")
                adv_dir = self.world.player.move(action, lstState)
                if adv_dir == 0:
                    gene_ptr = (gene_ptr + 1) % len(self.agent.chromosome)
                    action_ptr = self.agent.express_tree(self.agent.chromosome[gene_ptr])
                else: # adv_dir is either 1 or 2
                    if adv_dir < len(action_ptr): # some safety checks
                        action_ptr = action_ptr[adv_dir]
                    else:
                        gene_ptr = (gene_ptr + 1) % len(self.agent.chromosome)
                        action_ptr = self.agent.express_tree(self.agent.chromosome[gene_ptr])
            self.world.player.energy -= 1
            self.world.eval_position()            

            state = self.world.check_state()
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
            self._draw_text(DisplayText, (255, 0, 0), 50, 50)
            pygame.display.flip()  # Update the display

        pygame.quit()

if __name__ == "__main__":
    chIn = input("Choose an option:\n(1) play the game\n(2)load a trained agent\n:")
    if chIn == "1":
        vis = Visualizer(rows = 20, cols = 15, num_pits = 2, num_gold = 3, num_wumpi = 3)
        vis.Visualize()
    else:
        # world = None
        # with open("World.bin", "rb") as fp:
        #     world = pickle.load(fp)
        # world.reset()
        vis = Visualizer(10, 15, 15, 1, 3)
        # vis.world = world

        agent = None
        with open("Player.bin", "rb") as fp:
            agent = pickle.load(fp)
        vis.agent = agent
        vis.Visualize()
