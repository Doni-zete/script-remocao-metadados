import os
import json

# Carrega a lista de vídeos já processados para evitar retrabalho
def carregar_processados(pasta_videos):
    nome_pasta = os.path.basename(pasta_videos)
    caminho_json = os.path.join(
        "processados", f"{nome_pasta}_processados.json")
    if os.path.exists(caminho_json):
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salva a lista de vídeos já processados em um arquivo JSON
def salvar_processados(pasta_videos, processados):
    nome_pasta = os.path.basename(pasta_videos)
    caminho_json = os.path.join(
        "processados", f"{nome_pasta}_processados.json")
    os.makedirs("processados", exist_ok=True)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(processados, f, ensure_ascii=False, indent=4)

# Carrega o checkpoint do último arquivo processado, se existir
def carregar_checkpoint():
    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
            return checkpoint.get("ultimo_arquivo", None)
    return None

# Salva o nome do último arquivo processado em um arquivo checkpoint.json
def salvar_checkpoint(ultimo_arquivo):
    checkpoint = {"ultimo_arquivo": ultimo_arquivo}
    with open("checkpoint.json", "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=4)
