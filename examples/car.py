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

from .framework import (Framework, Keys, main)
from .bridge import create_bridge
from math import sqrt
import numpy as np
from random import random

from Box2D import (b2CircleShape, b2EdgeShape, b2FixtureDef, b2PolygonShape,
                   b2_pi)


def create_car(world, offset, wheel_radius, wheel_separation, density=1.0,
               wheel_friction=0.9, scale=(1.0, 1.0), chassis_vertices=None,
               wheel_axis=(0.0, 1.0), wheel_torques=[20.0, 10.0],
               wheel_drives=[True, False], hz=4.0, zeta=0.7, **kwargs):
    """
    """
    x_offset, y_offset = offset
    scale_x, scale_y = scale
    if chassis_vertices is None:
        chassis_vertices = [
            (-1.5, -0.5),
            (1.5, -0.5),
            (1.5, 0.0),
            (0.0, 0.9),
            (-1.15, 0.9),
            (-1.5, 0.2),
        ]

    chassis_vertices = [(scale_x * x, scale_y * y)
                        for x, y in chassis_vertices]
    radius_scale = sqrt(scale_x ** 2 + scale_y ** 2)
    wheel_radius *= radius_scale

    body = world.CreateDynamicBody(position=(x_offset, y_offset))

    for i in range(len(chassis_vertices)):
        vs = [(0.,0.), chassis_vertices[i], chassis_vertices[(i + 1) % len(chassis_vertices)]]
        body.CreatePolygonFixture(shape=b2PolygonShape(vertices=vs),
                density=density)
    # chassis = world.CreateDynamicBody(
    #     position=(x_offset, y_offset),
    #     fixtures=b2FixtureDef(
    #
    #     )
    # )
    # chassis = world.CreateDynamicBody(
    #     position=(x_offset, y_offset),
    #     fixtures=b2FixtureDef(
    #         shape=b2PolygonShape(vertices=chassis_vertices[3:6]),
    #
    #         density=density,
    #     )
    # )

    wheels, springs = [], []
    wheel_xs = [-wheel_separation * scale_x /
                2.0, wheel_separation * scale_x / 2.0]
    for x, torque, drive in zip(wheel_xs, wheel_torques, wheel_drives):
        wheel = world.CreateDynamicBody(
            position=(x_offset + x, y_offset - wheel_radius),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=wheel_radius),
                density=density,
            )
        )
        print ("POZYCJA: ", wheel.position)
        spring = world.CreateWheelJoint(
            bodyA=body,
            bodyB=wheel,
            anchor=wheel.position,
            axis=wheel_axis,
            motorSpeed=0.0,
            maxMotorTorque=torque,
            enableMotor=drive,
            frequencyHz=hz,
            dampingRatio=zeta
        )

        wheels.append(wheel)
        springs.append(spring)

    return body, wheels, springs


class WheelRepresentation:
    def __init__(self):
        random()
    
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
        self.wheelVertex = np.random.rand()
        self.axleAngle = np.random.rand()
        self.wheelRadius = np.random.rand()


class CarRepresentation:
    def __init__(self, damping_ratio, body_vectors, wheels):
        # body_vectors N x 2
        self.chromosome = \
            np.hstack([damping_ratio, body_vectors.reshape(-1), np.hstack([wheel.get_chromosome() for wheel in wheels])])

        self.body_vec_num = body_vectors.shape[0]
        self.wheel_num = len(wheels)

    def put_to_world(self, world, offset, scale, hz, zeta, density, max_torque):
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

        return main_body, wheels, springs

    def get_chromosome(self):
        return self.chromosome
        
    def random(self):
        dampingRatio = random()
        body_directions = np.rand(8)
        body_magnitudes = np.rand(8)
        wheels = []
        for i in range(2): # hardcoded number of wheels
            wheels += WheelRepresentation()

        self.chromosome = \
            np.hstack([dampingRatio, body_directions, body_magnitudes] \
            + [wheel.get_chromosome() for wheel in wheels])


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

    def __init__(self):
        super(Playground, self).__init__()
        
        terrain = Terrain(100)
        
        # create some terrain
        terrain.put_to_world(self.world)

        # The ground -- create some terrain

        # Teeter
        """
        body = self.world.CreateDynamicBody(
            position=(140, 0.90),
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(10, 0.25)),
                density=1.0,
            )
        )

        self.world.CreateRevoluteJoint(
            bodyA=ground,
            bodyB=body,
            anchor=body.position,
            lowerAngle=-8.0 * b2_pi / 180.0,
            upperAngle=8.0 * b2_pi / 180.0,
            enableLimit=True,
        )
        # Bridge
        create_bridge(self.world, ground, (2.0, 0.25),
                      (161.0, -0.125), self.bridgePlanks)

        # Boxes
        for y_pos in [0.5, 1.5, 2.5, 3.5, 4.5]:
            self.world.CreateDynamicBody(
                position=(230, y_pos),
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(0.5, 0.5)),
                    density=0.5,
                )
            )
        """
        c = CarRepresentation(1., np.array([
            (-1.5, -0.5),
            (1.5, -0.5),
            (1.5, 0.0),
            (0.0, 0.9),
            (-1.15, 0.9),
            (-1.5, 0.2),]),
        [WheelRepresentation([-1., -1], 0., 0.4), WheelRepresentation([1, -1], 0., 0.4)])
        car, wheels, springs = c.put_to_world(self.world, (0.0, 10.), (1, 1), 4., 0.7, 1., 40.)

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

if __name__ == "__main__":
    main(Playground)
