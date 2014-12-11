from animatedSprite import AnimatedSprite, ImageHolder
from vec2d import vec2d
from random import randint as ri
from random import choice as rc

class FireParticle(AnimatedSprite):
    @classmethod
    def init(cls):
        cls.anims = []
        cls.anims.append(ImageHolder.load_anim('fire', 'part'))

    def __init__(self, screen, camera, pos):
        super(FireParticle, self).__init__(
            screen, camera, pos, 'fire', FireParticle.anims)
        self.play()
        super(FireParticle, self).update(0)
        self.velocity = vec2d(0, ri(-4, -2))
        self.gone = False
        self.played = False

    def update(self, time_passed):
        super(FireParticle, self).update(time_passed)
        choices = [-1, 0, 1]
        sx = int(abs(self.velocity.x))
        choices += [-1 if self.velocity.x > 0 else 1]*sx
        self.velocity.x += rc(choices)
        self.pos += self.velocity
        if self.current_anim.frame > 0: self.played = True
        if self.current_anim.frame == 0 and self.played:
            self.gone = True

class Fire(object):
    def __init__(self, screen, camera, item):
        self.screen = screen
        self.camera = camera
        self.pos = item.pos
        self.item = item
        self.fire_parts = [FireParticle(screen, camera, item.pos)]

    def update(self, time_passed, add_fire=True):
        f = 0
        fp_count = len(self.fire_parts)
        while f < fp_count:
            part = self.fire_parts[f]
            part.update(time_passed)
            if part.gone: self.fire_parts.pop(f); fp_count -= 1
            else: f += 1
        self.pos = self.item.pos
        screen, camera, pos = self.screen, self.camera, self.pos
        if add_fire: self.fire_parts.append(FireParticle(screen, camera, pos))

    def blit_me(self):
        for p in self.fire_parts:
            p.blit_me()

FireParticle.init()