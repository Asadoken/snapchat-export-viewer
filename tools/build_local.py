#!/usr/bin/env python3
"""Puts an instant-opening copy of the viewer inside a Snapchat export folder.

    python3 tools/build_local.py /path/to/mydata~123456

Writes viewer/data.js and "Snapchat Viewer.html" into that folder. Double-click the
HTML file to open your data straight away, without choosing the folder each time.
Everything stays on your computer. Re-run it after updating the viewer or the export.

Mirrors buildData() in index.html; keep the two in step. Standard library only.
"""
import json, os, re, sys, collections

if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    sys.exit('usage: python3 tools/build_local.py /path/to/unzipped/export')
ROOT = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile(os.path.join(ROOT, 'json', 'chat_history.json')):
    sys.exit(f"No json/chat_history.json in {ROOT}. Request your data with 'Export JSON files' ticked and unzip it.")
J = lambda name: json.load(open(os.path.join(ROOT, 'json', name), encoding='utf-8'))


def load_or(name, default):
    try:
        return J(name)
    except (OSError, ValueError):
        return default


# --- media lookup: chat_media files are named DATE_<MediaID>.ext
chat_media = collections.defaultdict(list)
for f in (os.listdir(os.path.join(ROOT, 'chat_media')) if os.path.isdir(os.path.join(ROOT, 'chat_media')) else []):
    if '_' in f and not f.startswith('.'):
        chat_media[os.path.splitext(f.split('_', 1)[1])[0]].append(f)

account = load_or('account.json', {})
me = account.get('Basic Information', {}).get('Username', '')
friends = load_or('friends.json', {})
names = {f['Username']: f.get('Display Name') or f['Username']
         for group in friends.values() if isinstance(group, list)
         for f in group if isinstance(f, dict) and f.get('Username')}
if me:
    names[me] = account.get('Basic Information', {}).get('Name') or me

chats = load_or('chat_history.json', {})
snaps = load_or('snap_history.json', {})

conversations = []
for key in set(chats) | set(snaps):
    msgs = []
    title = None
    for m in chats.get(key, []):
        title = title or m.get('Conversation Title')
        files = []
        for mid in filter(None, (p.strip() for p in (m.get('Media IDs') or '').split('|'))):
            files += chat_media.get(mid, [])
        msgs.append({
            't': m['Created(microseconds)'],
            'f': m['From'],
            'k': m['Media Type'],
            'c': m.get('Content') or '',
            'm': files,
            'x': 1 if m.get('Media IDs') else 0,  # had media, even if not exported
            's': 1 if m.get('IsSaved') else 0,
        })
    for s in snaps.get(key, []):
        msgs.append({'t': s['Created(microseconds)'], 'f': s['From'], 'k': 'SNAP_' + s['Media Type'], 'c': '', 'm': [], 'x': 0, 's': 0})
    msgs.sort(key=lambda m: m['t'])
    people = sorted({m['f'] for m in msgs})
    conversations.append({
        'id': key,
        'group': bool(title),
        'name': (title.strip() if title else names.get(key, key)),
        'user': None if title else key,
        'members': people,
        'last': msgs[-1]['t'] if msgs else 0,
        'msgs': msgs,
    })
conversations.sort(key=lambda c: -c['last'])

# --- memories: DATE_UUID-main.ext (+ optional DATE_UUID-overlay.png)
mem = {}
pat = re.compile(r'^(\d{4}-\d{2}-\d{2})_(.+)-(main|overlay)\.(\w+)$')
for f in (os.listdir(os.path.join(ROOT, 'memories')) if os.path.isdir(os.path.join(ROOT, 'memories')) else []):
    m = pat.match(f)
    if not m:
        continue
    item = mem.setdefault(m.group(2), {'d': m.group(1)})
    item[m.group(3)] = f
memories = sorted((v for v in mem.values() if 'main' in v), key=lambda v: v['d'], reverse=True)

# --- where memories were taken: [epoch ms, 'I'|'V', lat, lng]; files carry no id, so the map links by day
from datetime import datetime, timezone
coord = re.compile(r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)')
mem_places = []
for m in load_or('memories_history.json', {}).get('Saved Media', []):
    c = coord.search(m.get('Location') or '')
    if not c or (float(c.group(1)) == 0 and float(c.group(2)) == 0):
        continue
    t = datetime.strptime(m['Date'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
    mem_places.append([int(t.timestamp() * 1000), m.get('Media Type', '')[:1], float(c.group(1)), float(c.group(2))])

data = {
    'me': me,
    'names': names,
    'conversations': conversations,
    'memories': memories,
    'memPlaces': mem_places,
    'friends': friends,
    'account': account,
    'profile': load_or('user_profile.json', {}),
    'accountHistory': load_or('account_history.json', {}),
    'location': load_or('location_history.json', {}),
    'places': load_or('snap_map_places_history.json', {}).get('Snap Map Places History', []),
    'stories': load_or('story_history.json', {}),
    'calls': load_or('talk_history.json', {}),
    'ranking': load_or('ranking.json', {}),
    'bitmoji': load_or('bitmoji.json', {}),
    'connectedApps': load_or('connected_apps.json', {}),
    'stickers': load_or('custom_sticker.json', {}).get('My Custom Stickers', []),
    'terms': load_or('terms_history.json', {}),
    'searches': load_or('search_history.json', {}),
}
os.makedirs(os.path.join(ROOT, 'viewer'), exist_ok=True)
out = os.path.join(ROOT, 'viewer', 'data.js')
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('window.SNAP=')
    json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
    fh.write(';')
html = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
marker = '<script>\n(() => {'
assert marker in html, 'index.html layout changed; update build_local.py'
page = os.path.join(ROOT, 'Snapchat Viewer.html')
with open(page, 'w', encoding='utf-8') as fh:
    fh.write(html.replace(marker, '<script src="viewer/data.js"></script>\n' + marker, 1))
print(f'{len(conversations)} conversations, {sum(len(c["msgs"]) for c in conversations)} messages, '
      f'{len(memories)} memories\nOpen: {page}')
