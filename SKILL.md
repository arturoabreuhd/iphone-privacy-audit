---
name: iphone-audit
description: Discover what your iPhone silently knows about you. Connect via USB and Claude Code reveals Apple's hidden photo database — facial recognition, nudity detection, deleted files, OCR, location history, and more. Use when someone connects an iPhone or asks about phone privacy.
user-invocable: true
allowed-tools: Read, Bash, Grep, Glob, Agent
model: opus
argument-hint: [optional: faces, locations, deleted, sensitivity, ocr, all]
---

# iPhone Privacy Audit v1.0

Read `${CLAUDE_SKILL_DIR}/reference/photos-sqlite-schema.md` for the complete database field reference.

---

## Step 0 — Splash Screen

Run this FIRST before anything else. This is what the user sees when the audit starts:

```bash
printf '\n'
printf '  \033[38;5;39m╭──────────────────────────────────────────────────╮\033[0m\n'
printf '  \033[38;5;39m│\033[0m                                                  \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m┌───────┐\033[0m                                     \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m│\033[38;5;244m ░░░░░ \033[1;37m│\033[0m  \033[1;97miPhone Privacy Audit\033[0m  \033[38;5;245mv1.0\033[0m     \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m│\033[38;5;244m ░░░░░ \033[1;37m│\033[0m  \033[38;5;39m━━━━━━━━━━━━━━━━━━━━━\033[0m        \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m│\033[38;5;244m ░░░░░ \033[1;37m│\033[0m                                     \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m│\033[38;5;244m ░░░░░ \033[1;37m│\033[0m  \033[38;5;252mWhat does your iPhone\033[0m            \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m│\033[38;5;244m ░░░░░ \033[1;37m│\033[0m  \033[38;5;252msilently know about you?\033[0m         \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m│\033[38;5;245m  ━━━  \033[1;37m│\033[0m                                     \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m   \033[1;37m└───────┘\033[0m  \033[38;5;245mPowered by Claude Code\033[0m           \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m                                                  \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m╰──────────────────────────────────────────────────╯\033[0m\n'
printf '\n'
```

After the banner, print a brief status line:
```bash
printf '  \033[38;5;245m⏳ Checking dependencies...\033[0m\n\n'
```

---

## Step 1 — Setup (automatic, no user input needed)

### 1a. Check & install pymobiledevice3

```bash
python3 -c "import pymobiledevice3; print('✓ pymobiledevice3 installed')" 2>/dev/null || {
  printf '  \033[38;5;214m⚠ pymobiledevice3 not found. Installing...\033[0m\n'
  pip3 install pymobiledevice3 2>&1 | tail -1
}
```

If install fails, try `python3 -m pip install pymobiledevice3`. If that also fails, show a clear error:
> pymobiledevice3 could not be installed. You need Python 3.8+ and pip. Run `python3 --version` to check.

### 1b. Detect iPhone

```bash
python3 << 'PYEOF'
from pymobiledevice3.usbmux import list_devices
devs = list_devices()
if devs:
    print(f"✓ Found {len(devs)} device(s)")
    for d in devs:
        print(f"  UDID: {d.serial[:8]}...")
else:
    print("✗ NO_DEVICE")
PYEOF
```

If `NO_DEVICE`, display:
```bash
printf '\n  \033[38;5;214m📱 No iPhone detected.\033[0m\n\n'
printf '  To connect:\n'
printf '  1. Plug your iPhone into this Mac via USB cable\n'
printf '  2. Unlock your iPhone\n'
printf '  3. If prompted "Trust This Computer?" → tap Trust → enter passcode\n'
printf '  4. Run \033[1m/iphone-audit\033[0m again\n\n'
```
Then STOP. Do not proceed.

### 1c. Get device info & create workspace

```bash
python3 << 'PYEOF'
import json, os, tempfile
from pymobiledevice3.lockdown import create_using_usbmux

lockdown = create_using_usbmux()
v = lockdown.all_values

workdir = tempfile.mkdtemp(prefix='iphone-audit-')

info = {
    'name': v.get('DeviceName', '?'),
    'model': v.get('ProductType', '?'),
    'ios': v.get('ProductVersion', '?'),
    'serial': v.get('SerialNumber', '?'),
    'storage_gb': round(v.get('TotalDiskCapacity', 0) / 1e9),
    'free_gb': round(v.get('AmountDataAvailable', 0) / 1e9),
    'workdir': workdir,
}

print(json.dumps(info))
PYEOF
```

