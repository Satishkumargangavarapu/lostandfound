# Lost & Found Board (Terminal + 2 CSV files)

A pure Python terminal app where people post **lost** and **found** items, search them, and mark them as resolved when the item is returned.

- **Only Python** (no Flask, no pip install, nothing extra)
- **Two CSV files:** all LOST items go to `lost_items.csv`, all FOUND items go to `found_items.csv`
- **Runs only in the terminal**
- One file: `lostfound.py` (197 lines)

## How to run

Python 3.8 or newer is needed.

```bash
python lostfound.py
```

On some systems use `python3 lostfound.py`. Each CSV file is created automatically when you post the first item of that kind.

## Menu

```
===== LOST & FOUND BOARD =====
1. Post an item
2. View all items (admin only)
3. Search FOUND items
4. Show only LOST or FOUND
5. Mark an item as resolved
6. Delete an item
7. Exit

Lost: 2 (1 open) | Found: 1 (1 open)
Choose 1-7:
```

The menu is shown **only once**, when the program starts. After that, only the `Choose 1-7:` question repeats until you choose 7 (Exit).

## Features

- Post an item. Your Lost/Found answer decides which CSV file it is saved in
- View all items (lost and found together, open ones first). **Admin only:** it asks for the admin password (typing is hidden)
- Search by name, details or place, in **found items only** (reads only `found_items.csv`), so someone who lost something sees what has been found
- Show only Lost items (reads only `lost_items.csv`) or only Found items (reads only `found_items.csv`)
- Mark an item as resolved
- Delete an item (asks for confirmation)
- Count of items in each file, shown with the menu at the start
- Input checks: required fields, length limits, valid ID and menu choice
- Safe exit with Ctrl+C

## Admin access

Option 2 (View all items) is protected. The program asks `Admin password:` and the typing is hidden. A wrong password shows `Access denied` and nothing else.

- Default password: `admin123`
- To change it, edit `ADMIN_PASSWORD` on line 8 of `lostfound.py`
- Options 3 (search found items) and 4 (show only Lost or only Found) stay open to everyone

## Item IDs

Each file has its own numbering, so the program shows the ID with a letter:

| ID    | Meaning                          |
|-------|----------------------------------|
| `L1`  | First item in `lost_items.csv`   |
| `L2`  | Second item in `lost_items.csv`  |
| `F1`  | First item in `found_items.csv`  |

When you resolve or delete, type the ID like `L1` or `F2` (small letters work too). The letter tells the program which file to open.

## The two CSV files

Both files have the same columns. The first row is the header.

```
id,title,description,location,contact,created,resolved
1,Blue bottle,"Steel, dent",Library,99999,"10 Nov 2026, 10:32 AM",1
```

| Column      | Meaning                               |
|-------------|---------------------------------------|
| id          | Number, starts at 1 inside each file  |
| title       | Item name                             |
| description | Extra details (optional)              |
| location    | Where it was lost/found (optional)    |
| contact     | Phone or email                        |
| created     | Date and time of posting              |
| resolved    | `0` = open, `1` = returned to owner   |

There is no `kind` column, because the file name already says if the item is lost or found.

Text containing commas (like `"Steel, dent"`) is wrapped in quotes automatically by Python's `csv` module, so the columns never break.

## Project files

```
lostfound_cli/
├── lostfound.py       # the whole program
├── lost_items.csv     # created automatically: all lost items
├── found_items.csv    # created automatically: all found items
├── README.md          # this file
└── WALKTHROUGH.md     # line-by-line explanation for presenting
```

The old `lostfound.csv` from the previous version is not used any more.

## Future ideas

- Auto-match: when a lost item is posted, show found items with similar words
- Store the admin password as a hash, not plain text
- Password for deleting, so only the poster can remove a post
- Edit an existing post
- Export a report of all unresolved items
- Upgrade CSV to a database, and the terminal to a web page
