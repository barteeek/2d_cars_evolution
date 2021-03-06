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

from math import sqrt
import numpy as np
from random import random
from copy import copy

from Box2D import (b2CircleShape, b2EdgeShape, b2FixtureDef, b2PolygonShape,
                   b2_pi)

class WheelRepresentation:
    def __init__(self, vertex_it, wheelRad):
        self.vertex_it = vertex_it
        self.wheelRadius = wheelRad
    
    def get_chromosome(self):
        return np.array([self.vertex_it, self.wheelRadius])

    def put_chromosome(self, chromosome):
        assert(chromosome.shape == (3,))

        self.vertex_it = chromosome[0]
        self.wheelRadius = chromosome[2]
    
    # def random(self):
    #     self.vertex_it =
    #     self.axleAngle = np.random.rand()
    #     self.wheelRadius = np.random.rand()

class CarBuilder:
    def get_random_car(self, **kwargs):
        return CarRepresentation(**kwargs)

class CarRepresentation:
    def __init__(self, **kwargs):
        self.random(6, **kwargs)

    def normalize(self):
        angles = np.array([self.chromosome[j] for j in [1,3,5,7,9,11]])

        for j in range(17):
            if j in [13, 15]: # joints
                self.chromosome[j] = np.clip(np.floor(self.chromosome[j]), 0, 5)
            elif j in [1, 3, 5, 7, 9, 11]: # angles
                self.chromosome[j] = 2 * np.pi * (self.chromosome[j] - angles.min() + 0.05) / (angles - angles.min() + 0.1).sum()
            else:
                self.chromosome[j] = np.clip(self.chromosome[j], 0.1, 30.0)

    def get_car(self):
        return self

    def construct_car(self, damping_ratio, body_vectors, wheels):
        # body_vectors N x 2
        self.damping_ratio = damping_ratio
        self.body_vectors = body_vectors
        self.wheels = wheels
        self.chromosome = \
            np.hstack([damping_ratio, body_vectors.reshape(-1), np.hstack([wheel.get_chromosome() for wheel in wheels])])

        self.body_vec_num = body_vectors.shape[0]
        self.wheel_num = len(wheels)
        
    def construct_from_chromosome(self, chromosome):
        chromosome_list = chromosome.tolist()
        self.damping_ratio = chromosome_list[0]
        self.body_vectors = chromosome[1:13].reshape(6, 2)
        self.wheels = [WheelRepresentation(chromosome_list[13], chromosome_list[14]),
                       WheelRepresentation(chromosome_list[15], chromosome_list[16])]
        self.chromosome = chromosome
        self.body_vec_num = self.body_vectors.shape[0]
        self.wheel_num = len(self.wheels)

    def is_ok(self, wheels):
        if len(wheels) <= 1:
            return True

        wheel_1_pos = np.array([wheels[0].position[0], wheels[0].position[1]])
        wheel_2_pos = np.array([wheels[1].position[0], wheels[1].position[1]])
        distance = np.sqrt(np.sum((wheel_1_pos - wheel_2_pos)**2))
        radius_sum = wheels[0].fixtures[0].shape.radius + wheels[1].fixtures[0].shape.radius

        return distance + 0.01 >= radius_sum

    def put_to_world(self, world, offset=(0.0, 10.), scale=(1, 1), hz=4.,
                     zeta=5., density=40., max_torque=40.):
        x_offset, y_offset = offset
        scale_x, scale_y = scale

        main_body = world.CreateDynamicBody(position=(x_offset, y_offset))

        # permuted_chromosome = []
        
        # for i in [0,  13,  1,2,3,  14,   4,5,6,  15,   7,8,9,   16,   10,11,12]:
        #     permuted_chromosome += [self.chromosome[i]]
        permuted_chromosome = self.chromosome
        angles = np.zeros(self.body_vec_num)
        lengths = np.zeros(self.body_vec_num)

        for i in range(self.body_vec_num):
            angles[i] = permuted_chromosome[2 * i + 1]
            lengths[i] = permuted_chromosome[2 * i + 2]

        angles = 2. * np.pi * (angles / angles.sum())
        vectors = np.zeros((self.body_vec_num, 2))
        currentAngle = 0.

        for i in range(self.body_vec_num):
            currentAngle += angles[i]
            length = lengths[i] #permuted_chromosome[2 * i + 2]
            vectors[i, 0] = length * np.cos(currentAngle)
            vectors[i, 1] = length * np.sin(currentAngle)

        for i in range(self.body_vec_num):
            triangle = [(0., 0.),
                (vectors[i, 0], vectors[i, 1]),
                (vectors[(i + 1) % self.body_vec_num, 0], vectors[(i + 1) % self.body_vec_num, 1])]
            main_body.CreatePolygonFixture(shape=b2PolygonShape(vertices=triangle),
                density=density)

        radius_scale = sqrt(scale_x ** 2 + scale_y ** 2)

        wheels, springs = [], []

        it_offset = 2 * self.body_vec_num + 1
        enableMotor = [False] * self.wheel_num
        enableMotor[0] = True

        for i in range(self.wheel_num):
            #vertex_x = self.chromosome[4 * i + it_offset]
            #vertex_y = self.chromosome[4 * i + it_offset + 1]
            #axle_angle = self.chromosome[4 * i + it_offset + 2]
            #radius = radius_scale * self.chromosome[4 * i + it_offset + 3]

            vertex_it = np.clip(int(permuted_chromosome[2 * i + it_offset]), -1, self.body_vec_num - 1)
            if vertex_it == -1:
                continue

            radius = radius_scale * permuted_chromosome[2 * i + it_offset + 1]

            vertex_x = vectors[vertex_it][0] #permuted_chromosome[2 * vertex_it + 1]
            vertex_y = vectors[vertex_it][1] #permuted_chromosome[2 * vertex_it + 2]

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
                dampingRatio=permuted_chromosome[0]
            )

            wheels.append(wheel)
            springs.append(spring)

        return main_body, wheels, springs, self.is_ok(wheels)

    def get_chromosome(self):
        return self.chromosome
    
    def apply_permutation(self, permutation = None):
        if permutation is None:
            permutation = self.permutation
        permuted_chromosome = []
        for i in permutation:
            permuted_chromosome += [self.chromosome[i]]
        return np.array(permuted_chromosome)

    def undo_permutation(self, permutation = None):
        if permutation is None:
            permutation = self.permutation
        original_chromosome = np.zeros(17)
        for i in permutation:
            original_chromosome[permutation[i]] += self.chromosome[i]
        self.chromosome = original_chromosome

    def set_permutation(self, permutation):
        self.permutation = permutation

    def get_permutation(self):
        return self.permutation

    def random(self, body_vec_num, **kwargs):
        self.damping_ratio = np.random.rand(1)
        self.body_vectors = np.random.rand(body_vec_num, 2) * 2

        # normalization for angles
        self.body_vectors[:, 0] = 2 * np.pi * self.body_vectors[:, 0] / self.body_vectors[:, 0].sum()

        self.wheels = [WheelRepresentation(np.random.randint(0, body_vec_num), random()) for _ in range(2)]
        self.body_vec_num = self.body_vectors.shape[0]
        
        self.wheel_num = len(self.wheels)
        self.chromosome = \
            np.hstack([self.damping_ratio, self.body_vectors.reshape(-1), np.hstack([wheel.get_chromosome() for wheel in self.wheels])])

        if "with_permutations" in kwargs and kwargs["with_permutations"] == True:
            self.permutation = np.random.permutation(17)
            print (self.permutation)

    def make_copy(self):
        result = type(self)()
        result.construct_car(copy(self.damping_ratio), copy(self.body_vectors), copy(self.wheels))
        if hasattr(self, 'permutation'):
            result.permutation = self.permutation
        return result

class Terrain:
    def __init__(self, heights, friction):
        self.heights = heights
        self.friction = friction
        self.flat_width = 20

    def put_to_world(self, world):
        ground = world.CreateStaticBody(
            shapes=b2EdgeShape(vertices=[(-self.flat_width, 0), (self.flat_width, 0)])
        )

        ground.CreateEdgeFixture(
            vertices=[(-self.flat_width, 0), (-self.flat_width, 100)],
            density=0,
            friction=self.friction,
        )

        x, y1, dx = 20, 0, 5
        vertices = self.heights
        for y2 in vertices * 2:  # iterate through vertices twice
            ground.CreateEdgeFixture(
                vertices=[(x, y1), (x + dx, y2)],
                density=0,
                friction=self.friction,
            )
            y1 = y2
            x += dx

        route_end = x
        ground.CreateEdgeFixture(
            vertices=[(x, y1), (x + self.flat_width, y1)],
            density=0,
            friction=self.friction,
        )

        x += self.flat_width
        ground.CreateEdgeFixture(
            vertices=[(x, y1), (x, 100)],
            density=0,
            friction=self.friction,
        )
        self.route_end = route_end

        return (route_end, route_end + self.flat_width)
