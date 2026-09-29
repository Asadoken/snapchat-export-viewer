#!/usr/bin/env python3
"""Generates a fake Snapchat export (invented people, places and pictures) for
trying the viewer, testing changes and taking screenshots without real data.

    python3 tools/make_demo_export.py            # writes ./demo-export
    python3 tools/make_demo_export.py some/dir

Standard library only.
"""
import json, os, random, struct, sys, uuid, zlib
from datetime import datetime, timedelta, timezone

random.seed(7)
OUT = sys.argv[1] if len(sys.argv) > 1 else 'demo-export'
NOW = datetime.now(timezone.utc).replace(microsecond=0)
ME = 'demo.user'
FRIENDS = [('alex.rivera', 'Alex'), ('sam_k', 'Sam K'), ('jordan.lee', 'Jordan'), ('priya.m', 'Priya'),
           ('noah_b', 'Noah'), ('mia.chen', 'Mia'), ('leo.s', 'Leo'), ('zara_x', 'Zara ✨')]
LINES = ["hey what's up", 'on my way 🚗', 'haha no way 😂', 'did you see that??', 'see you at 7',
         'that was so good 🔥', 'send me the pics!', 'lol', 'omw', "can't wait 🎉", 'miss you guys ❤️',
         'who is coming tonight?', 'running 10 mins late sorry', 'that view though 😍', 'gm ☀️', 'gn 🌙']
PLACES = [(51.5072, -0.1276, 'London'), (48.8566, 2.3522, 'Paris'), (40.7128, -74.006, 'New York'),
          (41.3874, 2.1686, 'Barcelona'), (35.6762, 139.6503, 'Tokyo')]


def utc(d):
    return d.strftime('%Y-%m-%d %H:%M:%S UTC')


