import numpy as np
import aifishes.config as cfg
from aifishes.environment import agent
from aifishes.environment.agent import Agent, random_position, random_velocity
from aifishes.environment.fish import Fish
import pygame as pg

PREDATOR_COLOR = pg.Color('darkblue')
PREDATOR_SPRITE = None

DEBUG_HUNT = False


def predator_sprite():
    global PREDATOR_SPRITE
    if PREDATOR_SPRITE is None:
        w, h = tuple(cfg.predator_dim())
        surf = pg.Surface((w, h), pg.SRCALPHA)
        shape = np.array([[0, 0], [w, h/2], [0, h]], dtype=np.float32)
        pg.gfxdraw.aapolygon(surf, shape, PREDATOR_COLOR)
        pg.gfxdraw.filled_polygon(surf, shape, PREDATOR_COLOR)
        pg.draw.line(surf, pg.Color('Gray'), [w/9, h/2], [w/3, h/2], 2)
        PREDATOR_SPRITE = surf
    return PREDATOR_SPRITE

def predator_shape():
    w, h = cfg.predator()['dim']
    vec = pg.Vector2
    return [vec(-w/2, -h/2), vec(w/2, 0), vec(-w/2, h/2)]

class Predator(Agent):
    def __init__(self):
        super().__init__(predator_sprite(), random_position(),
                         random_velocity(cfg.predator_vel_start_magnitude()), cfg.predator()['reaction_radius'])
        self.hitbox = predator_shape()

    def create_reaction_area(self):
        vision_angle = cfg.predator()['vision_angle']
        n = 8
        return super().create_reaction_area(vision_angle=vision_angle, n=n)

    def limit_velocity(self):
        min_limit = cfg.predator()['velocity']['min']
        max_limit = cfg.predator()['velocity']['max']
        return super().limit_velocity(min_limit=min_limit, max_limit=max_limit)

    def debug_print(self, screen: pg.Surface):
        pg.draw.circle(screen, pg.Color('green'), np.array(
            self.position, dtype=np.int32), 2)
        sprite_dim = pg.Vector2(self.showable_sprite.get_size())
        # pg.draw.rect(screen, (0, 255, 0), pg.Rect(
            # self.position - sprite_dim/2, sprite_dim), 2)
        pg.draw.polygon(screen, (0, 0, 0), self.reaction_area(), 2)
        if self.closest_target is not None:
            pg.draw.line(screen, pg.Color('red'), self.position, self.closest_target.position, 2)

        # axis_len = 200
        # X axis
        # pg.draw.line(screen, pg.Color('white'), np.array(self.position, dtype=np.int32), np.array(
        #     distance.position + axis_len * agent.X_AXIS_VEC, dtype=np.int32), 2)
        # # Y axis
        # pg.ddistanceline(screen, pg.Color('white'), np.array(self.position, dtype=np.int32), np.array(
        #     self.position + axis_len * agent.Y_AXIS_VEC, dtype=np.int32), 2)

        # pg.draw.line(screen, pg.Color('cyan'), self.position, self.position + axis_len * self.velocity.normalize(), 2)
    def action(self, surroundings):
        closest = self.choose_closest(surroundings)
        if closest:
            self.steer_to_closest(closest)
            self.dinner(surroundings)
        else:
            self.steer_to_center()

    def steer_to_closest(self, closest:Agent):
        self.velocity = self.velocity.lerp(self.velocity.magnitude() * (closest.position - self.position),  0.002) 

    def debug_hunt(self, surroundings):
        screen = pg.display.get_surface()
        for each in surroundings:
            pg.draw.circle(screen, (255, 0, 0), np.array(
                each.position, dtype=np.int32), 10)

    def detect_target(self, surroundings):
        super().detect_target(surroundings)
        self.dinner(surroundings)

    def hunt(self, surroundings):
        if DEBUG_HUNT:
            self.debug_hunt(surroundings)
        closest = self.choose_closest(surroundings)

        
        if closest is not None:
            self.velocity = self.velocity.lerp(self.velocity.magnitude() * (closest.position - self.position),  0.005)
        
        #TODO surroundings are only agents who are in reaction area but is that the case?
        self.dinner(surroundings)

    def dinner(self, surroundings):
        dinner = self.find_collisions(surroundings) #crappy but funny
        for dish in dinner:
            if isinstance(dish, Fish):
                dish.die()
