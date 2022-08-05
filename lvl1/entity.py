import pygame
from math import sin

class Entity(pygame.sprite.Sprite):
	def __init__(self, groups):
		super().__init__(groups)
		self.frame_indx = 0
		self.anim_speed = 0.15
		self.direction = pygame.math.Vector2()

	def collision(self, direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hbox.colliderect(self.hbox):
					if self.direction.x > 0: #moving right
						self.hbox.right = sprite.hbox.left
					if self.direction.x < 0: #moving left
						self.hbox.left = sprite.hbox.right
		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hbox.colliderect(self.hbox):
					if self.direction.y > 0: #moving down
						self.hbox.bottom = sprite.hbox.top
					if self.direction.y < 0: #moving up
						self.hbox.top = sprite.hbox.bottom

	def move(self, speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hbox.center


	def wave_value(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0: 
			return 255
		elif (-0.5 <= value < 0): 
			return abs(value)*255
		else: 
			return 0