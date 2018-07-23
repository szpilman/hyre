#!/usr/bin/env python
"""
Simple example of a CLI that demonstrates up-arrow partial string matching.

When you type some input, it's possible to use the up arrow to filter the
history on the items starting with the given input text.
"""
from functools import partial
from itertools import groupby
from collections import Counter, OrderedDict
from plumbum.cmd import ls, echo
from fuzzyfinder import fuzzyfinder
from plumbum import local
import climenu, re

def get_audio_ext():
    return ".wav"

def get_hyre_ext():
    return ".tnt"

def get_session_root():
    return "/home/vic/datav/datav/"

def get_session_repo():
    return get_session_root() + "tray/jul/"

def get_session_metarepo():
    return get_session_root() + "prod/gtar/2018/cata/jul/"

def print_var(variable):
    '''print the variable'''
    print(str(variable))

def get_listing():
    listing = ls[get_session_repo()]().split()
    regex = re.compile(r'180717\d\d\d[-ivxlc]*\d?.wav')
    selected = list(filter(regex.search, listing))
    return selected

def render_tracks(tracks, act):
    items = []
    for track in tracks:
        # strip out .wav extension from file name
        t = session[track] if track in session else track[:-4]
        items.append(
            (
                t,
                partial(act, track)
            )
        )
    return items

session = {'__autoplay__': True, '__view__': 'Bigconcatfile.wav'}
def edit_session(word, act, act_all, extra):
    tracks = get_listing()
    items = render_tracks(tracks, act)
    items.append(('%s all tracks' % word, partial(act_all, tracks)))
    items.append(('Save session to catalog', partial(save_session, tracks)))
    for e in extra:
        items.append(e)
    session = {pair[0]: pair[0] for pair in items}
    return items

def pad_three(pad, s):
    l = len(s)
    if l > 2:
        return s[:3]
    elif l == 2:
        return " " + s if pad == 3 else s
    else:
        if pad == 3:
            return "  " + s
        else:
            return " " + s if pad == 2 else s

def save_session(tracks):
    date = tracks[0][:6]
    with open(get_session_metarepo() + date + get_hyre_ext(), "w") as f:
        f.write('#+title: ' + date + '\n#+ppl-mod: ^UR\n#+stamp: ')
        l = len(tracks)
        pad = len(str(l))
        p = partial(pad_three, pad)
        for i in range(l):
            t = tracks[i]
            title = session[t] if t in session else t[:-4]
            f.write('\n   ' + p(str(i + 1)) + '. ' + title)

def change_session_autoplay(autoplay):
    session['__autoplay__'] = autoplay

def toggle_session_autoplay():
    session['__autoplay__'] = not session['__autoplay__']

def add_to_session():
    tracks = get_listing()
    items = render_tracks(tracks, play_track)
    return items

class OrderedCounter(Counter, OrderedDict):
    pass

play = local["play"]
smenu = local["smenu"]
def play_track(track):
    '''play the audio file track'''
    path = get_session_repo() + track


    #smenu[]
    play[path]()

def play_session(tracks):
    from pydub import AudioSegment
    if len(list(tracks)):
        session = AudioSegment.from_wav(tracks[0])
        for track in tracks[1:]:
            session += AudioSegment.from_wav(track)

dmenu = local["dmenu"]
parallel = local["parallel"]
def interact_title(track):
    with open('play.tnt') as f:
        seen = OrderedCounter([line[9:].strip() for line in f])
        titles = "\n".join([k for k,v in seen.items() if v == 1])
        if session['__autoplay__']:
            file = get_session_repo() + track
            selection = echo[titles] | parallel["--pipe", "0",
                    play[file]] | dmenu
        else:
            selection = echo[titles] | dmenu
        session[track] = selection()[:-1]
        print(session)

def interact_titles(tracks):
    for track in tracks:
        interact_title(track)

@climenu.group(items_getter=edit_session, items_getter_kwargs={
    'word': 'Play', 'act': play_track, 'act_all': play_session,
    'extra': []})
def build_group():
    '''play track'''
    pass

@climenu.group(items_getter=edit_session, items_getter_kwargs={#'count': 6,
    'word': 'Tag', 'act': interact_title, 'act_all': interact_titles,
    'extra': [('|x| autoplay track when tagging',
        toggle_session_autoplay)]})
def build_group():
    '''tag track'''
    pass

@climenu.group(items_getter=add_to_session, items_getter_kwargs={})
def build_group():
    '''record new track'''
    pass

@climenu.group(items_getter=add_to_session, items_getter_kwargs={})
def build_group():
    '''search for track'''
    pass

@climenu.menu(title='about this software')
def about():
    # A simple menu item
    print('Utility created by The Open Hyre')
    print('This is open source work under the')
    print('AGPLv3.')

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
