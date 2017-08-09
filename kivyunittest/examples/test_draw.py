from kivy.tests.common import GraphicUnitTest

from kivy.input.motionevent import MotionEvent
from kivy.graphics import Color, Point
from kivy.uix.widget import Widget
from kivy.base import EventLoop
from math import sqrt


class UTMotionEvent(MotionEvent):
    def depack(self, args):
        self.is_touch = True
        self.sx = args['sx']
        self.sy = args['sy']
        self.profile = ['pos']
        super(UTMotionEvent, self).depack(args)


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
            


class WidgetDrawTestCase(GraphicUnitTest):
    framecount = 0

    # debug test with / stop destroying window
    # def tearDown(self, *_): pass
    # def setUp(self, *_): pass

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

        # render the graphics
        self.render(child)


if __name__ == '__main__':
    import unittest
    unittest.main()
