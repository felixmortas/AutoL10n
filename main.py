import json
import shutil
import tempfile
from pathlib import Path
from typing import List

from llm import LLM


def atomic_write(file_path: Path, content: str):
    """Écriture atomique avec sauvegarde .bak"""
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    if file_path.exists():
        shutil.copy2(file_path, backup_path)
        print(f"[DEBUG] Sauvegarde .bak créée : {backup_path}")

    with tempfile.NamedTemporaryFile("w", delete=False, dir=file_path.parent, suffix=file_path.suffix) as tmp_file:
        tmp_file.write(content)
        tmp_name = tmp_file.name

    shutil.move(tmp_name, file_path)
    print(f"[DEBUG] Fichier mis à jour atomiquement : {file_path}")


def main(provider: str, model: str, arbs_folder_path: str, files_path: List[str]):
    print("[INFO] Initialisation du client LLM...")
    llm = LLM(provider=provider, model=model)

    l10n_folder = Path(arbs_folder_path)
    if not l10n_folder.exists():
        raise FileNotFoundError(f"Le dossier {l10n_folder} n'existe pas.")

    arb_files = list(l10n_folder.glob("app_*.arb"))
    langs = [f.stem.split("_")[1] for f in arb_files]
    print(f"[DEBUG] Langues détectées : {langs}")

    # Analyser la langue du premier fichier Flutter
    first_flutter_file = Path(files_path[0])
    if not first_flutter_file.exists():
        raise FileNotFoundError(f"Fichier Flutter introuvable : {first_flutter_file}")

    with open(first_flutter_file, "r", encoding="utf-8") as f:
        # read all the lines of the file
        lang_proof = f.read()

    print("[INFO] Détection de la langue...")
    lang_tag = llm.choose_language(lang_proof, langs)
    print(f"[INFO] Langue détectée : {lang_tag}")
    # Strip the lang_tag from any non_alpha characters, unless - or _
    lang_tag = ''.join(c for c in lang_tag if c.isalnum() or c in '-_')
    print(f"[INFO] Langue nettoyée : {lang_tag}")
    target_arb_path = l10n_folder / f"app_{lang_tag}.arb"

    fullArbLines = json.loads("{}")  # Initialiser avec un objet JSON vide

    with open(target_arb_path, "r", encoding="utf-8") as f:
        arb_content = f.read()

    # Traitement de chaque fichier Flutter
    for file_path_str in files_path:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"[WARNING] Fichier Flutter introuvable : {file_path}")
            continue

        print(f"[INFO] Traitement du fichier : {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            flutter_content = f.read()

        final_response = llm.process(flutter_content, arb_content, lang_tag)

        striped_response = final_response.strip('```dart').strip('```json')
        parts = striped_response.split('```')
        arb_lines = parts[0].strip()
        updated_flutter = parts[2]

        print(f"[DEBUG] Lignes ARB créées : {arb_lines}")

        fullArbLines.update(json.loads(arb_lines))
        fullArbLines = json.dumps(fullArbLines, indent=2, ensure_ascii=False)

        # Mise à jour du fichier .arb
        print(f"[INFO] Mise à jour du fichier ARB : {target_arb_path}")
        with open(target_arb_path, "r", encoding="utf-8") as f:
            existing = f.read()

        new_arb_content = merge_json_strings(existing, fullArbLines)

        atomic_write(target_arb_path, new_arb_content)

        # Mise à jour du fichier Flutter
        print(f"[INFO] Mise à jour du fichier Flutter : {file_path}")
        atomic_write(file_path, updated_flutter)

    # Traduction pour les autres langues
    other_arb_files = [f for f in arb_files if f != target_arb_path]
    print(f"[INFO] Traduction dans les autres langues : {[f.name for f in other_arb_files]}")

    for arb_file in other_arb_files:
        lang = arb_file.stem.split("_")[1]
        print(f"[INFO] Traduction en cours pour : {lang}")
        print(f"[DEBUG] Fichier ARB cible : {arb_file}")

        translated = llm.amend_arb(fullArbLines, lang)

        # read arb_file as json
        with open(arb_file, "r", encoding="utf-8") as f:
            existing = f.read()

        print(f"[DEBUG] Traduction obtenue pour {lang} : {translated}")

        new_arb_content = merge_json_strings(existing, translated)

        atomic_write(arb_file, new_arb_content)


def merge_json_strings(existing_json: str, new_json: str) -> str:
    """Fusionne deux fichiers JSON en gardant l'en-tête du premier"""
    import json
    try:
        print("[DEBUG] Fusion des fichiers JSON...")
        existing_data = json.loads(existing_json)
        new_data = json.loads(new_json)
        new_data.update(existing_data)
        return json.dumps(new_data, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Fusion JSON échouée : {e}")
        return existing_json


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, help="Fournisseur LLM (mistral, openai, google)")
    parser.add_argument("--model", required=True, help="Nom du modèle à utiliser")
    parser.add_argument("--arbs_folder", required=True, help="Chemin du dossier contenant les fichiers ARB")
    parser.add_argument("--files", nargs="+", required=True, help="Liste des fichiers Flutter à traiter")
    args = parser.parse_args()

    main(args.provider, args.model, args.arbs_folder, args.files)