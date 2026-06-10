#!/usr/bin/env python3
"""
Build a unified `journal` array inside metadata.json.

Each entry is one DATE, focused on the artist study + the artwork:
  - artist: {name, slug, intro, insight, principles[], noteFile}
  - rationale: Axel's voice — why this artist today (1-3 sentences)
  - artwork: {file, title, description}

The diary is NOT shown on the site. Axel's voice lives in `rationale`.
For new nightly entries, write the rationale into a sidecar JSON:
  ~/.openclaw/workspace-axel/memory/art-studies/<date>-<slug>-rationale.txt
or a `rationale` field in <date>-<slug>-inspired-meta.json.

For backfill, if no rationale source exists, we derive a brief one from
the existing diary mood (where present) bound to the artist's insight.
"""
import json, os, re, glob

SITE = "/Users/saberzou/.openclaw/workspace/axel-art"
STUDY_SRC = "/Users/saberzou/.openclaw/workspace-axel/memory/art-studies"
DIARY_SRC = "/Users/saberzou/.openclaw/workspace-axel/memory/diary"
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

    m = re.match(r"#\s*([^\n#—\-(]+?)(?:\s*[—\-]\s*\d{4}-\d{2}-\d{2})?(?:\s*\(.+?\))?\s*\n", text)
    if m:
        out["name"] = m.group(1).strip()

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

    intro = section("Who They Are", "Who", "Background")
    if intro:
        intro = re.sub(r"\*\*(.+?)\*\*", r"\1", intro)
        first_para = intro.split("\n\n")[0].strip()
        sents = re.split(r"(?<=[.!?])\s+", first_para)
        out["intro"] = " ".join(sents[:3]).strip()

    insight = section("Core Insight", "Core Philosophy", "The Deeper Insight",
                      "Deeper Principles", "Core Principles")
    if insight:
        mb = re.search(r"\*\*(.+?)\*\*", insight)
        if mb:
            out["insight"] = mb.group(1).strip()
        else:
            line = insight.split("\n")[0].lstrip("- *")
            out["insight"] = re.sub(r"\*\*(.+?)\*\*", r"\1", line).strip()

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


def find_diary_for_date(date_str):
    """Locate diary md. Site mirror first, then workspace-axel memory dir."""
    for d in (os.path.join(SITE, "diary"), DIARY_SRC):
        matches = sorted(glob.glob(os.path.join(d, f"{date_str}-*.md")))
        if matches:
            # Prefer dated-and-titled files over bare date.md
            for m in matches:
                if not re.search(rf"{date_str}\.md$", m):
                    return m
            return matches[0]
    return None


def extract_diary_mood(filepath):
    try:
        text = open(filepath).read()
    except Exception:
        return None
    mm = re.search(r"\*Favorite thought today:\s*(.+?)\*", text, re.IGNORECASE)
    if mm:
        return mm.group(1).strip().rstrip(".")
    # Fallback: first non-heading paragraph, trimmed to a sentence
    paras = [p.strip() for p in text.split("\n\n") if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("---")]
    if paras:
        first = re.sub(r"\*\*(.+?)\*\*", r"\1", paras[0])
        first = re.sub(r"\*(.+?)\*", r"\1", first)
        sents = re.split(r"(?<=[.!?])\s+", first)
        out = " ".join(sents[:1]).strip()
        if len(out) > 220:
            out = out[:217].rstrip() + "…"
        return out.rstrip(".")
    return None


def derive_rationale(artist, date_str):
    """For backfill: synthesize a short 'why today' line in Axel's voice."""
    # 1. Check for explicit sidecar rationale (try slug, then any same-date rationale)
    candidates = []
    if artist and artist.get("slug"):
        slug = artist["slug"]
        candidates.append(os.path.join(STUDY_SRC, f"{date_str}-{slug}-rationale.txt"))
    candidates += sorted(glob.glob(os.path.join(STUDY_SRC, f"{date_str}-*-rationale.txt")))
    for rtxt in candidates:
        if os.path.exists(rtxt):
            return open(rtxt).read().strip()

    # sidecar meta json
    if artist and artist.get("slug"):
        slug = artist["slug"]
        meta_json = os.path.join(STUDY_SRC, f"{date_str}-{slug}-inspired-meta.json")
        if os.path.exists(meta_json):
            try:
                m = json.load(open(meta_json))
                if m.get("rationale"):
                    return m["rationale"].strip()
            except Exception:
                pass

    # 2. Backfill from diary mood + insight
    diary_path = find_diary_for_date(date_str)
    mood = extract_diary_mood(diary_path) if diary_path else None
    insight = (artist or {}).get("insight")

    if mood and insight:
        return f"Today I was thinking about: {mood}. That's the thread that led me here — {insight.rstrip('.').lower()}."
    if mood:
        return f"Today I was thinking about: {mood}."
    if insight:
        return f"The thread today: {insight.rstrip('.')}."
    return None


def main():
    data = json.load(open(META_PATH))

    studies_by_date = {}
    for art in data.get("visualArt", []):
        is_study = (art.get("category") == "artist-study") or \
                   (art.get("tags") and "artist-study" in art["tags"]) or \
                   (art.get("file", "").endswith("-inspired.png"))
        if is_study:
            studies_by_date[art["date"]] = art

    all_dates = sorted(studies_by_date.keys(), reverse=True)
    journal = []

    notes_out = os.path.join(SITE, "art-studies")
    os.makedirs(notes_out, exist_ok=True)

    for date in all_dates:
        art = studies_by_date[date]
        mm = re.search(r"\d{4}-\d{2}-\d{2}-(.+?)-inspired\.png$", art["file"])
        slug = mm.group(1) if mm else None
        artist_md = None
        if slug:
            candidate = os.path.join(STUDY_SRC, f"{date}-{slug}.md")
            if os.path.exists(candidate):
                artist_md = candidate
            else:
                # Fallback: any artist md with same date prefix
                alt = [p for p in glob.glob(os.path.join(STUDY_SRC, f"{date}-*.md"))
                       if not p.endswith("-notion-summary.md")
                       and "-rationale" not in p]
                if alt:
                    artist_md = alt[0]
        artist_info = parse_artist_md(artist_md) if artist_md else {}
        if not artist_info.get("name"):
            artist_info["name"] = slug_to_name(slug) if slug else art["title"]
        artist_info["slug"] = slug

        # Mirror note into site for deep-link
        if artist_md:
            dst = os.path.join(notes_out, os.path.basename(artist_md))
            with open(artist_md) as fi, open(dst, "w") as fo:
                fo.write(fi.read())
            artist_info["noteFile"] = f"art-studies/{os.path.basename(artist_md)}"

        rationale = derive_rationale(artist_info, date)

        entry = {
            "date": date,
            "artist": {
                "name": artist_info.get("name"),
                "slug": artist_info.get("slug"),
                "intro": artist_info.get("intro"),
                "insight": artist_info.get("insight"),
                "principles": artist_info.get("principles") or [],
                "noteFile": artist_info.get("noteFile"),
            },
            "rationale": rationale,
            "artwork": {
                "file": art["file"],
                "title": art["title"],
                "description": art.get("description"),
            },
        }
        journal.append(entry)

    data["journal"] = journal
    # Drop legacy fields the site no longer renders
    data.pop("diaryEntries", None)
    data.pop("thoughts", None)

    with open(META_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with_rat = sum(1 for e in journal if e.get("rationale"))
    print(f"Built journal: {len(journal)} entries")
    print(f"  - with rationale: {with_rat}")
    print(f"  - missing rationale: {len(journal) - with_rat}")


if __name__ == "__main__":
    main()
