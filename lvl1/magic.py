import pygame
from settings import *
from random import randint

class Magic:
	def __init__(self, animation_player):
		self.animation_player = animation_player
		self.sounds = {
		'heal': pygame.mixer.Sound('../audio/heal.wav'),
		'flame': pygame.mixer.Sound('../audio/Fire.wav')
		}
			#sound.set_volume(0.4)

	def heal(self, player, strength, cost, groups):
		offset = player.rect.center + (player.direction * (TILESIZE // 2)) # for out of juice
		slightly_under = player.rect.center + pygame.math.Vector2(0, TILESIZE // 4)
		if player.energy >= cost:
			self.sounds['heal'].set_volume(0.4)
			self.sounds['heal'].play()
			player.health += strength
			player.energy -= cost
			if player.health >= player.stats['health']:
				player.health = player.stats['health']

			self.animation_player.generate_particle(player.rect.center, groups, 'heal')
			self.animation_player.generate_particle(slightly_under, groups, 'aura')
		else:
			self.no_juice(player, groups, offset)


	def fire(self, player, strength, cost, groups):
		offset = player.rect.center + (player.direction * (TILESIZE // 2))
		mbdirec = None
		direction = None
		if player.energy >= cost:
			self.sounds['flame'].set_volume(0.4)
			self.sounds['flame'].play()
			player.energy -= cost
			status = player.status.split('_')[0]

			if player.direction == (0,0):
				if status == 'down': mbdirec = pygame.math.Vector2(0,1)
				elif status == 'up': mbdirec = pygame.math.Vector2(0,-1)
				elif status == 'right': mbdirec = pygame.math.Vector2(1,0)
				else: mbdirec = pygame.math.Vector2(-1,0)

			if mbdirec:
				direction = mbdirec
			else:
				direction = player.direction

			for i in range(1,6):
				pos = player.rect.center + (direction *(i*TILESIZE)) + pygame.math.Vector2(randint(-TILESIZE // 4, TILESIZE // 4), randint(-TILESIZE // 4, TILESIZE // 4))
				self.animation_player.generate_particle(pos, groups, 'flame')
				# if direction.x:

				# elif direction.y:
				# 	pos = player.rect.center + (direction *(i*TILESIZE))
				# 	self.animation_player.generate_particle(pos, groups, 'flame')
		else:
			self.no_juice(player, groups, offset)

	def no_juice(self, player, groups, offset):
		# We only want visual sprites; there are no object or attack sprites when out of juice
		#print('No Juice!')
		new_groups = []
		for group in groups:
			if group.__class__.__name__ == 'SortYCameraGroup':
				new_groups.append(group)

		self.animation_player.generate_particle(offset, new_groups, 'smoke')