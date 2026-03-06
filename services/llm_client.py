from openai import OpenAI
from services.config_loader import load_model_config
from utils.event_logger import EventLogger


class LLMClient:

    def __init__(self):
        self.client = OpenAI()

        self.model_config = load_model_config()

        self.logger = EventLogger()

        self.default_model = self.model_config["default_model"]
        self.fallback_model = self.model_config["fallback_model"]


    def choose_model(self, user_input):

        complex_keywords = [
            "analyze",
            "architecture",
            "design",
            "algorithm",
            "optimize",
            "strategy",
            "explain deeply",
            "compare",
            "break down"
        ]

        text = user_input.lower()

        for word in complex_keywords:
            if word in text:
                return "gpt-4o"

        return "gpt-4o-mini"


    def call_model(self, model_name, messages):

        config = self.model_config["models"][model_name]

        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
            timeout=30
        )

        return response.choices[0].message.content


    def generate_response(self, messages, user_input="", tool_mode=False):

        if tool_mode:
            model_name = "gpt-4o-mini"
        else:
            model_name = self.choose_model(user_input)

        try:
            return self.call_model(model_name, messages)

        except Exception as e:

            self.logger.log_event("LLM_ERROR", f"{model_name} failed: {str(e)}")

            try:
                self.logger.log_event("LLM_FALLBACK", f"Retrying with {self.fallback_model}")
                return self.call_model(self.fallback_model, messages)

            except Exception as e2:

                self.logger.log_event("LLM_FATAL", str(e2))

                return "Sorry, I’m having trouble responding right now."