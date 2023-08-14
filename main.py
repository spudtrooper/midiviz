import pygame
import sys
import math
import midiviz

# Constants
WIDTH, HEIGHT = 1280, 720 # youtube
BACKGROUND_COLOR = (0, 0, 0)
MIN_SQUARE_SIZE = 10
SPACE_BETWEEN_DOTS = 35
LIGHT_GRID_COLOR = (30, 30, 30)

DRAW_TRACK_NUMBERS = False  # Use this boolean to turn on/off drawing track numbers
USE_COLOR = True  # Use this boolean to turn on/off color coding the squares
DRAW_GRID = False

def loop():
    # Load MIDI file into PrettyMIDI object
    midi_path = 'example/20210906-BrunchFull.mid'
    events, track_count = midiviz.load_event_data(midi_path)

    # Calculate grid layout based on 16:9 aspect ratio
    grid_columns = int(math.sqrt(track_count * 16 / 9))
    grid_rows = math.ceil(track_count / grid_columns)

    grid_width = grid_columns * SPACE_BETWEEN_DOTS
    grid_height = grid_rows * SPACE_BETWEEN_DOTS

    # Adjusted starting positions to include the padding
    start_x = (WIDTH - grid_width) // 2
    start_y = (HEIGHT - grid_height) // 2

    # Function to get a color based on the track number
    def get_color_for_track(track_num):
        return (track_num * 50 % 255, track_num * 30 % 255, track_num * 70 % 255)

    def draw_grid():
        for i in range(grid_rows + 1):
            pygame.draw.line(screen, LIGHT_GRID_COLOR, (start_x, start_y + i * SPACE_BETWEEN_DOTS), 
                            (start_x + grid_width, start_y + i * SPACE_BETWEEN_DOTS))
        for j in range(grid_columns + 1):
            pygame.draw.line(screen, LIGHT_GRID_COLOR, (start_x + j * SPACE_BETWEEN_DOTS, start_y), 
                            (start_x + j * SPACE_BETWEEN_DOTS, start_y + grid_height))

    def draw_track_numbers(x_pos, y_pos, square_size, idx):
        font = pygame.font.SysFont(None, 25)
        text_surface = font.render(str(idx), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x_pos + square_size / 2, y_pos + square_size / 2))
        screen.blit(text_surface, text_rect.topleft)

    # Pygame loop
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('MIDI Visualization')
    clock = pygame.time.Clock()
    pygame.mixer.music.load(midi_path)
    pygame.mixer.music.play()
    active_tracks = {}

    start_time = pygame.time.get_ticks()
    while True:
        screen.fill(BACKGROUND_COLOR)
        elapsed_time = clock.tick(60) / 1000.0  # converting to seconds to match MIDI timings
        current_time = (pygame.time.get_ticks() - start_time) / 1000.0

        # Drawing a light-colored grid
        if DRAW_GRID:
            draw_grid()

        while events and events[0][0] <= current_time:
            event_data = events.pop(0)
            _, event_type, track_number = event_data[:3]
            if event_type == 'on':
                velocity, duration = event_data[3], event_data[4]
                active_tracks[track_number] = (velocity, 0, duration)  # add a fade_time counter
            else:
                if track_number in active_tracks:
                    del active_tracks[track_number]

        for idx, (velocity, fade_time, duration) in list(active_tracks.items()):
            fade_factor = fade_time / duration  # fade based on how much of the note's duration has elapsed

            if fade_factor >= 1:  # if note has fully faded, remove it from active tracks
                del active_tracks[idx]
                continue

            col = idx % grid_columns
            row = idx // grid_columns
            square_size = MIN_SQUARE_SIZE + velocity / 128 * 15
            color = get_color_for_track(idx) if USE_COLOR else (255, 255, 255)
            faded_color = tuple([int(c * (1 - fade_factor)) for c in color])

            # Calculate centered positions for squares within the grid cell
            x_pos = start_x + col * SPACE_BETWEEN_DOTS + (SPACE_BETWEEN_DOTS - square_size) / 2
            y_pos = start_y + row * SPACE_BETWEEN_DOTS + (SPACE_BETWEEN_DOTS - square_size) / 2

            pygame.draw.rect(screen, faded_color, (x_pos, y_pos, square_size, square_size))

            if DRAW_TRACK_NUMBERS:
                draw_track_numbers(x_pos, y_pos, square_size, idx)

            active_tracks[idx] = (velocity, fade_time + elapsed_time, duration)  # increment fade_time by elapsed_time

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# main
pygame.init()
loop()            
