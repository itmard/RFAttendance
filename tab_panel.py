from kivy.gesture import Gesture, GestureDatabase
from kivy.graphics import Line
from kivy.uix.tabbedpanel import TabbedPanel

from main import RfAttendance


class TabPannel(TabbedPanel):
    def __init__(self, *args, **kwargs):
        super(TabPannel, self).__init__(*args, **kwargs)
        self.app = RfAttendance.get_running_app()

        self.gdb = GestureDatabase()
        self.left_to_right_gesture = self.gdb.str_to_gesture(left_to_right_gesture)
        self.right_to_left_gesture = self.gdb.str_to_gesture(right_to_left_gesture)

        self.gdb.add_gesture(self.left_to_right_gesture)
        self.gdb.add_gesture(self.right_to_left_gesture)

    def on_touch_down(self, touch):
        touch.ud['line'] = Line(points=(touch.x, touch.y))
        return super(TabPannel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        try:
            touch.ud['line'].points += [touch.x, touch.y]
            return super(TabbedPanel, self).on_touch_move(touch)
        except KeyError:
            pass

    def on_touch_up(self, touch):
        g = Gesture()
        g.add_stroke(list(zip(
            touch.ud['line'].points[::2],
            touch.ud['line'].points[1::2]
        )))
        g.normalize()
        g.name = ''

        g2 = self.gdb.find(g, minscore=0.70)
        if g2 and g2[1] == self.left_to_right_gesture:
            self.switch_to_left()
        elif g2 and g2[1] == self.right_to_left_gesture:
            self.switch_to_right()

        return super(TabPannel, self).on_touch_up(touch)

    def switch_to_right(self):
        current_tab_index = self.tab_list.index(self.current_tab)
        if current_tab_index == 0:
            return

        try:
            self.switch_to(self.tab_list[current_tab_index - 1])
        except IndexError:
            pass

    def switch_to_left(self):
        current_tab_index = self.tab_list.index(self.current_tab)

        try:
            self.switch_to(self.tab_list[current_tab_index + 1])
        except IndexError:
            pass


left_to_right_gesture = 'eNq1l91u4jAQhe/9IuVmoxnPj+0XoLcr9QFWbBtR1C5EQHe3b7/2mDZBhQ03RtEETsafnTkmmiw2L5vf7926Pxzf9r27P50HcIunAd3D3Xb1q79zg89f84nc4eHucNzvXvpD/slu8TqIW1yEPFiaG7SgQh4/7DbbYxkWy7B0Zdj3kuUGrCsoS3jPQ9C7JXQAMQEhUY0hhbKev+U6ueU36BQERFOEEkOK7vBz9f9p2KYRt74+w/oEF6EQOPlYI83D7dYx3AJn5cmlGHWeHo2e2tC91d9jI7o3Oo10PxY2R5zAQT/IOUKaL7s3T720gZun/uRpRgAC+aAkp6gy4j0rRK8eLcL8dvTmqU9t6GSeEjaim6dEjehmKkkjurlKE1c9IcfJMcJBAaOMh5+nm6uU2tDZXGVsRDdXmRrRzVWWRnRzlRu5yuYqz7sKHQJAQO+lRp5/QIqZKtgGbp4KtYGbpSJt4OaohDZwM1RuePjmJwz4UfcRZ+Fqhiq2gZuhSm3gZqhODAVKGCjEGoNM4D5OpuUb4GaohpvgjJA0qtbI839RNUc1zXUCmR2SSGTgGuf7gGB+BpxHEwimxAQ13oA2NwPNtl6ZLTrd/ZHn4eZmGJsjlBGdQHPv8QlPPC7bQ+5jM7z0/4/7vt9+dvNBSzsfglssCWMHbumj5tNxCNGtipjOxGSi16kYwUSGMxGreBouVfQmBq4iVZGKmJvQKmIV2UQfz0QxkfPw6UcnLK0Z8ULGl1E5PdT00yIvZVgVWOB6RqoZNL3RBFWULk0/PMnAmpGuZ1ixWOlCRq1xqpXTM99SrdxHjcPXFadcxroZnvvN+vmYt0HKFdLzTLHXsz+bp+NzSQhuiVJmyOJx99rvV9vH8m6ZX9PK87rIpz37Y9jvnt4eDZvyErqAMVISivlNA62f6/4B1VnQQg=='

right_to_left_gesture = 'eNq1l01uIzcQhfd9EXsTgfXPuoBnG8AHCBxb8BgzsQVbk2Run2KVbLUwcro3kgG19br4NVmPLLKvn749/f1z87h92/943U5fDtddm64fdjDdXj3f/bW9mnYY/8aFprfbq7f968u37Vv85On6+06m67OQ2wybdjpQFu13L0/P+9Gsj2b+SbPfR9S0g+rB6MLPaAI43bRNU+7N3dmcyaz30Z1/x20at6WrE/XexV27xd0/7/7/IZwPkenxwGcDaN3cpAG1eNz09nhgI3vgA83cMZossnPcYBdh92T7B5s6KhDGpweZ+gc68mXk4J2IscXjF9mYiUf4YGMTRWwGnUy6KB3h4QWjUQcxhLbcb8Rk00XY6SXKCjapqLNLE1bxZrwMTzPRLgNPN/HoJoABKrsqKDHTDI7AMY8UncQNFtGUZtLRzIZdqTkCuUB07jhT0Ll7Z2+kHutnOeGUZhKtYUvko6FGRKwB6ivg6SbJGngspYYOAtxJW19OOKWbZJeBp5vkK+BAosEXDitH1pcLFqefDJeBp6G8xtAoKjG5RZBAo5yJLsPTUJbLwNNQPhj626BLVNRYgFUY4/tIP/PgJXxayn4hvKSpAsv4cU8aRikXdCeMir+8lCRtFboUPo0VOeJrqSB6bHlkTW2Gzx2ucdNRBaK0L+PTWrFVeEDvvWGIHqMwXKans+Lr6GxiHv2u+cnL81LTWYV1eIeOBkaj55BVfwmfziqtwmPcsNhTmot14uW9Q9NYlVXzBjX+SIniLDP2xmV6+qq2jt4dDClmjTcx1eVZqWms+ip8gLsBIwDF7BRaxlsaa+uMpTp7ecgAbsu+WvpqM19p9ArIco8Wwjlde49TCJJ1j2nvy/T01Wa+MlDn2CLyhOoNZvCuAsZxpiZybtn18QZw/7rdPn+c503Hgd5sur4R6Js23VCDuOx3cQa/G6KV2Er0EmUu9lZitJt/dLqJUlQRkBFNNj7/8IjoFYEjgsevXxhaEVQRNB79IXKJ7UwzqQjJiN6r2UHUEvlMf7girCLa5xGZn6grBT6ImR9Wm4ue+WHxT1kOFQFnIqgiKj+sBT6IlRKGErHESgnZiVhZoHMDPkRUSqidNKssoJyINXDEk67UwBHmIrQaOfgZe95DaujQTxvWcMFOVTpR8aDWgEFP1Rox0Kcjhqafh8AhpBLQzljXf9FGfOWm1Wi6HyiVnHPT/z0E2nvIvGG8Q9/Vsv26fXr8uh+vy2PlwxhBqP88Pey/phhrPr5K3b98377ePd9v8w7niXLoh5ryx+715eHHfcEknrZxjBe1WEQSNdDGvr75D0fTLFE='
