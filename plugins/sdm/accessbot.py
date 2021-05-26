import os
import re
import time
from itertools import chain
from errbot import BotPlugin, re_botcmd

import config_template
from lib import ApproveHelper, create_sdm_service, GrantHelper, \
    PollerHelper, ShowResourcesHelper

ACCESS_REGEX = r"^\*{0,2}access to (.+)$"
APPROVE_REGEX = r"^\*{0,2}yes (.+)$"
SHOW_RESOURCES_REGEX = r"^\*{0,2}show available resources\*{0,2}$"
FIVE_SECONDS = 5

# pylint: disable=too-many-ancestors
class AccessBot(BotPlugin):
    __grant_requests = {}

    def activate(self):
        super().activate()
        # TODO Change name to stale_grant_requests_cleaner
        self.start_poller(FIVE_SECONDS, self.get_poller_helper().stale_grant_requests_cleaner)

    def get_configuration_template(self):
        return config_template.get()

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(config_template.get().items(), configuration.items()))
        else:
            config = config_template.get()
        super(AccessBot, self).configure(config)

    def check_configuration(self, configuration):
        pass

    @re_botcmd(pattern=ACCESS_REGEX, flags=re.IGNORECASE, prefixed=False, re_cmd_name_help="access to resource-name | access to role role-name")
    def access(self, message, match):
        """
        Grant access to a resource or resources in a role (using the requester's email address)
        """
        access_input = re.sub(ACCESS_REGEX, "\\1", match.string.replace("*", ""))
        role_name = re.sub("role (.*)", "\\1", access_input)
        if role_name != access_input:
            yield from self.get_grant_helper().assign_role(message, role_name)
            return
        yield from self.get_grant_helper().access_resource(message, access_input)

    @re_botcmd(pattern=APPROVE_REGEX, flags=re.IGNORECASE, prefixed=False, hidden=True)
    def approve(self, _, match):
        """
        Approve a grant (resource or role)
        """
        access_request_id = re.sub(APPROVE_REGEX, r"\1", match.string.replace("*", ""))
        yield from self.get_approve_helper().execute(access_request_id)

    #pylint: disable=unused-argument
    @re_botcmd(pattern=SHOW_RESOURCES_REGEX, flags=re.IGNORECASE, prefixed=False, re_cmd_name_help="show available resources")
    def show_resources(self, message, match):
        """
        Show all available resources
        """
        yield from self.get_show_resources_helper().execute()

    @staticmethod
    def get_admins():
        return os.getenv("SDM_ADMINS", "").split(" ")
 
    @staticmethod
    def get_api_access_key():
        return os.getenv("SDM_API_ACCESS_KEY")

    @staticmethod
    def get_api_secret_key():
        return os.getenv("SDM_API_SECRET_KEY")

    def get_sdm_service(self):
        return create_sdm_service(self.get_api_access_key(), self.get_api_secret_key(), self.log)

    def get_grant_helper(self):
        return GrantHelper(self)

    def get_approve_helper(self):
        return ApproveHelper(self)

    def get_poller_helper(self):
        return PollerHelper(self)

    def get_show_resources_helper(self):
        return ShowResourcesHelper(self)

    def get_admin_ids(self):
        return [self.build_identifier(admin) for admin in self.get_admins()]

    def is_valid_grant_request_id(self, request_id):
        return request_id in self.__grant_requests

    def enter_grant_request(self, request_id, message, sdm_object, sdm_account, grant_request_type):
        self.__grant_requests[request_id] = {
            'id': request_id,
            'status': 'PENDING', # TODO Remove?
            'timestamp': time.time(),
            'message': message, # cannot be persisted in errbot state
            'sdm_object': sdm_object,
            'sdm_account': sdm_account,
            'type': grant_request_type
        }

    def remove_grant_request(self, request_id):
        self.__grant_requests.pop(request_id, None)

    def get_grant_request(self, request_id):
        return self.__grant_requests[request_id]

    def get_grant_request_ids(self):
        return list(self.__grant_requests.keys())

    def add_thumbsup_reaction(self, message):
        if self._bot.mode == "slack":
            self._bot.add_reaction(message, "thumbsup")

    def get_sender_nick(self, message):
        override = self.config['SENDER_NICK_OVERRIDE']
        return override if override else str(message.frm.nick)

    def get_sender_email(self, message):
        override = self.config['SENDER_EMAIL_OVERRIDE']
        return override if override else str(message.frm.email)
