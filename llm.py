import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler

load_dotenv()

class LLM:
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.llm = self._init_llm()
        self._init_langfuse()
        self.langfuse_handler = CallbackHandler()

    def _init_llm(self):
        print(f"[DEBUG] Initialisation du LLM {self.provider} avec modèle {self.model}")
        if self.provider == "mistral":
            self.api_key = os.getenv("MISTRAL_API_KEY")
            return ChatMistralAI(model=self.model, api_key=self.api_key, temperature=0, max_retries=5)
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0)
        elif self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            return ChatGoogleGenerativeAI(model=self.model, api_key=self.api_key, temperature=0)
        else:
            raise ValueError(f"Fournisseur inconnu : {self.provider}")

    def _init_langfuse(self):
        print(f"[DEBUG] Initialisation de LangFuse")
        # Get keys for your project from the project settings page: https://cloud.langfuse.com
        os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC")
        os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET")
        os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"  # 🇪🇺 EU region

    def _load_prompt(self, name: str) -> tuple[str, str]:
        sys_path = Path("prompts") / f"{name}.sys"
        hum_path = Path("prompts") / f"{name}.hum"
        if not sys_path.exists() or not hum_path.exists():
            raise FileNotFoundError(f"Prompt {name} manquant : {sys_path} ou {hum_path}")
        with open(sys_path, "r", encoding="utf-8") as f:
            sys_prompt = f.read()
        with open(hum_path, "r", encoding="utf-8") as f:
            hum_prompt = f.read()
        return sys_prompt, hum_prompt

    def _invoke(self, sys_prompt: str, hum_prompt: str, config: dict) -> str:
        print("[DEBUG] Appel au LLM...")
        response = self.llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=hum_prompt)
        ], config=config)
        return response.content.strip()

    def choose_language(self, doc: str, langs: List[str]) -> str:
        sys_prompt, hum_prompt = self._load_prompt("chooseLanguage")
        sys_prompt = sys_prompt.format(langs=", ".join(langs))
        hum_prompt = hum_prompt.format(doc=doc)
        response = self._invoke(sys_prompt, hum_prompt, 
                                config={
                                    "callbacks": [self.langfuse_handler],
                                    "metadata": {
                                        "langfuse_user_id": "felix",
                                        "langfuse_session_id": "l10n-assistant",
                                        "langfuse_tags": ["choose_lang"]
                                    }
                                })
        try:
            return response.split("REPONSE FINALE :")[1].strip()
        except Exception:
            raise ValueError(f"Réponse invalide du LLM : {response}")

    def process(self, flutter_file: str, arb_file: str, lang: str) -> tuple[str, str]:
        sys_prompt, hum_prompt = self._load_prompt("process")
        hum_prompt = hum_prompt.format(arb_file=arb_file, flutter_file=flutter_file, lang=lang)
        response = self._invoke(sys_prompt, hum_prompt, 
                                config={
                                    "callbacks": [self.langfuse_handler],
                                    "metadata": {
                                        "langfuse_user_id": "felix",
                                        "langfuse_session_id": "l10n-assistant",
                                        "langfuse_tags": ["process"]
                                    }
                                })
        try:
            final_response = response.split("REPONSE FINALE :")[1].strip()
            return final_response
        except Exception:
            raise ValueError(f"Format de réponse invalide : {response}")

    def amend_arb(self, input_json: str, lang_tag: str) -> str:
        sys_prompt, hum_prompt = self._load_prompt("amendArb")
        hum_prompt = hum_prompt.format(lang_tag=lang_tag, input=input_json)
        response = self._invoke(sys_prompt, hum_prompt, 
                                config={
                                    "callbacks": [self.langfuse_handler],
                                    "metadata": {
                                        "langfuse_user_id": "felix",
                                        "langfuse_session_id": "l10n-assistant",
                                        "langfuse_tags": ["amend_arb"]
                                    }
                                })
        try:
            return response.split("REPONSE FINALE :")[-1].strip()
        except Exception:
            raise ValueError(f"Réponse invalide du LLM : {response}")