import pygame
from settings import *

class UI:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

		self.health_bar_rect = pygame.Rect(10,10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
		self.energy_bar_rect = pygame.Rect(10,12 + BAR_HEIGHT, ENERGY_BAR_WIDTH, BAR_HEIGHT)

		self.over_graphics = {
			'weapon': [],
			'magic': []
		}

		#self.wpn_graphics = []
		for weapon in weapon_data.values():
			path = weapon['graphic']
			weapon = pygame.image.load(path).convert_alpha()
			self.over_graphics['weapon'].append(weapon)
			#self.wpn_graphics.append(weapon)

		#self.magic_graphics = []
		for magic in magic_data.values():
			path = magic['graphic']
			magic = pygame.image.load(path).convert_alpha()
			self.over_graphics['magic'].append(magic)
			#self.magic_graphics.append(magic)

	def show_bar(self, current, max_amt, bg_rect, color):
		perc = current / max_amt
		current_width = bg_rect.width * perc

		pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

		current_rect = bg_rect.copy()
		current_rect.width = current_width
		pygame.draw.rect(self.display_surface, color, current_rect)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 4)

	def selec_box(self, left, top, has_switch):
		bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
		if has_switch:
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
		else:
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
		return bg_rect

	def overlay(self, intype, index, has_switch):
		if intype == 'weapon':
			bg_rect = self.selec_box(int(self.display_surface.get_size()[0] / 100), self.display_surface.get_size()[1] * 0.87, has_switch) #weapon
		elif intype == 'magic':
			bg_rect = self.selec_box(int(self.display_surface.get_size()[0] / 16), self.display_surface.get_size()[1] * 0.875, has_switch) #magic

		over_surf = self.over_graphics[intype][index]
		self.display_surface.blit(over_surf, over_surf.get_rect(center = bg_rect.center))

	# def overlay_weapon(self, weapon_indx, has_switch):
	# 	bg_rect = self.selec_box(int(self.display_surface.get_size()[0] / 100), self.display_surface.get_size()[1] * 0.87, has_switch) #weapon
	# 	weapon_surf = self.wpn_graphics[weapon_indx]
	# 	self.display_surface.blit(weapon_surf, weapon_surf.get_rect(center = bg_rect.center))

	# def overlay_magic(self, magic_indx, has_switch):
	# 	bg_rect = self.selec_box(int(self.display_surface.get_size()[0] / 16), self.display_surface.get_size()[1] * 0.875, has_switch) #magic
		
	# 	magic_surf = self.magic_graphics[magic_indx]
	# 	self.display_surface.blit(magic_surf, magic_surf.get_rect(center = bg_rect.center))

	def show_exp(self, exp):
		text_surface = self.font.render(str(int(exp)), False, TEXT_COLOR)
		texoffset = (20, 20)
		text_rect = text_surface.get_rect(bottomright = tuple(x-y for x,y in zip(self.display_surface.get_size(),texoffset)))

		pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(15,5))
		self.display_surface.blit(text_surface, text_rect)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(15,5), 3)

	def display(self,player):
		self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
		self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
		self.show_exp(player.exp)

		self.overlay('weapon', player.weapon_indx, not player.weapon_switch)
		self.overlay('magic', player.magic_indx, not player.magic_switch)
		#self.overlay_weapon(player.weapon_indx, not player.weapon_switch)
		#self.overlay_magic(player.magic_indx, not player.magic_switch)