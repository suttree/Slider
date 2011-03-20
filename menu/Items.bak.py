#! /usr/bin/env python

import os
import sys
import time
import pygame
import webbrowser
from pygame.locals import *

FONT = os.path.join('fonts', 'nrkis.ttf')

class Bonus(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.value = 0
		self.off_screen = 0
		self.last_update = 0
		self.colours = [ [255,255,0], [255,128,0], [255,255,0], [255,128,0], [255,255,0], [255,128,0] ]
		self.font = pygame.font.Font(FONT, 18)

	def award(self,value):
		self.value = 100*value
		self.image = self.font.render("Bonus +%d!" % self.value, 1, self.colours[0])
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([412,35])

	def reset(self):
		self.value = 0
		self.off_screen = 0
		self.colours = [ [255,255,0], [255,128,0], [255,255,0], [255,128,0], [255,255,0], [255,128,0] ]
		self.last_update = 0
		self.image = self.font.render("Bonus +%d!" % self.value, 1, self.colours[0])
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([412,35])

	def update(self):
		try:
			time_now = pygame.time.get_ticks()
			if (time_now - self.last_update) >= 125:
				self.last_update = time_now
				colour = self.colours.pop()
				self.image = self.font.render("Bonus +%d!" % self.value, 1, colour)
				self.rect = self.image.get_rect()
				self.rect = self.rect.move([412,35])
		except:
			self.off_screen = 1

class Collect(pygame.sprite.Sprite):
	def __init__(self,timer):
		pygame.sprite.Sprite.__init__(self)

		self.clicked = 0
		self.last_update = 0
		self.font = pygame.font.Font(FONT, 22)
		self.image = self.font.render("Collect", 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,205])
		self.timer = timer

	def click_test(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		if area.colliderect(self.rect):
			self.clicked = 1
		else:
			self.clicked = 0

	def reset(self):
		self.clicked = 0
		self.last_update = 0

	def update(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		time_now = pygame.time.get_ticks()
		if self.timer.timer <= 10:
			print time_now - self.last_update
			if time_now - self.last_update > 1000:
				self.image = self.font.render("Collect", 1, (255,128,0))
				self.last_update = time_now
			else:
				self.image = self.font.render("Collect", 1, (255,255,255))
				self.last_update = 0
		else:
			self.image = self.font.render("Collect", 1, (255,255,255))

		if area.colliderect(self.rect):
			self.image = self.font.render("Collect", 1, (255,0,0))

class EndGame(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.font = pygame.font.Font(FONT, 22)
		self.image = self.font.render("End Game", 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,330])

	def click_test(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		if area.colliderect(self.rect):
			webbrowser.open("http://www.playaholics.com")
			sys.exit()

	def update(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		if area.colliderect(self.rect):
			self.image = self.font.render("End Game", 1, (255,0,0))
		else:
			self.image = self.font.render("End Game", 1, (255,255,255))

class GameOver(pygame.sprite.Sprite):
	def __init__(self,game):
		pygame.sprite.Sprite.__init__(self)

		self.game = game
		self.font = pygame.font.Font(FONT, 24)
		self.image = self.font.render("Game Over!", 1, (0,0,0))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([150,200])

	def update(self):
		if self.game.game_over == 1:
			self.image = self.font.render("Game Over!", 1, (0,0,0))

class NewGame(pygame.sprite.Sprite):
	def __init__(self,game):
		pygame.sprite.Sprite.__init__(self)

		self.game = game
		self.font = pygame.font.Font(FONT, 22)
		self.image = self.font.render("New Game", 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,300])

	def click_test(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		if area.colliderect(self.rect):
			self.game.restart()

	def update(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		if area.colliderect(self.rect):
			self.image = self.font.render("New Game", 1, (255,0,0))
		else:
			self.image = self.font.render("New Game", 1, (255,255,255))

class SubmitScore(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.score = 0
		self.font = pygame.font.Font(FONT, 22)
		self.image = self.font.render("Submit your score", 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,260])

	def reset(self):
		self.score = 0

	def update(self):
		x,y = pygame.mouse.get_pos()
		area = pygame.Rect(x,y,1,1)

		if area.colliderect(self.rect):
			self.image = self.font.render("Submit your score", 1, (255,0,0))
			if pygame.mouse.get_pressed()[0]:
				webbrowser.open("http://www.playaholics.com/comp_entry.php?game=Slider&developer=playaholics&score=%d" % (self.score))
				# NOW DESTROY THE LINK!!!
				self.image = self.font.render("",1,(255,0,0))
				self.rect = self.image.get_rect()
				self.rect = self.rect.move([-100,-100])
		
		else:
			self.image = self.font.render("Submit your score", 1, (255,255,255))

class Timer(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.in_game = 0
		self.time_limit = 15
		self.last_update = 0
		self.timer = self.time_limit

		self.font = pygame.font.Font(FONT, 32)
		self.image = self.font.render("Time: %s" % self.time_limit, 1, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect = self.rect.move([410,55])

	def reset(self):
		"""Resets the timer for the next level"""
		self.time_limit = 15
		self.timer = self.time_limit
		self.start_time = int(time.time())
		self.last_update = 0

	def start(self):
		self.in_game = 1
		self.start_time = int(time.time())

	def stop(self):
		self.timer = 0
		self.in_game = 0

	def time_up(self):
		"""Boolean end of level check"""
		if self.timer <= 0:
			return 1
		else:
			return 0

	def update(self):
		time_now = pygame.time.get_ticks()
		if (time_now - self.last_update) >= 1000 and self.in_game:
			self.last_update = time_now
			self.timer = self.timer-1
			self.image = self.font.render("Time: %s" % self.timer, 1, (255,255,255))