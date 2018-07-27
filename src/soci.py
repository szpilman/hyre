#!/usr/bin/env python
"""
`soci` program

Manages social contacts, lists and messages.
"""
from functools import partial
from plumbum.cmd import ls, mv
import climenu, arrow, os, re, xerox

current_issue = 'hyre-G001'

climenu.settings.text['main_menu_title'] = 'soci.py'

def get_hyre_ext():
    return ".tnt"

def get_session_root():
    return "/home/vic/datav/datav/"

def get_session_repo():
    return get_session_root() + "note/repo/soci/2018/"

def get_session_metarepo():
    return get_session_root() + "note/repo/soci/"

def get_last_thread(s):
    soci = s['soci']
    n = len(soci)
    return soci[n - 1] if n > 0 else {}

def add_to_thread(s, data):
    s['soci'].append(data)

def add_to_last_thread(s, data):
    last = len(s['soci'])
    if last == 0:
        s['soci'][0] = [data]
    else:
        s['soci'][last - 1].append(data)

# TODO use canned msg templates to inverse match tray/clipboard data
def autoput_tray_data(target):
    data = xerox.paste()
    intro = data.find("I'm writing a technical article")
    if intro > -1:
        lib = re.compile('\w*')
        c = 'your library '
        ci = data.find(c)
        if ci > -1:
            repo = lib.match(data[ci + len(c) :]).group(0)
        else:
            d = 'The Open Hyre, and '
            di = data.find(c)
            repo = lib.match(data[di + len(d) :]).group(0)
        name = data[2: intro].strip()[:-1]
        target['name'] = name
        target['repo'] = repo
        add_to_thread(target, {'to': data})
    elif "\n" in data:
        last = get_last_thread(target)
        if 'to' in last or 'repo' in last:
            add_to_thread(target, {'from': data})
        elif 'from' in last:
            add_to_thread(target, {'to': data})
        else:
            add_to_thread(target, {'msg': data})
    else:
        gh = data.find('github.com/')
        if gh > -1:
            repo = data[gh + 11:]
            slash = repo.index('/')
            target['user'] = repo[:slash] 
            target['url'] = data
            add_to_thread(target, {'repo': repo[slash + 1:],
                'url': data})
        else:
            re_email = re.compile(data + '\w+@\w+')
            if re.compile(re_email).match(data):
                target['email'] = data
            else:
                # TODO user option between name and other info
                target['name'] = data

def load_to_clipboard(data):
    xerox.copy(data)

def make_session(name='[unnamed]', user='', repo='', email=''):
    ss = {}
    ss['soci'] = []
    ss['name'] = name
    ss['user'] = user
    ss['repo'] = repo
    ss['email'] = email
    return ss

session = make_session()
sessionlist = {'pick': session, 'prev': session}
def set_session(s):
    session = s

def set_session_attr(attr, val):
    session[attr] = val

def change_session(s):
    sessionlist['prev'] = session
    sessionlist['pick'] = s
    set_session(s)

def revert_session():
    prev = sessionlist['prev']
    sessionlist['pick'] = prev
    set_session(prev)

def timestamp():
    return arrow.now().format("DD/MM'YY HH:mm")

def contact_front_matter(name, email):
    info = '#+title: {0}\n#+email: {1}\n'.format(name, email)
    meta = '#+source: github\n#+stamp: {}\n'.format(timestamp())
    return info + meta

def serialize_session(s, require_filename=False):
    name = s['name'] if 'name' in s else '[unnamed]'
    email = s['email'] if 'email' in s else ''
    #if 'user' in s and len(s['user']):
    #    user = s['user']
    #    if require_filename and user == 'new_contact':
    #else:
    #    user = 'new_contact'
    user = s['user'] if 'user' in s and len(s['user']) else 'new_contact'
    contact = user + get_hyre_ext()
    filepath = get_session_metarepo() + 'contacts/' + contact
    with open(filepath, "w+") as f:
        f.write(contact_front_matter(name, email))
        text = '\n'
        for msg in s['soci']:
            if 'to' in msg:
                text += '## to\n' + msg['to'] + '\n'
            elif 'from' in msg:
                text += '## from\n' + msg['from'] + '\n'
            elif 'repo' in msg:
                t = '# [{0}] {1} in a Python open source newsletter\n'
                text = (t + '##+repo: {2}').format(current_issue,
                        msg['repo'], msg['url']) + text
        f.write(text)
    return filepath

def breadcrumbs(filepath):
    crumbs = ''
    root = get_session_root()
    if filepath.startswith(root):
        for crumb in filepath[len(root) :].split('/'):
            crumbs += ' > ' + crumb
    return crumbs

