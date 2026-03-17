# iPhone Privacy Audit

**Discover what your iPhone silently knows about you.**

Connect your iPhone via USB. Claude Code extracts Apple's hidden photo database and reveals — level by level — the facial recognition data, nudity detection scores, "deleted" files that aren't deleted, OCR text from your screenshots, location history, and the behavioral profile iOS built without your consent.

```
  ╭──────────────────────────────────────────────────╮
  │                                                  │
  │   ┌───────┐                                      │
  │   │ ░░░░░ │  iPhone Privacy Audit  v1.0          │
  │   │ ░░░░░ │  ━━━━━━━━━━━━━━━━━━━━━              │
  │   │ ░░░░░ │                                      │
  │   │ ░░░░░ │  What does your iPhone               │
  │   │ ░░░░░ │  silently know about you?            │
  │   │  ━━━  │                                      │
  │   └───────┘  Powered by Claude Code              │
  │                                                  │
  ╰──────────────────────────────────────────────────╯
```

## What it finds

| Level | What | Example |
|-------|------|---------|
| 1 | **The Basics** | Total photos, date range, deleted items still in DB |
| 2 | **Your Life Map** | GPS locations, activity hours, travel patterns |
| 3 | **Who iOS Thinks You Know** | Facial recognition database, biometric faceprints, demographics |
| 4 | **What iOS Sees** | Scene classification, aesthetic scores, "best/worst" photo ratings |
| 5 | **The Text iOS Read** | OCR on every screenshot, extracted conversations |
| 6 | **Sensitive Content** | Nudity detection scores, explicit content classification |
| 7 | **What You "Deleted"** | Files marked as deleted but still physically on disk |
| 8 | **The View Counter** | How many times you viewed each photo/video |
| 9 | **The Full Profile** | Behavioral synthesis — who iOS thinks you are |

## Install

### Requirements

