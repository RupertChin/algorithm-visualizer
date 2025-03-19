import pygame
import numpy as np
import random
import time
import sys
import collections
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
MENU_HEIGHT = 100
ARRAY_HEIGHT = HEIGHT - MENU_HEIGHT
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
FONT = pygame.font.SysFont('Arial', 20)
BUTTON_FONT = pygame.font.SysFont('Arial', 16)
NODE_FONT = pygame.font.SysFont('Arial', 14)
ARRAY_SIZE = 100
FPS = 60
GRAPH_NODES = 15
NODE_RADIUS = 20

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Algorithm Visualizer')
clock = pygame.time.Clock()

# How long to delay the visualization (in seconds)
delay_time = 0.01 # Default for sorting algorithms

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hover = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        text_surf = BUTTON_FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hover = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Generate random array
def generate_array(size):
    return np.random.randint(10, ARRAY_HEIGHT - 10, size)

# Draw the array as rectangles
def draw_array(array, highlighted=None, color_updates=None):
    screen.fill(WHITE)
    bar_width = (WIDTH // len(array)) - 1
    
    for i, height in enumerate(array):
        color = RED if highlighted and i in highlighted else BLUE
        if color_updates and i in color_updates:
            color = color_updates[i]
            
        x = i * (bar_width + 1)
        y = HEIGHT - height
        pygame.draw.rect(screen, color, (x, y, bar_width, height))
        

# Generate a random graph
def generate_graph(num_nodes):
    # Create nodes in a more circular arrangement to reduce crossings
    nodes = {}
    center_x, center_y = WIDTH // 2, ARRAY_HEIGHT // 2
    radius = min(center_x, center_y) - NODE_RADIUS * 3
    
    # Place nodes in a circular pattern
    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        # Add some randomness to avoid perfect circle
        x += random.randint(-radius//4, radius//4)
        y += random.randint(-radius//4, radius//4)
        # Ensure nodes stay within boundaries
        x = max(NODE_RADIUS * 2, min(WIDTH - NODE_RADIUS * 2, x))
        y = max(NODE_RADIUS * 2, min(ARRAY_HEIGHT - NODE_RADIUS * 2, y))
        nodes[i] = {'pos': (x, y), 'connections': []}
    
    # Create edges (connections between nodes)
    # Prefer connecting nearby nodes to reduce long crossing edges
    for i in range(num_nodes):
        # Calculate distances to all other nodes
        distances = []
        for j in range(num_nodes):
            if i != j:
                dist = math.sqrt((nodes[i]['pos'][0] - nodes[j]['pos'][0])**2 + 
                                (nodes[i]['pos'][1] - nodes[j]['pos'][1])**2)
                distances.append((j, dist))
        
        # Sort by distance
        distances.sort(key=lambda x: x[1])
        
        # Connect to 1-2 nearest neighbors
        num_connections = random.randint(1, 2)
        for j in range(min(num_connections, len(distances))):
            neighbor = distances[j][0]
            if neighbor not in nodes[i]['connections']:
                nodes[i]['connections'].append(neighbor)
                nodes[neighbor]['connections'].append(i)
    
    # Ensure graph is connected by creating a spanning tree
    connected = {0}  # Start with node 0
    unconnected = set(range(1, num_nodes))
    
    while unconnected:
        connect_from = random.choice(list(connected))
        connect_to = random.choice(list(unconnected))
        
        # Add connection between these nodes
        nodes[connect_from]['connections'].append(connect_to)
        nodes[connect_to]['connections'].append(connect_from)
        
        # Mark as connected
        connected.add(connect_to)
        unconnected.remove(connect_to)
    
    # Select random start and end nodes that are reasonably far apart
    start_candidates = list(range(num_nodes))
    start_node = random.choice(start_candidates)
    
    # Find nodes far from start node
    distances = []
    for i in range(num_nodes):
        if i != start_node:
            dist = math.sqrt((nodes[start_node]['pos'][0] - nodes[i]['pos'][0])**2 + 
                            (nodes[start_node]['pos'][1] - nodes[i]['pos'][1])**2)
            distances.append((i, dist))
    
    # Sort by distance (descending)
    distances.sort(key=lambda x: x[1], reverse=True)
    
    # Choose one of the farthest nodes as end node
    end_candidates = [distances[i][0] for i in range(min(3, len(distances)))]
    end_node = random.choice(end_candidates)
    
    return nodes, start_node, end_node

# Draw the graph
def draw_graph(nodes, start_node, end_node, visited=None, current=None, path=None):
    screen.fill(WHITE)
    
    # Draw edges first
    for node_id, data in nodes.items():
        x1, y1 = data['pos']
        for conn in data['connections']:
            x2, y2 = nodes[conn]['pos']
            pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)
    
    # Draw nodes
    for node_id, data in nodes.items():
        x, y = data['pos']
        color = BLUE  # Default color
        
        # Determine node color based on status
        if visited and node_id in visited:
            color = ORANGE  # Visited node
        if path and node_id in path:
            color = GREEN  # Path node
        if current and node_id == current:
            color = RED  # Current node being processed
        if node_id == start_node:
            color = PURPLE  # Start node
        if node_id == end_node:
            color = YELLOW  # End node
        
        pygame.draw.circle(screen, color, (x, y), NODE_RADIUS)
        pygame.draw.circle(screen, BLACK, (x, y), NODE_RADIUS, 2)
        
        # Draw node ID
        text = NODE_FONT.render(str(node_id), True, BLACK)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
    
    # Draw a line separating the graph from menu
    pygame.draw.line(screen, BLACK, (0, ARRAY_HEIGHT), (WIDTH, ARRAY_HEIGHT), 2)

# Visualization delay
def delay():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                raise Exception("Exit Algorithm")
    pygame.display.update()
    time.sleep(delay_time)  # Longer delay for search visualization
    return False

# Sorting algorithms
def bubble_sort(array):
    n = len(array)
    for i in range(n):
        for j in range(0, n-i-1):
            draw_array(array, highlighted=[j, j+1])
            delay()
            if array[j] > array[j+1]:
                array[j], array[j+1] = array[j+1], array[j]
                draw_array(array, highlighted=[j, j+1])
                delay()
    draw_array(array, color_updates={i: GREEN for i in range(len(array))})
    delay()
    return array

def insertion_sort(array):
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        while j >= 0 and array[j] > key:
            array[j+1] = array[j]
            draw_array(array, highlighted=[j, j+1])
            delay()
            j -= 1
        array[j+1] = key
        draw_array(array, highlighted=[j+1])
        delay()
    draw_array(array, color_updates={i: GREEN for i in range(len(array))})
    delay()
    return array

def merge_sort_visualization(array, start, end):
    if end <= start:
        return

    mid = start + (end - start) // 2
    merge_sort_visualization(array, start, mid)
    merge_sort_visualization(array, mid + 1, end)
    
    # Merge operation
    temp = np.copy(array[start:end+1])
    i, j, k = 0, mid - start + 1, start
    
    while i <= mid - start and j <= end - start:
        draw_array(array, highlighted=[start + i, start + j])
        delay()
        
        if temp[i] <= temp[j]:
            array[k] = temp[i]
            i += 1
        else:
            array[k] = temp[j]
            j += 1
            
        draw_array(array, highlighted=[k])
        delay()
        k += 1
    
    while i <= mid - start:
        array[k] = temp[i]
        draw_array(array, highlighted=[k])
        delay()
        i += 1
        k += 1
        
    while j <= end - start:
        array[k] = temp[j]
        draw_array(array, highlighted=[k])
        delay()
        j += 1
        k += 1

def merge_sort(array):
    temp_array = np.copy(array)
    merge_sort_visualization(temp_array, 0, len(temp_array) - 1)
    draw_array(temp_array, color_updates={i: GREEN for i in range(len(temp_array))})
    delay()
    return temp_array

def quick_sort_visualization(array, low, high):
    if low < high:
        pivot_idx = partition(array, low, high)
        quick_sort_visualization(array, low, pivot_idx - 1)
        quick_sort_visualization(array, pivot_idx + 1, high)

def partition(array, low, high):
    pivot = array[high]
    i = low - 1
    
    for j in range(low, high):
        draw_array(array, highlighted=[j, high])
        delay()
        
        if array[j] <= pivot:
            i += 1
            array[i], array[j] = array[j], array[i]
            draw_array(array, highlighted=[i, j])
            delay()
    
    array[i+1], array[high] = array[high], array[i+1]
    draw_array(array, highlighted=[i+1, high])
    delay()
    
    return i + 1

def quick_sort(array):
    temp_array = np.copy(array)
    quick_sort_visualization(temp_array, 0, len(temp_array) - 1)
    draw_array(temp_array, color_updates={i: GREEN for i in range(len(temp_array))})
    delay()
    return temp_array

# Search algorithms
def bfs(nodes, start, end):
    queue = collections.deque([start])
    visited = {start}
    parent = {start: None}
    
    while queue:
        node = queue.popleft()
        
        # Visualize current state
        path = reconstruct_path(parent, start, node)
        draw_graph(nodes, start, end, visited, node, path)
        delay()
        
        if node == end:
            path = reconstruct_path(parent, start, end)
            draw_graph(nodes, start, end, visited, None, path)
            delay()
            return path
        
        for neighbor in nodes[node]['connections']:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                queue.append(neighbor)
    
    # No path found
    draw_graph(nodes, start, end, visited)
    delay()
    return None

def dfs(nodes, start, end):
    stack = [start]
    visited = {start}
    parent = {start: None}
    
    while stack:
        node = stack.pop()
        
        # Visualize current state
        path = reconstruct_path(parent, start, node)
        draw_graph(nodes, start, end, visited, node, path)
        delay()
        
        if node == end:
            path = reconstruct_path(parent, start, end)
            draw_graph(nodes, start, end, visited, None, path)
            delay()
            return path
        
        for neighbor in reversed(nodes[node]['connections']):  # Reverse for visual consistency
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                stack.append(neighbor)
    
    # No path found
    draw_graph(nodes, start, end, visited)
    delay()
    return None

def reconstruct_path(parent, start, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent.get(current)
    return path[::-1]  # Reverse to get path from start to end

# Main loop
def main():
    global delay_time

    array = generate_array(ARRAY_SIZE)
    nodes, start_node, end_node = generate_graph(GRAPH_NODES)
    
    # Define buttons
    button_width, button_height = 120, 40
    button_y = ARRAY_HEIGHT + (MENU_HEIGHT - button_height) // 2
    padding = 10
    
    # Create a grid of buttons (2 rows, 4 columns)
    button_margin = 20
    grid_width = 4  # 4 buttons per row
    grid_height = 2  # 2 rows
    button_width = (WIDTH - (grid_width + 1) * button_margin) // grid_width
    
    buttons = []
    button_texts = ["Bubble Sort", "Insertion Sort", "Merge Sort", "Quick Sort", 
                   "BFS Search", "DFS Search", "New Array", "Exit"]
    
    for i, text in enumerate(button_texts):
        row = i // grid_width
        col = i % grid_width
        x = button_margin + col * (button_width + button_margin)
        y = 50 + button_margin + row * (button_height + button_margin)
        buttons.append(Button(x, y, button_width, button_height, text, GRAY, (180, 180, 180)))
    
    running = True
    current_screen = 0 # 0: Main menu, 1: Sorting visualization 
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        if current_screen == 0:
            screen.fill(WHITE)

            # Draw title
            title = FONT.render("Algorithm Visualizer - Select an Algorithm", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, 20))
            screen.blit(title, title_rect)
            
            # Draw buttons
            for button in buttons:
                button.check_hover(mouse_pos)
                button.draw(screen)
                
                # Check if button is clicked
                if button.is_clicked(mouse_pos, click):
                    current_screen = 1
                    
                    try:
                        if button.text == "Bubble Sort":
                            delay_time = 0.01
                            draw_array(array)
                            bubble_sort(np.copy(array))
                        elif button.text == "Insertion Sort":
                            delay_time = 0.01
                            draw_array(array)
                            insertion_sort(np.copy(array))
                        elif button.text == "Merge Sort":
                            delay_time
                            draw_array(array)
                            merge_sort(array)
                        elif button.text == "Quick Sort":
                            delay_time = 0.01
                            draw_array(array)
                            quick_sort(array)
                        elif button.text == "BFS Search":
                            delay_time = 0.5
                            draw_graph(nodes, start_node, end_node)
                            bfs(nodes, start_node, end_node)
                        elif button.text == "DFS Search":
                            delay_time = 0.5
                            draw_graph(nodes, start_node, end_node)
                            dfs(nodes, start_node, end_node)
                        elif button.text == "New Data":
                            array = generate_array(ARRAY_SIZE)
                            nodes, start_node, end_node = generate_graph(GRAPH_NODES)
                        elif button.text == "Exit":
                            running = False
                    except Exception as e:
                        # Return to main selection screen when 'q' is pressed
                        pass
                    current_screen = 0
        
        pygame.display.update()
        clock.tick(FPS)

# Run the program
if __name__ == "__main__":
    main()
    pygame.quit()