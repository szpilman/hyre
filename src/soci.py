#!/usr/bin/env python
"""
`soci` program

Manages social contacts, lists and messages.
That is, the Garden of Eden.
"""
from functools import partial
from plumbum.cmd import ls
import climenu, arrow, os, re, xerox

def current_issue():
    return 'hyre-G001'

climenu.settings.text['main_menu_title'] = 'soci.py'

intromsg = """
Hi {0},

I'm writing a technical article for my newsletter, The Open Hyre, and your library {1} is used for parts of code shown and also used in an open source tool to be released.

Since I'm using the library, I'd like to also feature {1} in the newsletter if it's fine with you. The newsletter's main and most important section is like classifieds for open source tasks. To feature {1}, I only need from you a task from your issues tracker that's easy to do for a beginner with Python/open source--it could be documentation or text corrections even.

Thanks,
Bernardo
"""

def get_hyre_ext():
    return ".tnt"

def get_session_root():
    return "/home/vic/datav/datav/"

def get_session_repo():
    return get_session_root() + "note/repo/soci/2018/"

def get_session_metarepo():
    return get_session_root() + "note/repo/soci/"

def get_fork_prodrepo():
    return get_session_root() + "prod/soci/2018/fork/"

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
        gh = get_threadref_from_url(data)
        if gh['repo'] != '-':
            target['user'] = gh['user']
            target['url'] = data
            add_to_thread(target, {'repo': gh['repo'], 'url': data})
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
sessionlist = {'pick': session, 'prev': session,
        'list': current_issue(), 'curr': ''}
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

def reset_list_pick():
    sessionlist['list'] = []

def timestamp():
    return arrow.now().format("DD/MM'YY HH:mm")

def stamp(s):
    return s + '\n#+stamp: {}\n'.format(timestamp())

def contact_front_matter(name, email):
    info = '#+title: {0}\n#+email: {1}\n'.format(name, email)
    meta = '#+source: github'
    return info + stamp(meta)

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
    filepath = get_session_metarepo() + 'contacts/python/' + contact
    with open(filepath, "w+") as f:
        f.write(contact_front_matter(name, email))
        text = '\n'
        l = current_issue()
        for msg in s['soci']:
            if 'to' in msg:
                text += '## to\n' + msg['to'] + '\n'
            elif 'from' in msg:
                text += '## from\n' + msg['from'] + '\n'
            elif 'repo' in msg:
                t = '# [{0}] {1} in a Python open source newsletter\n'
                text = (t + '##+repo: {2}').format(l, msg['repo'],
                        msg['url']) + text
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

def get_threadref_from_url(url):
    target = {'user': 'new_contact', 'repo': '-'}
    gh = url.find('github.com/')
    if gh > -1:
        repo = url[gh + 11:]
        slash = repo.index('/')
        target['user'] = repo[:slash] 
        target['repo'] = repo[slash + 1:]
        target['project'] = repo
        target['url'] = url
    target['threadref'] = '{0}/{1}/{2}'.format(sessionlist['list'],
            target['user'], target['repo'])
    return target

def get_last_message(s):
    soci = s['soci']
    item = soci[len(soci) - 1]
    return item['to'] if 'to' in item else item['from']

def get_contact_path(contact):
    dir = get_session_metarepo()
    ext = get_hyre_ext()
    e = '' if contact.endswith(ext) else ext
    return dir + 'contacts/python/' + contact + e

def load_contact(contact):
    soci = []
    name = '[unnamed]'
    repo = ''
    email = ''
    status = '[unknown]'
    last = ''
    s = session
    ext = get_hyre_ext()
    if contact.endswith(ext):
        user = contact[: len(contact) - len(ext)]
    else:
        user = contact
    with open(get_contact_path(contact), "r") as f:
        for line in f.readlines():
            if not line.startswith('#'):
                i = len(soci) - 1
                if 'to' in soci[i]:
                    soci[i]['to'] += line
                elif 'from' in soci[i]:
                    soci[i]['from'] += line
            elif line.startswith('#+title: '):
                name = line[8:].strip()
            elif line.startswith('#+email: '):
                email = line[8:].strip()
            elif line.startswith('#+'):
                continue
            elif line.startswith('## '):
                item = {}
                if line[3:7] == 'to: ':
                    status = 'sent'
                    item = {'to': '', 'date': line[8:]}
                if line[3:6] == 'to ':
                    status = 'outbox'
                    item = {'to': ''}
                elif line[3:7] == 'from':
                    status = 'inbox'
                    item = {'from': ''}
                soci.append(item)
            elif line.startswith('##+repo'):
                t = get_threadref_from_url(line)
                repo = t['repo']
                if t['user'] != user:
                    print('Contact name `{0}` different from repo owner `{1}`'.format(user, t['user']))
            # header lines contain the list name
            elif line.startswith('# '):
                #if len(acc):
                close = line.find('] ')
                l = line[2:close].strip()
        threadref = '{0}/{1}/{2}'.format(l, user, repo)
        s = make_session(name, user, repo, email)
        s['status'] = status
        s['soci'] = soci
        sessionlist[threadref] = s
        last = threadref
    return s

#def load_create_contact(contact):

#def load_contact_to_session():


def scan_contacts():
    for contact in ls[get_session_metarepo()]().split():
        load_contact(contact)

def get_list_path(l):
    return get_session_repo() + l + get_hyre_ext()

def get_list_sessions():
    for threadlist in ls[get_session_repo]().split():
        with open(threadlist, "r") as f:
            for repo in f.readlines():
                threadref = threadlist[:-3] + '/' + repo
                slash = repo.index('/')
                label = repo[:slash] + ' - ' + repo[slash:]
                items.append((label, partial(act, threadref)))

