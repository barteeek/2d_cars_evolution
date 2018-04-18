#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# C++ version Copyright (c) 2006-2007 Erin Catto http://www.box2d.org
# Python version by Ken Lauer / sirkne at gmail dot com
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

from visualization.framework import (Framework, Keys, main)
from visualization.bridge import create_bridge
from math import sqrt
import numpy as np
from random import random
from copy import copy

from Box2D import (b2CircleShape, b2EdgeShape, b2FixtureDef, b2PolygonShape,
                   b2_pi)


class WheelRepresentation:
    def __init__(self, wheelVer, axleAngl, wheelRad):
        self.wheelVertex = wheelVer
        self.axleAngle = axleAngl
        self.wheelRadius = wheelRad
    
    def get_chromosome(self):
        return np.array([self.wheelVertex[0], self.wheelVertex[1], self.axleAngle, self.wheelRadius])

    def put_chromosome(self, chromosome):
        assert(chromosome.shape == (3,))

        self.wheelVertex = chromosome[0]
        self.axleAngle = chromosome[1]
        self.wheelRadius = chromosome[2]
    
    def random(self):
        self.wheelVertex = [random(), random()]
        self.axleAngle = np.random.rand()
        self.wheelRadius = np.random.rand()

class CarBuilder:
    def get_random_car():
        return CarRepresentation()

class CarRepresentation:
    def __init__(self):
        self.random()
    
    def construct_car(self, damping_ratio, body_vectors, wheels):
        # body_vectors N x 2
        self.damping_ratio = damping_ratio
        self.body_vectors = body_vectors
        self.wheels = wheels
        self.chromosome = \
            np.hstack([damping_ratio, body_vectors.reshape(-1), np.hstack([wheel.get_chromosome() for wheel in wheels])])

        self.body_vec_num = body_vectors.shape[0]
        self.wheel_num = len(wheels)

    def put_to_world(self, world, offset = (0.0, 10.), scale = (1, 1), hz = 4.,
                     zeta = 5., density = 1., max_torque = 40.):
        x_offset, y_offset = offset
        scale_x, scale_y = scale

        main_body = world.CreateDynamicBody(position=(x_offset, y_offset))

        for i in range(self.body_vec_num):
            triangle = [(0., 0.),
                (scale_x * self.chromosome[2 * i + 1], scale_y * self.chromosome[2 * i + 2]),
                (scale_x * self.chromosome[(2 * ((i + 1) % self.body_vec_num)) + 1],
                 scale_y * self.chromosome[(2 * (((i + 1) % self.body_vec_num))) + 2])]
            main_body.CreatePolygonFixture(shape=b2PolygonShape(vertices=triangle),
                density=density)

        radius_scale = sqrt(scale_x ** 2 + scale_y ** 2)

        wheels, springs = [], []

        it_offset = 2 * self.body_vec_num + 1
        enableMotor = [False] * self.wheel_num
        enableMotor[0] = True

        for i in range(self.wheel_num):
            vertex_x = self.chromosome[4 * i + it_offset]
            vertex_y = self.chromosome[4 * i + it_offset + 1]
            axle_angle = self.chromosome[4 * i + it_offset + 2]
            radius = radius_scale * self.chromosome[4 * i + it_offset + 3]

            wheel = world.CreateDynamicBody(
                position=(x_offset + vertex_x * scale_x, y_offset + vertex_y * scale_y),
                fixtures=b2FixtureDef(
                    shape=b2CircleShape(radius=radius),
                    density=density,
                )
            )

            spring = world.CreateWheelJoint(
                bodyA=main_body,
                bodyB=wheel,
                anchor=wheel.position,
                axis=(0., 1.),
                motorSpeed=0.0,
                maxMotorTorque=max_torque,
                enableMotor=enableMotor[i],
                frequencyHz=hz,
                dampingRatio=zeta
            )

            wheels.append(wheel)
            springs.append(spring)
            
            self.main_body = main_body
            self.wheels_bodies = wheels
            self.springs = springs

        return main_body, wheels, springs

    def get_chromosome(self):
        return self.chromosome
        
    def random(self):
        self.damping_ratio = np.random.rand(1)
        self.body_vectors = np.random.rand(6,2)
        self.wheels = [WheelRepresentation([random(), random()], random(), random()) for _ in range(2)]
        self.body_vec_num = self.body_vectors.shape[0]
        
        self.wheel_num = len(self.wheels)
        self.chromosome = \
            np.hstack([self.damping_ratio, self.body_vectors.reshape(-1), np.hstack([wheel.get_chromosome() for wheel in self.wheels])])

        
    def destroy(self, world):
        world.DestroyBody(self.main_body)
        for wheel in self.wheels_bodies:
             world.DestroyBody(wheel)
             
    def make_copy(self):
        result = type(self)()
        result.construct_car(copy(self.damping_ratio), copy(self.body_vectors), copy(self.wheels))
        return result

class Terrain:
    def __init__(self, length):
        self.sticks = np.random.rand(length)
    def put_to_world(self, world):
        ground = world.CreateStaticBody(
            shapes=b2EdgeShape(vertices=[(-20, 0), (20, 0)])
        )

        x, y1, dx = 20, 0, 5
        vertices = self.sticks
        for y2 in vertices * 2:  # iterate through vertices twice
            ground.CreateEdgeFixture(
                vertices=[(x, y1), (x + dx, y2)],
                density=0,
                friction=0.6,
            )
            y1 = y2
            x += dx

class Playground (Framework):
    name = "Car"
    description = "Keys: left = a, brake = s, right = d, hz down = q, hz up = e"
    hz = 4
    zeta = 0.7
    speed = 50
    bridgePlanks = 20
    counter = 0

    def __init__(self):
        super(Playground, self).__init__()
        
        terrain = Terrain(100)
        
        # create some terrain
        terrain.put_to_world(self.world)

        self.c = CarRepresentation()
        self.c.construct_car(1., np.array([
            (-1.5, -0.5),
            (1.5, -0.5),
            (1.5, 0.0),
            (0.0, 0.9),
            (-1.15, 0.9),
            (-1.5, 0.2),]),
        [WheelRepresentation([-1., -1], 0., 0.4), WheelRepresentation([1, -1], 0., 0.4)])
        car, wheels, springs = self.c.put_to_world(self.world)

        self.car = car
        self.wheels = wheels
        self.springs = springs

    def Keyboard(self, key):
        if key == Keys.K_a:
            self.springs[0].motorSpeed = self.speed
        elif key == Keys.K_s:
            self.springs[0].motorSpeed = 0
        elif key == Keys.K_d:
            self.springs[0].motorSpeed = -self.speed
        elif key in (Keys.K_q, Keys.K_e):
            if key == Keys.K_q:
                self.hz = max(0, self.hz - 1.0)
            else:
                self.hz += 1.0

            for spring in self.springs:
                spring.springFrequencyHz = self.hz

    def Step(self, settings):
        super(Playground, self).Step(settings)
        self.viewCenter = (self.car.position.x, 20)
        self.Print("frequency = %g hz, damping ratio = %g" %
                   (self.hz, self.zeta))
