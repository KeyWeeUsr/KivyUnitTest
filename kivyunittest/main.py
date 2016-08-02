from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

Builder.load_string('''
<MyButton>:
    text: 'Hello Test'
    on_release: print('Hello from the other side!')

<Body>:
    MyButton:
''')

class MyButton(Button):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        app = App.get_running_app()
        app.my_button = self

class Body(BoxLayout):
    pass

class My(App):
    def build(self):
        return Body()
if __name__ == '__main__':
    My().run()
