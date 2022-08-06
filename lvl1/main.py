import pygame, sys
from settings import *
from debug import debug
from level import Level

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption('Gametest')
		self.clock = pygame.time.Clock()
		self.level = Level()

		self.main_track = pygame.mixer.Sound('../audio/main.ogg')
		self.main_track.set_volume(0.2)
		self.main_track.play(loops = -1)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_m:
						self.level.toggle_menu()
			self.screen.fill(WATER_COLOR)
			#debug()
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()