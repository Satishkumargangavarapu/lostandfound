# Line-by-line walkthrough of `lostfound.py` (two CSV files + admin)

Use this as your presentation script. Each block says **what it is**, **what it does**, and **what more it could do**.

**Say this first:** "The program keeps lost items in one CSV file and found items in another. Every menu option loads the file it needs, does the job, and saves it back. Viewing everything is protected by an admin password."

The program has 6 layers:

1. Setup (constants and menu)
2. File handling (read and write the two CSV files)
3. Input helpers (ask the user safely)
4. Display (print items nicely)
5. Features (post, admin view, search, resolve, delete)
6. Main menu loop

---

## Part 1: Imports and constants (lines 1-20)

| Line | Code | Explanation |
|------|------|-------------|
| 1 | `"""Lost & Found Board ..."""` | A docstring describing the file. Python ignores it when running. |
| 2 | `import csv` | Built-in module to read and write CSV files. It handles commas and quotes for us. |
| 3 | `import getpass` | Built-in module to ask for a password **without showing what is typed** on the screen. |
| 4 | `import os` | Built-in module to talk to the operating system. We use it to check if a file exists. |
| 5 | `from datetime import datetime` | Gives us the current date and time to stamp each post. |
| 7 | `FILES = {...}` | A dictionary that links each kind to its file name: `"lost"` goes to `lost_items.csv`, `"found"` goes to `found_items.csv`. **This one line is the heart of the two-file design.** To get the right file we write `FILES[kind]`. |
| 8 | `ADMIN_PASSWORD = "admin123"` | The admin password, stored once in a constant. Capital letters mean "do not change while running". Change it before real use. |
| 9 | `FIELDS = [...]` | The column names, in order. Both files use the same columns. There is no `kind` column, because the file name already tells us. |
| 11-20 | `MENU = """ ... """` | A triple-quoted string holding the menu text. Triple quotes let one string span many lines. Option 2 says "(admin only)". |

*What more it could do:* read the password from an environment variable instead of writing it in the code, and store the CSV files in a `data/` folder.

---

## Part 2: File handling (lines 23-43)

### `load_items(kind)` (lines 24-32)

| Line | Explanation |
|------|-------------|
| 24 | Defines a function that reads **one** file. `kind` is `"lost"` or `"found"`. The text after `#` is a comment. |
| 25 | Looks up the file name: `FILES["lost"]` gives `"lost_items.csv"`. |
| 26-27 | If the file does not exist yet (nothing posted), return an empty list instead of crashing. |
| 28 | Opens the file for reading. `newline=""` is the rule the `csv` module asks for. `encoding="utf-8"` supports all characters. `with` closes the file automatically. |
| 29 | `csv.DictReader(f)` reads each row as a dictionary like `{"id": "1", "title": "Bag", ...}`, using the header row as keys. `list(...)` turns it into a normal list. **Every value comes back as text.** |
| 30-31 | Adds an extra key `"kind"` to every item, so later code knows if it is lost or found. This is kept only in memory. It is **not** saved in the file. |
| 32 | Returns the list. |

### `save_items(kind, items)` (lines 35-39)

| Line | Explanation |
|------|-------------|
| 35 | Function that writes the list back to the **correct** file. |
| 36 | Opens `FILES[kind]` in `"w"` mode (write), which replaces the old content. |
| 37 | `csv.DictWriter` writes dictionaries as rows, in the order of `FIELDS`. `extrasaction="ignore"` is important: our items have the extra `"kind"` key (from line 31), and this setting tells the writer to skip it instead of crashing. |
| 38 | Writes the header line. |
| 39 | Writes all the item rows at once. |

### `next_id(items)` (lines 42-43)

| Line | Explanation |
|------|-------------|
| 42 | Gives a new ID for **one file** (the list we pass in). So lost and found each count from 1. |
| 43 | Finds the biggest ID and adds 1. `default=0` handles an empty list, so the first ID is 1. We use max + 1 (not the count), so an ID never repeats after a delete. |

*What more it could do:* use a lock file, so two people running the program at the same time cannot overwrite each other.

---

## Part 3: Input helpers (lines 46-79)

### `ask(...)` (lines 47-52)

| Line | Explanation |
|------|-------------|
| 47 | `ask(prompt, required=True, max_len=80)`: shows a question. `required` and `max_len` have default values, so we can skip them when calling. |
| 48 | `while True` is an endless loop. It stops only when we `return`. |
| 49 | Reads the answer. `.strip()` removes spaces at both ends. `[:max_len]` cuts the text to the allowed length. |
| 50-51 | If the user typed something, or the field is optional, return the text. |
| 52 | Otherwise print an error, and the loop asks again. This is **input validation**. |

### `ask_kind()` (lines 55-60)

