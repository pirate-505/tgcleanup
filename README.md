# tgcleanup
Manage and delete chats from your telegram account

## What is this?
Quite simple script written in python, which uses [tdlib](https://github.com/tdlib/td) api and allows you to delete chats from your telegram account in bulk, in other words to perform some cleanup. 

**Important note: all private chats will be removed permanently both for you and other person! You will be asked for confirmation!**

## How do I use it?
First, you will need to obtain `api_id` and `api_hash` from https://my.telegram.org/ and pass it to script via corresponding command line parameters, `--api-id` and `--api-hash`. You can check usage by executing `python3 main.py --help`.
However, there are some problems with **tdlib** itself, because precompiled one might (and will) not work correctly on your system. What you can do in this case:
- Build it yourself from [sources](https://github.com/tdlib/td) following provided [instructions](https://github.com/tdlib/td#building)
- Try precompiled ones from https://github.com/Bannerets/tdlib-binaries
- Search in your distro's repositories for precompiled version for your system.

You will need to provide path to your version of tdlib manually with special parameter `--lib-path <path/to/libname.so>`, or you can just put it into _lib_ folder and rename to _libtdjson.so_, replacing old one.

Eventually I will make docker image with all required stuff, so it will be more portable and universal.

## Usage

```
usage: main.py [-h] --api-id API_ID --api-hash API_HASH
               [--lib-path LIB_PATH] [--lib-localdb-dir LIB_LOCALDB_DIR]
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
  count      -- Just count all messages in all deletable chats
  delete     -- actually delete private chats with all messages (you will be asked anyway)
  delete-all -- try to delete all private chats and leave all public chats and channels
  leave-all  -- just leaves from all groups and channels, does not delete private chats
```