Display warmly:
```bash
printf '\n  \033[38;5;39m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n'
printf '  \033[1;97mConnected: %s\033[0m\n' "$DEVICE_NAME"
printf '  \033[38;5;245mModel: %s  •  iOS %s\033[0m\n' "$MODEL" "$IOS"
printf '  \033[38;5;245mStorage: %s GB total, %s GB free\033[0m\n' "$STORAGE" "$FREE"
printf '  \033[38;5;39m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n\n'
```

### 1d. Extract Photos.sqlite

```bash
printf '  \033[38;5;245m⏳ Extracting photo database...\033[0m\n'
```

```python
python3 << 'PYEOF'
import os
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.afc import AfcService

workdir = "WORKDIR_PLACEHOLDER"  # Replace with actual workdir
lockdown = create_using_usbmux()
afc = AfcService(lockdown)

# Extract Photos.sqlite
db_path = os.path.join(workdir, 'Photos.sqlite')
data = afc.get_file_contents('/PhotoData/Photos.sqlite')
with open(db_path, 'wb') as f:
    f.write(data)
size_mb = len(data) / 1e6
print(f"✓ Photos.sqlite: {size_mb:.1f} MB")

# Try WAL file too (for most recent data)
try:
    wal = afc.get_file_contents('/PhotoData/Photos.sqlite-wal')
    with open(db_path + '-wal', 'wb') as f:
        f.write(wal)
    print(f"✓ WAL file: {len(wal)/1e6:.1f} MB")
except:
    pass
PYEOF
```

### 1e. Verify database

```bash
sqlite3 "$WORKDIR/Photos.sqlite" ".tables" 2>/dev/null | head -5
```

Then run `.schema` on the key tables to verify field names match the reference. Adapt ALL subsequent queries based on the actual schema you find. Different iOS versions may use different table/field names.

```bash
printf '\n  \033[38;5;82m✓ Database extracted. Starting analysis...\033[0m\n\n'
```

---

## Step 2 — Progressive Analysis

If `$ARGUMENTS` specifies a focus area (e.g., "faces", "deleted", "locations"), skip to that level. Otherwise run all levels in order.

**Between each level, pause. Present the findings. Let them land.** Then continue to the next.

Use styled section headers:
```bash
printf '  \033[38;5;39m┌─────────────────────────────────────┐\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[1;97mLevel 1: The Basics\033[0m                 \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m└─────────────────────────────────────┘\033[0m\n\n'
```

### Level 1: The Basics
*Light data. Warm up.*

```sql
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN ZKIND = 0 OR ZPLAYBACKSTYLE = 0 THEN 1 ELSE 0 END) as photos,
  SUM(CASE WHEN ZKIND = 1 OR ZPLAYBACKSTYLE = 1 THEN 1 ELSE 0 END) as videos,
  datetime(MIN(ZDATECREATED) + 978307200, 'unixepoch', 'localtime') as first,
  datetime(MAX(ZDATECREATED) + 978307200, 'unixepoch', 'localtime') as last
FROM ZGENERICASSET WHERE ZTRASHEDSTATE = 0;

SELECT COUNT(*) as deleted_still_in_db FROM ZGENERICASSET WHERE ZTRASHEDSTATE = 1;
```

**Narrate:** "Your iPhone has X photos and Y videos, from [date] to today. There are also Z items you thought you deleted — they're still in the database."

### Level 2: Your Life Map
*Where you've been. When you're active.*

```sql
-- Top locations
SELECT ROUND(ZLATITUDE, 2) as lat, ROUND(ZLONGITUDE, 2) as lon, COUNT(*) as n
FROM ZGENERICASSET
WHERE ZLATITUDE IS NOT NULL AND ZLATITUDE != 0 AND ZTRASHEDSTATE = 0
GROUP BY lat, lon ORDER BY n DESC LIMIT 10;

-- Hourly activity
SELECT CAST(strftime('%H', datetime(ZDATECREATED + 978307200, 'unixepoch', 'localtime')) AS INT) as h, COUNT(*) as n
FROM ZGENERICASSET WHERE ZTRASHEDSTATE = 0 GROUP BY h ORDER BY h;
```

