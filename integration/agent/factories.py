import logging
import random
import re
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Callable
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Import separated prompts
from . import prompts

logger = logging.getLogger(__name__)

# WPPConnect Client Interface
class WPPConnectClientInterface(ABC):
    @abstractmethod
    def send_message(self, phone: str, message: str) -> dict:
        pass

# Implementation using the existing WPPConnectProvider or direct requests
class WPPConnectClient(WPPConnectClientInterface):
    def __init__(self, application):
        from ..providers import WPPConnectProvider
        self.provider = WPPConnectProvider(application)
    
    def send_message(self, phone, message):
        return self.provider.send_whatsapp_message(
            phone=phone,
            is_group=False,
            is_newsletter=False,
            message=message
        )

# AI Agent Interface
class AIAgentInterface(ABC):
    @abstractmethod
    def process_message(self, message: str) -> str:
        pass

class AccountingAgent(AIAgentInterface):
    def __init__(self, llm, tools, system_prompt):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self._agent = None
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self.compiled_patterns = []
        
        # Map keywords to responses
        # (Keywords List, Response Source)
        conversational_map = [
            (prompts.GOODBYE['keywords'], prompts.GOODBYE['responses']),
            (prompts.HELP_KEYWORDS, prompts.HELP_MESSAGE),
            (prompts.THANKS['keywords'], prompts.THANKS['responses']),
            (prompts.HOW_ARE_YOU['keywords'], prompts.HOW_ARE_YOU['responses']),
            (prompts.GREETINGS['keywords'], prompts.GREETINGS['responses']),
        ]

        for keywords, response_source in conversational_map:
            # Sort by length descending to ensure longer phrases matches first
            sorted_kws = sorted(keywords, key=len, reverse=True)
            escaped_kws = [re.escape(k) for k in sorted_kws]
            
            # Pattern: matches keyword with word boundaries or start/end of string
            # (?:^|\s) ensures it starts at beginning or after whitespace
            # (?=\s|$) ensures it ends at whitespace or end of string
            pattern_str = f"(?:^|\\s)({'|'.join(escaped_kws)})(?=\\s|$)"
            try:
                regex = re.compile(pattern_str, re.IGNORECASE)
                self.compiled_patterns.append((regex, response_source))
            except re.error as e:
                logger.error(f"Failed to compile regex part: {e}")

    @property
    def agent(self):
        if self._agent is None:
            from langgraph.prebuilt import create_react_agent
            self._agent = create_react_agent(model=self.llm, tools=self.tools)
        return self._agent
    
    def _handle_conversational(self, message: str) -> Optional[str]:
        """Check message against pre-compiled conversational patterns."""
        if not message: return None
        message = message.strip()
        
        for regex, response_source in self.compiled_patterns:
            if regex.search(message):
                if isinstance(response_source, list):
                    return random.choice(response_source)
                return response_source # String (like help message)
        return None
    
    def process_message(self, message: str) -> str:
        # Check conversational first (Pre-processing)
        conv_response = self._handle_conversational(message)
        if conv_response:
            return conv_response
        
        # Process with AI (LLM)
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            logger.info(f"📨 Processing financial query: {message}")
            
            response = self.agent.invoke({
                "messages": [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=message)
                ]
            })
            
            msgs = response.get("messages", [])
            if msgs:
                result = self._extract_content(msgs[-1].content)
                if not result or result.strip() == "":
                    return "🤔 لم أفهم طلبك\n\nاكتب 'مساعدة' لمعرفة الأوامر المتاحة"
                return result
            
            return _("⚠️ لم أجد نتائج")
            
        except Exception as e:
            logger.error(f"❌ Agent Error: {e}")
            if "429" in str(e):
                return "⏳ الخدمة مشغولة حالياً\n\nحاول مرة أخرى بعد 30 ثانية"
            return _("⚠️ حدث خطأ\n\nحاول مرة أخرى أو اكتب 'مساعدة'")

    def _extract_content(self, content: Union[str, list]) -> str:
        """Safely extract text content from LangChain response."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for p in content:
                if isinstance(p, dict) and p.get('type') == 'text':
                    texts.append(p.get('text', ''))
                elif isinstance(p, str):
                    texts.append(p)
            return "\n".join(texts).strip()
        return str(content)

class AIAgentFactory:
    _instance = None
    
    @classmethod
    def create(cls):
        if cls._instance is None:
            # Import tools dynamically to avoid heavy imports at module level if unused
            from .tools import (
                get_today_sales, get_monthly_sales, get_yearly_sales,
                get_top_selling_products, get_low_stock_products, 
                get_best_customers, get_financial_summary,
                get_customer_invoices, search_item, get_categories,
                get_vendors, get_unpaid_bills, get_all_customers,
                create_customer, search_customer, get_customer_details,
                get_user_preferences, set_display_format, set_items_per_page,
                manage_purchase_order, manage_sale, finalize_sale
            )
            
            tools = [
                get_today_sales, get_monthly_sales, get_yearly_sales,
                get_top_selling_products, get_low_stock_products, 
                get_best_customers, get_financial_summary,
                get_customer_invoices, search_item, get_categories,
                get_vendors, get_unpaid_bills, get_all_customers,
                create_customer, search_customer, get_customer_details,
                get_user_preferences, set_display_format, set_items_per_page,
                manage_purchase_order, manage_sale, finalize_sale
            ]
            
            llm = cls._create_llm()
            # Pass the extracted system prompt
            cls._instance = AccountingAgent(llm, tools, prompts.SYSTEM_PROMPT)
            logger.info("✅ Accounting Agent instance created.")
        
        return cls._instance
    
    @classmethod
    def _create_llm(cls):
        from langchain_openai import ChatOpenAI
        
        # Use settings for API keys and configuration
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        base_url = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        model = getattr(settings, 'AI_MODEL_NAME', 'gpt-3.5-turbo')
        
        return ChatOpenAI(
            model=model,
            temperature=0.2,
            api_key=api_key,
            base_url=base_url,
            max_tokens=6000, # Increased for Gemini
            timeout=30,
        )
    
    @classmethod
    def reset(cls):
        cls._instance = None
