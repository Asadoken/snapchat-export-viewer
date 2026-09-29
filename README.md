# Snapchat Export Viewer

Browse the data you download from Snapchat the way it looks in the app. Snapchat's own export pages are plain tables and don't show your chat photos or videos; this page lays everything out properly.

**It runs entirely in your browser.** You open one HTML file and drop in your export folder. Nothing is uploaded, installed or saved.

## What you get

- **Chats**: every conversation with its messages, photos, videos and voice notes. Captions are shown on top of the media, like in the app. Includes Snaps sent and received, and search within a chat or across your chat list.
- **Map**: memories plotted where you took them, places Snapchat logged you at, your home and work as Snapchat worked them out, and the places you posted from.
- **Stories**: story circles for the accounts you watch most, views on your own story, and your Spotlight topics.
- **Memories**: a grid by month with an "On this day" row. Filter by photos, videos or year, and open anything full screen.
- **Recap**: messages per year or month, the days and hours you chat most, your top chats, your most-sent emoji, where your time in the app goes, and what Snapchat thinks you're into.
- **Friend profiles**: messages exchanged, your longest streak, when you became friends, and a chart of messages by year.
- **Profile**: Snapscore, devices, display name history, calls, connected apps, and every other part of the export.

It supports light and dark mode and works on phones.

## How to use it

1. **Get your data.** In Snapchat go to **Settings → My Data** (or [accounts.snapchat.com](https://accounts.snapchat.com) → My Data). Tick **Export your Memories** and **Export JSON files**, choose what to include, and submit. Snapchat emails you when it's ready.
2. **Unzip it.** Big accounts come in several zip files; unzip them all.
3. **Open the viewer.** Either:
   - use the hosted version: `https://<your-github-username>.github.io/snapchat-export-viewer/` (see [Hosting](#hosting-on-github-pages)), or
   - download `index.html` and double-click it.
4. **Drop your folder(s) onto the page**, or click to choose the folder.

Works in current Chrome, Edge, Firefox and Safari. Very large exports (tens of GB) are fine, because media is read only when it's on screen.

## Privacy

- Your files are read by your browser with the standard File API and shown through temporary `blob:` URLs. Nothing is sent to a server, and nothing is kept after you close the tab.
- The **Map** loads two things from the internet: the [Leaflet](https://leafletjs.com) map library from cdnjs, and map images from Esri's tile servers. Only the area of the map you're looking at is requested; your data isn't sent. Every other section works offline.
- When you choose a folder with the file picker, some browsers ask whether to "upload" the files. That's the browser's standard wording for giving a page access to a folder. Nothing leaves your computer. Dragging the folder in avoids the prompt.

## Trying it without your own data

```bash
python3 tools/make_demo_export.py
```

This writes a `demo-export/` folder with invented people, messages, places and pictures (standard library only). Drop that folder onto the page. It's also the safe way to take screenshots.

## Hosting on GitHub Pages

The viewer is one static file, so Pages can serve it as is: **Settings → Pages → Deploy from a branch → `main` / root**. Everyone who uses the hosted copy still keeps their data on their own computer.

## Limitations

- Snapchat leaves some things out of the export: chat photos and videos that had expired, who each call was with, and the images for custom stickers. The viewer marks missing media instead of leaving gaps.
- Memories files carry only a date, so each map point links to the memories from that day, not to one exact file.
- It reads the JSON format Snapchat uses as of 2026. Older exports with a different layout may load only partly. Issues and pull requests with (anonymised) samples are welcome.

## Contributing

Everything is in `index.html`: plain HTML, CSS and JavaScript with no build step. Test changes with the demo export. **Never commit a real export or screenshots of real data.** `.gitignore` excludes the usual folder names, but check before you push.

## Disclaimer

This is an independent project. It is not affiliated with, endorsed by, or sponsored by Snap Inc. Snapchat is a trademark of Snap Inc.

## License

[MIT](LICENSE)