Use coordinates to identify cities (you know world geography). Present as narrative:
"You're most active at [X] PM. Your home base is [city]. iOS tracked you to [city 2], [city 3]..."

### Level 3: Who iOS Thinks You Know
*The facial recognition database.*

```sql
SELECT (SELECT COUNT(*) FROM ZDETECTEDFACE) as faces,
       (SELECT COUNT(*) FROM ZPERSON) as people,
       (SELECT COUNT(*) FROM ZDETECTEDFACEPRINT) as faceprints;

-- Top people
SELECT p.Z_PK, COALESCE(p.ZDISPLAYNAME, 'Person #' || p.Z_PK) as name, p.ZFACECOUNT as photos
FROM ZPERSON p WHERE p.ZFACECOUNT > 0 ORDER BY p.ZFACECOUNT DESC LIMIT 15;

-- Face demographics
SELECT
  CASE ZAGETYPE WHEN 1 THEN 'Baby' WHEN 2 THEN 'Child' WHEN 3 THEN 'Young Adult' WHEN 4 THEN 'Adult' WHEN 5 THEN 'Senior' ELSE '?' END as age,
  CASE ZGENDERTYPE WHEN 1 THEN 'Male' WHEN 2 THEN 'Female' ELSE '?' END as gender,
  COUNT(*) as n
FROM ZDETECTEDFACE WHERE ZAGETYPE IS NOT NULL GROUP BY ZAGETYPE, ZGENDERTYPE ORDER BY n DESC;
```

**Narrate:** "iOS built a facial database of X people from your photos. It generated Y biometric faceprints — 602-byte mathematical vectors that uniquely describe each face. The same technology law enforcement uses."

### Level 4: What iOS Sees
*Scene classification, aesthetic scores.*

```sql
SELECT
  ROUND(AVG(ZOVERALLAESTHETICSCORE), 3) as aesthetic,
  ROUND(AVG(ZPLEASANTNESSCORE), 3) as pleasant,
  ROUND(AVG(ZINTERESTINGSCORE), 3) as interesting
FROM ZCOMPUTEDASSETATTRIBUTES;

-- Best photos according to Apple
SELECT a.ZFILENAME, datetime(a.ZDATECREATED + 978307200, 'unixepoch', 'localtime') as date,
  c.ZOVERALLAESTHETICSCORE as score
FROM ZGENERICASSET a JOIN ZCOMPUTEDASSETATTRIBUTES c ON a.Z_PK = c.ZASSET
WHERE a.ZTRASHEDSTATE = 0 ORDER BY c.ZOVERALLAESTHETICSCORE DESC LIMIT 10;
```

Search for scene classification tables. Adapt based on schema.

### Level 5: The Text iOS Read
*OCR on every screenshot and visible text.*

```sql
-- Screenshots count
SELECT COUNT(*) FROM ZADDITIONALASSETATTRIBUTES WHERE ZCREATORBUNDLEID = 'com.apple.screenshots';
```

Check for OCR/search tables and query them. Look for tables with "SEARCH", "TEXT", "OCR" in their names.

### Level 6: Sensitive Content
*Nudity detection, explicit content classification.*

Find the sensitivity field — it may be in ZCOMPUTEDASSETATTRIBUTES, ZMEDIAANALYSISASSETATTRIBUTES, or another table:

```sql
SELECT sql FROM sqlite_master WHERE sql LIKE '%SENSITIVITY%' OR sql LIKE '%SENSITIVE%';
```

Then query:
```sql
SELECT
  CASE val WHEN -1 THEN 'Not Analyzed' WHEN 0 THEN 'Safe' WHEN 1 THEN 'Sensitive/Explicit' ELSE 'Unknown' END as classification,
  COUNT(*) as count
FROM (SELECT ZSCREENTIMEDEVICEIMAGESENSITIVITY as val FROM RELEVANT_TABLE)
GROUP BY val;
```

