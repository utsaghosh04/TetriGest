# -*- coding: utf-8 -*-
# Hello ! Myself Utsa Ghosh ... Hope you enjoy playing this game ...
import pygame
import random
import sys
from tetris_gesture_control import HandGestureController

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
SCREEN_WIDTH = BOARD_WIDTH * BLOCK_SIZE + 300
SCREEN_HEIGHT = 600

# Define arrow symbols
ASCII_ARROWS = {
    'LEFT': '<<',
    'RIGHT': '>>',
    'UP': '/\\',
    'DOWN': '\\/',
    'SPACE': '_|_'
}

# Define colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
GRID_COLOR = (50, 50, 50)

# Bright, distinct colors for tetris pieces
PIECE_COLORS = [
    (255, 50, 50),    # Bright Red
    (50, 255, 50),    # Bright Green
    (50, 50, 255),    # Bright Blue
    (255, 255, 50),   # Bright Yellow
    (255, 50, 255),   # Bright Magenta
    (50, 255, 255),   # Bright Cyan
]

# Define tetromino shapes using 2D arrays
TETROMINO_SHAPES = [
    [[1, 1, 1, 1]],           # I piece
    [[1, 1], [1, 1]],         # O piece
    [[1, 1, 1], [0, 1, 0]],   # T piece
    [[1, 1, 1], [1, 0, 0]],   # L piece
    [[1, 1, 1], [0, 0, 1]],   # J piece
    [[1, 1, 0], [0, 1, 1]],   # S piece
    [[0, 1, 1], [1, 1, 0]]    # Z piece
]

