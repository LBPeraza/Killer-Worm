import pygame, sys
from vec2d import vec2d
from camera import Camera

class ImageHolder(object):
    @classmethod
    def load_anim(cls, folder, anim):
        path = 'images/%s/%s' % (folder, anim)
        with open('%s/times.txt' % path, 'r') as times:
            lines = times.read().split('\n')
        fc = int(lines[0])
        frame_times = [float(lines[i]) for i in xrange(1, fc+1)]
        images = [pygame.image.load('%s/%d.png' % (path, i))
                            for i in xrange(fc)]
        return ImageHolder(fc, frame_times, images, anim)

    def __init__(self, frame_count, frame_times, images, name):
        self.frame_count = frame_count
        self.frame_times = frame_times
        self.images = images
        self.name = name

    def read(self):
        return (self.name,
                self.frame_count,
                self.frame_times,
                self.images)

    def __repr__(self):
        return self.name

class Animation(object):
    def __init__(self, img_holder):
        n, self.frame_count, self.frame_times, self.images = img_holder.read()
        self.base_image = self.images[0]
        self.image = self.base_image
        self.image_w, self.image_h = self.image.get_size()
        self.playing = False
        self.time = 0.0
        self.rotation = 0
    
    def play(self, frame=0):
        self.playing = True
        self.time = 0.0
        self.frame = frame % self.frame_count

    def stop(self):
        self.time = 0.0
        self.frame = 0
        self.playing = False

    def pause(self):
        self.playing = False

    def unpause(self):
        self.playing = True

    def update(self, time_passed, pos):
        if self.playing:
            self.time += time_passed
            if self.time >= self.frame_times[self.frame]:
                self.frame = (self.frame+1) % self.frame_count
                self.time = 0.0
                self.base_image = self.images[self.frame]
            self.image = pygame.transform.rotate(self.base_image,
                                                 -self.rotation)
            self.image_w, self.image_h = self.image.get_size()
        self.world_pos = self.image.get_rect().move(
            pos.x - self.image_w / 2,
            pos.y - self.image_h / 2)

    def blit_me(self, screen, camera, flip=False):
        draw_pos = camera.rect_world_to_screen(self.world_pos)
        if flip: image = pygame.transform.flip(self.image, True, False)
        else: image = self.image
        screen.blit(image, draw_pos)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, screen, camera, pos, name, img_holders):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.anims = dict()
        for img_holder in img_holders:
            sprite_name = img_holder.name
            self.anims[sprite_name] = Animation(img_holder)
        self.curr_anim = img_holders[0].name
        self.pos = vec2d(pos)
        self.camera = camera
        self.keep_frame = False

    def _get_anim(self):
        return self.anims[self.curr_anim]
    def _set_anim(self, name):
        try:
            if name == self.curr_anim: return
        except: pass
        old_rotation = self.current_anim.rotation
        old_playing = self.current_anim.playing
        old_frame = self.current_anim.frame+1 if self.keep_frame else 0
        self.curr_anim = name
        self.current_anim.rotation = old_rotation
        if old_playing: self.current_anim.play(old_frame)
    current_anim = property(_get_anim, _set_anim, None, '')

    def _get_rotation(self):
        return self.current_anim.rotation
    def _set_rotation(self, angle):
        self.current_anim.rotation = angle
    rotation = property(_get_rotation, _set_rotation, None, '')

    def switch_anim(self, name):
        self.keep_frame = True
        self.current_anim = name
        self.keep_frame = False

    def update(self, time_passed):
        self.current_anim.update(time_passed, self.pos)

    def blit_me(self, flip=False):
        if self.camera.rect_on_screen(self.current_anim.world_pos):
            self.current_anim.blit_me(self.screen, self.camera, flip)

    def play(self):
        self.current_anim.play()

    def pause(self):
        self.current_anim.pause()

    def unpause(self):
        self.current_anim.unpause()
