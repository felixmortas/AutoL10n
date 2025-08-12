import os
from pathlib import Path
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


class LLM:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.llm = self._init_llm()

    def _init_llm(self):
        print(f"[DEBUG] Initialisation du LLM {self.provider} avec modèle {self.model}")
        if self.provider == "mistral":
            return ChatMistralAI(model=self.model, api_key=self.api_key, temperature=0, max_retries=5)
        elif self.provider == "openai":
            return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0, max_tokens=2048)
        elif self.provider == "google":
            return ChatGoogleGenerativeAI(model=self.model, google_api_key=self.api_key, temperature=0)
        else:
            raise ValueError(f"Fournisseur inconnu : {self.provider}")

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

    def _invoke(self, sys_prompt: str, hum_prompt: str) -> str:
        print("[DEBUG] Appel au LLM...")
        response = self.llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=hum_prompt)
        ])
        return response.content.strip()

    def choose_language(self, doc: str, langs: List[str]) -> str:
        sys_prompt, hum_prompt = self._load_prompt("chooseLanguage")
        sys_prompt = sys_prompt.format(langs=", ".join(langs))
        hum_prompt = hum_prompt.format(doc=doc)
        response = self._invoke(sys_prompt, hum_prompt)
        try:
            return response.split("REPONSE FINALE :")[1].strip()
        except Exception:
            raise ValueError(f"Réponse invalide du LLM : {response}")

    def process(self, flutter_file: str, arb_file: str, lang: str) -> tuple[str, str]:
        sys_prompt, hum_prompt = self._load_prompt("process")
        sys_prompt = sys_prompt.format(lang=lang)
        hum_prompt = hum_prompt.format(arb_file=arb_file, flutter_file=flutter_file, lang=lang)
        response = self._invoke(sys_prompt, hum_prompt)
        try:
            parts = response.split("```")
            arb_lines = parts[1].strip()
            flutter_code = parts[3].strip()
            return arb_lines, flutter_code
        except Exception:
            raise ValueError(f"Format de réponse invalide : {response}")

    def amend_arb(self, input_json: str, lang_tag: str) -> str:
        sys_prompt, hum_prompt = self._load_prompt("amendArb")
        hum_prompt = hum_prompt.format(lang_tag=lang_tag, input=input_json)
        response = self._invoke(sys_prompt, hum_prompt)
        try:
            return response.split("REPONSE FINALE :")[1].strip()
        except Exception:
            raise ValueError(f"Réponse invalide du LLM : {response}")