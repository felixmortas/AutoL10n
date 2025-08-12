# Pseudo-code

import llm

def main(provider:str, api_key_:str, model:str, files_path:[file_path:str]):

    llm = llm(provider:str, api_key_:str, model:str)

    l10nFolder = 'lib/l10n/'
    langsArb = os.find(l10nFolder + '*.arb')
    langs = langsArb.split('_')[1].split('.')[0]
    
    with f as file.open(files_path[0], 'r'):
        langProof = f.readlines()

    lang_tag = llm.chooseLanguage(langProof, langs)
    arbFilePath = os.join(l10nFolder, f'app_{lang_tag}.arb')

    for file_path in files_path:
        with f as file.read(arbFilePath, 'r'):
            arbFile = f.lines

        with f as file.open(file_path, 'r'):
            input = f.readlines()

        arbLines, flutterFile = llm.process(input, arbFile, lang_tag)

        with f as file.open(arbFilePath, 'rw'):
            f.drop_first_line()

            file_header = "{\n"
            file_body = arbLines
            file_footer = f.readlines()

            f.overwrite(file_header, file_body, file_footer)

        with f as file.open(file_path, 'rw'):
            f.overwrite(flutterFile)