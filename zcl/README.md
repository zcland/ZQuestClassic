# ZC Land's fork of ZQuest Classic

This fork builds the web player that ZC Land's Arcade (https://www.zcland.net/arcade) uses to play quests from ZC Land's
Database in the browser. It is ZQuest Classic, unchanged, plus these files:

- `.github/workflows/zcl-web-player.yml`: once a day, checks ZQuest Classic's `main`. When it has a commit without a
  release here, it builds the web player (zplayer) from that commit and publishes a `web-player-<commit>` release.
  It also merges upstream into this fork's `main` and `zcl` branches.
- `zcl/patch_web_package.py`: ZC Land's edits to the built player. It removes analytics, the service worker, and every
  request to ZQuest Classic's quest data, and adds an embedded mode (`#embed`) that shows only the game's screen.

Only files are added, never changed, so merging upstream never conflicts. Upstream's own workflows are turned off here.

To use a new release on ZC Land, put its tag and checksum in `site/plugins/zcl-portal/config/zc_player.json` in
zcland/zcl. The site installs it on its next deploy.

ZQuest Classic is GPL-3.0. Every release's `SOURCE.txt` names the exact commits it was built from.
