# Pseudo-code

import langgraph

class LLM(provider:str, api_key:str, model:str):

def __init__(self):    
    self.provider = provider,
    self.api_key = api_key,
    self.model = model,
    self.llm = None,
    
    initLLM()

def initLLM():
    swtich(self.provider): self.llm = langchain_google(api_key)
        case('mistral'): ...
        case('openai'): ...
        case('anthropic'): ...
    
def chooseLanguage(doc:str, langs:[lang:str]):
    sys_prompt = f"""
    Tu es un expert en langue. Dans ce fichier en code flutter, évalue la langue de l'utilisateur à partir du texte dans les objets d'interface utilisateur.
    Ton choix doit se faire à partir de cette liste de lang tags : {langs}.
    Ta réponse finale doit être le tag de la langue.
    Explique ton raisonnement puis formule ta réponse finale de cette manière :
    REPONSE FINALE : [REPONSE FINALE] 
    """

    hum_prompt = f"""
    Voici le document à analyser :
    <flutter_file>
    {doc}
    </flutter_file>
    """

    response = self.llm.chat(sys_prompt=sys_prompt, hum_prompt=hum_prompt, model=self.model)

    language = response.split('REPONSE FINALE : ')[1]

def process(flutter_file:str, arbFile:str, lang:str):

    sys_prompt = f"""
    Tu es un expert en internationalisation de texte d'application mobiles flutter.
    Tu as 2 tâches :

    La première tâche consiste à créer de la donnée pour ammender le fichier clef/valeur 'app_{lang}.arb'. 
    Le processus pour créer la donnée est le suivant :
    1) Dans le fichier flutter, repérer les textes dans les widgets pouvant afficher du texte statique dans l'interface utilisateur.
    2) Pour toutes les valeurs qui ne sont pas dans le fichier .arb, leur associer une clef et les ajouter au fichier.
    3) Génère les traductions à ajouter au fichier 'app_{lang}.arb'. Ne génère pas les traductions qui sont déjà dans le fichier .arb. Attention à NE SURTOUT PAS mettre de {}, et à bien mettre des virgules à la fin de la denrière ligne.
    
    La seconde tâche consiste à modifier le fichier flutter pour remplacer le texte statique par du texte dynamique.
    Le processus pour modifier le fichier est le suivant :
    1) Pour chaque texte statique dans un widget, remplacer le texte brute par AppLocalization.of(context)!.key.
    2) Regénère le fichier flutter. Attention à ne pas remplacer les textes des dictionnaires ou autres objets n'étant pas affiché dans l'interface utilisateur. Attention à également bien ajouter le ! à AppLocalization.of(context).

    Voici le format de réponse attendu :
    
    REPONSE FINALE : 
    app_{lang}.arb
    ```
    "key1": "value1",
    "key2": "value2",
    ```

    flutter_file.dart
    ```
    ...
    ElevatedButton(
        Text(AppLocalization.of(context)!.tryAgain)
    )
    ...
    ```
    """
    
    hum_prompt = f"""
    Voici le fichier 'app_{lang}.arb' :
    <app_{lang}.arb>
    {arbFile}
    </app_{lang}.arb>

    et voici le fichier flutter :
    <flutter_file.dart>
    {flutter_file}
    </flutter_file.dart>
    """

    response = self.llm.chat(sys_prompt=sys_prompt, hum_prompt=hum_prompt, model=self.model)

    final_response = response.split('REPONSE FINALE : ')[1]

    response_split = final_response.split('```')

    arblines = response_split[1]
    flutterFile = response_split[3]

    return arblines, flutterFile