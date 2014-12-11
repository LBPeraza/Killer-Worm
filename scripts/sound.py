import pygame.mixer, random
import os

class SoundManager(object):
    initted = False

    @classmethod
    def init(cls):
        cls.initted = True
        cls.sounds = dict()
        for sound_type in os.listdir("sounds"):
            cls.sounds[sound_type] = []
            for sound in os.listdir(os.path.join("sounds", sound_type)):
                sound_file = os.path.join("sounds",
                                          os.path.join(sound_type, sound))
                cls.sounds[sound_type].append(pygame.mixer.Sound(sound_file))
        scream_count = 3
        screams = ["sounds/scream/%d.wav" % i for i in xrange(scream_count)]
        crunch_count = 3
        crunches = ["sounds/crunch/%d.wav" % i for i in xrange(crunch_count)]
        cls.screams = [pygame.mixer.Sound(scream) for scream in screams]
        cls.crunches = [pygame.mixer.Sound(crunch) for crunch in crunches]

    def __init__(self):
        if not self.__class__.initted: self.__class__.init()
        self.curr_channel = 0
        self.num_channels = pygame.mixer.get_num_channels()
        self.channels = [pygame.mixer.Channel(i)
                         for i in xrange(self.num_channels)]

    def play(self, sound):
        channel = self.channels[self.curr_channel]
        channel.play(sound)
        self.curr_channel += 1
        self.curr_channel %= self.num_channels

    def play_sound(self, filename):
        path = os.path.join("sounds", filename)
        print path
        sound = pygame.mixer.Sound(path)
        self.play(sound)

    def play_sound_by_type(self, sound_type):
        if (sound_type not in SoundManager.sounds):
            raise Exception("Sound type %s not found" % sound_type)
        else:
            sound = random.choice(SoundManager.sounds[sound_type])
            self.play(sound)