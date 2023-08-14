import pygame
import pretty_midi
import sys
import math

# Initialize pygame
pygame.init()

# Constants
SIDE_LENGTH = 800  # Square side length
WIDTH, HEIGHT = SIDE_LENGTH, SIDE_LENGTH
BACKGROUND_COLOR = (0, 0, 0)
MIN_SQUARE_SIZE = 10
SPACE_BETWEEN_DOTS = 35
LIGHT_GRID_COLOR = (220, 220, 220)
MIN_FADE_TIME = 0.5  # minimum fade time in seconds

DRAW_TRACK_NUMBERS = False  # Use this boolean to turn on/off drawing track numbers
USE_COLOR = True  # Use this boolean to turn on/off color coding the squares
DRAW_GRID = False

# Load MIDI file into PrettyMIDI object
midi_path = '20210906-BrunchFull.mid'
midi_data = pretty_midi.PrettyMIDI(midi_path)

# Extract track-wise notes and their timings
track_count = len(midi_data.instruments)
events = []

max_velocity = 0
for idx, instrument in enumerate(midi_data.instruments):
    for note in instrument.notes:
        max_velocity = max(max_velocity, note.velocity)
        start_time = note.start
        end_time = note.end
        events.append((start_time, 'on', idx, note.velocity, max(end_time - start_time, MIN_FADE_TIME)))
        events.append((end_time, 'off', idx))

# Sort events by time
events.sort(key=lambda x: x[0])

# Calculate grid layout for a square
grid_size = math.ceil(math.sqrt(track_count))
grid_width = grid_size * SPACE_BETWEEN_DOTS
grid_height = grid_width  # Making it square

# Adjusted starting positions to center the grid
start_x = (WIDTH - grid_width) // 2
start_y = (HEIGHT - grid_height) // 2

# Function to get a color based on the track number
def get_color_for_track(track_num):
    return (track_num * 50 % 255, track_num * 30 % 255, track_num * 70 % 255)

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
        for i in range(grid_size + 1):
            pygame.draw.line(screen, LIGHT_GRID_COLOR, (start_x, start_y + i * SPACE_BETWEEN_DOTS), 
                            (start_x + grid_width, start_y + i * SPACE_BETWEEN_DOTS))
        for j in range(grid_size + 1):
            pygame.draw.line(screen, LIGHT_GRID_COLOR, (start_x + j * SPACE_BETWEEN_DOTS, start_y), 
                            (start_x + j * SPACE_BETWEEN_DOTS, start_y + grid_height))

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

        col = idx % grid_size
        row = idx // grid_size
        square_size = MIN_SQUARE_SIZE + velocity / 128 * 15
        color = get_color_for_track(idx) if USE_COLOR else (255, 255, 255)
        faded_color = tuple([int(c * (1 - fade_factor)) for c in color])

        # Calculate centered positions for squares within the grid cell
        x_pos = start_x + col * SPACE_BETWEEN_DOTS + (SPACE_BETWEEN_DOTS - square_size) / 2
        y_pos = start_y + row * SPACE_BETWEEN_DOTS + (SPACE_BETWEEN_DOTS - square_size) / 2

        pygame.draw.rect(screen, faded_color, (x_pos, y_pos, square_size, square_size))

        if DRAW_TRACK_NUMBERS:
            font = pygame.font.SysFont(None, 25)
            text_surface = font.render(str(idx), True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x_pos + square_size / 2, y_pos + square_size / 2))
            screen.blit(text_surface, text_rect.topleft)

        active_tracks[idx] = (velocity, fade_time + elapsed_time, duration)  # increment fade_time by elapsed_time

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
