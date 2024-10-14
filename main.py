from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

class MyGameApp(App):
    def build(self):
        Window.size = (Window.width, Window.height)
        layout = BoxLayout()
        label = Label(text="align it")
        layout.add_widget(label)
        return layout

if __name__ == '__main__':
    MyGameApp().run()
