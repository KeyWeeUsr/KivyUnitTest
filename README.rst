KivyUnitTest
============

.. image:: https://img.shields.io/pypi/pyversions/kivyunittest.svg
   :target: https://pypi.python.org/pypi/kivyunittest

.. image:: https://img.shields.io/pypi/v/kivyunittest.svg
   :target: https://pypi.python.org/pypi/kivyunittest

*Test more, cry less!*

This script is meant to launch a folder of your tests which will behave as one
big test suite. It's done this way because of necessity having a fresh ``python``
interpreter for each Kivy application test to run without mistakes (otherwise
mess from previous ``App().run()`` interferes).

Each unittest file in a folder consisting of tests must start with ``test_``
prefix and end with ``.py``

Run from console:

.. code::

    python -m kivyunittest --folder "FOLDER" --pythonpath "FOLDER"

Without ``--folder`` flag the file assumes it's placed into a folder full of
tests presumably as ``__init__.py``. It makes a list of files, filters
everything not starting with ``test_`` and ending with ``.py`` and runs each test.

Flag ``--pythonpath`` appends a folder to the ``sys.path`` automatically,
therefore it's not necessary to include it in each test manually.

Errors
------

If there is an error of whatever kind that unittest recognizes as failure,
KivyUnitTest will save the name of the test and its log. When the testing ends
all error logs are put together into console divided by pretty headers with
test's name.

Writing Unit Test for Kivy application
--------------------------------------

Basic tests
~~~~~~~~~~~

When the Kivy application starts, it creates a loop and until the loop is
there, nothing will execute after ``App().run()`` line. That's why we need to
probe the loop.

This can be achieved by a simple ``time.sleep()`` as you've surely noticed
sooner when trying to pause the app for a while. That's exactly what a custom
unittest for Kivy does - pauses the main loop as much as possible
as a scheduled interval and executes the testing ``run_test`` function.

Example:

.. code::

    import kivy
    import unittest

    import os
    import sys
    import time
    import os.path as op
    from functools import partial
    from kivy.clock import Clock

First we need to set up importing of the application set ``main_path``
to be the folder of ``main.py`` e.g. when you have tests in
``<app dir>/tests/test_example.py``. Or choose the folder with the
``--pythonpath`` flag.

.. code::

    main_path = op.dirname(op.dirname(op.abspath(__file__)))
    sys.path.append(main_path)

Import your main class that inherits from App (``class My(App):``) or even
additional stuff that's not connected with App class or its children.

.. code::

    from main import My


    class Test(unittest.TestCase):
        # sleep function that catches ``dt`` from Clock
        def pause(*args):
            time.sleep(0.000001)

        # main test function
        def run_test(self, app, *args):
            Clock.schedule_interval(self.pause, 0.000001)

            # Do something

            # Comment out if you are editing the test, it'll leave the
            # Window opened.
            app.stop()

Create an instance of your application, put it as a parameter into partial
(so that you could access it later), schedule main function with Clock and
launch the application (working Window will appear).

.. code::

        # same named function as the filename(!)
        def test_example(self):
            app = My()
            p = partial(self.run_test, app)
            Clock.schedule_once(p, 0.000001)
            app.run()

    if __name__ == '__main__':
        unittest.main()

Intermediate tests
~~~~~~~~~~~~~~~~~~

This kind of tests is used directly for testing in the Kivy core and might
not be easy and/or suitable enough for your needs, however it brings a way
extended control over the testing environment. In this test you can render
each frame manually, move ``Clock`` each tick on your own and dispatch raw
input from (mocked) providers through ``MotionEvent``.

There is a class with all necessary stuff prepared in the background, so
that it launches a Kivy window, but waits for you to move it further e.g.
if you decide to ``render()`` a widget.

.. code::

    from kivy.tests.common import GraphicUnitTest

    from kivy.input.motionevent import MotionEvent
    from kivy.graphics import Color, Point
    from kivy.uix.widget import Widget
    from kivy.base import EventLoop
    from math import sqrt

After you import ``MotionEvent``, you can create own class that inherits
from it and use it later as a mocked input. We will use ``sx`` and ``sy``
which are just positions on X and Y axis in 0 - 1 range (percents, if
you will). This class will dispatch a ``touch``.

