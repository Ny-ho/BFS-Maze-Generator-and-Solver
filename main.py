import pygame
import random

# --- CONFIG ---
WIDTH = 600
ROWS = 25 
CELL_SIZE = WIDTH // ROWS

# DYNAMIC SPEEDS
GEN_FPS = 120   # Fast generation
SOLVE_FPS = 20  # Slower for the 'struggle' visuals

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * CELL_SIZE
        self.y = row * CELL_SIZE
        self.walls = [True, True, True, True] # Top, Right, Bottom, Left
        self.visited = False # Used by Maze Gen
        self.queued = False  # Used by BFS
        self.parent = None   # For path reconstruction
        
    def draw(self, screen):
        if self.walls[0]: # Top
            pygame.draw.line(screen, (200, 200, 200), (self.x, self.y), (self.x + CELL_SIZE, self.y), 1)
        if self.walls[1]: # Right
            pygame.draw.line(screen, (200, 200, 200), (self.x + CELL_SIZE, self.y), (self.x + CELL_SIZE, self.y + CELL_SIZE), 1)
        if self.walls[2]: # Bottom
            pygame.draw.line(screen, (200, 200, 200), (self.x + CELL_SIZE, self.y + CELL_SIZE), (self.x, self.y + CELL_SIZE), 1)
        if self.walls[3]: # Left
            pygame.draw.line(screen, (200, 200, 200), (self.x, self.y + CELL_SIZE), (self.x, self.y), 1)

    def check_neighbours(self, grid):
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < ROWS and 0 <= c < ROWS:
                neighbor = grid[r][c]
                if not neighbor.visited:
                    neighbors.append(neighbor)
        if len(neighbors) > 0:
            return random.choice(neighbors)
        return None

# --- HELPERS ---
def remove_walls(a, b):
    x = a.col - b.col
    if x == 1: a.walls[3], b.walls[1] = False, False
    elif x == -1: a.walls[1], b.walls[3] = False, False
    y = a.row - b.row
    if y == 1: a.walls[0], b.walls[2] = False, False
    elif y == -1: a.walls[2], b.walls[0] = False, False

def get_walkable_neighbors(cell, grid):
    neighbors = []
    # Check actual wall status for pathfinding
    if not cell.walls[0] and cell.row > 0: neighbors.append(grid[cell.row - 1][cell.col])
    if not cell.walls[1] and cell.col < ROWS - 1: neighbors.append(grid[cell.row][cell.col + 1])
    if not cell.walls[2] and cell.row < ROWS - 1: neighbors.append(grid[cell.row + 1][cell.col])
    if not cell.walls[3] and cell.col > 0: neighbors.append(grid[cell.row][cell.col - 1])
    return neighbors

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("DSA: BFS Shortest Path (Multiple Routes)")
clock = pygame.time.Clock()

grid = [[Cell(r, c) for c in range(ROWS)] for r in range(ROWS)]

# States
stack = [grid[0][0]]
grid[0][0].visited = True
current = grid[0][0]

queue = [] # For BFS
visited_by_ai = []
path = []
maze_finished = False

# --- MAIN LOOP ---
running = True
while running:
    screen.fill((15, 15, 25))
    current_fps = GEN_FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. PHASE ONE: MAZE GENERATION (DFS)
    if len(stack) > 0:
        next_cell = current.check_neighbours(grid)
        if next_cell:
            next_cell.visited = True
            stack.append(current)
            remove_walls(current, next_cell)
            current = next_cell
        else:
            current = stack.pop()
        
        # Highlight generator head
        pygame.draw.rect(screen, (255, 0, 100), (current.x, current.y, CELL_SIZE, CELL_SIZE))

    # 2. PHASE TWO: BFS SOLVER (The "Struggle")
    else:
        current_fps = SOLVE_FPS
        if not maze_finished:
            # BREAK EXTRA WALLS to create multiple paths
            for _ in range(40): 
                r, c = random.randint(1, ROWS-2), random.randint(1, ROWS-2)
                grid[r][c].walls[random.randint(0, 3)] = False
            
            queue.append(grid[0][0])
            grid[0][0].queued = True
            maze_finished = True

        if len(queue) > 0 and not path:
            current_node = queue.pop(0) # BFS = FIFO (Pop from front)
            visited_by_ai.append(current_node)

            if current_node == grid[ROWS-1][ROWS-1]:
                # Found the goal! Trace back
                temp = current_node
                while temp.parent:
                    path.append(temp)
                    temp = temp.parent
                print("Shortest Path Found!")

            for neighbor in get_walkable_neighbors(current_node, grid):
                if not neighbor.queued:
                    neighbor.queued = True
                    neighbor.parent = current_node
                    queue.append(neighbor)

# --- DRAWING ---
    
    # 1. Draw every cell the AI explored (The "Brain/Noise")
    for node in visited_by_ai:
        pygame.draw.rect(screen, (60, 20, 100), (node.x, node.y, CELL_SIZE, CELL_SIZE))
    
    # 2. Draw the nodes currently waiting to be checked (The "Frontier")
    for node in queue:
        pygame.draw.rect(screen, (40, 40, 80), (node.x, node.y, CELL_SIZE, CELL_SIZE))

    # 3. Draw the shortest path (The "Signal/Winner")
    # We draw this AFTER purple so it sits on top
    for node in path:
        pygame.draw.rect(screen, (0, 255, 200), (node.x, node.y, CELL_SIZE, CELL_SIZE))

    # 4. Draw walls (Always on top so the paths look like they are inside a maze)
    for row in grid:
        for cell_obj in row:
            cell_obj.draw(screen)

    # 5. START & END BOXES (Both Gold/Yellow)
    # Start
    pygame.draw.rect(screen, (255, 200, 0), (grid[0][0].x+4, grid[0][0].y+4, CELL_SIZE-8, CELL_SIZE-8))
    # End
    pygame.draw.rect(screen, (255, 200, 0), (grid[ROWS-1][ROWS-1].x+4, grid[ROWS-1][ROWS-1].y+4, CELL_SIZE-8, CELL_SIZE-8))

    pygame.display.flip()
    clock.tick(current_fps)

pygame.quit()