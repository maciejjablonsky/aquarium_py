'''This module combines boid vision preprocessing'''

import pygame as pg
from pygame.gfxdraw import textured_polygon
import torch
import aifishes.config as cfg


def boid_reaction_area_surface(boid, frame: int) -> torch.Tensor:
    '''Cutting boid reaction area from game screen'''
    screen = pg.display.get_surface()
    vision_area = boid.reaction_area()
    position = boid.position
    radius = cfg.fish()['reaction_radius']

    left = int(max(0, round(position.x - radius)))
    up = int(max(0, round(position.y - radius)))
    right = int(min(screen.get_width() - 1, round(position.x + radius)))
    bottom = int(min(screen.get_height() - 1, round(position.y + radius)))
    bounding_box = pg.Rect(left, up, right - left, bottom - up)
    vision_surface = pg.Surface((radius * 2, radius * 2))
    clipped = vision_surface.copy()
    dest = (max(0, radius - position.x), max(0, radius - position.y))
    vision_surface.blit(screen,dest=dest, area=bounding_box)
    textured_polygon(clipped, vision_area - position + pg.Vector2(radius, radius), vision_surface, 20, 0)
    pg.image.save(clipped, 'tex_boid_%d.png' % frame)
