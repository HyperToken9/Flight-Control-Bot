import pygame, random
import numpy as np
import math, time
from PIL import Image
from pynput.mouse import Button, Controller

# TODO:
# Spawn Optimization
# Landing Bug


# Setup the clock for a decent frame rate
clock = pygame.time.Clock()

# Creating a Window
screen_width = 1920 / 2
screen_height = 1080 / 2
screen = pygame.display.set_mode((1920 / 2, 1080 / 2))

green_dots = []
background = pygame.image.load('Flight-Control-Bot/map.png')
red_dot = pygame.image.load('Flight-Control-Bot/red_dot.png')
green_dot = pygame.image.load('Flight-Control-Bot/green_dot.png')


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
        if math.dist(p1, p3) < math.dist(p2, p3):
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
        self.true_rect = self.image_aligned.get_rect()

        self.image = pygame.image.load(self.image_path)
        self.rect = self.image.get_rect()
        # self.img_pure = Image.open(self.Image_Path)
        # self.img_gpy = pygame.transform.rotate(self.img_og, offset_angle)

        # Speed
        self.speed = 0.4
        self.flying = True

        # Position
        self.position = [300, 300]#spawn_at  # [random.randint(0, 1920/2), random.randint(0, 540)]

        # Angle In Degrees
        self.angle =  self.angle_to_center()  # random.randint(0, 180)
        print(f"{self.angle}")

        self.OffsetAngle = offset_angle

        self.landing_strip = np.array([(372, 192), (565, 248)])

        # self.Tow = False
        self.shrinkage = [j for j in range(80, 10, -3)]

        self.way_points = []

        self.towing_status = False

        self.alpha = 255

        self.size = -1
        self.tick = 0

        self.red_dots = []
        for dot in self.way_points:
            self.red_dots.append(dot)
        self.turn(0)


    # # Turns the plane by a certain bank angle
    def turn(self, bank):
        self.angle += bank
        self.image = pygame.transform.rotate(self.image_aligned, self.OffsetAngle + self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        # print(dir(self.rect))
        # print(self.rect)

    # Turns the plane to a Certain Angle
    def turn_to(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.image_aligned, self.OffsetAngle + self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


    # Starts to fade the sprite on approaching landing

    def update(self, click_pos, click_status):
        self.fly()  # FLYs The Plane to NEW Location
        self.draw()  # DRAWs the Game Sprite to NEW Location
        self.Towing(click_pos, click_status)


    def fade(self):
        self.img_og.fill((255, 255, 255, int(self.alpha)), special_flags=pygame.BLEND_RGBA_MULT)
        self.alpha /= 1.2

    # def Shrink(self, size):
    #     if (self.size != -1):
    #         self.Pos = [self.Pos[0] + 5,
    #                     self.Pos[1] + 5]
    #     self.img_og = pygame.transform.scale(self.img_og, (size, size))
    #     self.size = size
    # def Stanley_Control(self):
    #     k = 100
    #
    #     distances_to_waypoints = list(map(math.dist, [self.position] * len(self.way_points), self.way_points))
    #     # print(distances_to_waypoints)
    #     smallest_distance = min(distances_to_waypoints)
    #     closest_point_index = distances_to_waypoints.index(smallest_distance)
    #
    #     prev_wp = self.way_points[closest_point_index - 1]
    #     next_wp = self.way_points[closest_point_index]
    #
    #     # cross track error
    #     cte_num = (next_wp[0] - prev_wp[0]) * (prev_wp[1] - self.position[1]) - (prev_wp[0] - self.position[0]) * (next_wp[1] - prev_wp[1])
    #
    #     cte_den = math.dist(prev_wp, next_wp)
    #     cross_track_error = cte_num / (cte_den + 1)
    #
    #     theta_track = math.atan2(next_wp[1] - prev_wp[1], next_wp[0] - prev_wp[0])
    #
    #     heading_error = theta_track - self.angle
    #
    #     delta = heading_error + math.atan2(self.speed, k * cross_track_error)
    #
    #     return delta

    def fly(self):
        self.tick += 1

        # Tuning Turing Intensity
        fine_bank = 0.01

        if not self.flying:
            if self.tick % 40 == 0:
                # print("Tick")
                # print("landing: ",self.landing_strip)
                if self.way_points[0] in self.landing_strip:
                    self.fade()

        if len(self.way_points) != 0:
            # if (self.Path[0] not in red_dots):
            #     red_dots.append(self.Path[0])
            goal = self.way_points[0]
            head = self.head_pose()
            tail = self.tail_pose()
            mid = (head + tail) / 2

            turn_direction = orientation(head, tail, goal) * fine_bank
            # print("Ore", orientation(head, tail, dest))
            # print("turnDir", turnDir)
            self.turn(turn_direction)

            if math.dist(head, self.way_points[0]) < 2 or math.dist(mid,self.way_points[0]) < 8:
                reached = self.way_points.pop(0)
                self.red_dots.pop(0)

        self.restrict_fly_zone()

        self.position = [self.position[0] + self.speed * math.cos(math.radians(self.angle)),
                         self.position[1] - self.speed * math.sin(math.radians(self.angle))]

    # Keeps the plane bound to the screen
    def restrict_fly_zone(self):
        # No restriction during early flight

        if self.tick < 500:
            return

        if self.is_out_of_bounds():
            self.turn_to(self.angle_to_center())
            print("Out of Bounds")

    # Checks if plane has left screen
    def is_out_of_bounds(self):
        if -25 < self.position[0] < screen_width - 10 and -25 < self.position[1] < screen_height - 10:
            return False
        return True


    def land(self):
        if len(self.LandLoc) == 1:
            self.flying = False

    def draw(self):
        self.rect.center = self.position
        self.path_vis()

    def Towing(self, mouse_position, click_status):
        # When Clicked Start towing plane with mouse
        if click_status[0] and ~self.towing_status:
            if self.rect.collidepoint(mouse_position):
                if len(self.way_points) > 0:
                    self.way_points.clear()
                    self.red_dots.clear()
                self.towing_status = True
                # print("Towing")

        if self.towing_status:
            if not click_status[0]:
                self.towing_status = False
                # print("UnTOWED")
            elif math.dist(mouse_position, self.landing_strip[0]) < 15:
                self.flying = False
                for i in self.landing_strip:
                    self.way_points.append(i)
                    self.red_dots.append(i)
                # print("Locked")
                self.towing_status = False

            else:
                self.red_dots.append(mouse_position)
                self.way_points.append(mouse_position)

    # Give angle to center from current position
    def angle_to_center(self):
        screen_center = [screen_width / 2, screen_height / 2]
        # print(type(self.position), type(screen_center))
        return self.angle_of_points(self.position, screen_center)

    @staticmethod
    def angle_of_points(coord1, coord2):

        numerator = coord1[1] - coord2[1]
        denominator = coord2[0] - coord1[0]
        degrees = math.degrees(math.atan2(numerator, denominator))

        return degrees

    def head_pose(self):

        w, _ = self.true_rect.size

        delta = self.rotate(np.array([w/2, 0]), degrees= -1 * self.angle)

        head_loc = self.position + delta

        # red_dots.append(head_loc)
        return head_loc

    def tail_pose(self):
        w, _ = self.true_rect.size

        delta = self.rotate(np.array([-w / 2, 0]), degrees=-1 * self.angle)

        tail_loc = self.position + delta

        # red_dots.append(head_loc)
        return tail_loc

    # def Spin(self):
    #     self.Angle += 1
    #     self.img_gpy = pygame.transform.rotate(self.img_og, self.OffsetAngle + self.Angle)

    def path_vis(self):
        for dot in self.red_dots:
            screen.blit(red_dot, (dot[0] - 4, dot[1] - 4))

    @staticmethod
    def rotate(p, origin=(0, 0), degrees=0):
        angle = np.deg2rad(degrees)
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])
        o = np.atleast_2d(origin)
        p = np.atleast_2d(p)
        return np.squeeze((R @ (p.T - o.T) + o.T).T)

class Fleet:

    def __init__(self):
        self.planes_group = pygame.sprite.Group()
        # print(dir(self.planes_group))

    def Manage(self):
        # if (time.time() == 1000)
        self.planes_group.draw(screen)
        self.planes_group.update(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

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

    # test_fleet.Spawner()
    test_fleet.Manage()

    # DEBUGGING TOOLS
    for i in green_dots:
        screen.blit(green_dot, (i[0] - 4, i[1] - 4))

    # if(int(time.time())%10 == 0):
    #     print(pygame.mouse.get_pressed())
    # for i in planes:
    #     i.Head()

    pygame.display.update()