def new_contact(old_session):
    s = old_session
    #print(str(s))
    p = s['path'] if 'path' in s else ''
    if s['user'] != 'new_contact' and p.endswith('new_contact'
            + get_hyre_ext()):
        #filepath = serialize_session(s)
        #print(breadcrumbs(filepath))
        #set_session_attr('path', filepath)
        os.remove(p)
    else:
        if 'name' not in s or s['name'] != '[unnamed]':
            s = make_session()
        autoput_tray_data(s)
        #filepath = serialize_session(s)
        #print(breadcrumbs(filepath))
        change_session(s)
        #set_session_attr('path', filepath)
    filepath = serialize_session(s)
    print(breadcrumbs(filepath))
    set_session_attr('path', filepath)

def abort_new_contact():
    os.remove(session['path'])
    revert_session()
    climenu.run()

def save_contact(then=False):
    serialize_session(session, True)
    if then:
        then()

def edit_thread(act):
    '''Creates a list view of items in a thread, allowing items to be
    copied to clipboard and new items to be inserted from clipboard.'''
    act(session)
    name = session['name']
    items = [
        ('add data from clipboard', partial(autoput_tray_data, session)),
        (name + ' | copy', partial(load_to_clipboard, name))
    ]

    email = session['email']
    if len(email):
        items.append((email + ' | copy', partial(load_to_clipboard, email)))

    user = session['user']
    if len(user):
        items.append(('save contact', save_contact))
        items.append(('save and leave', partial(save_contact,
            climenu.run)))
    else:
        items.append(('cancel and leave', abort_new_contact))

    soci = session['soci']
    if len(soci):
        items.append(('__ALL MESSAGES__ | copy all', partial(autoput_tray_data, session)))
        for msg in soci:
            items.append((msg, partial(autoput_tray_data, session)))
    return items
    #for msg in session['soci']:
    #    items.append(('[autotitle]: newsletter issue or email subject',
            # TODO let message take you to thread/list &c i.e. its context
    #        partial(print, msg)))

def get_thread_by_ref(r):
    return sessionlist[r]

def add_to_thread_by_ref(r):
    s = get_thread_by_ref(r)
    autoput_tray_data(s)

def scan_contacts():
    dir = get_session_metarepo()
    extlen = len(get_hyre_ext())
    t = '#+title:'
    e = '#+email:'
    for contact in ls[dir]().split():
        with open(dir + '/' + contact, "r") as f:
            name = '[unnamed]'
            email = ''
            last = ''
            for line in f.readlines():
                if line.index(t):
                    name = line[t:].strip()
                elif line.index(e):
                    email = line[e:].strip()
                elif line.startswith('#+'):
                    continue
                elif line.startswith('# '):
                    #if len(acc):
                    slash = line.index('/')
                    l = line[2:slash].strip()
                    repo = line[slash:].strip()
                    user = contact[: len(contact) - extlen]
                    threadref = '{0}/{1}/{2}'.format(l, user, repo)
                    s = make_session(name, user, repo, email)
                    sessionlist[threadref] = s
                    last = threadref
                #elif line.startswith('## '):

def list_threads(act):
    '''Creates a list view of threads with their corresponding contact
    names beside them.'''
    scan_contacts()
    items = []
    for threadlist in ls[get_session_repo]().split():
        with open(threadlist, "r") as f:
            for repo in f.readlines():
                threadref = threadlist[:-3] + '/' + repo
                slash = repo.index('/')
                label = repo[:slash] + ' - ' + repo[slash:]
                items.append((label, partial(act, threadref)))
    return items

@climenu.group(items_getter=edit_thread, items_getter_kwargs={
    'act': autoput_tray_data })
def build_group():
    '''add data from clipboard'''
    pass

#@climenu.group(items_getter=list_threads, items_getter_kwargs={
#    'act': add_to_thread_by_ref })
#def build_group():
#    '''add to thread | list'''
#    pass

#@climenu.group(items_getter=edit_session, items_getter_kwargs={
#    'act': add_to_thread,
#    'extra': [('|x| autoplay track when tagging',
#        toggle_session_autoplay)]})
#def build_group():
#    '''add to thread | search'''
#    pass

@climenu.group(items_getter=edit_thread, items_getter_kwargs={
    'act': new_contact })
def build_group():
    '''add new contact'''
    pass

#@climenu.group(items_getter=add_to_session, items_getter_kwargs={})
#def build_group():
#    '''search contact'''
#    pass

#@climenu.group(items_getter=add_to_session, items_getter_kwargs={})
#def build_group():
#    '''open list'''
#    pass

@climenu.menu(title='about this software')
def about():
    # A simple menu item
    print('Utility created by The Open Hyre.')
    print('This is open source work under the AGPLv3.')

if __name__ == '__main__':
    climenu.run()
