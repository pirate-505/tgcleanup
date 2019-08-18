# tgcleanup
Manage and delete chats from your telegram account

**Docker image available now!** [See below](#docker-image-with-prebuilt-tdlib)

## What is this?
Quite simple script written in python, which uses [tdlib](https://github.com/tdlib/td) api and allows you to delete chats from your telegram account in bulk, in other words to perform some cleanup. 

**Important note: all private chats will be removed permanently both for you and other person! You will be asked for confirmation!**

## Requirements

- Python 3.6+
- Your `api_id` and `api_hash` from https://my.telegram.org/
- Compiled _libtdjson_ ([dependencies for building](https://github.com/tdlib/td#dependencies), details below)

## Docker image with prebuilt tdlib

Try `docker run -it --rm pirate505/tgcleanup --api-id API_ID --api-hash API_HASH ...`

Or `docker run -it --rm -v /mnt/tdlib:/app/tgcleanup/tdlib pirate505/tgcleanup` if you want to perform multiple actions without re-entering phone and code each time (preserves local db between launches).

## How to make it work?
First of all, you will need to obtain `api_id` and `api_hash` from https://my.telegram.org/ and pass it to script via corresponding command line parameters, `--api-id` and `--api-hash`. 

However, there may be some problems with **tdlib** itself, because precompiled one might (and will) not work correctly on your system, failing login process. Thats what you can do in this case:
- Build it yourself from [sources](https://github.com/tdlib/td) following provided [instructions](https://github.com/tdlib/td#building)
- Try precompiled ones from https://github.com/Bannerets/tdlib-binaries
- Search in your distro's repositories for precompiled version for your system.
- Or just try docker image with prebuilt library.

You will have to provide path to your version of libtdjson manually with special parameter `--lib-path path/to/libtdjson.so`. Or just put it into _lib_ folder and rename to _libtdjson.so_, replacing old one.

## Windows?

The script will work absolutely the same way with one difference only -- you will need to provide path to libtdjson manually via `--lib-path path/to/libtdjson.dll`. [Precompiled versions](https://github.com/Bannerets/tdlib-binaries#windows-x86_64) of **tdlib** should work fine, but you can [build it yourself](https://github.com/tdlib/td#windows) as well.

## Usage

If you followed the instructions and did everything correctly, try `python main.py --api-id <API_ID> --api-hash <API_HASH> login` to login to your telegram account and count all chats. Don't worry, not a single chat will be deleted without explicit command and your confirmation.

You can check out the output of `--help` below to see other available actions and flags.

```
usage: main.py [-h] --api-id API_ID --api-hash API_HASH [--lib-path LIB_PATH]
               [--lib-localdb-dir LIB_LOCALDB_DIR]
               [--lib-localdb-key LIB_LOCALDB_KEY]
               ACTION

Manage your chats in telegram

positional arguments:
  ACTION                Select one action to execute

optional arguments:
  -h, --help            show this help message and exit
  --api-id API_ID       Your api_id from https://my.telegram.org
  --api-hash API_HASH   Your api_hash from https://my.telegram.org
  --lib-path LIB_PATH   Provide custom path to libtdjson.so
  --lib-localdb-dir LIB_LOCALDB_DIR
                        Directory for local db, default: tdlib
  --lib-localdb-key LIB_LOCALDB_KEY
                        Key for accessing local db, default: my_key

available actions:
  login      -- just login and obtain quantity of chats
  count      -- Just count all messages in all deletable chats
  delete     -- actually delete private chats with all messages (you will be asked anyway)
  delete-all -- try to delete all private chats and leave all public chats and channels
  leave-all  -- just leaves from all groups and channels, does not delete private chats
  logout     -- log out from client and remove all local data

```
