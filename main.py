import pygame, random
import math, time
from PIL import Image
from pynput.mouse import Button, Controller

# AVG = []

# Initalize Pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Background Image
background = pygame.image.load('Map.png')

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



red_dots = []
green_dots = []
red_dot = pygame.image.load('red_dot.png')
green_dot = pygame.image.load('green_dot.png')

class Plane:
    global screen
    def __init__(self, image_path , Speed,
                 Angle = 0, offset_Angle = -2, LandAngle = 0,
                 LandLoc = [(378 ,195), (467,221)], Pos = [750,100]):

        self.Image_Path = image_path

        # Angle In Degrees
        self.Angle = Angle#random.randint(0, 180)
        self.OffsetAngle = offset_Angle

        # Images
        self.img_pure = Image.open(image_path)
        self.img_og =  pygame.image.load(self.Image_Path)
        self.img_gpy = pygame.transform.rotate(self.img_og, offset_Angle + self.Angle)

        # Position
        self.Pos = Pos#[random.randint(0, 1920/2), random.randint(0, 540)]

        # Speed
        self.Speed = Speed

        self.Active = True

        self.LandLoc = LandLoc

        self.LandAngle = 30

        # self.Tow = False

        self.Path = []#[[200, 200], [300, 300], [400, 200], [500, 300], [600, 200]]

        self.Tow = False

        self.shrinkage = [50, 40 , 30, 20, 10]

        self.tick = 0

        for i in self.Path:
            red_dots.append(i)

    def Turn(self, bank):
        self.Angle += bank
        self.img_gpy = pygame.transform.rotate(self.img_og, self.OffsetAngle + self.Angle)


    def fly(self):
        self.tick += 1

        bank = 5
        fine_bank = 0.01

        if (self.Pos[0] > 875 and math.cos(math.radians(self.Angle)) > 0 or
                self.Pos[1] < 10 and math.cos(math.radians(self.Angle - 90)) > 0 or
                self.Pos[0] < 10 and math.cos(math.radians(self.Angle - 180) > 0) or
                self.Pos[1] > 450 and math.cos(math.radians(self.Angle + 90) > 0)):

            self.Turn(bank)

        if (self.Active == False):
            if (self.tick% 20 == 0):
                print("Tick")
                if (self.Path[0] == self.LandLoc[1]):
                    s = self.shrinkage.pop(0)
                    self.img_gpy = pygame.transform.scale(self.img_og, (s,s))



        #TODO: Try Setting Speed to 0 and turning until next point is in angle range
        if (len(self.Path) != 0):
            # if (self.Path[0] not in red_dots):
            #     red_dots.append(self.Path[0])
            dest = self.Path[0]
            head = self.Head()
            tail = self.Tail()


            # AVG.append(orientation(head,tail,dest))
            turnDir = orientation(head, tail ,dest) * fine_bank
            # print("Ore", orientation(head, tail, dest))
            # print("turnDir", turnDir)
            self.Turn(turnDir)
            if (dist(self.Head(), self.Path[0]) < 20):
                reached = self.Path.pop(0)
                red_dots.pop(0)
                # green_dots.append(reached)
                # print("Reached", reached)

        self.Pos = [self.Pos[0] + self.Speed * math.cos(math.radians(self.Angle)),
                    self.Pos[1] - self.Speed * math.sin(math.radians(self.Angle))]



    # def land(self):
    #     if (dist(self.Pos, self.LandLoc) == 0):
    #         self.Active = False


    def draw(self):
        screen.blit(self.img_gpy, self.Pos)

    def Towing(self, mouse_position, click_status):
        if (click_status[0] == True):
            if (dist(mouse_position, (self.Pos[0] + (self.img_pure.size[0]/2),
                                      self.Pos[1] + (self.img_pure.size[1]/2))) < 35):
                if (len(self.Path) > 0):
                    self.Path.clear()
                    red_dots.clear()
                self.Tow = True
                print("Towing")

        if (self.Tow == True):
            if (click_status[0] == False):
                self.Tow = False
                print("UnTOWED")
            elif (dist(mouse_position, self.LandLoc[0]) < 20):
                self.Active = False
                for i in self.LandLoc:
                    self.Path.append(i)
                    red_dots.append(i)
                print("Locked")
                self.Tow = False;

            else:
                print(mouse_position)
                red_dots.append(mouse_position)
                self.Path.append(mouse_position)
                # print(self.Path)





    def Head(self):
        # green_dots.append(self.Pos)
        theta = 90
        angle = self.Angle + theta
        head_loc = (self.Pos[0] + 30 + (27 * math.cos(math.radians(self.Angle))
                                            - 2 * math.sin(math.radians(self.Angle))),
                         self.Pos[1] + 30 + (-27 * math.sin(math.radians(self.Angle))
                                              -2 * math.cos(math.radians(self.Angle))))

        # red_dots.append(head_loc)
        return head_loc

    def Tail(self):
        theta = 90
        angle = self.Angle + theta
        tail_loc = (self.Pos[0] + 30 + (-29 * math.cos(math.radians(self.Angle))),
                    self.Pos[1] + 30 + ( 29 * math.sin(math.radians(self.Angle))))

        # red_dots.append(tail_loc)
        return tail_loc

    def Spin(self):
        self.Angle += 1
        self.img_gpy = pygame.transform.rotate(self.img_og, self.OffsetAngle + self.Angle)





# Plane1 h = 37.5685 w = 37.56
plane1 = Plane('Plane1.png', Angle = -10, Speed = 1, Pos = (50, 50))
# plane2 = Plane('Plane1.png', Angle = 180 , Speed = 0, Pos = (200, 200))
# plane3 = Plane('Plane1.png', Angle = -90 , Speed = 0, Pos = (50, 200))
# plane4 = Plane('Plane1.png', Angle = 90 , Speed = 0, Pos = (200, 50))
# plane5 = Plane('Plane1.png', offset_Angle = 0, Speed = 0, Pos = (500, 500))


planes = [plane1]#, plane2, plane3, plane4, plane5]

# Running Indicator
running = True
h = []
w = []
c =0
# GAME LOOP
while running:
    # Screen Color
    screen.fill((255, 255, 255))
    screen.blit(background, (0,0))
    c += 1



    # Loop through pygame fucntions
    for event in pygame.event.get():
        ## Here we are looking for a very specific event
        ## Which is quit. and when it has occured we change a variable which
        ## causes our program to end
        if event.type == pygame.QUIT:
            running = False

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     pos = pygame.mouse.get_pos()
            # plane1.Path_Track(pos)
            # print(pos)
            # plane1.drag(pos)

    # if(c%10 == 0):
    #     print(pygame.mouse.get_pressed())
        # for i in planes:
        #     i.Head()

    for i in green_dots:
        screen.blit(green_dot, (i[0] - 4, i[1] - 4))

    for i in red_dots:
        screen.blit(red_dot, (i[0] - 4, i[1] - 4))

    for i in planes:
        i.draw()
        i.fly()
        i.Towing(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
        # i.Path_Track(pygame.mouse.get_pos())

    # print(pygame.mouse.get_pos())
    clock.tick(30)
    pygame.display.update()



