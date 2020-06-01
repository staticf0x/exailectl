# -*- coding: utf-8 -*-
"""


Copyright (C) 2016 Michal Horáček <mail@horacekm.cz>
"""

import re
from subprocess import Popen, PIPE, call
import json
import dbus
from flask import Flask, send_from_directory, send_file

app = Flask('exailectl')


def exaile_cmd(cmd):
    prc = Popen('qdbus org.exaile.Exaile /org/exaile/Exaile ' + cmd, shell=True, stdout=PIPE)
    ret = prc.communicate()[0]

    return ret.decode('utf8').replace('\n', '')


@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf8') as fread:
        content = fread.read()

    return content


@app.route('/js/<path:path>')
def jq(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def css(path):
    return send_from_directory('css', path)


@app.route('/fonts/<path:path>')
def fonts(path):
    return send_from_directory('fonts', path)


@app.route('/ico/<path:path>')
def ico(path):
    return send_from_directory('ico', path)


@app.route('/get_track_info')
def get_track_info():
    return json.dumps({'title': exaile_cmd('GetTrackAttr title'),
                       'artist': exaile_cmd('GetTrackAttr artist'),
                       'album': exaile_cmd('GetTrackAttr album'),
                       'length': exaile_cmd('GetTrackAttr __length')})


@app.route('/get_state')
def get_state():
    state = exaile_cmd('GetState')
    progress = int(exaile_cmd('CurrentProgress'))

    return json.dumps({'state': state,
                       'progress': progress})


@app.route('/toggle_play')
def playback_toggle():
    exaile_cmd('PlayPause')

    return ''


@app.route('/prev')
def playback_prev():
    exaile_cmd('Prev')

    return ''


@app.route('/next')
def playback_next():
    exaile_cmd('Next')

    return ''


@app.route('/stop')
def playback_stop():
    exaile_cmd('Stop')

    return ''


@app.route('/volume_up')
def volume_up():
    call(['amixer', '-D', 'pulse', 'sset', 'Master', '5%+'])

    return ''


@app.route('/volume_down')
def volume_down():
    call(['amixer', '-D', 'pulse', 'sset', 'Master', '5%-'])

    return ''


@app.route('/playlist')
def playlist():
    exaile_cmd('ExportPlaylist /tmp/exaileplaylist.m3u')

    with open('/tmp/exaileplaylist.m3u', 'r', encoding='utf8') as fread:
        lines = fread.readlines()

    tracks = []

    for line in lines[::2]:
        line = line.replace('\n', '')

        m = re.search(r'^#EXTINF:(\d+),(.+)$', line)

        if m:
            length = int(m.group(1))
            info = m.group(2).split(' - ')

            title = ' - '.join(info[:-1])
            artist = info[-1]

            length_info = '{}:{:02d}'.format(length//60, length % 60)

            tracks.append({'title': title,
                           'artist': artist,
                           'length': length_info})

    return json.dumps(tracks)


@app.route('/seek/<float:secs>')
def seek(secs):
    exaile_cmd('Seek {}'.format(secs))

    return ''


@app.route('/playlist_go/<int:offset>')
def playlist_go(offset):
    for _ in range(offset):
        exaile_cmd('Next')

    return ''


@app.route('/playlist_go_back/<int:offset>')
def playlist_go_back(offset):
    if float(exaile_cmd('CurrentProgress')) > 1:
        offset += 1

    for _ in range(offset):
        exaile_cmd('Prev')

    return ''


bus = dbus.SessionBus()
obj = bus.get_object('org.exaile.Exaile', '/org/exaile/Exaile')
iface = dbus.Interface(obj, 'org.exaile.Exaile')

app.debug = True
app.run(host='0.0.0.0', port=8001)
