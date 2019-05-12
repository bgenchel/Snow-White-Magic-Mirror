# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import timeit
import time
import os.path as op
import pdb
import pygame
import speech_recognition as sr
import sys
import pickle
from pathlib import Path
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
# from objloader import *
from classes import *
from tqdm import tqdm

pygame.mixer.init()

CMD = ["mirror mirror on the wall who's the fairest of them all",
        "mirror mirror on the wall who is the fairest of them all"]


SOUND_PATH = op.join(str(Path(op.abspath(__file__)).parents[1]), 'itisyoumyqueen.wav')
PHRASE = pygame.mixer.Sound(SOUND_PATH)



def getCommand(recognizer):
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        cmd = recognizer.recognize_google(audio)
        sys.stderr.write("Google Speech Recognition thinks you said " + cmd)
        return cmd
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")

    return ""


def getFramePath(n):
    fname = 'anim1_' + '0' * (6 - len(str(n))) + str(n) + '.obj'
    return op.join(str(Path(op.abspath(__file__)).parents[1]), 'model', 'animations', 'phrase_1', fname)


def getFrame(n):
    return OBJ(getFramePath(n), swapyz=True)


pygame.init()
viewport = (1200,900)
hx = viewport[0]/2
hy = viewport[1]/2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
# srf = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

# LOAD INITIAL OBJECT AFTER PYGAME INITimport timeit

ANIM_LEN = 250
# if op.exists('anim.pkl'):
    # with open('anim.pkl', 'rb') as fp:
        # FRAMES = pickle.load(fp)
# else:
    # FRAMES = [getFrame(n) for n in tqdm(range(1, ANIM_LEN + 1), desc="- Loading Frames")]
    # with open('anim.pkl', 'wb') as fp:
        # pickle.dump(FRAMES, fp)

FRAMES = [getFrame(n) for n in tqdm(range(1, ANIM_LEN + 1), desc="- Loading Frames")]

obj = FRAMES[0]

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90.0, width/float(height), 1, 100.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

rx, ry = (0,0)
tx, ty = (0,0)
zpos = 5
rotate = move = False

r = sr.Recognizer()
animating = False
frame_count = 1
while 1:
    clock.tick(24)

    if animating:
        obj = FRAMES[frame_count - 1]
        if frame_count >= ANIM_LEN:
            frame_count = 1
            animating = False
        else:
            frame_count += 1

    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            elif e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # RENDER OBJECT
    glTranslate(tx/20., ty/20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(obj.gl_list)

    pygame.display.flip()

    if not animating:
        cmd = getCommand(r)
        if cmd in CMD:
            animating = True
            PHRASE.play()