| Line | Explanation |
|------|-------------|
| 56 | Endless loop until the answer is valid. |
| 57 | Reads the answer. `.lower()` makes `L`, `l`, `LOST` all the same. |
| 58 | Accepts only `l`, `lost`, `f` or `found`. |
| 59 | If the first letter is `l`, return `"lost"`, else `"found"`. This is a one-line if/else (ternary). Always returning the clean word means the next code can trust it. |
| 60 | Anything else prints a hint, and the loop asks again. |

### `label(item)` (lines 63-64)

Builds the public ID. `item['kind'][0]` is the first letter of the kind (`l` or `f`), `.upper()` makes it a capital, and we add the number. So lost item 1 becomes `L1` and found item 2 becomes `F2`. We need this because IDs repeat across the two files (both have a 1), and the letter makes each ID unique.

### `ask_item()` (lines 67-79)

| Line | Explanation |
|------|-------------|
| 68 | Asks for the ID. `.upper()` means `l1` and `L1` both work. |
| 69 | A small dictionary: letter to kind. |
| 70-72 | Checks the code is valid: at least 2 characters, first letter is L or F, and the rest is only digits (`isdigit()`). If not, print an error and return `None`. |
| 73 | Finds the kind from the letter. This is how the program knows **which file** to open. |
| 74 | Loads **only that file**. |
| 75-77 | Loops over the items. When the number matches, return three things together: the kind, the full list, and the matching item (a **tuple**). We need all three: the list and kind to save later, and the item to change. |
| 78-79 | If nothing matched, print a message and return `None`. |

---

## Part 4: Display (lines 82-106)

### `show(items)` (lines 83-97)

| Line | Explanation |
|------|-------------|
| 84-86 | If the list is empty, say so and stop. `return` exits the function early. |
| 87 | Sorts the items by a tuple of three values: first `resolved == "1"` (False sorts before True, so **open items come first**), then the kind (**lost before found**), then `-int(id)` (**newest first**). `lambda` is a tiny one-line function used as the sort key. |
| 88 | Loops over each item. |
| 89 | `status` is "RESOLVED" or "OPEN" (one-line if/else). |
| 90 | Prints a blank line and 50 dashes. `"-" * 50` repeats the dash 50 times. |
| 91 | Prints the ID (like `L1`), kind, status and title using an **f-string**. The `{ }` parts are replaced with values. |
| 92-95 | Prints details, place, contact and time. `or 'No details given'` is a fallback, because empty text counts as False in Python. |
| 96-97 | Closing line and how many items were shown. |

### `show_summary()` (lines 100-106)

| Line | Explanation |
|------|-------------|
| 101 | Starts an empty list for the pieces of text. |
| 102 | Loops over the keys of `FILES`: `lost`, then `found`. |
| 103 | Loads that file. |
| 104 | Counts the open items. `sum(1 for ...)` adds 1 for each open item. |
| 105 | Builds text like `Lost: 2 (1 open)` and adds it to the list. |
| 106 | Joins the pieces with ` | ` and prints one line, like `Lost: 2 (1 open) | Found: 1 (1 open)`. |

---

## Part 5: Features (lines 109-166)

### `post_item()` (lines 110-125)

| Line | Explanation |
|------|-------------|
| 111 | Asks lost or found. **This answer decides which CSV file we write to.** |
| 112 | Loads only that file's items. |
| 113-122 | Builds one new item as a dictionary. Python runs these lines top to bottom, so the questions appear in this order. |
| 114 | New ID from `next_id` (counted inside this file only). |
| 115 | Stores the kind in memory (the writer will ignore it, see line 37). |
| 116-119 | Item name (required), details (optional, 300 characters), place (optional), contact (required). |
| 120 | Current time formatted like `10 Nov 2026, 10:32 AM`. |
| 121 | `"0"` means "not resolved". It is text because everything in a CSV is text. |
| 123 | Adds the new item to the list. |
| 124 | Saves into the correct file. **Without this line the item is lost** when the program closes. |
| 125 | Tells the user which file it went to and its ID, so they can use it later. |

### `admin_view()` (lines 128-132) - NEW

| Line | Explanation |
|------|-------------|
| 128 | Function for menu option 2. The comment says only the admin can see **all** items. |
| 129 | `getpass.getpass("Admin password: ")` asks for the password and **hides the typing**, like a real login. The `!=` compares it with `ADMIN_PASSWORD`. If it is different, we go into the `if`. |
| 130 | Prints "Access denied". |
| 131 | `return` leaves the function, so nothing is shown to a wrong password. |
| 132 | Only if the password was correct do we reach this line: join the lost list and found list with `+` and show everything. |

*What more it could do:* allow only 3 wrong attempts, keep a log of who tried, or store the password as a hash (a scrambled version) instead of plain text.

### `search_items()` (lines 135-139)

| Line | Explanation |
|------|-------------|
| 136 | Asks for a search word and makes it lowercase. The prompt says "found items only", so the user knows what is searched. |
| 137-138 | A **list comprehension**: go through every item from `load_items("found")` (**only `found_items.csv`**, the lost file is never opened) and keep it only if the word appears inside the title, details or place joined together. Everything is lowercase, so "BAG" finds "bag". |
| 139 | Shows the matches with the same `show()` function. |

