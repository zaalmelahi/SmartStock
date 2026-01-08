from abc import ABC, abstractmethod
from django.http import HttpRequest

class ConnectorProvider(ABC):
    @abstractmethod
    def send_whatsapp_message(self, phone, is_group, is_newsletter, message):
        pass

    @abstractmethod
    def send_file(self, phone, is_group, is_newsletter, filename, caption, base64):
       pass

    @abstractmethod
    def send_list_message(self, phone, is_group, description, sections, button_text):
       pass

    @abstractmethod
    def send_reply(self, phone, is_group, message, id_message):
        pass

    @abstractmethod
    def get_groups(self):
       pass

    @abstractmethod
    def get_group_members(self, group_number: str):
       pass

    @abstractmethod
    def generate_token(self, request: HttpRequest):
        pass

    @abstractmethod
    def start_session(self, request: HttpRequest):
        pass

    @abstractmethod
    def get_qrcode(self, request: HttpRequest):
        pass

    @abstractmethod
    def check_status(self, request: HttpRequest):
        pass

    @abstractmethod
    def check_connection_session(self, request: HttpRequest):
        pass

    @abstractmethod
    def get_phone_number(self, request: HttpRequest):
        pass

    @abstractmethod
    def logout_session(self, request: HttpRequest):
        pass
    
    @abstractmethod
    def close_session(self, request: HttpRequest):
        pass
    
    @abstractmethod
    def get_lid_from_phone_number(self, identifier: str):
        pass
