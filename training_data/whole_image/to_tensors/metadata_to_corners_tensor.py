#!/usr/bin/env python

# Make a tensor containing grid corner locations from the image metadata

import os
import sys
import math

import tensorflow as tf
import numpy
import pickle

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rootd", help="root directory", type=str, required=True)
parser.add_argument("--docn", help="Document name", type=str, required=True)
args = parser.parse_args()

# Load the metadata
with open(
    "%s/meta/%s.pkl" % (args.rootd, args.docn),
    "rb",
) as pkf:
    mdata = pickle.load(pkf)

# mdata is a dictionary - convert it to a class so contents are attributes
#  and we can share code with tyrImage.
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


mdata = AttrDict(mdata)

# From the metadata, find the corners of the data grid
#  (Eight floats on the range 0-1)
# Functions copied from the ATB2 image class - should reuse that class instead

# Rotate by angle degrees clockwise
def gRotate(self, point, angle=None, origin=None):
    if angle is None:
        angle = self.rotate
    if angle == 0:
        return point
    if origin is None:
        origin = gCentre(self)
    ox, oy = origin[0] * self.pageWidth, origin[1] * self.pageHeight
    px, py = point[0] * self.pageWidth, point[1] * self.pageHeight
    angle = math.radians(angle) * -1
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx / self.pageWidth, qy / self.pageHeight


def gCentre(self):
    return (
        0.5 + self.xshift / self.pageWidth + (self.xscale - 1) * 0.43,
        0.525 + self.yshift / self.pageHeight - (self.yscale - 1) * 0.2,
    )


# Corners of grid
def topLeft(self):
    return (
        0.1 + self.xshift / self.pageWidth,
        0.725 + self.yshift / self.pageHeight,
    )


def topRight(self):
    return (
        0.96 + self.xshift / self.pageWidth + (self.xscale - 1) * 0.86,
        0.725 + self.yshift / self.pageHeight,
    )


def bottomLeft(self):
    return (
        0.1 + self.xshift / self.pageWidth,
        0.325 + self.yshift / self.pageHeight - (self.yscale - 1) * 0.4,
    )


def bottomRight(self):
    return (
        0.96 + self.xshift / self.pageWidth + (self.xscale - 1) * 0.86,
        0.325 + self.yshift / self.pageHeight - (self.yscale - 1) * 0.4,
    )


def topAt(self, x):
    return (
        topRight(self)[0] * x + topLeft(self)[0] * (1 - x),
        topRight(self)[1] * x + topLeft(self)[1] * (1 - x),
    )


def leftAt(self, y):
    return (
        topLeft(self)[0] * y + bottomLeft(self)[0] * (1 - y),
        topLeft(self)[1] * y + bottomLeft(self)[1] * (1 - y),
    )


target = []
for yrl in range(0, 11):
    x = topAt(
        mdata,
        mdata.monthsWidth + yrl * (1.0 - mdata.meansWidth - mdata.monthsWidth) / 10,
    )
    y = leftAt(mdata, 1.0 - mdata.yearHeight)
    tp = gRotate(mdata, [x[0], y[1]])
    target.extend(tp)
    y = leftAt(mdata, mdata.totalsHeight)
    tp = gRotate(mdata, [x[0], y[1]])
    target.extend(tp)


ict = tf.convert_to_tensor(target, numpy.float32)

# Output the tensor
opdir = "%s/tensors/corners/" % args.rootd
if not os.path.isdir(opdir):
    try:  # These calls sometimes collide
        os.makedirs(opdir)
    except FileExistsError:
        pass

# Write to file
sict = tf.io.serialize_tensor(ict)
tf.io.write_file("%s/%s.tfd" % (opdir, args.docn), sict)