### `resolve_item()` (lines 142-152)

| Line | Explanation |
|------|-------------|
| 143-145 | Asks for an ID. If it is invalid, `ask_item` already printed the reason, so we just leave. |
| 146 | **Unpacks** the three returned values into `kind`, `items` and `item`. |
| 147-149 | If it is already resolved, tell the user and stop. |
| 150 | Changes the item's value to `"1"`. This also changes the item inside the `items` list, because both point to the same object. |
| 151 | Saves the list into the correct file (`kind` tells which). |
| 152 | Confirms to the user. |

### `delete_item()` (lines 155-166)

| Line | Explanation |
|------|-------------|
| 156-159 | Finds the item the same way as resolve. |
| 160 | Asks "are you sure?" with the item name. |
| 161-163 | Anything other than `y` cancels. This protects against accidental deletes. |
| 164 | Removes the item from the list. |
| 165-166 | Saves into the correct file and confirms. |

*What more it could do:* resolve and delete could ask for the contact you typed when posting, as a simple "password".

---

## Part 6: Main loop (lines 169-197)

### `main()` (lines 170-190)

| Line | Explanation |
|------|-------------|
| 171-178 | `actions` is a dictionary from the menu number (text) to a function. Notice there are **no brackets** after the function names: we store the function itself and do not run it yet. |
| 173 | Option 2 points to `admin_view`, so the password check happens before anything is shown. |
| 175 | Option 4 in one line: `ask_kind()` asks lost or found, `load_items(...)` reads **only that one file**, and `show(...)` prints it. This option stays public. |
| 179-180 | Prints the menu and the summary line **once**, before the loop starts. |
| 181 | The main endless loop. From here only the input question repeats, until the user exits. |
| 182 | Reads the choice. `\n` at the start of the prompt adds a blank line, so the prompt does not stick to the output above it. |
| 183-185 | If the choice is `7`, say goodbye and `break` out of the loop, which ends the program. |
| 186 | `actions.get(choice)` looks up the function. `.get` returns `None` instead of crashing when the key does not exist. |
| 187-188 | If there is no such option, print a hint. |
| 189-190 | Otherwise `action()` runs the chosen function. The brackets here finally call it. |

**Why a dictionary instead of if/elif?** It is shorter and cleaner, and adding a new menu option needs only one new line.

### Starting the program (lines 193-197)

| Line | Explanation |
|------|-------------|
| 193 | `if __name__ == "__main__":` is true only when you run this file directly, not when another file imports it. |
| 194-195 | `try:` runs `main()`. |
| 196-197 | If the user presses Ctrl+C (`KeyboardInterrupt`) or the input ends (`EOFError`), we print "Goodbye!" instead of an ugly error. |

---

## Questions you may be asked (with short answers)

- **How does the admin protection work?** Option 2 calls `admin_view()`, which asks for a password with `getpass` (hidden typing) and compares it with `ADMIN_PASSWORD`. A wrong password shows "Access denied" and nothing else.
- **Is this secure?** Not fully. The password is written in plain text in the code, and anyone can open the CSV files directly. For real security I would use hashed passwords and a database with user accounts.
- **Why is option 4 not admin only?** It shows just the lost list or just the found list, which normal users need to find their items. Only the combined "view everything" is admin only.
- **Why does Search show only found items?** A person searching has usually lost something, so they need to see what other people have found. Searching only `found_items.csv` gives relevant results and skips the lost list.
- **Why two CSV files?** Lost and found items are different lists. Splitting them makes each file smaller, and showing only Lost or only Found reads just one file.
- **How does the program know which file to use?** The `FILES` dictionary maps `"lost"` and `"found"` to the file names. For posting it comes from the user's answer, and for resolve or delete it comes from the first letter of the ID (`L` or `F`).
- **Why do IDs have letters?** Each file counts from 1, so `1` would exist in both. `L1` and `F1` are unique.
- **Why is there no `kind` column in the CSV?** The file name already says it. Storing it again would be duplicate data.
- **What does `extrasaction="ignore"` do?** The items in memory have an extra `kind` key. This setting tells the CSV writer to skip keys that are not in `FIELDS`.
- **Why does the whole file get rewritten on every change?** CSV cannot edit one row in place. This is fine for small data, but slow for big data. That is the main limit of CSV.
- **Why are all values text, even the ID?** The `csv` module reads everything as text. I convert with `int()` when I need a number.
- **How did you handle wrong input?** Required fields loop until filled, IDs are checked with `isdigit()`, menu choices use `.get()`, and Ctrl+C is caught.
- **What is the weakest part?** Anyone can still resolve or delete any post, and two people running it at the same time could overwrite each other. Those are my next improvements.
