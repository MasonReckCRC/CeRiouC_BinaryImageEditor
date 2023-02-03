# File containing the Screen object


import pygame




class Screen:

    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
        self.fpsClock = pygame.time.Clock()
        self.pyScreen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("CeRiouC Binary Image Editor")


    def resetScreen(self, width, height):
        self.width = width
        self.height = height
        self.pyScreen = pygame.display.set_mode((self.width, self.height))














