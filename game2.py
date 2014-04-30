#credit for the skeleton that got me goiing goes to http://www.nandnor.net/?p=64
#bump.aiff is from https://www.freesound.org/people/timgormly/sounds/170141/ under the CC Atribution License
#yay.wav is from https://www.freesound.org/people/timtube/sounds/69338/ under CC Atribution License
#Sprite Pack is from the Raspberry Pi Raspbian developer pack

import pygame
import math
from pygame import *
import glob

DISPLAY = (1024, 768)
DEPTH = 32
FLAGS = 0
# in blocks, 32 x 24

NEXTLEVEL = pygame.event.Event(pygame.USEREVENT+1)

def play_sound(sound):
    if not pygame.mixer.get_busy():
        pygame.mixer.Sound(sound).play()
def make_level(level, player, entities, platforms):
    x = y = 0
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "E":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)
            if col == "L":
                l = LevelBlock(x,y)
                platforms.append(l)
                entities.add(l)
            x += 32
        y += 32
        x = 0
    entities.add(player)

def main():
    pygame.init()
    screen = display.set_mode(DISPLAY, FLAGS, DEPTH)
    display.set_caption("Sonar_Mario")
    timer = time.Clock()
    #display.toggle_fullscreen()

    up = down = left = right = False
    bg = Surface((32,32))
    bg.convert()
    bg.fill(Color("#000000"))
    entities = pygame.sprite.Group()
    player = Player(32, 32)
    platforms = []
    #ascii levels
    levels = []
    current_level = 0
    #get all of the level files
    levelnames = glob.glob('data/*.lvl')
    for l in levelnames:
        level = [line.strip() for line in open(l)]
        levels.append(level)
    # build the level
    #NOTE that all blocks are treated as 32*32 to keep the level in the window. Not all sprites are 32*32
    make_level(levels[current_level], player, entities, platforms)

    #sonar objects
    sonars = []
    sonar_num = 0
    while 1:
        timer.tick(25)
        sonar = False
        for e in pygame.event.get():
            UD, LR = 0, 0
            if e.type == QUIT: raise SystemExit, "QUIT"
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit, "ESCAPE"
            if e.type == USEREVENT+1:
                print "GOTO NEXT LEVEL"
                entities = pygame.sprite.Group()
                platforms = []
                player = Player(32,32)
                current_level +=1
                make_level(levels[current_level], player, entities, platforms)
            if e.type == USEREVENT+2: # sonar dead
                play_sound("data/sonar.ogg")
                if e.sonar in sonars:
                    print 'sonar ' , e.sonar.snum , ' dead'
                    entities.remove(e.sonar)
                    sonars.remove(e.sonar)


            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True

            if e.type == KEYDOWN and e.key == K_w:
                sonar = True
                UD = -1
            if e.type == KEYDOWN and e.key == K_a:
                sonar = True
                LR = -1
            if e.type == KEYDOWN and e.key == K_s:
                sonar = True
                UD = 1
            if e.type == KEYDOWN and e.key == K_d:
                sonar = True
                LR = 1

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_DOWN:
                down = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False

        # draw background
        for y in range(24):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        # update player, draw everything else
        player.update(up, down, left, right, platforms)

        #also create sonar if needed
        if sonar:
            sonar_element = Sonar(player.rect.left, player.rect.top, LR, UD, sonar_num)
            sonars.append(sonar_element)
            entities.add(sonar_element)
            sonar_num += 1
        for s in sonars:
            s.update(platforms)
        entities.draw(screen)

        pygame.display.flip()

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        image = pygame.image.load("data/bat.gif")
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        self.image = image
        self.rect = Rect(x, y, 32, 32)

    def update(self, up, down, left, right, platforms):
        if up:
            self.yvel = -1
        if down:
            self.yvel = 6
        if left:
            self.xvel = -3
        if right:
            self.xvel = 3
        if not(left or right):
            self.xvel = 0
        if not(up or down):
            self.yvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        # do y-axis collisions
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    play_sound("data/win.flac")
                    event.post(event.Event(QUIT))
                elif isinstance(p, LevelBlock):
                    play_sound("data/yay.wav")
                    event.post(NEXTLEVEL)
                else:
                    play_sound("data/bump.aiff")
                if xvel > 0: self.rect.right = p.rect.left
                if xvel < 0: self.rect.left = p.rect.right
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0: self.rect.top = p.rect.bottom

class Platform(Entity):
    def __init__(self, x, y, sprite="data/Tree_Short.png"):
        Entity.__init__(self)
        image = pygame.image.load(sprite)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        self.image = image
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y, "data/gem1.png")

class LevelBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y, "data/gem1.png")

class Sonar(Entity):
    def __init__(self, x, y, LEFTRIGHT=0, UPDOWN=0, sonar_num=0):
        print "New sonar at ",x, y, " with LR/UD ", LEFTRIGHT, UPDOWN
        #LEFTRIGHT is a int multiplier (1 or -1) that determines the LR direction of the sonar. UPDOWN is the same for the vertical
        Entity.__init__(self)
        self.snum = sonar_num
        self.speed = 9

        self.init_time = time.get_ticks()

        self.image = Surface((1,1))
        self.image.convert()
        self.image.fill(Color("#DDDDDD"))
        self.rect = Rect(x+15, y+15, 1 , 1 )

        self.LR = LEFTRIGHT
        self.UD = UPDOWN
        #create a psudo sprite place holder
        self.init_rect = Entity()
        self.init_rect.rect = Rect(x+15,y+15, 1, 1)
        play_sound("data/sonar.ogg")

    def update(self, platforms):
        #print self.rect.left, self.rect.top
        self.rect.left += (self.speed * self.LR)
        self.collide((self.speed * self.LR) , 0, platforms)
        self.rect.top += (self.speed * self.UD)
        self.collide(0, (self.speed * self.UD), platforms)

    def collide(self, xvel, yvel, platforms):
        if sprite.collide_rect(self, self.init_rect):
            # is it back where it started
            if (time.get_ticks() - self.init_time) > 50:
                event.post(event.Event(pygame.USEREVENT+2, sonar = self )) # put sonar object in event for 'is' test
        for p in platforms:
            if sprite.collide_rect(self, p):
                print 'sonar collision'
                if xvel != 0:
                    self.LR *= -1
                if yvel != 0:
                    self.UD *= -1
if __name__ == "__main__": main()
