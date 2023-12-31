import pygame
import squares
import sys
import midiviz

def loop(clock, events, screen, start_time):
  while True:
      elapsed_time = clock.tick(60) / 1000.0  # converting to seconds to match MIDI timings
      current_time = (pygame.time.get_ticks() - start_time) / 1000.0

      o.each(screen, events, current_time, elapsed_time)

      pygame.display.flip()

      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              return
              
def run(midi_path, o):
    events, track_count = midiviz.load_event_data(midi_path)
    o.init(events, track_count)
    screen, clock = midiviz.start_game(midi_path, o.width(), o.height())
    start_time = pygame.time.get_ticks()
    
    loop(clock, events, screen, start_time)

    pygame.quit()
    sys.exit()
    
pygame.init()
# midi_path = 'example/20210906-BrunchFull.mid'
midi_path = 'data/smoke2.mid'
o = squares.Squares()
run(midi_path, o)