.. code::

    class UTMotionEvent(MotionEvent):
        def depack(self, args):
            self.is_touch = True
            self.sx = args['sx']
            self.sy = args['sy']
            self.profile = ['pos']
            super(UTMotionEvent, self).depack(args)

If we know how to assemble a class to create a touch input, we might draw
something with it as well. Kivy includes a nice demo, Touchtracer, for
showcasing multitouch. We fetch ``calculate_points`` from that example.
It basically returns a new set of points we'll input to a drawing function.

.. code::

    # taken from Kivy's Touchtracer
    def calculate_points(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        dist = sqrt(dx * dx + dy * dy)
        o = []
        m = dist
        for i in range(1, int(m)):
            mi = i / m
            o.extend([
                x1 + dx * mi,
                y1 + dy * mi
            ])
        return o

For drawing we'll use a very similar thing to the one used in the Touchtracer.
Let's draw a ``Point`` on ``on_touch_down`` event. Then, if we move the touch
append new points along the line between an old and a new point and draw them.

.. code::

    # core taken from Kivy's Touchtracer
    class WidgetCanvasDraw(Widget):
        def on_touch_down(self, touch):
            win = self.get_parent_window()
            ud = touch.ud

            with self.canvas:
                Color(1, 0, 0, 1)
                ud['lines'] = Point(points=(
                    touch.x, touch.y
                ))

            touch.grab(self)
            return True

        def on_touch_move(self, touch):
            if touch.grab_current is not self:
                return
            ud = touch.ud

            points = ud['lines'].points
            oldx, oldy = points[-2], points[-1]

            points = calculate_points(oldx, oldy, touch.x, touch.y)

            if not points:
                return

            add_point = ud['lines'].add_point
            for idx in range(0, len(points), 2):
                add_point(
                    points[idx],
                    points[idx + 1]
                )

        def on_touch_up(self, touch):
            if touch.grab_current is not self:
                return
            touch.ungrab(self)

We have input, drawing behavior, let's set up a test. You might want to
get used to this "template" if you intend to use the ``GraphicsUnitTest``
class. It's not that scary though. Set a class attribute ``framecount``
to zero, prepare some debugging behavior (``setUp`` prepares a new Window,
``tearDown`` purges it). After overriding them with empty functions, such
actions won't happen.

.. code::

    class WidgetDrawTestCase(GraphicUnitTest):
        framecount = 0

        # debug test with / stop destroying window
        # def tearDown(self, *_): pass
        # def setUp(self, *_): pass

We make sure the Window is available to us with ``EventLoop``, prepare
all out widgets and then call ``EventLoop.idle()`` which makes a lot of
internals ready for an application to show like you are used to it. More
or less.

.. code::

        def test_touch_draw(self):
            # get Window instance for creating visible
            # widget tree and for calculating coordinates
            EventLoop.ensure_window()
            win = EventLoop.window

            # add widget for testing
            child = WidgetCanvasDraw()
            win.add_widget(child)

            # get widgets ready
            EventLoop.idle()

You can happily start testing now.

The little bit problematic part comes now, because you have to be sure
where you want your touch to go and do it in 0 - 1 range, so that the
test works even after Window resizing. Absolute values are not the way
you want to go. Always try to generalise the movement and find a way
how to simplify them into a small list.

.. code::

            # default "cursor" position in the middle
            pos = [win.width / 2.0, win.height / 2.0]

            # default pos, new pos
            points = [
                [pos[0] - 5, pos[1], pos[0] + 5, pos[1]],
                [pos[0], pos[1] - 5, pos[0], pos[1] + 5]
            ]

            # general behavior for touch+move+release
            for i, point in enumerate(points):
                x, y, nx, ny = point

                # create custom MotionEvent (touch) instance
                touch = UTMotionEvent("unittest", 1, {
                    "sx": x / float(win.width),
                    "sy": y / float(win.height),
                })

The points and touch are ready. Let's dispatch the input in the test.
For that we use ``EventLoop`` again and its method
``post_dispatch_input(event_type, motion_event)``.

* touch down with ``begin`` event type
* touch move with ``update`` event type
* touch up with ``end`` event type

.. code::

                # dispatch the MotionEvent in EventLoop as
                # touch/press/click, see Profiles for more info:
                # https://kivy.org/docs/api-kivy.input.motionevent.html#profiles
                EventLoop.post_dispatch_input("begin", touch)

                # the touch is dispatched and has ud['lines']
                # available from on_touch_down
                self.assertIn('lines', touch.ud)
                self.assertTrue(isinstance(touch.ud['lines'], Point))

                # move touch from current to the new position
                touch.move({
                    "sx": nx / float(win.width),
                    "sy": ny / float(win.height)
                })
                # update the MotionEvent in EventLoop
                EventLoop.post_dispatch_input("update", touch)

                # release the MotionEvent in EventLoop
                EventLoop.post_dispatch_input("end", touch)

                # still available, but released
                self.assertIn('lines', touch.ud)
                self.assertTrue(isinstance(touch.ud['lines'], Point))

                expected_points = [[
                    x + 0, y, x + 1, y,
                    x + 2, y, x + 3, y,
                    x + 4, y, x + 5, y,
                    x + 6, y, x + 7, y,
                    x + 8, y, x + 9, y
                ], [
                    x, y + 0, x, y + 1,
                    x, y + 2, x, y + 3,
                    x, y + 4, x, y + 5,
                    x, y + 6, x, y + 7,
                    x, y + 8, x, y + 9
                ]]

                # check if the instruction points == expected ones
                self.assertEqual(
                    touch.ud['lines'].points,
                    expected_points[i]
                )

The less obvious part comes now, because we need to trigger the rendering
of our graphics in the application. Fortunately that's easy to do with
simple ``GraphicUnitTest.render()``. You most likely want to put there the
root widget like when building an application with ``App.build()`` method.

.. code::

            # render the graphics
            self.render(child)

It's quite useful to add ``unittest.main()`` at the end of your test,
because if you only try to write a single test then you most likely don't
want to run the whole suite. Especially if the suite is large.

.. code::

    if __name__ == '__main__':
        import unittest
        unittest.main()


Tips for testing
~~~~~~~~~~~~~~~~

Handle class communication through App class via ``App.get_running_app()`` in
your application, put every needed widget inside App class like this:

.. code::

    class MyButton(Button):
        def __init__(self, **kwargs):
            super(<class name>, self).__init__(**kwargs)
            self.text = 'Hello Test'
            app = App.get_running_app()
            app.my_button = self

and then access your widgets in test's ``run_test()`` function via ``app``
parameter like this:

.. code::

    self.assertEqual('Hello Test', app.my_button.text)

Use ``app.root`` to get instance of a class you pass in the ``build()``
function in the App class.

Dispatch events through widgets e.g. ``<widget>.dispatch('on_release')`` to
execute function bound to ``on_release``.

.. |rec| replace:: Recorder module
.. _rec: https://kivy.org/docs/api-kivy.input.recorder.html
.. |ins| replace:: Inspector module
.. _ins: https://kivy.org/docs/api-kivy.modules.inspector.html

Use Kivy's |ins|_ as help to navigate down the path of App class and use ``ids``
in ``kv language``, it'll make targeting a specific widget easier.

Try even Kivy's |rec|_ to record steps and play them later instead of
dispatching events manually. However, this way is heavy time-consuming as it
plays the steps exactly as long as they were recorded.

Example:

.. code::

    from kivy.input.recorder import Recorder

    # place this inside ``run_test()``
    rec = Recorder(filename='myrecorder.kvi')
    rec.bind(on_stop=<function>)
    rec.play = True

This will play all steps and then executes a function bound to ``on_stop``.
May be useful for testing touch gestures, swipes, dragging and other rather
annoying to write manually stuff.

There's also possibility to change time the steps were recorded in in ``.kvi``
file (that long number), which will speed things up.

There's also a very interesting Python package made by Mathieu Virbel that
allows you to go down the widget tree rabit hole in a more sane way than
using this:

.. code::

    my_widget.children[0].children[1].children[2]...

which gets tedious and annoying the more you use it when you navigate the
tree from the application's root widget itself through complex layouts.
This is where [Telenium](https://github.com/tito/telenium) might save you
a lot of minutes instead of typing the same thing over and over.

License
-------

The MIT License (MIT)