- **Claude Code** ([install](https://docs.anthropic.com/en/docs/claude-code))
- **Python 3.8+** (check: `python3 --version`)
- **iPhone + USB cable**
- **macOS** (the Mac must have been "trusted" by your iPhone at least once)

### Install (two commands)

```bash
git clone https://github.com/arturoabreuhd/iphone-privacy-audit.git
cp -r iphone-privacy-audit ~/.claude/skills/iphone-audit
```

### Verify

Open Claude Code and type `/iphone` — you should see `iphone-audit` in the autocomplete.

## Usage

### Full audit

```
/iphone-audit
```

Runs all 9 levels automatically. Takes 2-5 minutes depending on library size.

### Focus on a specific area

```
/iphone-audit faces
/iphone-audit deleted
/iphone-audit locations
/iphone-audit sensitivity
/iphone-audit ocr
```

## How it works

```
┌─────────────┐         USB          ┌─────────────────┐
│             │  ◄──────────────────► │                 │
│   iPhone    │    AFC Protocol       │    Your Mac     │
│             │    (Apple's own)      │                 │
└──────┬──────┘                       └────────┬────────┘
       │                                       │
       │  /PhotoData/Photos.sqlite             │  Claude Code
       │  (unencrypted SQLite DB)              │  + pymobiledevice3
       │                                       │
       │  Contains:                            │  Copies DB to /tmp
       │  ├── ZGENERICASSET (all photos)       │  Runs SQL queries
       │  ├── ZDETECTEDFACE (facial rec.)      │  Presents findings
       │  ├── ZDETECTEDFACEPRINT (biometrics)  │  Deletes everything
       │  ├── ZCOMPUTEDASSETATTRIBUTES (AI)    │
       │  ├── ZADDITIONALASSETATTRIBUTES       │
       │  │   └── ZVIEWCOUNT (how often        │
       │  │       you look at each photo)      │
       │  └── Sensitivity classification       │
       │      (nudity detection scores)        │
       │                                       │
       ▼                                       ▼
  11 billion computations              9 levels of analysis
  per photo by Neural Engine           presented progressively
  4,432 objects & scenes               then all temp files
  recognized silently                  deleted. Nothing stays.
```

### The flow

```
/iphone-audit
      │
      ▼
 ┌─────────┐    ┌──────────┐    ┌──────────────┐
 │  Setup   │───►│ Extract  │───►│   Analyze    │
 │          │    │          │    │              │
 │ Install  │    │ Copy     │    │ Level 1: Basics
 │ pymobile │    │ Photos   │    │ Level 2: Locations
 │ device3  │    │ .sqlite  │    │ Level 3: Faces
 │          │    │ to /tmp  │    │ Level 4: AI scores
 │ Detect   │    │          │    │ Level 5: OCR text
 │ iPhone   │    │ Verify   │    │ Level 6: Sensitivity
 │          │    │ schema   │    │ Level 7: "Deleted" files
 └─────────┘    └──────────┘    │ Level 8: View counts
                                │ Level 9: Full profile
                                └───────┬──────┘
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │   Cleanup    │
                                 │              │
                                 │ rm -rf /tmp  │
                                 │ /iphone-     │
                                 │ audit-*      │
                                 │              │
                                 │ Zero data    │
                                 │ remains.     │
                                 └──────────────┘
```

### What each level reveals

```
Level 1  The Basics         Total photos, date range, deleted items still in DB
Level 2  Your Life Map      GPS coordinates, travel patterns, active hours
Level 3  Faces              1,000+ people identified, biometric faceprints (602 bytes each)
Level 4  What iOS Sees      Aesthetic scores, scene classification, "best/worst" ratings
Level 5  Text               OCR on every screenshot, extracted conversations
Level 6  Sensitivity        Nudity detection, explicit content classification (99.5% confidence)
Level 7  "Deleted"          Files marked deleted but still physically on disk
Level 8  View Counter       How many times you opened each photo/video
Level 9  Full Profile       Behavioral synthesis: who iOS thinks you are
```

## Privacy & Safety

```
  ✓  Your data never leaves your Mac. No cloud. No API calls. No telemetry.
  ✓  No photos are accessed. The audit reads the database (metadata), not images.
  ✓  Temp files auto-delete. If session ends abruptly: rm -rf /tmp/iphone-audit-*
  ✓  This is YOUR data. The audit shows what Apple collected about you.
  ✓  100% open source. Read every line before you run it.
```

## How is this possible?

When you pair your iPhone with a Mac ("Trust This Computer"), macOS gets a pairing certificate that grants access to the iPhone's media filesystem via Apple's AFC (Apple File Conduit) protocol. Same access Finder and Image Capture use to import your photos.

`Photos.sqlite` sits in `/PhotoData/` on the device. Accessible through AFC. No jailbreak needed. This database contains every piece of metadata iOS generates about your photos using on-device machine learning: facial recognition, scene classification, nudity detection, OCR, GPS, aesthetic scores.

Apple runs **11 billion computations per photo** and recognizes **4,432 objects and scenes**. All silent. No toggle to disable. Stored in an unencrypted SQLite database.

## FAQ

**Q: Does this require jailbreaking?**
No. It uses the same USB access your Mac already has when you import photos.

**Q: Will this damage my iPhone?**
No. The audit only reads data. It doesn't write, modify, or delete anything on your device.

**Q: Does Apple know I ran this?**
No. The connection uses standard Apple protocols. There's no way for Apple to distinguish this from a normal photo import.

**Q: Can I run this on someone else's iPhone?**
Only if their iPhone trusts your Mac. This requires physical access to the iPhone and entering the passcode when prompted to "Trust This Computer."

**Q: What iOS versions are supported?**
Tested on iOS 17-26. The database schema may vary between versions — the skill adapts automatically.

## What's coming next

This is the first tool in a series. I'm building open-source privacy auditing tools that anyone can run, inspect, and verify before using. No black boxes. No trust-me-bro. You read the code, you decide if you want to run it.

Planned:
- **Browser audit** - what Chrome/Safari know about your browsing patterns, saved passwords exposure, tracker inventory
- **iCloud backup inspector** - decrypt and analyze what's actually in your iPhone backups
- **Location history mapper** - full GPS timeline reconstruction from your devices
- **Network traffic audit** - what your phone sends home when you're not looking
- **Android equivalent** - same audit for Google's photo analysis on Android devices

Every tool will be open source, run locally, and delete its temp files when done.

If you want to know when these drop, follow me: **[@arthurresearch](https://x.com/arthurresearch)**

I also write about trading, AI, philosophy, and building things that actually work. If that sounds interesting, come hang out.

## Credits

Built by [Arthur Abreu](https://x.com/arthurresearch) using [Claude Code](https://claude.ai/code).

Started at 2 AM because I didn't want to pay $50 for UltData. Ended up finding something worth a lot more than a recovered video.

## Contributing

Found a bug? iOS version that breaks the queries? Ideas for new audit levels? Open an issue or PR. This is meant to be community-driven.

If you're a security researcher and want to add detection for something I missed in Photos.sqlite, I'd love that.

## License

MIT
