from ctypes import *
import json
import sys
import time


class TGthingy:
    def __init__(self, api_id, api_hash, library_path, verbosity=1, localdb_dir="tdlib", localdb_key="my_key"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.verbosity = verbosity
        if library_path:
            self.library_path = library_path
            self._init_lib(self.library_path)
            self.client = None
        else:
            raise ValueError("No library path provided")
        if localdb_dir:
            self.localdb_dir = localdb_dir
        else:
            raise ValueError("Provide correct database directory name!")
        if localdb_key:
            self.localdb_key = localdb_key
        else:
            raise ValueError("Provide some key for local db!")

        self.auth_completed = False

    def _init_lib(self, library_path):
        self.tdjson = CDLL(library_path)
        self._td_json_client_create = self.tdjson.td_json_client_create
        self._td_json_client_create.restype = c_void_p
        self._td_json_client_create.argtypes = []

        self._td_json_client_receive = self.tdjson.td_json_client_receive
        self._td_json_client_receive.restype = c_char_p
        self._td_json_client_receive.argtypes = [c_void_p, c_double]

        self._td_json_client_send = self.tdjson.td_json_client_send
        self._td_json_client_send.restype = None
        self._td_json_client_send.argtypes = [c_void_p, c_char_p]

        self._td_json_client_execute = self.tdjson.td_json_client_execute
        self._td_json_client_execute.restype = c_char_p
        self._td_json_client_execute.argtypes = [c_void_p, c_char_p]

        self._td_json_client_destroy = self.tdjson.td_json_client_destroy
        self._td_json_client_destroy.restype = None
        self._td_json_client_destroy.argtypes = [c_void_p]

        self._td_set_log_verbosity_level = self.tdjson.td_set_log_verbosity_level
        self._td_set_log_verbosity_level.restype = None
        self._td_set_log_verbosity_level.argtypes = [c_int]

        self._td_set_log_verbosity_level(self.verbosity)

        fatal_error_callback_type = CFUNCTYPE(None, c_char_p)

        def on_fatal_error_callback(error_message):
            print("TDLib fatal error: ", error_message)

        self._td_set_log_fatal_error_callback = self.tdjson.td_set_log_fatal_error_callback
        self._td_set_log_fatal_error_callback.restype = None
        self._td_set_log_fatal_error_callback.argtypes = [
            fatal_error_callback_type]
        c_on_fatal_error_callback = fatal_error_callback_type(
            on_fatal_error_callback)
        self._td_set_log_fatal_error_callback(c_on_fatal_error_callback)

    def build_client(self):
        self.client = self._td_json_client_create()

    def td_execute(self, query):
        query = json.dumps(query).encode("utf-8")
        result = self._td_json_client_execute(None, query)
        if result:
            result = json.loads(result.decode("utf-8"))
        return result

    def td_send(self, query, extra=None):
        if not self.client:
            print("Please, call build_client() first!")
            return
        query = json.dumps(query).encode("utf-8")
        self._td_json_client_send(self.client, query)

    def td_receive(self):
        if not self.client:
            print("Please, call build_client() first!")
            return
        result = self._td_json_client_receive(self.client, 1.0)
        if result:
            result = json.loads(result.decode("utf-8"))
        return result

    def _get_stamp(self):
        return str(time.time())

    def get_answer(self, query):
        if "@extra" not in query:
            extra = self._get_stamp()
            query.update((("@extra", extra),))
        else:
            extra = query["@extra"]
        self.td_send(query)
        while True:
            event = self.td_receive()
            if event:
                if ("@extra" in event) and (event["@extra"] == extra):
                    return event

    def close_client(self):
        self._td_json_client_destroy(self.client)

    def log_out(self):
        ans = self.get_answer({"@type": "logOut"})
        return ans

    def _get_chats(self, offset_order, offset_id=0, limit=100):
        ans = self.get_answer({"@type": "getChats",
                               "offset_order": offset_order,
                               "offset_chat_id": offset_id,
                               "limit": limit})
        return ans["chat_ids"]

    def get_all_chats(self):
        ids = []
        infos = []
        offset_order = 2**63 - 1
        offset_id = 0
        while True:
            recv_ids = self._get_chats(offset_order, offset_id)
            if len(recv_ids) < 1:
                break
            for cid in recv_ids:
                if not cid in ids:
                    ids.append(cid)
                    infos.append(self.get_short_chat_info(cid))
            offset_order = infos[-1]["order"]
            offset_id = ids[-1]
        return ids, infos

    def _get_chat_info(self, chat_id):
        ans = self.get_answer({"@type": "getChat", "chat_id": chat_id})
        return ans

    def get_short_chat_info(self, chat_id):
        info = self._get_chat_info(chat_id)
        res = {"id": info["id"], "chat_type": info["type"]["@type"], "title": info["title"], "can_be_deleted_for_all_users": info["can_be_deleted_for_all_users"], "order": info["order"], "last_message_id": -1}
        if "last_message" in info:
            res["last_message_id"] = info["last_message"]["id"]
        return res

    def delete_messages(self, chat_id, message_ids, revoke=False):
        ans = self.get_answer({"@type": "deleteMessages", "chat_id": chat_id,
                               "message_ids": message_ids, "revoke": revoke})
        return ans

    def delete_chat_history(self, chat_id, remove_from_chat=False, revoke=False):
        ans = self.get_answer({"@type": "deleteChatHistory",
                               "chat_id": chat_id,
                               "remove_from_chat_list": remove_from_chat,
                               "revoke": revoke})
        return ans

    def leave_from_chat(self, chat_id):
        ans = self.get_answer({"@type": "leaveChat",
                               "chat_id": chat_id})
        return ans

    def get_full_chat_histroy(self, chat_id):
        message_ids = []
        from_message_id = 0

        while True:
            recv = self._get_chat_messages(chat_id, from_message_id=from_message_id)
            recv_msgs = recv["messages"]
            if recv["total_count"] < 1:
                break
            for msg in recv_msgs:
                if msg["id"] not in message_ids:
                    message_ids.append(msg["id"])
            from_message_id = message_ids[-1]
        return message_ids

    def _get_chat_messages(self, chat_id, from_message_id=0, offset=0, limit=99, only_local=False):
        ans = self.get_answer({"@type": "getChatHistory",
                               "chat_id": chat_id,
                               "from_message_id": from_message_id,
                               "offset": offset,
                               "limit": limit,
                               "only_local": only_local})
        return ans

    def handle_auth_routine(self):
        # horrible, isnt it?
        stamp = self._get_stamp()
        self.td_send({"@type": "getAuthorizationState", "@extra": stamp})
        while True:
            event = self.td_receive()
            if not event:
                continue
            if event["@type"] == "updateAuthorizationState":
                auth_state = event["authorization_state"]

                # if client is closed, we need to destroy it and create new client
                if auth_state["@type"] == "authorizationStateClosed":
                    #print("Authorization routine fail!")
                    return False

                # set tdlib parameters
                # you MUST obtain your own api_id and api_hash at https://my.telegram.org
                # and use them in the setTdlibParameters call
                if auth_state["@type"] == "authorizationStateWaitTdlibParameters":
                    self.td_send({"@type": "setTdlibParameters",
                                  "parameters": {"database_directory": self.localdb_dir,
                                                 "use_message_database": True,
                                                 "use_file_database": False,
                                                 "use_secret_chats": True,
                                                 "api_id": self.api_id,
                                                 "api_hash": self.api_hash,
                                                 "system_language_code": "en",
                                                 "device_model": "Desktop",
                                                 "system_version": "Linux",
                                                 "application_version": "0.1",
                                                 "enable_storage_optimizer": True}})

                # set an encryption key for database to let know tdlib how to open the database
                if auth_state["@type"] == "authorizationStateWaitEncryptionKey":
                    self.td_send(
                        {"@type": "checkDatabaseEncryptionKey", "key": self.localdb_key})

                # insert phone number for login
                if auth_state["@type"] == "authorizationStateWaitPhoneNumber":
                    sys.stdout.flush()
                    phone_number = input("Please insert your phone number: ")
                    self.td_send(
                        {"@type": "setAuthenticationPhoneNumber", "phone_number": phone_number})

                # wait for authorization code
                if auth_state["@type"] == "authorizationStateWaitCode":
                    sys.stdout.flush()
                    code = input(
                        "Please insert the authentication code you received: ")
                    self.td_send(
                        {"@type": "checkAuthenticationCode", "code": code})

                # wait for password if present
                if auth_state["@type"] == "authorizationStateWaitPassword":
                    sys.stdout.flush()
                    password = input("Please insert your password: ")
                    self.td_send(
                        {"@type": "checkAuthenticationPassword", "password": password})

                if auth_state["@type"] == "authorizationStateReady":
                    self.auth_completed = True
                    return True

            #print(event)
            sys.stdout.flush()


if __name__ == "__main__":
    print("Wrong file dude")
