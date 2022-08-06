import pygame
from support import import_folder
from debug import debug
from entity import Entity
from settings import *

class Player(Entity):
	def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
	 super().__init__(groups)
	 self.image = pygame.image.load('../graphics/player/down_idle/idle_down.png').convert_alpha()
	 self.rect = self.image.get_rect(topleft = pos)
	 self.hbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])
	 self.obstacle_sprites = obstacle_sprites

	 self.import_player_assets()
	 self.status = 'down'
	 
	 #self.frame_indx = 0
	 #self.anim_speed = 0.15

	 #self.direction = pygame.math.Vector2()

	 self.weapon_switch = True
	 self.weapon_switch_time = None
	 self.weapon_switch_cd = 400 

	 self.magic_switch = True
	 self.magic_switch_time = None
	 self.magic_switch_cd = 400 

	 self.attacking = False
	 self.magicking = False
	 self.attack_time = None
	 self.create_attack = create_attack
	 self.destroy_attack = destroy_attack

	 self.weapon_indx = 2
	 self.weapon = list(weapon_data.keys())[self.weapon_indx]
	 self.attack_cd = 150

	 self.create_magic = create_magic
	 self.magic_indx = 0
	 self.magic = list(magic_data.keys())[self.magic_indx]

	 self.stats = {'health':100, 'energy':60, 'attack': 10, 'magic':4, 'speed':5, 'mp recovery': 0.01}
	 self.max_stats = {'health':600, 'energy':200, 'attack': 40, 'magic': 20, 'speed': 10, 'mp recovery': 0.6}
	 self.upgrade_cost = {'health':100, 'energy':100, 'attack': 100, 'magic':100, 'speed':100, 'mp recovery': 100}
	 self.upgrade_amount = {'health':50, 'energy':15, 'attack': 5, 'magic':4, 'speed':1, 'mp recovery': 0.03}
	 self.health = self.stats['health']
	 self.energy = self.stats['energy']
	 self.speed = self.stats['speed']
	 self.mp_recovery = self.stats['mp recovery']
	 self.exp = 6000

	 self.vulnerable = True
	 self.hurt_time = None
	 self.invuln_duration = 500

	 self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
	 self.weapon_attack_sound.set_volume(0.4)

	def import_player_assets(self):
		character_path = '../graphics/player/'
		self.animations = {
		'up':[], 'down':[], 'left':[], 'right':[], 
		'up_idle':[], 'down_idle':[], 'left_idle':[], 'right_idle':[], 
		'up_attack':[], 'down_attack':[], 'left_attack':[], 'right_attack':[]
		}
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def get_damage(self, atk_sprite_type):
		if atk_sprite_type == 'weapon':
			return (weapon_data[self.weapon]['damage'] + self.stats['attack'], weapon_data[self.weapon]['knockback'])
		elif atk_sprite_type == 'particle':
			return (magic_data[self.magic]['strength'] + self.stats['magic'], magic_data[self.magic]['knockback'])


	def input(self):
		keys = pygame.key.get_pressed()
		if not self.attacking and not self.magicking:
			#movement
			if keys[pygame.K_UP]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.status = 'left'
			elif keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.status = 'right'
			else:
				self.direction.x = 0
			#attack
			if keys[pygame.K_SPACE]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack()
				self.weapon_attack_sound.play()

			#magic
			if keys[pygame.K_LALT]:
				self.magicking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_magic(style = self.magic, strength = magic_data[self.magic]['strength'] + self.stats['magic'], cost = magic_data[self.magic]['cost'])

			if keys[pygame.K_q] and self.weapon_switch:
				self.weapon_switch = False
				self.weapon_switch_time = pygame.time.get_ticks()
				
				self.weapon_indx = (self.weapon_indx + 1) % len(weapon_data)
				self.weapon = list(weapon_data.keys())[self.weapon_indx]

			if keys[pygame.K_w] and self.magic_switch:
				self.magic_switch = False
				self.magic_switch_time = pygame.time.get_ticks()
				
				self.magic_indx = (self.magic_indx + 1) % len(magic_data)
				self.magic = list(magic_data.keys())[self.magic_indx]
				self.attack_cd = 400
				#self.magic_cd = magic_data[self.magic]['cooldown']


	def get_status(self):
		#idle
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'

		if self.attacking or self.magicking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle', '_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack', '')


	def value_by_index(self, index, get_type):
		if get_type == 'cost':
			return list(self.upgrade_cost.values())[index]
		elif get_type == 'value':
			return list(self.stats.values())[index]


	def animate(self):
		animation = self.animations[self.status]
		self.frame_indx += self.anim_speed
		self.frame_indx = self.frame_indx % len(self.animations[self.status])

		self.image = animation[int(self.frame_indx)]
		self.rect = self.image.get_rect(center = self.hbox.center)

		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	# def move(self, speed):
	# 	if self.direction.magnitude() != 0:
	# 		self.direction = self.direction.normalize()

	# 	self.hbox.x += self.direction.x * speed
	# 	self.collision('horizontal')
	# 	self.hbox.y += self.direction.y * speed
	# 	self.collision('vertical')
	# 	self.rect.center = self.hbox.center


	# def collision(self, direction):
	# 	if direction == 'horizontal':
	# 		for sprite in self.obstacle_sprites:
	# 			if sprite.hbox.colliderect(self.hbox):
	# 				if self.direction.x > 0: #moving right
	# 					self.hbox.right = sprite.hbox.left
	# 				if self.direction.x < 0: #moving left
	# 					self.hbox.left = sprite.hbox.right
	# 	if direction == 'vertical':
	# 		for sprite in self.obstacle_sprites:
	# 			if sprite.hbox.colliderect(self.hbox):
	# 				if self.direction.y > 0: #moving down
	# 					self.hbox.bottom = sprite.hbox.top
	# 				if self.direction.y < 0: #moving up
	# 					self.hbox.top = sprite.hbox.bottom

	def cds(self):
		current_time = pygame.time.get_ticks()
		if not self.weapon_switch:
			if current_time - self.weapon_switch_time >= self.weapon_switch_cd:
				self.weapon_switch = True

		if self.attacking or self.magicking:
			if self.magicking and (current_time - self.attack_time >= self.attack_cd + magic_data[self.magic]['cooldown']):
				self.magicking = False
				self.destroy_attack()

			if self.attacking and (current_time - self.attack_time >= self.attack_cd + weapon_data[self.weapon]['cooldown']):
				self.attacking = False
				self.destroy_attack()

		if not self.magic_switch:
			if current_time - self.magic_switch_time >= self.magic_switch_cd:
				self.magic_switch = True

		if not self.vulnerable:
			if current_time - self.hurt_time >= self.invuln_duration:
				self.vulnerable = True

		# if self.attacking:
		# 	if current_time - self.attack_time >= self.attack_cd:
		# 		self.attacking = False
		# 		self.destroy_attack()

	def energy_recovery(self):
		if self.energy < self.stats['energy']:
			self.energy += self.stats['mp recovery']
		else:
			self.energy = self.stats['energy']

	def update(self):
		self.input()
		self.cds()
		self.get_status()
		self.animate()
		self.energy_recovery()
		self.move(self.stats['speed'])
