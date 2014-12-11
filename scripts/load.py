import pygame

def load_stuff():
    global GROUND_IMG
    global WORM_LINK_IMG
    global WORM_FANG_IMG
    global MEGAMAN_IMGS
    global SAMUS_IMGS
    GROUND_IMG = pygame.image.load('ground_big.jpg')
    WORM_LINK_IMG = pygame.image.load('worm_piece.png').convert_alpha()
    WORM_FANG_IMG = pygame.image.load('worm_small_fang.png').convert_alpha()
