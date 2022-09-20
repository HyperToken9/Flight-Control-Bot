import pygame, random
import numpy as np
import math, time
from PIL import Image
from pynput.mouse import Button, Controller

# AVG = []

# Initalize Pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Background Image
background = pygame.image.load('Flight-Control-Bot/Map.png')

# Creating a Window
screen = pygame.display.set_mode((1920/2, 1080/2))

def dist(x,y):
    distance = (((x[0] - y[0]) ** 2) + ((x[1] - y[1] ) ** 2)) ** (0.5)
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

    if (val == 0):
        # Clockwise orientation
        if (dist(p1, p3) < dist(p2, p3)):
            result = 0
        else:
            result = 100
    else:
        # Counterclockwise orientation
        result =  -1 * val

    # print(result)
    return (result - 0.5)


green_dots = []
red_dot = pygame.image.load('Flight-Control-Bot/red_dot.png')
green_dot = pygame.image.load('Flight-Control-Bot/green_dot.png')

class Plane:
    global screen
    def __init__(self, Angle = 0, offset_Angle = -2, LandAngle = 0, Pos = [750,100], Path = []):

        self.Image_Path = "Flight-Control-Bot/Plane1.png"

        # Angle In Degrees
        self.Angle = Angle#random.randint(0, 180)
        self.OffsetAngle = offset_Angle

        # Images
        self.img_pure = Image.open(self.Image_Path)
        self.img_og =  pygame.image.load(self.Image_Path)
        self.img_gpy = pygame.transform.rotate(self.img_og, offset_Angle + self.Angle)

        # Position
        self.Pos = Pos#[random.randint(0, 1920/2), random.randint(0, 540)]

        # Speed
        self.Speed = 0.4
        self.flying = True

        self.landing_strip = np.array([(372, 192), (565, 248)])

        # self.Tow = False
        self.shrinkage = [i for i in range(80, 10, -3)]
        print(self.shrinkage)

        self.Path = Path#[[200, 200], [300, 300], [400, 200], [500, 300], [600, 200]]

        self.Tow = False

        self.alpha = 255

        self.size = -1
        self.tick = 0

        self.red_dots = []
        for i in self.Path:
            self.red_dots.append(i)

    def turn(self, bank):
        self.Angle += bank
        self.img_gpy = pygame.transform.rotate(self.img_og, self.OffsetAngle + self.Angle)

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

        bank = 5
        fine_bank = 0.01


        if (self.flying == False):
            if (self.tick% 40 == 0):
                print("Tick")
                print("landing: ",self.landing_strip)
                if (self.Path[0] in self.landing_strip):
                    self.fade()



        if (len(self.Path) != 0):
            # if (self.Path[0] not in red_dots):
            #     red_dots.append(self.Path[0])
            dest = self.Path[0]
            head = self.head_pose()
            tail = self.tail_pose()
            mid = (head + tail) / 2

            turn_direction = orientation(head, tail ,dest) * fine_bank
            # print("Ore", orientation(head, tail, dest))
            # print("turnDir", turnDir)
            self.turn(turn_direction)

            if (dist(mid, self.Path[0]) < 15):
                reached = self.Path.pop(0)
                self.red_dots.pop(0)
                # green_dots.append(reached)
                # print("Reached", reached)

        self.Pos = [self.Pos[0] + self.Speed * math.cos(math.radians(self.Angle)),
                    self.Pos[1] - self.Speed * math.sin(math.radians(self.Angle))]

    def land(self):
        if (len(self.LandLoc) == 1):
            self.flying = False

    def draw(self):
        screen.blit(self.img_gpy, self.Pos)
        # Path Visualization
        self.path_vis()

    def Towing(self, mouse_position, click_status):
        # When Clicked Start towing plane with mouse
        if (click_status[0] == True):
            if (dist(mouse_position, (self.Pos[0] + (self.img_pure.size[0]/2),
                                      self.Pos[1] + (self.img_pure.size[1]/2))) < 35):
                if (len(self.Path) > 0):
                    self.Path.clear()
                    self.red_dots.clear()
                self.Tow = True
                # print("Towing")

        if (self.Tow == True):
            if (click_status[0] == False):
                self.Tow = False
                # print("UnTOWED")
            elif (dist(mouse_position, self.landing_strip[0]) < 15):
                self.flying = False
                for i in self.landing_strip:
                    self.Path.append(i)
                    self.red_dots.append(i)
                # print("Locked")
                self.Tow = False;

            else:
                print(mouse_position)
                self.red_dots.append(mouse_position)
                self.Path.append(mouse_position)
                # print(self.Path)

    def head_pose(self):
        # green_dots.append(self.Pos)
        theta = 90
        angle = self.Angle + theta
        head_loc = (self.Pos[0] + 30 + (27 * math.cos(math.radians(self.Angle))
                                            - 2 * math.sin(math.radians(self.Angle))),
                         self.Pos[1] + 30 + (-27 * math.sin(math.radians(self.Angle))
                                              -2 * math.cos(math.radians(self.Angle))))

        # red_dots.append(head_loc)
        return np.array(head_loc)

    def tail_pose(self):
        theta = 90
        angle = self.Angle + theta
        tail_loc = (self.Pos[0] + 30 + (-29 * math.cos(math.radians(self.Angle))),
                    self.Pos[1] + 30 + ( 29 * math.sin(math.radians(self.Angle))))

        # red_dots.append(tail_loc)
        return np.array(tail_loc)

    # def Spin(self):
    #     self.Angle += 1
    #     self.img_gpy = pygame.transform.rotate(self.img_og, self.OffsetAngle + self.Angle)

    def path_vis(self):
        for i in self.red_dots:
            screen.blit(red_dot, (i[0] - 4, i[1] - 4))


class Fleet:

    planes = []

    def spawn(self):
        self.planes.append(Plane())

    def Manage(self, mouse_position, mouse_press_status):
        # if (time.time() == 1000)
        for i in self.planes:
            i.draw()
            i.fly()
            i.Towing(mouse_position, mouse_press_status)
            if(i.alpha < 100):
                self.planes.pop(self.planes.index(i))

    def speacialPlane(self, plane):
        self.planes.append(plane)


test_fleet = Fleet()

# Plane1 h = 37.5685 w = 37.56
plane1 = Plane( Angle = 90, Pos = (20, 170))

test_fleet.speacialPlane(plane1)


# Running Indicator
running = True
h = []
w = []

# GAME LOOP
while running:
    # Screen Color
    screen.fill((255, 255, 255))
    screen.blit(background, (0,0))


    # Loop through pygame functions
    for event in pygame.event.get():
        ## Here we are looking for a very specific event
        ## Which is quit. and when it has occured we change a variable which
        ## causes our program to end
        if event.type == pygame.QUIT:
            running = False


    test_fleet.Manage(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

    # print(pygame.mouse.get_pos())


    ## DEBUGGING TOOLS
    # for i in green_dots:
    #     screen.blit(green_dot, (i[0] - 4, i[1] - 4))


    # if(int(time.time())%10 == 0):
    #     print(pygame.mouse.get_pressed())
    # for i in planes:
    #     i.Head()


    pygame.display.update()



