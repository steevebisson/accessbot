import json
import time
from collections import namedtuple
import os
from strongdm.models import User

from grant_request_type import GrantRequestType
from lib.models.base_resource import BaseResource

class GrantRequestHelper:
    __grant_requests = {}
    # INFO: we might want to make it configurable
    folder_path = "./data/grant_requests"
    file_path = f"{folder_path}/state.json"

    def __init__(self, bot):
        self._bot = bot
        self.__restore_state()

    def save_state(self):
        if not self.__can_perform_state_handling():
            return
        try:
            if not os.path.exists(self.folder_path):
                os.mkdir(self.folder_path)
            with open(self.file_path, "w") as state:
                grant_requests_list = [
                    self.__serialize_grant_request(grant_request)
                    for grant_request in self.__grant_requests.values()
                ]
                state.write(json.dumps(grant_requests_list))
        except Exception as e:
            self._bot.log.error("An error occurred while saving the grant requests state: ", str(e))

    def __serialize_grant_request(self, grant_request):
        msg_to = grant_request['message'].to
        return {
            'id': grant_request['id'],
            'timestamp': grant_request['timestamp'],
            'message': {
                'frm': grant_request['message'].frm.__str__(),
                'to': {
                    'identifier': msg_to.__str__(),
                    'channelid': msg_to.channelid if hasattr(msg_to, 'channelid') else None
                },
                'extras': grant_request['message'].extras,
                'is_group': grant_request['message'].is_group,
            },
            'sdm_object': self.__sdm_model_to_dict(grant_request['sdm_object']),
            'sdm_account': self.__sdm_model_to_dict(grant_request['sdm_account']),
            'type': grant_request['type'],
            'flags': grant_request['flags'],
        }

    def __restore_state(self):
        self.__grant_requests = {}
        if not self.__can_perform_state_handling():
            return
        if not os.path.isfile(self.file_path):
            return
        try:
            state_text = open(self.file_path, "r").read()
            if state_text == "":
                return
            grant_requests_list = json.loads(state_text)
            for grant_request in grant_requests_list:
                self.__grant_requests[grant_request['id']] = self.__deserialize_grant_request(grant_request)
        except Exception as e:
            self._bot.log.error("An error occurred while restoring the grant requests state: ", str(e))

    def __deserialize_grant_request(self, source_grant_request):
        grant_request = dict(source_grant_request)
        grant_request['message'] = self.__build_grant_request_message(grant_request)
        grant_request['sdm_account'] = User.from_dict(grant_request['sdm_account'])
        grant_request['sdm_object'] = BaseResource(grant_request['sdm_object'])
        return grant_request

    def __build_grant_request_message(self, grant_request):
        message_dict = {
            'frm': self._bot.build_identifier(grant_request['message']['frm']),
            'to': self._bot.build_identifier(grant_request['message']['to']['identifier']),
            'extras': grant_request['message'].get('extras'),
            'is_group': grant_request['message'].get('is_group'),
        }
        message_dict['to']._channelid = grant_request['message']['to'].get('channelid')
        return namedtuple('message', message_dict.keys())(*message_dict.values())

    def __can_perform_state_handling(self):
        return self._bot.mode != 'test' and self._bot.config["ENABLE_BOT_STATE_HANDLING"]

    def add(self, request_id: str, message, sdm_object, sdm_account, grant_request_type: GrantRequestType, flags: dict = None):
        self.__grant_requests[request_id] = {
            'id': request_id,
            'timestamp': time.time(),
            'message': message,
            'sdm_object': sdm_object,
            'sdm_account': sdm_account,
            'type': grant_request_type.value,
            'flags': flags,
        }
        self.save_state()

    def get(self, request_id: str):
        return self.__grant_requests.get(request_id)

    def get_request_ids(self):
        return list(self.__grant_requests.keys())

    def exists(self, request_id: str) -> bool:
        return self.__grant_requests.get(request_id) is not None

    def remove(self, request_id: str):
        self.__grant_requests.pop(request_id, None)
        self.save_state()

    def check_request_already_exists(self, sdm_object_name: str, grant_request_type: GrantRequestType, user: str):
        for grant_request in self.__grant_requests.values():
            if grant_request["type"] == grant_request_type.value and grant_request["message"].frm.person == user \
                    and grant_request["sdm_object"].name.lower() == sdm_object_name.lower():
                obj_type_name = "resource" if grant_request_type == GrantRequestType.ACCESS_RESOURCE else "role"
                raise Exception(
                    f"You already have a pending grant request for that {obj_type_name}. Please, wait for an admin evaluation.")

    def __sdm_model_to_dict(self, object):
        return object if type(object) is dict else object.to_dict()

    def clear_cached_state(self):
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
        except Exception as e:
            self._bot.log.error("An error occurred while clearing the cached state: ", str(e))
