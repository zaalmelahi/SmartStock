from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from ..models import Application, Conversation, Message
from ..providers import WPPConnectProvider

from ..utils.common import clean_phone_number
import requests

@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """
    WebhookView handles incoming webhook requests from WPPConnect.
    """
    def post(self, request, webhook_key):
        application = get_object_or_404(Application, webhook_key=webhook_key)
        
        if not application.enabled:
            return Response({"status": "error", "message": "Application disabled"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        event = data.get("event")
        
        # Log the event for debugging
        logging.info(f"Webhook received for {application.name}: Event={event}")
        
        # Handle events
        if event == "onmessage":
            print(data,'data')
            phone = clean_phone_number(data.get("from"))
            is_group = data.get("isGroupMsg", False)
            message_body = data.get("body", "").strip()
            
            if phone:
                # Log the conversation and message
                try:
                    conversation, created = Conversation.objects.get_or_create(
                        application=application,
                        session_id=phone,
                        defaults={'user_identifier': phone}
                    )
                    conversation.save() # Update updated_at
                    
                    Message.objects.create(
                        conversation=conversation,
                        direction='incoming',
                        content=message_body,
                        metadata=data
                    )
                except Exception as e:
                    logging.error(f"Failed to log message: {e}")

                # Determine response
                response_text = None
                
                # 1. Flow AI Integration
                if application.flow_ai and application.flow_url:
                    response_text = self.process_flow_ai_message(application, message_body, phone, data)
                
                # 2. Accounting Agent Integration (Fallback if Flow AI not enabled or returned None? Optional)
                # Current logic implies exclusive or sequential. If Flow AI enabled, we use it.
                if not response_text and application.use_accounting_agent:
                    from ..agent.factories import AIAgentFactory
                    try:
                        agent = AIAgentFactory.create()
                        response_text = agent.process_message(message_body)
                    except Exception as e:
                        logging.error(f"Agent processing failed: {e}")
                        response_text = "⚠️ عذراً، حدث خطأ في معالجة طلبك."
                
                # 3. Default Auto-Reply
                if not response_text and not application.flow_ai and not application.use_accounting_agent:
                    response_text = "وعليكم السلام" if "سلام" in message_body.lower() else None

                if response_text:
                    provider = WPPConnectProvider(application)
                    result = provider.send_whatsapp_message(
                        phone=phone,
                        is_group=is_group,
                        is_newsletter=False,
                        message=response_text
                    )
                    logging.info(f"Response sent to {phone}. Result: {result}")
        
        return Response({"status": "success", "received": True}, status=status.HTTP_200_OK)

    def process_flow_ai_message(self, application, message_body, phone, message_data=None):
        """Send message to Flow AI and get response."""
        try:
            # Construct URL: base_url + /api/v1/prediction/ + flow_id
            print(phone,'phonephonephonephone')
            base_url = application.flow_url.rstrip('/')
            flow_id = application.flow_id
            
            if not flow_id:
                logging.error("Flow ID is missing")
                return None
                
            api_url = f"{base_url}/api/v1/prediction/{flow_id}"

            # Extract sender name
            user_name = phone
            if message_data:
                sender_data = message_data.get("sender") or {}
                user_name = (
                    sender_data.get("name") 
                    or sender_data.get("pushname") 
                    or sender_data.get("notifyName")
                    or phone
                )

            payload = {
                "question": message_body,
                "chatId": phone,
                "overrideConfig": {
                    "sessionId": phone,
                    "vars": {
                        "user_name": user_name
                    }
                }
            }
            # Add socketIOClientId for some Flowise versions
            payload["socketIOClientId"] = phone
            print(payload,'hhhhhhhhhhhhhhhhhhhhh')
            headers = {"Content-Type": "application/json"}
            if application.decrypted_flow_token:
                headers["Authorization"] = f"Bearer {application.decrypted_flow_token}"

            logging.info(f"Sending to Flow AI: {api_url}")
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict):
                # Handle standard Flowise response formats
                text = data.get("text") or data.get("message") or data.get("response")
                if isinstance(text, dict): # Sometimes it's nested
                    text = text.get("text") or str(text)
                return text
            return str(data)
            
        except requests.exceptions.HTTPError as e:
            logging.error(f"Flowise HTTP error: {e} - Status: {e.response.status_code} - Response: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Flowise request failed (Flow ID: {flow_id}): {e}")
            return None
        except Exception as e:
            logging.error(f"Flow AI processing failed: {e}")
            return None
