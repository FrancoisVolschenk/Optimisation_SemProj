import random

ROWS = 20
COLS = 20

world = [
    [".", ".", ".", "P", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "P", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", "W", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "W", "."],
    [".", ".", ".", ".", "G", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", "P", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "P", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", "P", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", "G", ".", ".", ".", ".", ".", ".", "G", ".", ".", ".", ".", ".", ".", "G", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "P", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", "P", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", "G", ".", ".", ".", ".", ".", ".", ".", "P", ".", ".", ".", ".", ".", ".", ".", "."],
    [".", "W", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "W", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    ["G", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
]

ACTIONS = ["U", "D", "L", "R"]

def copy_world(world):
    lstRet = []
    for r in range(ROWS):
        lstRet.append([])
        for c in range(COLS):
            lstRet[r].append(world[r][c])
    return lstRet

def gen_indiv(size):
    return [random.choice(ACTIONS) for _ in range(size)]

POP_SIZE = 50
NUM_GENS = 100

def mutate(individual):
    if random.random() < 0.5:
        for i in range(len(individual)):
            individual[i] = random.choice(ACTIONS)
    else:
        for r in range(random.randint(0, 5)):
            individual.append(random.choice(ACTIONS))

def crossover(population):
    new_gen = []
    new_gen.append(population[0][1])

    index = 0
    while len(new_gen) < POP_SIZE:
        p1 = population[index][1]
        index += 1
        p2 = population[index][1]

        max_p = min(len(p1), len(p2))
        c_point = random.randint(0, max_p)

        off1 = p1[:c_point] + p2[c_point:]
        off2 = p2[:c_point] + p1[c_point:]

        mutate(off1)
        mutate(off2)

        new_gen.append(off1)
        new_gen.append(off2)

    return new_gen

size = 15
population = [gen_indiv(size) for _ in range(POP_SIZE)]
top_score = 0
# for gen in range(NUM_GENS):
while top_score < 10000:
    score_board = []
    for p in range(len(population)):
        action_ptr = -1
        run = True
        px, py = 0, 0
        score = 0
        energy = len(population[p])
        seen = set()
        play_world = copy_world(world)

        while run:
            if energy <= 0:
                run = False
                continue
            action_ptr += 1
            if action_ptr >= len(population[p]):
                run = False
                continue
            else:
                move = population[p][action_ptr]
                
                tx, ty = px, py
                if move == "U":
                    ty -= 1
                if move == "D":
                    ty += 1
                if move == "L":
                    tx -= 1
                if move == "R":
                    tx += 1

                if tx >= 0 and tx < COLS:
                    px = tx
                if ty >= 0 and ty < ROWS:
                    py = ty
                energy -= 1

                if (py, px) not in seen:
                    seen.add((py, px))
                    score += 1

                if play_world[py][px] == "W" or play_world[py][px] == "P":
                    run = False
                    score -= 10
                elif play_world[py][px] == "G":
                    score += 400
                    play_world[py][px] = "."
            golds = 0
            for r in range(ROWS):
                for c in range(COLS):
                    if play_world[r][c] == "G":
                        golds += 1
            if golds == 0:
                run = False
                score += 10000                

        score_board.append((score, population[p]))
        if score > top_score:
            top_score = score
    score_board.sort(key = lambda p: p[0], reverse=True)
    print(f"Best score {score_board[0][0]}| length: {len(score_board[0][1])}     Worst {score_board[-1][0]}")
    population = crossover(score_board)

                
            


                

