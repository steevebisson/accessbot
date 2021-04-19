import os

class Properties:
    def __init__(
        self, 
        admins,
        admin_timeout,
        api_access_key, 
        api_secret_key,
        sender_nick_override,
        sender_email_override,
        auto_approve_all,
        auto_approve_tag,
        hide_resource_tag
    ):
        self.__admins = admins.split(" ")
        self.__admin_timeout = int(admin_timeout)
        self.__api_access_key = api_access_key
        self.__api_secret_key = api_secret_key
        self.__sender_nick_override = sender_nick_override
        self.__sender_email_override = sender_email_override
        self.__auto_approve_all = str(auto_approve_all).lower() == 'true'
        self.__auto_approve_tag = auto_approve_tag
        self.__hide_resource_tag = hide_resource_tag

    def admins(self):
        return self.__admins

    def admin_timeout(self):
        return self.__admin_timeout

    def api_access_key(self):
        return self.__api_access_key

    def api_secret_key(self):
        return self.__api_secret_key

    def sender_nick_override(self):
        return self.__sender_nick_override

    def sender_email_override(self):
        return self.__sender_email_override

    def auto_approve_all(self):
        return self.__auto_approve_all

    def auto_approve_tag(self):
        return self.__auto_approve_tag

    def hide_resource_tag(self):
        return self.__hide_resource_tag


_INSTANCE = Properties(
    os.getenv("SDM_ADMINS", ""),
    os.getenv("SDM_ADMIN_TIMEOUT", "30"),
    os.getenv("SDM_API_ACCESS_KEY"),
    os.getenv("SDM_API_SECRET_KEY"),
    os.getenv("SDM_SENDER_NICK_OVERRIDE"),
    os.getenv("SDM_SENDER_EMAIL_OVERRIDE"),
    os.getenv("SDM_AUTO_APPROVE_ALL"),
    os.getenv("SDM_AUTO_APPROVE_TAG"),
    os.getenv("SDM_HIDE_RESOURCE_TAG")
) 
def get():
    return _INSTANCE
