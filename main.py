
import tgthingy
import time
import threading
import json
import sys
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='Manage your chats in telegram', epilog='''available actions:
  count      -- Just count all messages in all deletable chats
  delete     -- actually delete private chats with all messages (you will be asked anyway)
  delete-all -- try to delete all private chats and leave all public chats and channels
  leave-all  -- just leaves from all groups and channels, does not delete private chats''')
parser.add_argument('action', metavar="ACTION", nargs=1, choices=["count", "delete", "delete-all", "leave-all"], help='Select one action to execute')
parser.add_argument('--api-id', required=True, type=int, metavar="API_ID", help='Your api_id from https://my.telegram.org')
parser.add_argument('--api-hash', required=True, metavar="API_HASH", help='Your api_hash from https://my.telegram.org')
#parser.add_argument('--filter-kwords-exclude', default=[], help='[WIP] Comma-separated list of words to preserve chats which contain any of these words in title')
parser.add_argument('--lib-path', help='Provide custom path to libtdjson.so')
parser.add_argument('--lib-localdb-dir', default='tdlib', help='Directory for local db, default: tdlib')
parser.add_argument('--lib-localdb-key', default='my_key', help='Key for accessing local db, default: my_key')

args = parser.parse_args()

api_id = args.api_id
api_hash = args.api_hash
chat_ids = []
chats = []
lib_path = args.lib_path or "lib/libtdjson.so"  # find_library('tdjson') or 'tdjson.dll'
localdb_dir = args.lib_localdb_dir
localdb_key = args.lib_localdb_key
action = args.action[0]
#filter_kwords = args.filter_kwords_exclude


def continue_check(text, variants_y=['y', 'yes'], variants_n=['n', 'no'], default="n", exact=False):
    while True:
        inp = input(text).lower() or default
        if inp in variants_y:
            return True
        elif inp in variants_n:
            return False
        elif exact:
            print("Please, type %s or %s" % (str(variants_y[0]), str(variants_n[0])))


def safe_quit():
    print("Stopping client...", end="")
    tg.close_client()
    print("done")
    print("Exitting...")
    sys.exit()


def filter_deletable(chats):
    return [elem for elem in chats if elem["can_be_deleted_for_all_users"]]


def delete_act():
    if continue_check("Delete all private chats? This cannot be undone! (yes/NO) ", variants_y=["yes"], variants_n=["no", "n"], default="no", exact=True):
        sys.stdout.flush()
        print("Deleting private deletable chats (this might take some time)...0    ", end="")
        sys.stdout.flush()
        c_count = 0
        for c in chats_deletable:
            #r = tg.delete_chat_history(c['id'], remove_from_chat=True, revoke=True)
            r = {"ok": "okay"}
            if "ok" in r:
                c_count += 1
                print("\b\b\b\b\b%5d" % c_count, end="")
                sys.stdout.flush()
        print()
        print("Done!")


def delete_all_act():
    if continue_check("Delete ALL chats and groups? This cannot be undone! (yes/NO) ", variants_y=["yes"], variants_n=["no", "n"], default="no", exact=True):
        sys.stdout.flush()
        print("Deleting all chats and groups (this might take some time)...0    ", end="")
        c_count = 0
        for c in chats:
            if c["chat_type"] == "chatTypeSupergroup" or c["chat_type"] == "chatTypeBasicGroup":
                r = tg.leave_from_chat(c["id"])
            else:
                r = tg.delete_chat_history(c['id'], remove_from_chat=True, revoke=True)
            if "ok" in r:
                c_count += 1
                print("\b\b\b\b\b%5d" % c_count, end="")
                sys.stdout.flush()
        print()
        print("Done!")


def count_act():
    print("Counting all messages (this may take some time)...")
    print("Processing chat no. 0    ", end="")
    c_count = 0
    total = 0
    sys.stdout.flush()
    for c in chats_deletable:
        m = tg.get_full_chat_histroy(c["id"])
        total += len(m)
        c_count += 1
        print("\b\b\b\b\b%5d" % c_count, end="")
        sys.stdout.flush()
    print()
    print("Total messages: %d" % total)


def leave_act():
    if continue_check("Leave from all public chats and groups? This cannot be undone! (yes/NO) ", variants_y=["yes"], variants_n=["no", "n"], default="no", exact=True):
        sys.stdout.flush()
        print("Leaving all public chats and groups (this might take some time)...0    ", end="")
        c_count = 0
        for c in chats:
            if c["chat_type"] == "chatTypeSupergroup" or c["chat_type"] == "chatTypeBasicGroup":
                r = tg.leave_from_chat(c["id"])
            r = {"ok": "okay"}
            if "ok" in r:
                c_count += 1
                print("\b\b\b\b\b%5d" % c_count, end="")
                sys.stdout.flush()
        print()
        print("Done!")


actions = {"count": count_act, "delete": delete_act, "delete-all": delete_all_act, "leave-all": leave_act}

print("Initializing tg client...", end="")

try:
    tg = tgthingy.TGthingy(api_id,
                           api_hash,
                           library_path=lib_path,
                           verbosity=1,
                           localdb_dir=localdb_dir,
                           localdb_key=localdb_key)
    tg.build_client()
except Exception as e:
    print("fail (%s)" % str(e))
else:
    print("done")


print("Checking authorization...", end="")
try:
    tg.handle_auth_routine()
except Exception as e:
    print("fail (%s)" % str(e))
    safe_quit()
if tg.auth_completed:
    print("done")
else:
    print("fail")
    safe_quit()

print("Getting all chats...", end="")
chat_ids, chats = tg.get_all_chats()
if chat_ids and chats:
    print("done")
    print("Got %d chats" % len(chats))
else:
    print("failed")
    print("No chats found!")
    safe_quit()


print("Filtering only deletable chats...", end="")
chats_deletable = filter_deletable(chats)
print("done")
print("%d private chats can be deleted" % len(chats_deletable))

if action in actions:
    actions[action]()
safe_quit()
