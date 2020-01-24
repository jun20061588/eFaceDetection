#
import sys
import os
import random
import numpy
import cv2
import struct
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
"""
#
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('src', help='CaltechFaces source folder')
args = parser.parse_args()
"""

# h, w, im[h*w]
def write_rid_to_stdout(im):
    h = im.shape[0]
    w = im.shape[1]
    hw = struct.pack('ii', h, w)
    pixels = struct.pack('%sB' % h*w, *im.reshape(-1))
    sys.stdout.buffer.write(hw)
    sys.stdout.buffer.write(pixels)

# h, w, im[h*w], len(bboxes), box[3]xlen(bboxes)
def write_sample_to_stdout(img, bboxes):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    write_rid_to_stdout(img)
    sys.stdout.buffer.write(struct.pack('i', len(bboxes)))
    for box in bboxes:
        sys.stdout.buffer.write(struct.pack('iii', box[0], box[1], box[2]))


def visualize_bboxes(img, bboxes):
    for box in bboxes:
        cv2.circle(img, (int(box[1]), int(box[0])), int(
            box[2]/2.0), (0, 0, 255), thickness=2)
    cv2.imshow('...', img)
    cv2.waitKey(0)

# change scale, flip to get more positive samples
def export_img_and_boxes(img, bboxes):
    for i in range(0, 8): # 7
		# resize
        scalefactor = 0.7 + 0.6*numpy.random.random()
        resized_img = cv2.resize(img, (0, 0), fx=scalefactor, fy=scalefactor)
		# flip
        flip = numpy.random.random() < 0.5
        if flip:
            resized_img = cv2.flip(resized_img, 1)

        resized_bboxes = []
        for box in bboxes:
            if flip:
                resized_box = (int(scalefactor*box[0]), resized_img.shape[1] - int(scalefactor*box[1]), int(scalefactor*box[2]))
            else:
                resized_box = (int(scalefactor*box[0]), int(scalefactor*box[1]), int(scalefactor*box[2]))
            if resized_box[2] >= 24:
                resized_bboxes.append(resized_box)

        write_sample_to_stdout(resized_img, resized_bboxes)
        #visualize_bboxes(resized_img, resized_bboxes)


annots = open(os.path.join('./caltechfaces/',
                           'WebFaces_GroundThruth.txt'), 'r')
imgpaths = []
faces = []
dict = {}

for line in annots.readlines():
    if line.strip() != '':
        imgname = line.split()[0]
        # print(imgname)
        if imgname in dict:
            i = dict[imgname]
            faces[i].append([float(x) for x in line.split()[1:]])
        else:
            dict[imgname] = len(imgpaths)
            imgpaths.append(os.path.join('./caltechfaces/', imgname))
            faces.append([[float(x) for x in line.split()[1:]]])

for i in range(0, len(imgpaths)):
    img = cv2.imread(imgpaths[i])
    # print(imgpaths[i])
    bboxes = []
    for face in faces[i]:
        eyedist = ((face[0]-face[2])**2 + (face[1]-face[3])**2)**0.5
        r = (face[1]+face[3])/2.0 + 0.25*eyedist
        c = (face[0]+face[2])/2.0
        s = 2.0*1.5*eyedist
        bboxes.append((r, c, s))
    #export_img_and_boxes(img, bboxes)

        fig, ax = plt.subplots(1)
        ax.set_aspect('equal')
        plt.imshow(img)

        i = 1
        x = []
        y = []
        for i in range(4):
            x.append(face[i*2])
            y.append(face[i*2+1])
        i = 1
        for xx, yy in zip(x, y):
            circ = Circle((xx, yy), i)
            i = i+1
            ax.add_patch(circ)
        
        plt.show()
        exit(0)