class Tetris:
    def __init__(self):
        """Initialize the game state"""
        self.reset()
        
    def reset(self):
        """Reset the game to initial state"""
        # Create empty game board
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.view_offset = 0  # For scrolling view
        self.spawn_new_piece()
        
    def spawn_new_piece(self):
        """Create and position a new falling piece"""
        self.current_piece = random.choice(TETROMINO_SHAPES)
        self.current_color = random.randint(0, len(PIECE_COLORS) - 1)
        # Center the piece horizontally
        self.piece_x = BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        
        # Calculate ghost piece position (preview of where piece will land)
        self.ghost_y = self.piece_y
        while not self.check_collision(self.piece_x, self.ghost_y + 1, self.current_piece):
            self.ghost_y += 1
            
        # Check if new piece overlaps with existing pieces (game over condition)
        if self.check_collision(self.piece_x, self.piece_y, self.current_piece):
            self.game_over = True
            
    def check_collision(self, x, y, piece):
        """Check if piece collides with board boundaries or other pieces"""
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    # Check boundaries and existing pieces
                    if (board_x < 0 or board_x >= BOARD_WIDTH or 
                        board_y >= BOARD_HEIGHT or 
                        (board_y >= 0 and self.board[board_y][board_x])):
                        return True
        return False
        
    def move_piece(self, dx):
        """Move piece horizontally if no collision"""
        if not self.check_collision(self.piece_x + dx, self.piece_y, self.current_piece):
            self.piece_x += dx
            # Update ghost piece position after movement
            self.ghost_y = self.piece_y
            while not self.check_collision(self.piece_x, self.ghost_y + 1, self.current_piece):
                self.ghost_y += 1
            
    def rotate_piece(self):
        """Rotate piece if rotation is possible"""
        # Create rotated version of piece
        rotated = list(zip(*reversed(self.current_piece)))
        rotated = [list(row) for row in rotated]
        if not self.check_collision(self.piece_x, self.piece_y, rotated):
            self.current_piece = rotated
            # Update ghost piece position after rotation
            self.ghost_y = self.piece_y
            while not self.check_collision(self.piece_x, self.ghost_y + 1, self.current_piece):
                self.ghost_y += 1
            
    def drop_piece(self):
        """Move piece down one step, return False if piece is locked"""
        if not self.check_collision(self.piece_x, self.piece_y + 1, self.current_piece):
            self.piece_y += 1
            return True
        else:
            self.lock_piece()
            self.spawn_new_piece()
            return False
            
    def lock_piece(self):
        """Lock the current piece in place and check for completed lines"""
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    if 0 <= self.piece_y + y < BOARD_HEIGHT:
                        self.board[self.piece_y + y][self.piece_x + x] = self.current_color + 1
        self.clear_lines()
        
    def clear_lines(self):
        """Remove completed lines and update score"""
        lines_cleared = 0
        for y in range(BOARD_HEIGHT):
            if all(self.board[y]):
                lines_cleared += 1
                del self.board[y]
                self.board.insert(0, [0] * BOARD_WIDTH)
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * 100 * self.level
            self.level = self.lines_cleared // 10 + 1

    def draw_grid(self, screen):
        """Draw the game grid"""
        # Draw vertical grid lines
        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(screen, GRID_COLOR, 
                           (x * BLOCK_SIZE, 0),
                           (x * BLOCK_SIZE, SCREEN_HEIGHT))

        # Draw horizontal grid lines
        visible_start = self.view_offset
        visible_end = min(BOARD_HEIGHT, self.view_offset + 30)
        for y in range(visible_start, visible_end + 1):
            screen_y = (y - self.view_offset) * BLOCK_SIZE
            pygame.draw.line(screen, GRID_COLOR,
                           (0, screen_y),
                           (BOARD_WIDTH * BLOCK_SIZE, screen_y))
            
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw game border
        border_padding = 5
        pygame.draw.rect(screen, WHITE, 
                        (-border_padding, -border_padding, 
                         BOARD_WIDTH * BLOCK_SIZE + 2*border_padding, 
                         SCREEN_HEIGHT + 2*border_padding), 2)
        
        self.draw_grid(screen)
        
        # Draw ghost piece
        if not self.game_over:
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        ghost_color = (PIECE_COLORS[self.current_color][0] // 4,
                                     PIECE_COLORS[self.current_color][1] // 4,
                                     PIECE_COLORS[self.current_color][2] // 4)
                        pygame.draw.rect(screen, ghost_color,
                                       ((self.piece_x + x) * BLOCK_SIZE + 1,
                                        (self.ghost_y - self.view_offset + y) * BLOCK_SIZE + 1,
                                        BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # Draw board
        visible_start = max(0, self.view_offset)
        visible_end = min(BOARD_HEIGHT, self.view_offset + 30)
        
        for y in range(visible_start, visible_end):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    color = PIECE_COLORS[self.board[y][x] - 1]
                    pygame.draw.rect(screen, color,
                                   (x * BLOCK_SIZE + 1,
                                    (y - self.view_offset) * BLOCK_SIZE + 1,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                    
        # Draw current piece
        if not self.game_over:
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, PIECE_COLORS[self.current_color],
                                       ((self.piece_x + x) * BLOCK_SIZE + 1,
                                        (self.piece_y - self.view_offset + y) * BLOCK_SIZE + 1,
                                        BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        
        # Draw side panel
        panel_x = BOARD_WIDTH * BLOCK_SIZE + 20
        panel_width = SCREEN_WIDTH - panel_x - 10
        
        # Draw panel background
        pygame.draw.rect(screen, GRAY,
                        (panel_x - 10, 0, panel_width + 10, SCREEN_HEIGHT))
        
        # Draw game info
        header_font = pygame.font.Font(None, 32)
        normal_font = pygame.font.Font(None, 28)
        
        # Game stats section
        y_pos = 20
        stats = [
            ("SCORE", str(self.score)),
            ("LEVEL", str(self.level)),
            ("LINES", str(self.lines_cleared))
        ]
        
        for header, value in stats:
            box_height = 60
            pygame.draw.rect(screen, (60, 60, 60),
                           (panel_x, y_pos, panel_width - 20, box_height))
            
            header_text = header_font.render(header, True, (200, 200, 200))
            value_text = header_font.render(value, True, (255, 255, 0))
            
            header_x = panel_x + (panel_width - 20 - header_text.get_width()) // 2
            value_x = panel_x + (panel_width - 20 - value_text.get_width()) // 2
            
            screen.blit(header_text, (header_x, y_pos + 8))
            screen.blit(value_text, (value_x, y_pos + 32))
            
            y_pos += box_height + 8
        
        # Controls section
        y_pos += 15
        controls_header = header_font.render("CONTROLS", True, (255, 255, 0))
        header_x = panel_x + (panel_width - 20 - controls_header.get_width()) // 2
        screen.blit(controls_header, (header_x, y_pos))
        
        y_pos += 35
        
        # Draw control box
        control_box_height = 200
        pygame.draw.rect(screen, (60, 60, 60),
                        (panel_x, y_pos, panel_width - 20, control_box_height))
        
        # Draw controls
        controls = [
            (ASCII_ARROWS['LEFT'], "Move Left"),
            (ASCII_ARROWS['RIGHT'], "Move Right"),
            (ASCII_ARROWS['UP'], "Rotate"),
            (ASCII_ARROWS['DOWN'], "Soft Drop"),
            (ASCII_ARROWS['SPACE'], "Hard Drop"),
            ("R", "Reset Game"),
            ("Q", "Quit Game")
        ]
        
        y_pos += 15
        for symbol, action in controls:
            # Create a small box for the symbol
            symbol_box_width = 50  # Increased width for new symbols
            pygame.draw.rect(screen, (80, 80, 80),
                           (panel_x + 15, y_pos - 5, 
                            symbol_box_width, 30))
            
            # Draw symbol in box
            symbol_text = header_font.render(symbol, True, (255, 255, 0))
            action_text = normal_font.render(action, True, WHITE)
            
            # Center symbol in its box
            symbol_x = panel_x + 15 + (symbol_box_width - symbol_text.get_width()) // 2
            screen.blit(symbol_text, (symbol_x, y_pos))
            
            # Draw action text after the symbol box
            screen.blit(action_text, (panel_x + symbol_box_width + 25, y_pos + 5))
            
            y_pos += 27
        
        # Game Over message
        if self.game_over:
            game_over_font = pygame.font.Font(None, 48)
            game_over_text = game_over_font.render('GAME OVER', True, (255, 0, 0))
            text_x = panel_x + (panel_width - 20 - game_over_text.get_width()) // 2
            text_y = SCREEN_HEIGHT - 100
            
            pygame.draw.rect(screen, (60, 60, 60),
                           (panel_x, text_y - 8, 
                            panel_width - 20, game_over_text.get_height() + 16))
            screen.blit(game_over_text, (text_x, text_y))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    game = Tetris()
    
    # Initialize hand gesture controller
    controller = HandGestureController()
    
    fall_time = 0
    
    try:
        while True:
            # Calculate fall speed based on level
            fall_speed = max(50 - (game.level * 3), 10)
            
            # Get gesture command
            command = controller.get_finger_position()
            
            # Handle gesture commands
            if not game.game_over:
                if command == "LEFT":
                    game.move_piece(-1)
                elif command == "RIGHT":
                    game.move_piece(1)
                elif command == "ROTATE":
                    game.rotate_piece()
                elif command == "DOWN":
                    game.drop_piece()
            
            # Handle keyboard events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return
                    if not game.game_over:
                        if event.key == pygame.K_LEFT:
                            game.move_piece(-1)
                        elif event.key == pygame.K_RIGHT:
                            game.move_piece(1)
                        elif event.key == pygame.K_UP:
                            game.rotate_piece()
                        elif event.key == pygame.K_DOWN:
                            game.drop_piece()
                        elif event.key == pygame.K_SPACE:
                            while game.drop_piece():
                                pass
                    elif event.key == pygame.K_r:
                        game.reset()
            
            # Regular game updates
            if not game.game_over:
                fall_time += 1
                if fall_time >= fall_speed:
                    game.drop_piece()
                    fall_time = 0
            
            # Update view offset
            if game.piece_y >= 25:
                game.view_offset = max(0, min(game.piece_y - 20, BOARD_HEIGHT - 30))
            else:
                game.view_offset = 0
            
            # Draw game
            game.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main() 
