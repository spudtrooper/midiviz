import pygame
import math

# Constants
WIDTH, HEIGHT = 1280, 720 # youtube
BACKGROUND_COLOR = (0, 0, 0)
MIN_SQUARE_SIZE = 10
SPACE_BETWEEN_DOTS = 35
LIGHT_GRID_COLOR = (30, 30, 30)

DRAW_TRACK_NUMBERS = False  # Use this boolean to turn on/off drawing track numbers
USE_COLOR = True  # Use this boolean to turn on/off color coding the squares
DRAW_GRID = False

class Squares(object):
    
    def width(self):
        return WIDTH
    
    def height(self):
        return HEIGHT
    
    def each(self, screen, events, current_time, elapsed_time):
        screen.fill(BACKGROUND_COLOR)

        # Drawing a light-colored grid
        if DRAW_GRID:
            self._draw_grid()

        while events and events[0][0] <= current_time:
            event_data = events.pop(0)
            _, event_type, track_number = event_data[:3]
            if event_type == 'on':
                velocity, duration = event_data[3], event_data[4]
                self.active_tracks[track_number] = (velocity, 0, duration)  # add a fade_time counter
            else:
                if track_number in self.active_tracks:
                    del self.active_tracks[track_number]

        for idx, (velocity, fade_time, duration) in list(self.active_tracks.items()):
            fade_factor = fade_time / duration  # fade based on how much of the note's duration has elapsed

            if fade_factor >= 1:  # if note has fully faded, remove it from active tracks
                del self.active_tracks[idx]
                continue

            col = idx % self.grid_columns
            row = idx // self.grid_columns
            square_size = MIN_SQUARE_SIZE + velocity / 128 * 15
            color = self._get_color_for_track(idx) if USE_COLOR else (255, 255, 255)
            faded_color = tuple([int(c * (1 - fade_factor)) for c in color])

            # Calculate centered positions for squares within the grid cell
            x_pos = self.start_x + col * SPACE_BETWEEN_DOTS + (SPACE_BETWEEN_DOTS - square_size) / 2
            y_pos = self.start_y + row * SPACE_BETWEEN_DOTS + (SPACE_BETWEEN_DOTS - square_size) / 2

            pygame.draw.rect(screen, faded_color, (x_pos, y_pos, square_size, square_size))

            if DRAW_TRACK_NUMBERS:
                self._draw_track_numbers(x_pos, y_pos, square_size, idx)

            self.active_tracks[idx] = (velocity, fade_time + elapsed_time, duration)  # increment fade_time by elapsed_time
    
    def init(self, events, track_count):
        # Calculate grid layout based on 16:9 aspect ratio
        self.grid_columns = int(math.sqrt(track_count * 16 / 9))
        self.grid_rows = math.ceil(track_count / self.grid_columns)

        self.grid_width = self.grid_columns * SPACE_BETWEEN_DOTS
        self.grid_height = self.grid_rows * SPACE_BETWEEN_DOTS

        # Adjusted starting positions to include the padding
        self.start_x = (WIDTH - self.grid_width) // 2
        self.start_y = (HEIGHT - self.grid_height) // 2    

        self.active_tracks = {}

    # Function to get a color based on the track number
    def _get_color_for_track(self, track_num):
        return (track_num * 50 % 255, track_num * 30 % 255, track_num * 70 % 255)

    def _draw_grid(self, screen):
        for i in range(self.grid_rows + 1):
            pygame.draw.line(screen, LIGHT_GRID_COLOR, (self.start_x, self.start_y + i * SPACE_BETWEEN_DOTS), 
                            (self.start_x + self.grid_width, self.start_y + i * SPACE_BETWEEN_DOTS))
        for j in range(self.grid_columns + 1):
            pygame.draw.line(screen, LIGHT_GRID_COLOR, (self.start_x + j * SPACE_BETWEEN_DOTS, start_y), 
                            (self.start_x + j * SPACE_BETWEEN_DOTS, self.start_y + self.grid_height))

    def _draw_track_numbers(self, screen, x_pos, y_pos, square_size, idx):
        font = pygame.font.SysFont(None, 25)
        text_surface = font.render(str(idx), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x_pos + square_size / 2, y_pos + square_size / 2))
        screen.blit(text_surface, text_rect.topleft)