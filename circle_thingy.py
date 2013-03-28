#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple utility to determine the size of circles in a picture.

Dependencies:
    * Python 2.7.x (might work with 2.6.x)
    * matplotlib

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import sys
import matplotlib

# The OSX backend has a problem with blitting. This is well documented and
# there is no real way around it. Therefore just force the use of the TkAgg
# backend. This is a good idea on other platforms as well because Tk is used
# for dialogs.
matplotlib.use('TkAgg')

import math
import matplotlib.pylab as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Cursor

import Tkinter
import tkMessageBox
import tkSimpleDialog

root = Tkinter.Tk()
root.withdraw()


class ScaleDialog(tkSimpleDialog.Dialog):
    """
    Simple dialog asking for length of the scale.
    """
    def body(self, master):
        Tkinter.Label(master, text="Set the length of the scale:")\
            .pack(side=Tkinter.LEFT)
        self.scale = Tkinter.Entry(master)
        self.scale.pack(side=Tkinter.LEFT)
        Tkinter.Label(master, text="10E-6 meter")\
            .pack(side=Tkinter.LEFT)

    def validate(self):
        try:
            self.scale_in_mu_meter = float(self.scale.get())
            return 1
        except:
            tkMessageBox.showwarning("Bad input", "Needs to be a number.")
            return 0


class GlobalHandler(object):
    def __init__(self, image):
        self.scale = {
            "end_points": [],
            "length_of_scale_in_px": None,
            "length_of_scale_in_mu_meter": None,
            "mpl_object": []}
        self.circles = []
        self.current_circle_points = []
        self.scale_units = "E-6 m"
        self.fig = plt.gcf()
        plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
        plt.suptitle("Pick scale with right mouse button, circles with left.")
        self.image = image[::-1, :]
        plt.imshow(self.image)
        self.redraw()

        self.color_index = 0
        self.colors = ["yellow", "orange", "red", "violet", "lightblue"]

    def redraw(self):
        self.fig.canvas.draw()
        plt.xlim(0, self.image.shape[1])
        plt.ylim(0, self.image.shape[0])
        plt.yticks([])
        plt.xticks([])

    def on_left_click(self, x, y):
        if not self.scale["length_of_scale_in_mu_meter"]:
            tkMessageBox.showerror("Error", "Please set the scale before "
                "picking cirles.")
            return
        plt.scatter(x, y, color="white", s=60, edgecolor="blue", marker="x",
            lw=2.5)

        if len(self.current_circle_points) == 3:
            self.current_circle_points[:] = []
        self.current_circle_points.append((x, y))
        if len(self.current_circle_points) == 3:
            p = self.current_circle_points

            point, radius = cirle_from_three_points(p[0][0], p[0][1], p[1][0],
                p[1][1], p[2][0], p[2][1])

            color = self.colors[self.color_index % len(self.colors)]
            self.color_index += 1

            circle = matplotlib.patches.Circle(point, radius, lw=4,
                facecolor="none", edgecolor=color)

            factor = self.scale["length_of_scale_in_mu_meter"] / \
                self.scale["length_of_scale_in_px"]

            plt.text(point[0], point[1], "Radius: %.4fE-6 m" % (radius *
                factor), horizontalalignment='center', color="black",
                verticalalignment='center', fontsize=11,
                bbox=dict(facecolor=color, alpha=0.85, edgecolor="0.7"))

            plt.gca().add_patch(circle)
        self.redraw()

    def on_right_click(self, x, y):
        sc = self.scale

        # Reset if already exising.
        if len(sc["end_points"]) == 2:
            sc["end_points"][:] = []
            sc["length_of_scale_in_mu_meter"] = None
            sc["length_of_scale_in_px"] = None
            if sc["mpl_object"]:
                for _i in sc["mpl_object"]:
                    _i.remove()
                sc["mpl_object"] = []
                self.redraw()

        sc["end_points"].append((x, y))

        # Set a new scale if it now has two points.
        if len(sc["end_points"]) == 2:
            diag = ScaleDialog(root, title="Set Scale Length")
            try:
                sc["length_of_scale_in_mu_meter"] = \
                    diag.scale_in_mu_meter
            except:
                return

            scale_x_1 = sc["end_points"][0][0]
            scale_x_2 = sc["end_points"][1][0]
            scale_y_1 = sc["end_points"][0][1]
            scale_y_2 = sc["end_points"][1][1]

            sc["length_of_scale_in_px"] = abs(scale_x_1 - scale_x_2)

            midpoint_x = min(scale_x_1, scale_x_2) + \
                sc["length_of_scale_in_px"] / 2.0
            midpoint_y = min(scale_y_1, scale_y_2) + \
                abs(scale_y_1 - scale_y_2) / 2.0

            sc["mpl_object"] = plt.plot((scale_x_1, scale_x_2), (scale_y_1,
                scale_y_2), color="green", lw=3, marker="|", markersize=20,
                markeredgecolor="green", markeredgewidth=3)

            sc["mpl_object"].append(plt.text(midpoint_x, midpoint_y,
                "Scale length: %.2fE-6 m" %
                sc["length_of_scale_in_mu_meter"],
                horizontalalignment='center', verticalalignment='center',
                fontsize=11, bbox=dict(facecolor="white", alpha=0.85,
                edgecolor="0.7")))
            self.redraw()


def cirle_from_three_points(x1, y1, x2, y2, x3, y3):
    """
    Simple function taking three points and returning a tuple containing the
    center and radius of a circle through these three points.
    """
    # Make sure to avoid integer division.
    x1, y1, x2, y2, x3, y3 = map(float, (x1, y1, x2, y2, x3, y3))
    slope_1 = (y1 - y2) / (x1 - x2)
    slope_2 = (y3 - y2) / (x3 - x2)

    x = (slope_1 * slope_2 * (y3 - y1) + slope_1 * (x2 + x3) -
        slope_2 * (x1 + x2)) / (2 * (slope_1 - slope_2))
    y = - 1.0 / slope_1 * (x - (x1 + x2) / 2.0) + (y1 + y2) / 2.0

    r = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)

    return ((x, y), r)

filename = sys.argv[-1]
handler = GlobalHandler(image=mpimg.imread(filename))


# Bind the matplotlib events.
def on_mouse_click(event):
    global handler
    x, y = event.xdata, event.ydata
    if event.button == 1:
        handler.on_left_click(x, y)
    elif event.button == 3:
        handler.on_right_click(x, y)


def on_close(event):
    root.quit()


plt.gcf().canvas.mpl_connect('button_press_event', on_mouse_click)
plt.gcf().canvas.mpl_connect('close_event', on_close)

# Add a cursor just for fun.
cursor = Cursor(plt.gca(), useblit=True, color='lime', linewidth=1)

plt.show()