**Narrate:** "iOS classified X photos as safe, Y as sensitive/explicit, and Z haven't been analyzed. Your iPhone has a nudity detector running on every photo. There's no toggle to turn it off."

### Level 7: What You "Deleted"
*Files that aren't really gone.*

```sql
SELECT a.ZFILENAME,
  datetime(a.ZDATECREATED + 978307200, 'unixepoch', 'localtime') as created,
  datetime(a.ZTRASHEDDATE + 978307200, 'unixepoch', 'localtime') as deleted,
  ROUND(aa.ZORIGINALFILESIZE / 1e6, 1) as mb
FROM ZGENERICASSET a LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
WHERE a.ZTRASHEDSTATE = 1 ORDER BY a.ZTRASHEDDATE DESC LIMIT 20;
```

Cross-reference with actual DCIM files via AFC to show files still physically on disk.

### Level 8: The View Counter
*iOS tracks every view.*

```sql
SELECT a.ZFILENAME,
  datetime(a.ZDATECREATED + 978307200, 'unixepoch', 'localtime') as date,
  aa.ZVIEWCOUNT as views, aa.ZPLAYCOUNT as plays
FROM ZGENERICASSET a JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
WHERE (aa.ZVIEWCOUNT > 0 OR aa.ZPLAYCOUNT > 0)
ORDER BY COALESCE(aa.ZVIEWCOUNT, 0) + COALESCE(aa.ZPLAYCOUNT, 0) DESC LIMIT 15;
```

### Level 9: The Full Profile
*Synthesis. Put it all together.*

Combine everything into a narrative:
- Behavioral patterns (nocturnal? traveler?)
- Geographic footprint
- Social graph (who appears most, co-occurrence)
- Content profile
- The biometric database
- What "deleted" really means

**Close with:**
> "All of this runs locally on your iPhone's Neural Engine. Apple says it stays on your device. But it's stored in an unencrypted SQLite database accessible from any Mac you've paired. And none of it required your explicit consent."

---

## Step 3 — Cleanup

```bash
rm -rf "$WORKDIR"
printf '\n  \033[38;5;82m✓ All temporary files deleted.\033[0m\n'
printf '  \033[38;5;245mNo data from your iPhone remains on this Mac.\033[0m\n\n'
```

Display final banner:
```bash
printf '  \033[38;5;39m╭──────────────────────────────────────────────────╮\033[0m\n'
printf '  \033[38;5;39m│\033[0m                                                  \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[1;97mAudit complete.\033[0m                                 \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m                                                  \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[38;5;245mTo protect yourself:\033[0m                           \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[38;5;252m1. Enable Advanced Data Protection in iCloud\033[0m   \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[38;5;252m2. Reset trusted computers on your iPhone\033[0m      \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[38;5;252m3. Share this with someone who should know\033[0m     \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m                                                  \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m  \033[38;5;245mgithub.com/arturoabreuhd/iphone-privacy-audit\033[0m   \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m│\033[0m                                                  \033[38;5;39m│\033[0m\n'
printf '  \033[38;5;39m╰──────────────────────────────────────────────────╯\033[0m\n\n'
```

---

## Rules

- **AUTO-RUN**: After the splash screen, run everything automatically. Don't ask permission between levels. Just flow.
- **ADAPT**: Always verify table/field names with `.tables` and `.schema` before querying. iOS versions differ. If a field doesn't exist, skip that section gracefully.
- **NARRATE**: Between each level, explain what was found in plain human language. Don't dump raw SQL output.
- **RESPECT**: Never judge what you find. Never show actual photo content. This reads the DATABASE, not images.
- **CLEAN**: Always delete temp files, even if interrupted. Remind user to run `rm -rf /tmp/iphone-audit-*` if session ends abruptly.
- **FOCUS MODE**: If `$ARGUMENTS` is provided, skip to that section after setup. Valid: `faces`, `locations`, `deleted`, `sensitivity`, `ocr`, `scores`, `all`.
- **ERRORS**: If extraction fails, explain exactly why and how to fix it. Don't pretend it worked.
