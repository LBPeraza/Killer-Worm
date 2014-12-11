import pygame

class FontManager(pygame.font.Font):
    def __init__(self, font_name, size):
        font_path = pygame.font.match_font(font_name)
        super(FontManager, self).__init__(font_path, size)
        self.height = self.get_height()

    def write(self, screen, x, y, text, color=(0, 0, 0)):
        for i, line in enumerate(text.split('\n')):
            dy = self.height*i
            self.write_line(screen, x, y+dy, line, color)

    def write_line(self, screen, x, y, text, color):
        line_surf = self.render(text, True, color)
        size = self.size(text)
        text_rect = pygame.Rect(x, y, *size)
        screen.blit(line_surf, text_rect)