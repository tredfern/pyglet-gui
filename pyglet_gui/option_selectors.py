import pyglet

from pyglet_gui.controllers import Option, Selector
from pyglet_gui.dialog import Dialog
from pyglet_gui.gui import Frame
from pyglet_gui.containers import VerticalLayout
from pyglet_gui.constants import ANCHOR_TOP_LEFT, ANCHOR_BOTTOM_LEFT, HALIGN_CENTER, VALIGN_TOP
from pyglet_gui.scrollable import Scrollable
from pyglet_gui.buttons import Button, OneTimeButton


class OptionButton(Option, Button):
    def __init__(self, option_name, button_text="", is_selected=False, parent=None):
        Option.__init__(self, option_name, parent)
        Button.__init__(self, label=button_text, is_pressed=is_selected)

    def expand(self, width, height):
        self.width = width
        self.height = height

    def is_expandable(self):
        return True

    def on_mouse_press(self, x, y, button, modifiers):
        self.select()
        self.parent.layout()
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.select()
            self.parent.layout()
            return True


class VerticalButtonSelector(VerticalLayout, Selector):
    def __init__(self, options, labels=None, align=HALIGN_CENTER, padding=4, on_select=None):
        Selector.__init__(self, options, labels, on_select)
        VerticalLayout.__init__(self, list(self._options.values()), align=align, padding=padding)

    def _make_options(self, options, labels):
        widget_options = []
        for option, label in zip(options, labels):
            widget_options.append(OptionButton(option, label, is_selected=(option == self._selected), parent=self))
        return widget_options

    def set_options(self, options, labels=None):
        self.unload()
        Selector.set_options(self, options, labels)
        self.set(self._options.items())
        self.reset_size()


class Dropdown(Selector, OneTimeButton):
    def __init__(self, options, labels=None, max_height=400, align=VALIGN_TOP, on_select=None):
        Selector.__init__(self, options, labels, on_select=on_select, selected=options[0])
        OneTimeButton.__init__(self)

        self.max_height = max_height
        self.align = align

        self._pulldown_menu = None

    def _make_options(self, options, labels):
        widget_options = []
        for option, label in zip(options, labels):
            widget_options.append(OptionButton(option, label, is_selected=(option == self._selected), parent=self))
        return widget_options

    def _delete_pulldown_menu(self):
        if self._pulldown_menu is not None:
            self._pulldown_menu.window.remove_handlers(self._pulldown_menu)
            self._pulldown_menu.delete()
            self._pulldown_menu = None

    def get_path(self):
        return 'dropdown'

    def load(self):
        self.label = self._options[self._selected].label
        OneTimeButton.load(self)

    def unload(self):
        OneTimeButton.unload(self)
        self._delete_pulldown_menu()

    def select(self, option_name):
        Selector.select(self, option_name)
        self._delete_pulldown_menu()
        self.reload()
        self.reset_size()
        self.layout()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        A mouse press is going to create a dialog with the options.
        """
        # if it's already opened, we just close it.
        if self._pulldown_menu is not None:
            self._delete_pulldown_menu()
            return

        # the function we pass to the dialog.
        def on_escape(_):
            self._delete_pulldown_menu()

        # Compute the anchor point and location for the dialog
        width, height = self._manager.window.get_size()
        if self.align == VALIGN_TOP:
            # Dropdown is at the top, pulldown appears below it
            anchor = ANCHOR_TOP_LEFT
            x = self.x
            y = -(height - self.y - 1)
        else:
            # Dropdown is at the bottom, pulldown appears above it
            anchor = ANCHOR_BOTTOM_LEFT
            x = self.x
            y = self.y + self.height + 1

        # we set the dialog
        self._pulldown_menu = Dialog(
            Frame(Scrollable(VerticalLayout(list(self._options.values())),
                             height=self.max_height), path=['dropdown', 'pulldown']),
            window=self._manager.window, batch=self._manager.batch,
            group=self._manager.root_group.parent, theme=self._manager.theme,
            movable=False, anchor=anchor, offset=(x, y),
            on_escape=on_escape)

    def set_options(self, options, labels=None):
        on_select = self._on_select
        del self
        self.__init__(options, labels, on_select)

    def delete(self):
        self._delete_pulldown_menu()
        OneTimeButton.delete(self)
