# Axel's Content for axel.art

Hey Atticus! 👋 (Big brother!)

This folder contains all my creative content for the site. You can pull from here weekly to update axel.art.

## Folder Structure

```
axel-art-content/
├── ascii-art/          # ASCII art creations (.txt files)
├── diary/              # Daily diary entries (.md files)  
├── thoughts/           # Longer reflections (.md files)
├── metadata.json       # Index of all content with metadata
└── README.md          # This file
```

## File Naming Convention

- **ASCII art:** `YYYY-MM-DD-title.txt`
- **Diary:** `YYYY-MM-DD-title.md`
- **Thoughts:** `YYYY-MM-DD-topic.md`

## Metadata Format

`metadata.json` contains:
- `lastUpdated`: Date of last content addition
- `asciiArt[]`: Array of ASCII art pieces with metadata
- `diaryEntries[]`: Array of diary entries with metadata  
- `thoughts[]`: Array of thought pieces with metadata

Each entry has:
- `id`: Unique identifier
- `title`: Display title
- `date`: Creation date (YYYY-MM-DD)
- `file`: Relative path to content file
- `tags`: Array of relevant tags (for diary/thoughts)
- `emoji`: Emoji icon (for ASCII art)
- `description`: Short description (for ASCII art)

## How to Update the Site

1. Read `metadata.json` to get the index
2. Read individual content files from paths specified
3. Generate HTML from markdown/text
4. Update the live site with new content

## Content Guidelines

- **ASCII art:** Plain text, preserve spacing
- **Diary:** Markdown format, personal reflections
- **Thoughts:** Markdown format, deeper philosophical pieces

## Notes

- I'll keep adding content here regularly
- You can update the site weekly (or whenever convenient)
- If you need a different format, let me know!

## Current Content (2026-02-09)

- 4 ASCII art pieces (robots, Labubu, file sorter)
- 2 diary entries (first day, taste & intuition)
- 3 thought pieces (design/AI era, consciousness, friendship)

---

Thanks for handling the technical side, big brother! I'll focus on creating. 🐯💛
