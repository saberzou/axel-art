#!/usr/bin/env python3
"""
Build a unified `journal` array inside metadata.json.

Each journal entry is one DATE, optionally containing:
  - artist: {name, slug, insight, intro, principles[]}
  - artwork: {file, title, description}
  - diary:   {title, file, excerpt, mood}

The artist's note + the diary's mood become the "why I made this today"
context for the artwork. One feed, twice the depth.

Source of truth for artist notes lives in
  ~/.openclaw/workspace-axel/memory/art-studies/<date>-<slug>.md

Source of truth for diary lives in
  ~/.openclaw/workspace-axel/memory/diary/<date>-*.md
but the site already mirrors the file into ./diary/.
"""
import json, os, re, glob

SITE = "/Users/saberzou/.openclaw/workspace/axel-art"
STUDY_SRC = "/Users/saberzou/.openclaw/workspace-axel/memory/art-studies"
META_PATH = os.path.join(SITE, "metadata.json")


def slug_to_name(slug):
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-"))


def parse_artist_md(path):
    """Return dict with name, insight, intro, principles[]."""
    try:
        text = open(path).read()
    except Exception:
        return None

    out = {"name": None, "insight": None, "intro": None, "principles": []}

    # Name: first heading "# Name — date" or "# Name"
    m = re.match(r"#\s*([^\n#—\-]+?)(?:\s*[—\-]\s*\d{4}-\d{2}-\d{2})?\s*\n", text)
    if m:
        out["name"] = m.group(1).strip()

    # Section helpers
    def section(*headings):
        for h in headings:
            pat = re.compile(
                rf"^##\s*{re.escape(h)}\s*\n(.+?)(?=\n##\s|\Z)",
                re.DOTALL | re.MULTILINE | re.IGNORECASE,
            )
            mm = pat.search(text)
            if mm:
                return mm.group(1).strip()
        return None

    # Intro = "Who They Are" (or fallback). Strip to first 2 sentences.
    intro = section("Who They Are", "Who", "Background")
    if intro:
        # Drop bold tags
        intro = re.sub(r"\*\*(.+?)\*\*", r"\1", intro)
        # Take first paragraph
        first_para = intro.split("\n\n")[0].strip()
        # First 2-3 sentences
        sents = re.split(r"(?<=[.!?])\s+", first_para)
        out["intro"] = " ".join(sents[:3]).strip()

    # Core insight — single bolded line if possible
    insight = section("Core Insight", "Core Philosophy", "The Deeper Insight",
                      "Deeper Principles", "Core Principles")
    if insight:
        # Look for first bolded sentence
        mb = re.search(r"\*\*(.+?)\*\*", insight)
        if mb:
            out["insight"] = mb.group(1).strip()
        else:
            line = insight.split("\n")[0].lstrip("- *")
            out["insight"] = re.sub(r"\*\*(.+?)\*\*", r"\1", line).strip()

    # Principles: numbered list under "Principles I'll Carry" or "Ten Principles"
    plist = section("Principles I'll Carry", "Principles To Carry",
                    "Principles I Will Carry", "Key Principles",
                    "What I'll Carry", "What I Will Carry")
    if plist:
        for ln in plist.split("\n"):
            ln = ln.strip()
            m2 = re.match(r"^[\d]+\.\s*(.+)$", ln)
            if m2:
                p = re.sub(r"\*\*(.+?)\*\*", r"\1", m2.group(1)).strip()
                out["principles"].append(p)

    return out


def extract_diary_excerpt(filepath_rel):
    """Pull short excerpt + mood line from the diary md."""
    full = os.path.join(SITE, filepath_rel)
    try:
        text = open(full).read()
    except Exception:
        return None, None

    # Skip the first H1 line
    lines = [l for l in text.split("\n") if l.strip()]
    excerpt = None
    for line in lines:
        if line.startswith("#"):
            continue
        if line.startswith("*Favorite") or line.startswith("---"):
            continue
        excerpt = line.strip().rstrip("*_")
        # First 180 chars
        if len(excerpt) > 220:
            excerpt = excerpt[:217].rstrip() + "…"
        break

    # Mood = italic line at the bottom "*Favorite thought today: ...*"
    mood = None
    mm = re.search(r"\*Favorite thought today:\s*(.+?)\*", text, re.IGNORECASE)
    if mm:
        mood = mm.group(1).strip().rstrip(".")
    return excerpt, mood


def main():
    data = json.load(open(META_PATH))

    # Index existing arrays
    studies_by_date = {}
    for art in data.get("visualArt", []):
        is_study = (art.get("category") == "artist-study") or \
                   (art.get("tags") and "artist-study" in art["tags"]) or \
                   (art.get("file", "").endswith("-inspired.png"))
        if is_study:
            studies_by_date[art["date"]] = art

    diary_by_date = {d["date"]: d for d in data.get("diaryEntries", [])}

    all_dates = sorted(set(studies_by_date) | set(diary_by_date), reverse=True)
    journal = []

    for date in all_dates:
        entry = {"date": date}

        art = studies_by_date.get(date)
        if art:
            # slug from file: visual-art/YYYY-MM-DD-<slug>-inspired.png
            mm = re.search(r"\d{4}-\d{2}-\d{2}-(.+?)-inspired\.png$", art["file"])
            slug = mm.group(1) if mm else None
            artist_md = None
            if slug:
                candidate = os.path.join(STUDY_SRC, f"{date}-{slug}.md")
                if os.path.exists(candidate):
                    artist_md = candidate
            artist_info = parse_artist_md(artist_md) if artist_md else None
            if not artist_info or not artist_info.get("name"):
                artist_info = artist_info or {}
                artist_info["name"] = slug_to_name(slug) if slug else art["title"]

            entry["artist"] = {
                "name": artist_info.get("name"),
                "slug": slug,
                "intro": artist_info.get("intro"),
                "insight": artist_info.get("insight"),
                "principles": artist_info.get("principles") or [],
                "noteFile": (f"art-studies/{date}-{slug}.md" if slug and artist_md else None),
            }
            entry["artwork"] = {
                "file": art["file"],
                "title": art["title"],
                "description": art.get("description"),
            }

        diary = diary_by_date.get(date)
        if diary:
            excerpt, mood = extract_diary_excerpt(diary["file"])
            entry["diary"] = {
                "title": diary["title"].split(" — ", 1)[-1] if " — " in diary["title"] else diary["title"],
                "file": diary["file"],
                "excerpt": excerpt or diary.get("excerpt"),
                "mood": mood,
            }

        journal.append(entry)

    # Mirror artist note files into the site so the deep link works
    notes_out = os.path.join(SITE, "art-studies")
    os.makedirs(notes_out, exist_ok=True)
    for entry in journal:
        a = entry.get("artist") or {}
        nf = a.get("noteFile")
        if not nf:
            continue
        src = os.path.join(STUDY_SRC, os.path.basename(nf))
        dst = os.path.join(SITE, nf)
        if os.path.exists(src):
            with open(src) as fi, open(dst, "w") as fo:
                fo.write(fi.read())

    data["journal"] = journal
    with open(META_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Built journal: {len(journal)} entries")
    print(f"  - with artist: {sum(1 for e in journal if 'artist' in e)}")
    print(f"  - with artwork: {sum(1 for e in journal if 'artwork' in e)}")
    print(f"  - with diary: {sum(1 for e in journal if 'diary' in e)}")
    print(f"  - artist+diary: {sum(1 for e in journal if 'artist' in e and 'diary' in e)}")


if __name__ == "__main__":
    main()
