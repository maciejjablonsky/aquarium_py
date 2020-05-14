import numpy as np
import aifishes.config as cfg
import typing
import pygame as pg
import scipy as scp


def random_position():
    borders = cfg.borders()
    return pg.Vector2(
        scale(np.random.rand(), [0, 1], [0, borders[0]]),
        scale(np.random.rand(), [0, 1], [0, borders[1]])
    )


def random_velocity():
    magnitude = cfg.fish_vel_start_magnitude()
    angle = scale(np.random.rand(), [0, 1], [0, 360])
    vec = pg.Vector2()
    vec.from_polar((magnitude, angle))
    return vec


def scale(value, old, new):
    return (value / (old[1] - old[0])) * (new[1] - new[0]) + new[0]

X_AXIS_VEC = pg.Vector2(1, 0)
Y_AXIS_VEC = pg.Vector2(0, 1)

class Agent:
    def __init__(self, sprite: pg.Surface, position: pg.Vector2, velocity: pg.Vector2):
        self.sprite = sprite
        self.position = position
        self.velocity = velocity
        self.acceleration = pg.Vector2(0, 0)
        self.alive = True

    def update_position(self, dtime):
        self.position += self.velocity * dtime

    def limit_velocity(self):
        limit = cfg.fish_vel_max_magnitude()
        if self.velocity.length() > limit:
            self.velocity = limit * self.velocity.normalize()

    def update_velocity(self, dtime):
        self.velocity += self.acceleration * dtime

    def apply_force(self, acceleration: pg.Vector2):
        self.acceleration = acceleration

    def update(self, dtime):
        self.update_velocity(dtime)
        self.limit_velocity()
        self.update_position(dtime)

    def get_showable(self):
        angle = self.velocity.angle_to(X_AXIS_VEC)
        return pg.transform.rotate(self.sprite, angle)