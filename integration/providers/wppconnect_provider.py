import base64
import requests
import json
import logging
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from urllib.parse import urljoin, quote
from ..interfaces import ConnectorProvider

logger = logging.getLogger(__name__)

class WPPConnectProvider(ConnectorProvider):
    """
    WPPConnectProvider handles communication with the WPPConnect API.
    It is responsible for sending messages, files, list messages, and retrieving groups.
    """
    def __init__(self, application):
        self.app = application
        # Use application configuration for URL and token
        self.base_url = self.app.url
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        self.session = self.app.session
        self.token = self.app.decrypted_token
        # Secret key for token generation - usually configured in WPPConnect server
        self.secret_key = self.app.webhook_key or getattr(settings, 'WPPCONNECT_SECRET_KEY', 'THISISMYSECURETOKEN')
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Accept-Language": "ar",
        }

    def _compose_url(self, *parts):
        """
        Utility method to safely compose URLs.
        Example usage: _compose_url(session, "start-session")
        """
        return urljoin(self.base_url, "/".join(str(part).strip("/") for part in parts))

    def _send_request(self, endpoint, data):
        """
        Helper method to send HTTP POST requests to the WPPConnect API for messaging.
        """
        url = self._compose_url(self.session, endpoint)
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send request to {endpoint}: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _check_auth(self, request):
        if not self.token:
            messages.error(request, _("No token found for this application."))
            return False
        if not self.session:
            messages.error(request, _("No session name found for this application."))
            return False
        if not self.base_url:
            messages.error(request, _("No provider URL found for this application."))
            return False
        return True

    def _compose_webhook_url(self):
        """
        Builds the full webhook URL using the application's webhook key.
        In this implementation, we use the request-based URL generation from start_session.
        """
        pass # Handled dynamically in start_session for now

    # --- Messaging Methods ---

    def send_whatsapp_message(self, phone, is_group, is_newsletter, message):
        data = {
            "phone": phone,
            "isGroup": is_group,
            "isNewsletter": is_newsletter,
            "message": message,
        }
        return self._send_request("send-message", data)
        
    def send_file(self, phone, is_group, is_newsletter, filename, caption, base64_data):
        data = {
            "phone": phone,
            "isGroup": is_group,
            "isNewsletter": is_newsletter,
            "filename": filename,
            "caption": caption,
            "base64": base64_data,
        }
        return self._send_request("send-file", data)

    def send_list_message(self, phone, is_group, description, sections, button_text):
        data = {
            "phone": phone,
            "isGroup": is_group,
            "buttonText": button_text,
            "description": description,
            "sections": sections,
        }
        return self._send_request("send-list-message", data)
    
    def send_reply(self, phone, is_group, message, id_message):
        data = {
            "phone": phone,
            "isGroup": is_group,
            "message": message,
            "messageId": id_message,
        }
        return self._send_request("send-reply", data)

    # --- Session Management Methods ---

    def generate_token(self, request):
        if not self.session:
            messages.error(request, _("No session name found for this application."))
            return False
            
        # Try different potential secrets starting with the one in settings
        secrets_to_try = []
        if hasattr(settings, 'WPPCONNECT_SECRET_KEY'):
            secrets_to_try.append(settings.WPPCONNECT_SECRET_KEY)
        if self.app.webhook_key:
            secrets_to_try.append(self.app.webhook_key)
        if 'THISISMYSECURETOKEN' not in secrets_to_try:
            secrets_to_try.append('THISISMYSECURETOKEN')

        last_error = ""
        for secret in secrets_to_try:
            url = self._compose_url(self.session, secret, "generate-token")
            try:
                response = requests.post(url, headers={"Content-Type": "application/json"}, timeout=30)
                if response.status_code in [200, 201]:
                    data = response.json()
                    new_token = data.get("token")
                    if new_token:
                        # Explicitly update configuration if it exists
                        if self.app.configuration:
                            self.app.configuration.token = new_token
                            self.app.configuration.save()
                            messages.success(request, f"Token generated and saved to Configuration: {self.app.configuration.name}")
                        else:
                            # Fallback if no configuration is linked (though models imply it's needed)
                            self.app.token = new_token
                            self.app.save()
                            messages.success(request, f"Token generated and saved to Application!")
                        return True
                    else:
                        last_error = "API returned success but no token was found."
                else:
                    last_error = f"Error {response.status_code}: {response.text}"
            except Exception as e:
                last_error = str(e)
        
        # If all secrets failed
        messages.error(request, f"Failed to generate token. Last error: {last_error}")
        return False

    def start_session(self, request):
        if not self._check_auth(request):
            return False
        
        url = self._compose_url(self.session, "start-session")
        
        # Use configured webhook base URL if provided in settings, otherwise use request host
        webhook_base = getattr(settings, 'WPPCONNECT_WEBHOOK_URL', f"{request.scheme}://{request.get_host()}")
        if not webhook_base.endswith('/'):
            webhook_base = webhook_base.rstrip('/')
            
        relative_webhook_url = reverse('webhook', kwargs={'webhook_key': self.app.webhook_key})
        webhook_url = f"{webhook_base.rstrip('/')}{relative_webhook_url}"
        
        payload = {
            "webhook": webhook_url,
            "waitQrCode": False,
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.ok:
                data = response.json()
                status = data.get("status") or data.get("message") or "Requested"
                
                if status == "CONNECTED":
                    messages.success(request, _("Session already connected!"))
                elif status == "QRCODE":
                    messages.info(request, _("Session starting. Please scan the QR code."))
                elif status == "STARTING":
                    messages.info(request, _("Session is initializing..."))
                else:
                    messages.success(request, f"Session started! Status: {status}")
                return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect start_session failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def get_qrcode(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "qrcode-session")
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.ok:
                if 'image' in response.headers.get('Content-Type', ''):
                    image_bytes = response.content
                    b64_str = base64.b64encode(image_bytes).decode("utf-8")
                    data_uri = f"data:image/png;base64,{b64_str}"
                    img_html = f"<div class='mt-2'><img src='{data_uri}' width='250' class='img-thumbnail shadow' alt='QR Code' /></div>"
                    messages.success(request, mark_safe(f"QR code fetched successfully!{img_html}"))
                    return True
                else:
                    data = response.json()
                    status = data.get("status")
                    message = data.get("message", "QR Code not ready or already connected")
                    messages.info(request, f"QR Status: {message} ({status})")
                    return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect get_qrcode failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def check_status(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "status-session")
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.ok:
                data = response.json()
                status = data.get("status") or data.get("response") or "Unknown"
                messages.info(request, f"Session Status: {status}")
                return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect check_status failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def logout_session(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "logout-session")
        try:
            response = requests.post(url, headers=self.headers, timeout=30)
            if response.ok:
                messages.success(request, "Session logged out successfully.")
                return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect logout_session failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def close_session(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "close-session")
        try:
            response = requests.post(url, headers=self.headers, timeout=30)
            if response.ok:
                messages.success(request, "Session closed successfully.")
                return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect close_session failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def check_connection_session(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "check-connection-session")
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.ok:
                payload = response.json()
                is_connected = bool(payload.get("status"))
                message = payload.get("message") or (_("Connected") if is_connected else _("Disconnected"))
                if is_connected:
                    messages.success(request, message)
                else:
                    messages.warning(request, message)
                return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect check_connection failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    # --- Data Retrieval Methods ---

    def get_phone_number(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "get-phone-number")
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.ok:
                data = response.json()
                phone = data.get("response") or data.get("phoneNumber")
                if phone:
                    if str(phone) != self.app.phone:
                        self.app.phone = str(phone)
                        self.app.save()
                        messages.success(request, f"Phone number updated: {phone}")
                    else:
                        messages.info(request, f"Phone number confirmed: {phone}")
                    return True
                else:
                    messages.warning(request, "Phone number not found in response.")
                    return False
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect get_phone_number failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def sync_contacts(self, request):
        if not self._check_auth(request):
            return False
            
        url = self._compose_url(self.session, "all-contacts")
        try:
            response = requests.get(url, headers=self.headers, timeout=60)
            if response.ok:
                data = response.json()
                contacts = data.get("response", [])
                messages.success(request, f"Contacts synced! Total found: {len(contacts)}")
                return True
            else:
                messages.error(request, f"Error {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"WPPConnect sync_contacts failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return False

    def sync_messages(self, request):
        messages.info(request, "Sync Messages action triggered. WPPConnect usually handles this via Webhooks in real-time.")
        return True

    # --- Group Management ---

    def get_groups(self):
        url = self._compose_url("all-groups")
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()
            
            if isinstance(response_data, dict) and "response" in response_data:
                groups = []
                for item in response_data["response"]:
                    if item.get("isGroup") is True:
                        group_metadata = item.get("groupMetadata", {})
                        contact = item.get("contact", {})
                        group_id = item.get("id", {}).get("_serialized", "")
                        group_name = contact.get("name") or group_metadata.get("subject", "")
                        
                        participants = []
                        for participant in group_metadata.get("participants", []):
                            participant_id = participant.get("id", {}).get("_serialized", "")
                            if participant_id:
                                phone_number = participant_id.split("@")[0] if "@" in participant_id else participant_id
                                participants.append({
                                    "phone_number": phone_number,
                                    "wid": participant_id,
                                    "isAdmin": participant.get("isAdmin", False),
                                })
                        
                        groups.append({
                            "group_name": group_name,
                            "group_id": group_id,
                            "participants": participants,
                            "size": group_metadata.get("size", len(participants))
                        })
                return {"status": "success", "groups": groups}
            else:
                return {"status": "error", "message": "Invalid response structure"}
        except Exception as e:
            logger.error(f"Failed to fetch groups: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_group_members(self, group_number: str):
        encoded_group = quote(str(group_number), safe="")
        url = self._compose_url(f"group-members/{encoded_group}")

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return {"status": "success", "members": data.get("response", [])}
            return {"status": "error", "message": data.get("message")}
        except Exception as exc:
            logger.error("Failed to fetch group members: %s", exc)
            return {"status": "error", "message": str(exc)}

    # --- Phone/LID Utilities ---

    def get_lid_from_phone_number(self, identifier: str):
        clean_identifier = identifier.strip()
        safe_identifier = quote(clean_identifier, safe="") if "@" in clean_identifier else clean_identifier
        
        url = self._compose_url("contact", "pn-lid", safe_identifier)
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            lid_id = data.get("lid", {}).get("_serialized") or data.get("lid", {}).get("id")
            phone_id = data.get("phoneNumber", {}).get("id") or data.get("phoneNumber", {}).get("_serialized")
            
            phone_number = str(phone_id).split("@")[0] if phone_id and "@" in str(phone_id) else phone_id
            name = data.get("contact", {}).get("pushname") or data.get("contact", {}).get("name")
            
            result = {}
            if lid_id: result["lid"] = lid_id
            if phone_number: result["phone_number"] = phone_number
            if name: result["name"] = name
            
            return result if result else None
        except Exception as e:
            logger.error(f"Failed to fetch contact info for {identifier}: {str(e)}")
            return None