def serialize_list(s, require_filename=False):
    name = s['name'] if 'name' in s else '[unnamed]'
    email = s['email'] if 'email' in s else ''
    #if 'user' in s and len(s['user']):
    #    user = s['user']
    #    if require_filename and user == 'new_contact':
    #else:
    #    user = 'new_contact'
    user = s['user'] if 'user' in s and len(s['user']) else 'new_contact'
    contact = user + get_hyre_ext()
    filepath = get_session_metarepo() + 'contacts/python/' + contact
    with open(filepath, "w+") as f:
        f.write(contact_front_matter(name, email))
        text = '\n'
        l = current_issue()
        for msg in s['soci']:
            if 'to' in msg:
                text += '## to\n' + msg['to'] + '\n'
            elif 'from' in msg:
                text += '## from\n' + msg['from'] + '\n'
            elif 'repo' in msg:
                t = '# [{0}] {1} in a Python open source newsletter\n'
                text = (t + '##+repo: {2}').format(l, msg['repo'],
                        msg['url']) + text
        f.write(text)
    return filepath

def select_list_project(project):
    sessionlist['curr'] = project

def reset_list_selection():
    sessionlist['curr'] = ''

def append_save_thread_to_list():
    import os
    import errno
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    data = xerox.paste()
    target = get_threadref_from_url(data)
    repo = target['user'] + '/' + target['repo']
    select_list_project(repo)
    l = sessionlist['list']
    p = get_list_path(l)
    try:
        hndl = os.open(p, flags)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # pass
            with open(p, "a") as f:
                f.write('\n' + repo)
        else:
            raise
    else:
        with os.fdopen(hndl, "w+") as f:
            f.write(stamp('#+title: Contact sheet for magazine issue {}'
                ).format(l) + repo)

def list_threads(act):
    '''Creates a list view of threads with their corresponding contact
    names beside them.'''
    scan_contacts()
    items = []
    items = get_list_sessions()
    return items

def autoput_contact_profile_info(s):
    data = xerox.paste()
    i = 0
    for line in data.split():
        if len(line):
            if i == 0:
                l = line.split(' ')
                s['name'] = l[0] + ' ' + l[1]
            elif i == 1:
                s['bio'] = line
            elif i == 3:
                s['job'] = line
            elif i == 4:
                s['loc'] = line
            elif i == 5:
                s['email'] = line
            elif i == 6:
                s['page'] = line
            i += 1

def add_status_actions(s, status, items):
    items.append(('actions| |-+ add contact profile info',
        partial(autoput_contact_profile_info, s)))
    items.append(('       |-+ put intro message in outbox',
        partial(autoput_contact_profile_info, s)))
    items.append(('       vwv |-+ view last message',
        lambda: print(get_last_message(s))))
    return items

def process_list_headers(lines):
    i = 0
    for line in lines:
        if line.startswith('#+'):
            i += 1
            if line.startswith('#+stamp'):
                print(line)
        else:
            return lines[i:]

def add_list_prompt(n):
    l = len(n)
    p = '{} item' if l == 1 else '{} items'
    print(p.format(l) + '       | Select to see available actions:')

def pad_n(n, s):
    from math import floor
    d = n - len(s)
    if d % 2 == 0:
        x = int(d / 2)
        p = ''.join([' '] * x)
        return p + s + p
    else:
        x = int(floor(d / 2))
        p = ''.join([' '] * x)
        p1 = ''.join([' '] * (x + 1))
    return p1 + s + p

def edit_list():
    '''Creates a list build view of campaigns (plans) or of projects
    to feature in a given campaign.'''
    items = []
    l = sessionlist['list']
    if len(l) > 0:
        print('current: {} [listbuilder]'.format(l))
        items.append((' ← pick a different list to edit',
            reset_list_pick))
        items.append((' + add thread to list',
            append_save_thread_to_list))
        listfile = get_list_path(l)
        try:
            with open(listfile, "r") as f:
                n = process_list_headers(f.readlines())
                add_list_prompt(n)
                for project in n: 
                #def get_thread_status(project):
                    prj = project.strip()
                    slash = prj.index('/')
                    user = prj[:slash]
                    repo = prj[slash + 1:]
                    c = load_contact(user)
                    #return project + '[{}]'.format(c['status'])
                    #status = get_thread_status(project)
                    status = c['status']
                    items.append(('{0}| {1}'.format(pad_n(9, status), 
                        prj), partial(select_list_project, prj)))
                    if prj == sessionlist['curr']:
                        if session['repo'] == c['repo']:
                            reset_list_selection()
                        else:
                            set_session(c)
                            add_status_actions(c, status, items)
        except FileNotFoundError:
            print('[No items in list]')
    else:
        print('Pick a plan list to edit:')
        for threadlist in ls[get_session_repo]().split():
            with open(threadlist, "r") as f:
                for repo in f.readlines():
                    print(repo)
    return items

def edit_settings():
    '''Creates a list view of settings with their toggles.'''
    items = []
    items.append(
        ('|x| autoclone repository when git url is given',
            partial(print, 'autoclone'))
    )
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
#    '''plan campaign'''
#    pass

@climenu.group(items_getter=edit_list, items_getter_kwargs={})
def build_group():
    '''open list'''
    pass

@climenu.group(items_getter=edit_settings, items_getter_kwargs={})
def build_group():
    '''edit settings'''
    pass

@climenu.menu(title='about this software')
def about():
    # A simple menu item
    print('Utility created by The Open Hyre.')
    print('This is open source work under the AGPLv3.')

if __name__ == '__main__':
    climenu.run()
