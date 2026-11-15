"""Turns ZQuest Classic's packaged web player (build_emscripten/<config>/packages/web) into ZC Land's.

ZC Land's Arcade plays quests from its own Database, in a pane on its player page or popped out on its own. This
script only edits the built files, so the zcl branch never changes upstream's sources and merging upstream stays
conflict-free. Every edit is checked: if upstream changes what an edit looks for, this fails instead of shipping a
player that still reaches out to ZQuest Classic's servers.

- No quest data from ZQuest Classic: the player's data origin (its quest list and quest files) becomes an empty list
  served with the player (zcl-data/manifest.json), and the preload of ZC's list is removed. ZC Land opens each quest
  by its own address on www.zcland.net.
- No analytics, and no service worker (ZC Land versions the player's address instead).
- An embedded mode (#embed in the address): only the game's screen, filling the frame.
- SOURCE.txt says where the source is (the GPL's offer), and VERSION.json which commits were built.
"""
import argparse
import json
import re
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('package', type=Path, help='the packages/web folder')
parser.add_argument('--fork-commit', required=True)
parser.add_argument('--upstream-commit', required=True)
parser.add_argument('--repository', required=True)
args = parser.parse_args()
web = args.package


def edit(path, pattern, replacement, count=None):
    text = path.read_text(encoding='utf-8')
    found = len(re.findall(pattern, text))
    if not found or (count is not None and found != count):
        sys.exit(f'{path}: expected {count or "some"} match(es) of {pattern!r}, found {found}. Upstream changed; update this script.')
    path.write_text(re.sub(pattern, replacement, text), encoding='utf-8')


page = web / 'play/index.html'
main = web / 'main.js'

# ZC's quest data: the list the player reads, and the files it names.
edit(main, r'''dataOrigin\s*:\s*(['"])https://data\.zquestclassic\.com\1''',
     'dataOrigin:new URL("../zcl-data",location.href).href.replace(/\\/$/,"")', count=1)
(web / 'zcl-data').mkdir(exist_ok=True)
(web / 'zcl-data/manifest.json').write_text('{}\n', encoding='utf-8')
edit(page, r'\s*<link rel="(?:preload|preconnect)" href="https://data\.zquestclassic\.com[^>]*>', '')

# Analytics.
edit(page, r'\s*<script async src="https://www\.googletagmanager\.com/[^"]*"></script>\s*<script>[^<]*gtag\([^<]*</script>', '', count=1)

# The service worker.
edit(page, r'''navigator\.serviceWorker\.register\((['"])\.\./sw\.js\1\);?''', '', count=1)
for name in ('sw.js', 'sw.js.map'):
    (web / name).unlink(missing_ok=True)
for worker in web.glob('workbox-*.js*'):
    worker.unlink()

# Embedded: only the screen. The address's hash says so, since every query parameter is passed to the player.
embed = '''
  <style>
    html.zcl-embed, html.zcl-embed body { margin: 0; height: 100%; overflow: hidden; background: #000; }
    html.zcl-embed header, html.zcl-embed .panel, html.zcl-embed .content { display: none !important; }
  </style>
  <script>
    if (/(^|[#&])embed(&|$)/.test(location.hash.slice(1))) document.documentElement.classList.add('zcl-embed');
  </script>
</head>'''
edit(page, r'</head>', embed, count=1)

for path in [page, main]:
    text = path.read_text(encoding='utf-8')
    for host in ('data.zquestclassic.com', 'googletagmanager.com'):
        if host in text:
            sys.exit(f'{path} still mentions {host}.')

(web / 'SOURCE.txt').write_text(
    'ZC Land\'s web player is ZQuest Classic (GPL-3.0), built from\n'
    f'https://github.com/{args.repository}/tree/{args.fork_commit}\n'
    f'which merges ZQuest Classic {args.upstream_commit} (https://github.com/ZQuestClassic/ZQuestClassic).\n',
    encoding='utf-8')
(web / 'VERSION.json').write_text(json.dumps({
    'fork_commit': args.fork_commit, 'upstream_commit': args.upstream_commit, 'repository': args.repository,
}, indent=2) + '\n', encoding='utf-8')
print('Patched', web)
