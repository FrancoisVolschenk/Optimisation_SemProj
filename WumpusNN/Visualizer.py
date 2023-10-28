
from World import World, Player
from Constants import *
import pickle
from time import sleep
from NN import *

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
            x, y = 1, 1
            self.world.player = Player(self.rows, self.cols, x, y)

        if self.screen is None:
            # Create the display
            self.screen = pygame.display.set_mode((self.cols * TOKEN_SIZE, self.rows * TOKEN_SIZE))
            pygame.display.set_caption("Wumpus World")
        if self.clock is None:
            self.clock = pygame.time.Clock()

        run = True
        sleep(5) # give enough time to move to new screen
        while run:
            self.clock.tick(5)
            # sleep(1)
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
                if keys[pygame.K_UP]:
                    action = 0
                if keys[pygame.K_RIGHT]:
                    action = 1
                if keys[pygame.K_DOWN]:
                    action = 2
                if keys[pygame.K_LEFT]:
                    action = 3

                self.world.player.move(action, lstState)

            else:
                cx = self.world.player.x
                cy = self.world.player.y

                lstPercepts = []
                if (cy - 1, cx) in self.world.player.seen:
                    up = self.world.cpy_world[cy - 1][cx]
                    lstPercepts.append(1 if SAFE in up else -1)
                    lstPercepts.append(1 if DRAFT in up else -1)
                    lstPercepts.append(1 if SMELL in up else -1)
                    lstPercepts.append(1 if SHIMMER in up else -1)
                else:
                    for _ in range(4):
                        lstPercepts.append(0)
                if (cy, cx + 1) in self.world.player.seen:
                    right = self.world.cpy_world[cy][cx + 1]
                    lstPercepts.append(1 if SAFE in right else -1)
                    lstPercepts.append(1 if DRAFT in right else -1)
                    lstPercepts.append(1 if SMELL in right else -1)
                    lstPercepts.append(1 if SHIMMER in right else -1)
                else:
                    for _ in range(4):
                        lstPercepts.append(0)
                if (cy + 1, cx) in self.world.player.seen:
                    down = self.world.cpy_world[cy + 1][cx]
                    lstPercepts.append(1 if SAFE in down else -1)
                    lstPercepts.append(1 if DRAFT in down else -1)
                    lstPercepts.append(1 if SMELL in down else -1)
                    lstPercepts.append(1 if SHIMMER in down else -1)
                else:
                    for _ in range(4):
                        lstPercepts.append(0)
                if (cy, cx - 1) in self.world.player.seen:
                    left = self.world.cpy_world[cy][cx - 1]
                    lstPercepts.append(1 if SAFE in left else -1)
                    lstPercepts.append(1 if DRAFT in left else -1)
                    lstPercepts.append(1 if SMELL in left else -1)
                    lstPercepts.append(1 if SHIMMER in left else -1)
                else:
                    for _ in range(4):
                        lstPercepts.append(0)

                
                action = self.agent.decideAction(lstPercepts)
                pygame.display.set_caption(f"A: {ACTIONS_TRANSLATION[action]}")
                self.world.player.move(action, lstState)

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
        world = None
        with open("World.bin", "rb") as fp:
            world = pickle.load(fp)
        world.reset()
        vis = Visualizer(world.rows, world.cols, world.num_pits, world.num_gold, world.num_wumpi)
        vis.world = world

        agent = None
        with open("Player.bin", "rb") as fp:
            agent = pickle.load(fp)
        print(type(agent))
        vis.agent = agent
        vis.Visualize()
