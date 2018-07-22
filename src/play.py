#!/usr/bin/env python
"""
Simple example of a CLI that demonstrates up-arrow partial string matching.

When you type some input, it's possible to use the up arrow to filter the
history on the items starting with the given input text.
"""
from functools import partial
from itertools import groupby
from plumbum.cmd import ls
import climenu, re


def print_var(variable):
    '''print the variable'''
    print(str(variable))

def get_listing():
    listing = ls["/home/vic/datav/datav/tray/jul"]().split()
    regex = re.compile(r'180717\d\d\d[-ivxlc]*\d?.wav')
    selected = filter(regex.search, listing)
    return selected

def build_items(count):
    # In this example, we're generating menu items based on some
    # thing that's determined at runtime (e.g. files in a directory).

    # For this case, we're simply using `range` to generate a range of
    # items.  The function that eventually gets called takes 1 argument.
    # Therefore, we need to use ``partial`` to pass in those arguments at
    # runtime.
    items = []
    for track in get_listing(): # range(count):
        items.append(
            (
                # 'Run item %i' % (index + 1),
                track,
                partial(print_var, 'Item %s' % track)
            )
        )

    return items

@climenu.menu(title='Do the first thing')
def first_thing():
    # A simple menu item
    print('Did the first thing!')


@climenu.group(items_getter=build_items, items_getter_kwargs={'count': 6})
def build_group():
    '''A dynamic menu'''
    # This is just a placeholder for a MenuGroup.  The items in the menu
    # will be dymanically generated when this module loads by calling
    # `build_items`.
    pass


if __name__ == '__main__':
    climenu.run()

"""
def main():
    loc = '/home/vic/datav/datav/'
    print("This CLI has up-arrow partial string matching enabled.")
    print("Type a substring followed by up-arrow and you'll get")
    while True:
        try:
            clip = xerox.paste()
            words = len(clip.split())
            #words = format(wordn, 'd')
            if len(clip):
                print(HTML('<ansigreen><b>1</b> item on clipboard:</ansigreen>'))
                t = '[{} words]'.format(words)
                t = session.prompt(t + HTML('<ansiyellow>Give this clip a title: </ansiyellow>'))
            else:
                t = session.prompt('Put a new item on the tray: ')

        except KeyboardInterrupt:
            pass  # Ctrl-C pressed. Try again.
        else:
            break

    print('You said: %s' % t)
"""