def png(path, w=270, h=480):
    """Writes a vertical gradient PNG in a random hue."""
    a = [random.randint(40, 255) for _ in range(3)]
    b = [random.randint(0, 120) for _ in range(3)]
    raw = bytearray()
    for y in range(h):
        t = y / (h - 1)
        px = bytes(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
        raw += b'\x00' + px * w
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    with open(path, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                 + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def rand_time(days_back):
    return NOW - timedelta(days=random.uniform(0, days_back), seconds=random.randint(0, 86400))


for d in ('json', 'chat_media', 'memories'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
J = lambda name, data: json.dump(data, open(os.path.join(OUT, 'json', name), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# chats
chats = {}
for i, (user, _) in enumerate(FRIENDS):
    msgs = []
    for _ in range(random.randint(40, 400) // (i + 1) + 20):
        t = rand_time(365 * 3)
        mine = random.random() < .5
        media_id = ''
        kind = 'TEXT'
        if random.random() < .08:
            kind, media_id = 'MEDIA', 'b~' + uuid.uuid4().hex
            png(os.path.join(OUT, 'chat_media', f'{t:%Y-%m-%d}_{media_id}.png'))
        msgs.append({'From': ME if mine else user, 'Media Type': kind, 'Created': utc(t),
                     'Content': random.choice(LINES) if kind == 'TEXT' or random.random() < .3 else '',
                     'Conversation Title': None, 'IsSender': mine, 'Created(microseconds)': int(t.timestamp() * 1000),
                     'IsSaved': True, 'Media IDs': media_id})
    chats[user] = sorted(msgs, key=lambda m: -m['Created(microseconds)'])
group = []
for _ in range(120):
    t = rand_time(400)
    who = random.choice([ME] + [u for u, _ in FRIENDS[:4]])
    group.append({'From': who, 'Media Type': 'TEXT', 'Created': utc(t), 'Content': random.choice(LINES),
                  'Conversation Title': 'Weekend Plans 🏖️', 'IsSender': who == ME,
                  'Created(microseconds)': int(t.timestamp() * 1000), 'IsSaved': True, 'Media IDs': ''})
chats[str(uuid.uuid4())] = group
J('chat_history.json', chats)
J('snap_history.json', {u: [{'From': random.choice([u, ME]), 'Media Type': random.choice(['IMAGE', 'VIDEO']),
                             'Created': utc(t), 'Conversation Title': None, 'IsSender': False,
                             'Created(microseconds)': int(t.timestamp() * 1000)}
                            for t in [rand_time(30) for _ in range(random.randint(1, 6))]] for u, _ in FRIENDS[:4]})

# memories: files + history with locations
history = []
for _ in range(90):
    t = rand_time(365 * 4)
    lat, lng, _ = random.choice(PLACES)
    png(os.path.join(OUT, 'memories', f'{t:%Y-%m-%d}_{str(uuid.uuid4()).upper()}-main.png'))
    history.append({'Date': utc(t), 'Media Type': 'Image',
                    'Location': f'Latitude, Longitude: {lat + random.uniform(-.03, .03):.5f}, {lng + random.uniform(-.03, .03):.5f}'})
J('memories_history.json', {'Saved Media': history})

created = NOW - timedelta(days=365 * 6)
J('account.json', {'Basic Information': {'Username': ME, 'Name': 'Demo', 'Creation Date': utc(created), 'Country': 'GB'},
                   'Device History': [{'Make': 'Apple', 'Model': 'iPhone16,2', 'Start Time': utc(NOW - timedelta(days=300))},
                                      {'Make': 'Apple', 'Model': 'iPhone14,2', 'Start Time': utc(NOW - timedelta(days=1100))}]})
J('friends.json', {'Friends': [{'Username': u, 'Display Name': n, 'Creation Timestamp': utc(rand_time(365 * 5)),
                                'Source': random.choice(['Added by username', 'Added by Quick Add', 'Added by phone'])} for u, n in FRIENDS],
                   'Deleted Friends': [{'Username': 'old.pal', 'Display Name': 'Old Pal', 'Creation Timestamp': utc(rand_time(2000))}]})
J('account_history.json', {'Display Name Change': [{'Date': utc(created), 'Display Name': 'D'}, {'Date': utc(NOW - timedelta(days=700)), 'Display Name': 'Demo'}]})
J('ranking.json', {'Statistics': {'Snapscore': '48210.0', 'Your Total Friends': str(len(FRIENDS))}})
J('story_history.json', {
    'Your Story Views': [{'Story Date': utc(NOW - timedelta(days=d)), 'Story Views': random.randint(3, 40), 'Story Replies': random.randint(0, 3)} for d in range(1, 25, 2)],
    'Friend and Public Story Views': [{'View': random.choice(FRIENDS)[0], 'Media Type': random.choice(['STORY', 'VIDEO']), 'View Date': utc(rand_time(30))} for _ in range(80)]})
J('snap_map_places_history.json', {'Snap Map Places History': [
    {'Date': utc(rand_time(500)), 'Place': p, 'Place Location': c, 'Share Type': 'Story Post'}
    for p, c in [('Riverside Café', 'London, England'), ('Parc Güell', 'Barcelona, Spain'), ('Shibuya Crossing', 'Tokyo, Japan')]]})
J('location_history.json', {
    'Home, School & Work': {'inferredHome': 'lat 51.507 ± 20 meters, long -0.128 ± 20 meters', 'inferredWork': 'lat 51.515 ± 20 meters, long -0.09 ± 20 meters'},
    'Location History': [[utc(rand_time(60)), f'{51.5 + random.uniform(-.05, .05):.3f}, {-0.12 + random.uniform(-.08, .08):.3f}'] for _ in range(40)],
    'Areas you may have visited in the last two years': [{'Time': utc(rand_time(700)).replace('-', '/'), 'City': c, 'Region': r}
                                                         for c, r in random.choices([('camden', 'London'), ('hackney', 'London'), ('brighton', 'Sussex')], k=30)],
    'Businesses and places you may have visited': {'inferredVisitationList': [['City Gym', 'London'], ['Corner Books', 'London']],
                                                   'businessList': [[f'{rand_time(300):%Y-%m-%d}', 'Coffee Co']]}})
J('talk_history.json', {'Outgoing Calls': [{'Date & Time': utc(rand_time(60)), 'Type': 'VIDEO', 'Result': 'Call Succeeded', 'City': 'london', 'Length (sec)': '312'}],
                        'Incoming Calls': [{'Date & Time': utc(rand_time(60)), 'Type': 'AUDIO', 'Result': 'Call Received', 'City': 'london', 'Length (sec)': '45'}]})
J('user_profile.json', {
    'Engagement': [{'Event': 'Application Opens', 'Occurrences': 212}, {'Event': 'Snaps Viewed in a Story', 'Occurrences': 180}, {'Event': 'Chats Sent', 'Occurrences': 96}],
    'Breakdown of Time Spent on App': ['Camera: 48.2%', 'Messaging: 22.5%', 'Stories: 14.1%', 'Map: 8.9%', 'Others: 6.3%'],
    'Interest Categories': ['Music', 'Travel', 'Coffee Shops', 'Sneakers', 'Gaming'],
    'Content Categories': ['Comedy', 'Sports/Football', 'Food & Drink'],
    'Ads You Interacted With': [{'Advertiser Name': 'Example Shoes', 'Date': f'{rand_time(200):%Y-%m-%d}'}]})
print(f'Demo export written to {OUT}/')
