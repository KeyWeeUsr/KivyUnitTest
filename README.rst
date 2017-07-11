KivyUnitTest
============

.. image:: https://img.shields.io/pypi/pyversions/kivyunittest.svg
   :target: https://pypi.python.org/pypi/kivyunittest

.. image:: https://img.shields.io/pypi/v/kivyunittest.svg
   :target: https://pypi.python.org/pypi/kivyunittest

*Test more, cry less!*

This script is meant to launch a folder of your tests which will behave as one
big test suite. It's done this way because of necessity having a fresh `python`
interpreter for each Kivy application test to run without mistakes (otherwise
mess from previous ``App().run()`` interferes).

Each unittest file in a folder consisting of tests must start with `test_`
prefix and end with `.py`

Run from console:

.. code::

    python -m kivyunittest --folder "FOLDER"

Without ``--folder`` flag the file assumes it's placed into a folder full of
tests presumably as ``__init__.py``. It makes a list of files, filters
everything not starting with `test_` and ending with `.py` and runs each test.

Errors
------

If there is an error of whatever kind that unittest recognizes as failure,
KivyUnitTest will save the name of the test and its log. When the testing ends
all error logs are put together into console divided by pretty headers with
test's name.

Writing Unit Test for Kivy application
--------------------------------------

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
to be the folder of `main.py` e.g. when you have tests in
`<app dir>/tests/test_example.py`.

.. code::

    main_path = op.dirname(op.dirname(op.abspath(__file__)))
    sys.path.append(main_path)

Import your main class that inherits from App (``class My(App):``) or even
additional stuff that's not connected with App class or its children.

.. code::

    from main import My


    class Test(unittest.TestCase):
        # sleep function that catches `dt` from Clock
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
execute function bound to `on_release`.

.. |rec| replace:: Recorder module
.. _rec: https://kivy.org/docs/api-kivy.input.recorder.html
.. |ins| replace:: Inspector module
.. _ins: https://kivy.org/docs/api-kivy.modules.inspector.html

Use Kivy's |ins|_ as help to navigate down the path of App class and use `ids`
in `kv language`, it'll make targeting a specific widget easier.

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

There's also possibility to change time the steps were recorded in in `.kvi`
file (that long number), which will speed things up.

License
-------

The MIT License (MIT)
