import pygame

class SpeedBoost:
    def __init__(self, x, y, tile_size, duration=200, image=None):
        self.rect = pygame.Rect(x, y, tile_size + 5, tile_size + 5)
        self.duration = duration
        self.active = False
        self.timer = 0
        # self.image = pygame.image.load("../images/lightning_bolt.png").convert_alpha()
        # self.image = pygame.transform.scale(self.image, (tile_size, tile_size))  # scale to tile size if needed
        self.image = image
        self.color = (19, 232, 83)  # neon green

    def apply(self, player, enemies):
        self.active = True
        self.timer = self.duration
        player.speed *= 2
        # hide power-up
        self.rect.x = -100
        self.rect.y = -100

    def update(self, player, enemies):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.remove(player, enemies)
                self.active = False

    def remove(self, player, enemies):
        player.speed //= 2

    def reset(self, player):
        player.speed = 4

    # def draw(self, screen):
    #     if not self.active:
    #         pygame.draw.rect(screen, self.color, self.rect, border_radius=23)

    def draw(self, screen):
        if not self.active:
            screen.blit(self.image, self.rect.topleft)

