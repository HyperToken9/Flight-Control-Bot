import pygame, random
import numpy as np
import math, time
from PIL import Image
from pynput.mouse import Button, Controller

# TODO:
# Spawn Optimization
# Landing Bug

# Initialize Pygame
pygame.init()

# Setup the clock for a decent frame rate
clock = pygame.time.Clock()

# Background Image
background = pygame.image.load('Flight-Control-Bot/Map.png')

# Creating a Window
screen_width = 1920 / 2
screen_height = 1080 / 2
screen = pygame.display.set_mode((1920 / 2, 1080 / 2))

green_dots = []
red_dot = pygame.image.load('Flight-Control-Bot/red_dot.png')
green_dot = pygame.image.load('Flight-Control-Bot/green_dot.png')


def dist(x, y):
    distance = (((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2)) ** 0.5
    return distance


def orientation(p1, p2, p3):
    # to find the orientation of
    # an ordered triplet (p1,p2,p3)
    # function returns the following values:
    # 0 : Collinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise
    # result = [clock/anti, behind?]
    result = 0
    val = (float(p2[1] - p1[1]) * (p3[0] - p2[0])) - \
          (float(p2[0] - p1[0]) * (p3[1] - p2[1]))
    # print(val)

    if val == 0:
        # Clockwise orientation
        if dist(p1, p3) < dist(p2, p3):
            result = 0
        else:
            result = 100
    else:
        # Counterclockwise orientation
        result = -1 * val

    # print(result)
    return result - 0.5


class Plane(pygame.sprite.Sprite):

    def __init__(self, spawn_at=[750, 100], offset_angle=-2):
        print("Plane")
        super().__init__()
        # Images
        self.image_path = "Flight-Control-Bot/Plane1.png"
        self.image_aligned = pygame.image.load(self.image_path)
        self.image = pygame.image.load(self.image_path)
        self.rect = self.image.get_rect()
        # self.img_pure = Image.open(self.Image_Path)
        # self.img_gpy = pygame.transform.rotate(self.img_og, offset_angle)

        # Speed
        self.Speed = 0.4
        self.flying = True

        # Position
        self.position = spawn_at  # [random.randint(0, 1920/2), random.randint(0, 540)]

        # Angle In Degrees
        self.Angle = self.angle_to_center()  # random.randint(0, 180)
        print(f"{self.Angle}")

        self.OffsetAngle = offset_angle

        self.landing_strip = np.array([(372, 192), (565, 248)])

        # self.Tow = False
        self.shrinkage = [j for j in range(80, 10, -3)]

        self.Path = []

        self.Tow = False

        self.alpha = 255

        self.size = -1
        self.tick = 0

        self.red_dots = []
        for i in self.Path:
            self.red_dots.append(i)
        self.turn(0)

    # # Turns the plane by a certain bank angle
    def turn(self, bank):
        self.Angle += bank
        self.image = pygame.transform.rotate(self.image_aligned, self.OffsetAngle + self.Angle)
        self.rect = self.image.get_rect()

    # Turns the plane to a Certain Angle
    def turn_to(self, angle):
        self.Angle = angle
        self.image = pygame.transform.rotate(self.image_aligned, self.OffsetAngle + self.Angle)
        self.rect = self.image.get_rect()

    # Starts to fade the sprite on approaching landing

    def update(self):
        # for i in self.planes:
        #     i.draw()
        #     i.fly()
        #     i.Towing(mouse_position, mouse_press_status)
        #     if i.alpha < 100:
        #         self.planes.pop(self.planes.index(i))
        self.draw()
        self.fly()
        self.Towing(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

    def fade(self):
        self.img_og.fill((255, 255, 255, int(self.alpha)), special_flags=pygame.BLEND_RGBA_MULT)
        self.alpha /= 1.2

    # def Shrink(self, size):
    #     if (self.size != -1):
    #         self.Pos = [self.Pos[0] + 5,
    #                     self.Pos[1] + 5]
    #     self.img_og = pygame.transform.scale(self.img_og, (size, size))
    #     self.size = size

    def fly(self):
        self.tick += 1

        # Tuning Turing Intensity
        fine_bank = 0.01

        if not self.flying:
            if self.tick % 40 == 0:
                # print("Tick")
                # print("landing: ",self.landing_strip)
                if self.Path[0] in self.landing_strip:
                    self.fade()

        if len(self.Path) != 0:
            # if (self.Path[0] not in red_dots):
            #     red_dots.append(self.Path[0])
            dest = self.Path[0]
            head = self.head_pose()
            tail = self.tail_pose()
            mid = (head + tail) / 2

            turn_direction = orientation(head, tail, dest) * fine_bank
            # print("Ore", orientation(head, tail, dest))
            # print("turnDir", turnDir)
            self.turn(turn_direction)

            if dist(mid, self.Path[0]) < 15:
                reached = self.Path.pop(0)
                self.red_dots.pop(0)
                # green_dots.append(reached)
                # print("Reached", reached)

        self.restrict_fly_zone()

        self.position = [self.position[0] + self.Speed * math.cos(math.radians(self.Angle)),
                         self.position[1] - self.Speed * math.sin(math.radians(self.Angle))]

    # Keeps the plane bound to the screen
    def restrict_fly_zone(self):
        # No restriction during early flight

        if self.tick < 500:
            return

        if -25 < self.position[0] < screen_width - 10 and -25 < self.position[1] < screen_height - 10:
            return

        self.turn_to(self.angle_to_center())
        print("Out of Bounds")

    def land(self):
        if len(self.LandLoc) == 1:
            self.flying = False

    def draw(self):
        # print( self.position)
        self.rect.center = self.position
        # screen.blit(self.img_gpy, self.position)
        # Path Visualization
        # Comment to disable Path Visualization
        self.path_vis()

    def Towing(self, mouse_position, click_status):
        # When Clicked Start towing plane with mouse
        if click_status[0]:
            if self.rect.collidepoint(mouse_position):
                if len(self.Path) > 0:
                    self.Path.clear()
                    self.red_dots.clear()
                self.Tow = True
                # print("Towing")

        if self.Tow:
            if not click_status[0]:
                self.Tow = False
                # print("UnTOWED")
            elif dist(mouse_position, self.landing_strip[0]) < 15:
                self.flying = False
                for i in self.landing_strip:
                    self.Path.append(i)
                    self.red_dots.append(i)
                # print("Locked")
                self.Tow = False

            else:
                # print(mouse_position)
                self.red_dots.append(mouse_position)
                self.Path.append(mouse_position)
                # print(self.Path)

    # Give angle to center from current position
    def angle_to_center(self):
        screen_center = [screen_width / 2, screen_height / 2]
        return self.angle(self.position, screen_center)

    @staticmethod
    def angle(coord1, coord2):

        numerator =  coord1[1] - coord2[1]
        denominator = coord2[0] - coord1[0]
        degrees = math.degrees(math.atan2(numerator, denominator))

        return degrees

    def head_pose(self):
        # green_dots.append(self.Pos)
        theta = 90
        angle = self.Angle + theta
        head_loc = (self.position[0] + 30 + (27 * math.cos(math.radians(self.Angle))
                                             - 2 * math.sin(math.radians(self.Angle))),
                    self.position[1] + 30 + (-27 * math.sin(math.radians(self.Angle))
                                             - 2 * math.cos(math.radians(self.Angle))))

        # red_dots.append(head_loc)
        return np.array(head_loc)

    def tail_pose(self):
        theta = 90
        angle = self.Angle + theta
        tail_loc = (self.position[0] + 30 + (-29 * math.cos(math.radians(self.Angle))),
                    self.position[1] + 30 + (29 * math.sin(math.radians(self.Angle))))

        # red_dots.append(tail_loc)
        return np.array(tail_loc)

    # def Spin(self):
    #     self.Angle += 1
    #     self.img_gpy = pygame.transform.rotate(self.img_og, self.OffsetAngle + self.Angle)

    def path_vis(self):
        for i in self.red_dots:
            screen.blit(red_dot, (i[0] - 4, i[1] - 4))


class Fleet:

    def __init__(self):

        self.planes_group =  pygame.sprite.Group()
        print(dir(self.planes_group))
    def Manage(self):
        # if (time.time() == 1000)
        self.planes_group.draw(screen)
        self.planes_group.update()


    def specialPlane(self, plane):
        self.planes.append(plane)

    def Spawner(self):
        should_spawn = random.choices([1, 0], weights=(1, 10000), k=1)[0]
        if should_spawn:
            self.spawn()

    def spawn(self):
        spawn_spots = {'up': [[0, -60], [screen_width, -10]],
                       'down': [[0, screen_height - 60], [screen_width, screen_height]],
                       'left': [[-60, 0], [0, screen_height]],
                       'right': [[screen_width, 0], [screen_width + 60, screen_height]]}

        _, spawn_rect = random.choice(list(spawn_spots.items()))

        spawn_location = [random.randint(spawn_rect[0][0], spawn_rect[1][0]),
                          random.randint(spawn_rect[0][1], spawn_rect[1][1])]

        plane_sprite = Plane(spawn_at=spawn_location)

        self.planes_group.add(plane_sprite)


# test_fleet = Fleet()
test_fleet = Fleet()


# Special Plane Instance
# Plane1 h = 37.5685 w = 37.56
# plane1 = Plane( Angle = 90, Pos = (20, 170))
# test_fleet.specialPlane(plane1)

# Running Indicator
running = True
h = []
w = []
test_fleet.spawn()

# GAME LOOP
while running:
    # Screen Color
    screen.fill((255, 255, 255))
    screen.blit(background, (0, 0))

    # Loop through pygame functions
    for event in pygame.event.get():
        # Here we are looking for a very specific event
        # Which is quit. and when it has occurred we change a variable which
        # causes our program to end
        if event.type == pygame.QUIT:
            running = False

    test_fleet.Spawner()
    test_fleet.Manage()

    # DEBUGGING TOOLS
    for i in green_dots:
        screen.blit(green_dot, (i[0] - 4, i[1] - 4))

    # if(int(time.time())%10 == 0):
    #     print(pygame.mouse.get_pressed())
    # for i in planes:
    #     i.Head()

    pygame.display.update()
