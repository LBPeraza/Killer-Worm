import pygame, sys

class PygameGame(object):
    ''' Pygame Game basis class
        modeled after Animation class from 15-112 at CMU
        '''
    ##### INTERFACE #####

    ''' Override these functions '''
    # define initialization behavior #
    def init(self): pass
    # define frame-by-frame behavior #
    #    time_passed: time, in ms, since last frame #
    def timer_fired(self, time_passed): pass
    # define key press behavior #
    def key_pressed(self, key): pass
    # define key release behavior #
    def key_released(self, key): pass
    # define drawing behavior #
    def redraw_all(self): pass
    # define exit behavior #
    def exit(self): pass

    ''' Use these functions '''
    # is_key_down(_key_)
    #    True if _key_ is pressed
    #    else False

    ##### IMPLEMENTATION #####
    ''' '''
    def _redraw_all(self):
        self.redraw_all()
        pygame.display.flip()

    def is_key_down(self, key):
        return self.key_dict.get(key, False)

    def _init(self):
        self.clock = pygame.time.Clock()
        self.key_dict = dict()
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 0, 32)
        self.bg_color = 0, 0, 0
        self.init()

    def _exit(self):
        self.exit()
        sys.exit()

    def _key_pressed(self, key):
        self.key_dict[key] = True
        self.key_pressed(key)

    def _key_released(self, key):
        self.key_dict[key] = False
        self.key_released(key)

    def run(self, screen_width=600, screen_height=400, fps=30, title="Game"):
        pygame.init()
        pygame.display.set_caption(title)
        self.screen_width, self.screen_height = screen_width, screen_height
        self._init()
        while True:
            time_passed = self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._exit()
                elif event.type == pygame.KEYDOWN:
                    self._key_pressed(event.key)
                elif event.type == pygame.KEYUP:
                    self._key_released(event.key)
            self.timer_fired(time_passed/1000.)
            self._redraw_all()
