"""Lost & Found Board - lost items go to lost_items.csv, found items to found_items.csv."""
import csv
import getpass
import os
from datetime import datetime

FILES = {"lost": "lost_items.csv", "found": "found_items.csv"}
ADMIN_PASSWORD = "admin123"  # change this before using the app for real
FIELDS = ["id", "title", "description", "location", "contact", "created", "resolved"]

MENU = """
===== LOST & FOUND BOARD =====
1. Post an item
2. View all items (admin only)
3. Search FOUND items
4. Show only LOST or FOUND
5. Mark an item as resolved
6. Delete an item
7. Exit
"""


# ---------- File handling (two CSV files) ----------
def load_items(kind):  # read ONE csv file ('lost' or 'found') into a list of dictionaries
    path = FILES[kind]
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    for item in items:
        item["kind"] = kind  # remember which file it came from (this is not saved)
    return items


def save_items(kind, items):  # write the list back into the correct csv file
    with open(FILES[kind], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)


def next_id(items):  # biggest id in THIS file + 1 (1 for an empty file)
    return max((int(i["id"]) for i in items), default=0) + 1


# ---------- Input helpers ----------
def ask(prompt, required=True, max_len=80):  # keep asking until the text is valid
    while True:
        text = input(prompt).strip()[:max_len]
        if text or not required:
            return text
        print("  ! This field is required.")


def ask_kind():  # returns 'lost' or 'found'
    while True:
        choice = input("Did you (L)ose or (F)ind an item? ").strip().lower()
        if choice in ("l", "lost", "f", "found"):
            return "lost" if choice[0] == "l" else "found"
        print("  ! Please type L or F.")


def label(item):  # public id: L1, L2 for lost items and F1, F2 for found items
    return f"{item['kind'][0].upper()}{item['id']}"


def ask_item():  # ask for an id like L1 or F2; returns (kind, items, item) or None
    code = input("Enter item ID (like L1 or F2): ").strip().upper()
    kinds = {"L": "lost", "F": "found"}
    if len(code) < 2 or code[0] not in kinds or not code[1:].isdigit():
        print("  ! Use a letter and a number, like L1 or F2.")
        return None
    kind = kinds[code[0]]
    items = load_items(kind)  # open only the file this id belongs to
    for item in items:
        if int(item["id"]) == int(code[1:]):
            return kind, items, item
    print(f"  ! No item with ID {code}.")
    return None


# ---------- Display ----------
def show(items):  # open items first, then lost before found, newest first
    if not items:
        print("\n  Nothing to show.")
        return
    items = sorted(items, key=lambda i: (i["resolved"] == "1", i["kind"], -int(i["id"])))
    for it in items:
        status = "RESOLVED" if it["resolved"] == "1" else "OPEN"
        print("\n" + "-" * 50)
        print(f"#{label(it)}  [{it['kind'].upper()}]  [{status}]  {it['title']}")
        print(f"   Details : {it['description'] or 'No details given'}")
        print(f"   Place   : {it['location'] or 'unknown'}")
        print(f"   Contact : {it['contact']}")
        print(f"   Posted  : {it['created']}")
    print("-" * 50)
    print(f"  {len(items)} item(s) shown.")


def show_summary():  # one line above the menu: totals for each of the two files
    parts = []
    for kind in FILES:
        items = load_items(kind)
        open_count = sum(1 for i in items if i["resolved"] == "0")
        parts.append(f"{kind.capitalize()}: {len(items)} ({open_count} open)")
    print(" | ".join(parts))


# ---------- Features ----------
def post_item():
    kind = ask_kind()  # this choice decides which csv file we write to
    items = load_items(kind)
    item = {
        "id": next_id(items),
        "kind": kind,
        "title": ask("Item name: "),
        "description": ask("Details - colour, brand, marks (optional): ", False, 300),
        "location": ask("Where was it lost/found? (optional): ", False),
        "contact": ask("Your phone / email: "),
        "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "resolved": "0",
    }
    items.append(item)
    save_items(kind, items)
    print(f"\n  Posted in {FILES[kind]}! Your item ID is {label(item)}.")


def admin_view():  # option 2: only the admin can see ALL items (lost + found)
    if getpass.getpass("Admin password: ") != ADMIN_PASSWORD:  # typing is hidden
        print("  ! Access denied. Only the admin can view all items.")
        return
    show(load_items("lost") + load_items("found"))


def search_items():
    word = ask("Search word (found items only): ").lower()
    matches = [i for i in load_items("found")  # only the found_items.csv file
               if word in f"{i['title']} {i['description']} {i['location']}".lower()]
    show(matches)


def resolve_item():
    found = ask_item()
    if found is None:
        return
    kind, items, item = found
    if item["resolved"] == "1":
        print("  This item is already resolved.")
        return
    item["resolved"] = "1"
    save_items(kind, items)
    print(f"  '{item['title']}' marked as resolved.")


def delete_item():
    found = ask_item()
    if found is None:
        return
    kind, items, item = found
    sure = input(f"Delete '{item['title']}'? (y/n): ").strip().lower()
    if sure != "y":
        print("  Cancelled.")
        return
    items.remove(item)
    save_items(kind, items)
    print("  Deleted.")


# ---------- Main loop ----------
def main():
    actions = {
        "1": post_item,
        "2": admin_view,
        "3": search_items,
        "4": lambda: show(load_items(ask_kind())),
        "5": resolve_item,
        "6": delete_item,
    }
    print(MENU)  # the menu is printed only ONCE, before the loop starts
    show_summary()
    while True:
        choice = input("\nChoose 1-7: ").strip()
        if choice == "7":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("  ! Please choose a number from 1 to 7.")
        else:
            action()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
