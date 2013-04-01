## CircleThingy

Very simple graphical circle picker. Useful, e.g. for determining the trajectories of bacteria. Very basic right
now but maybe useful for some people.

### Requirements

* Python 2.7.x (might work with Python 2.6.x)
* matplotlib

### Installation

```bash
git clone https://github.com/krischer/CircleThingy.git
cd CircleThingy
```

### Usage

It currently works for one picture at a time (only tested with PNG images but might work for other formats as well).
Run the script with the path to the picture as the only argument:

```bash
python circle_thingy.py test_image.png
```

This will open a window with the image. Two right mouse button clicks will be used to pick both ends of the scale on
the picture. After entering the physical size of the scale, it will appear on the picture.

After this point, three left mouse button clicks will be used to mark one circle. This can be repeated as often as
desired.

### Screenshot
![Screenshot](https://raw.github.com/krischer/CircleThingy/master/screenshot_1.png)
![Screenshot](https://raw.github.com/krischer/CircleThingy/master/screenshot_2.png)


### Caveat

This is a very simple utility created to solve a very simple problem. It does not have a proper code structure and
if anyone plans on adding a significant amount of new features - please take the time to refactor the whole thing.
