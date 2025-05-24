import os
import subprocess
import json
from pymediainfo import MediaInfo
from server import log_realtime
from utils.metadados import limpar_melhorar_metadados
from utils.ffmpeg import rodar_ffmpeg_com_progresso
import re

# Carrega a lista de vídeos já processados para evitar retrabalho
def caminho_para_nome_json(pasta_raiz):
    # Use só o nome da pasta raiz, tornando seguro para nome de arquivo
    nome = re.sub(r'[^a-zA-Z0-9_\-]', '_', pasta_raiz)
    return f"{nome}_processados.json"


def carregar_processados(pasta_raiz):
    nome_json = caminho_para_nome_json(pasta_raiz)
    caminho_json = os.path.join("processados", nome_json)
    if os.path.exists(caminho_json):
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_processados(pasta_raiz, processados):
    nome_json = caminho_para_nome_json(pasta_raiz)
    caminho_json = os.path.join("processados", nome_json)
    os.makedirs("processados", exist_ok=True)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(processados, f, ensure_ascii=False, indent=4)

# Carrega o checkpoint do último arquivo processado
def carregar_checkpoint():
    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
            return checkpoint.get("ultimo_arquivo", None)
    return None

# Salva o checkpoint do último arquivo processado
def salvar_checkpoint(ultimo_arquivo):
    checkpoint = {"ultimo_arquivo": ultimo_arquivo}
    with open("checkpoint.json", "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=4)

# Obtém parâmetros do vídeo (largura, altura, fps) usando ffprobe
def obter_parametros_video(video_path):
    comando = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "json", video_path
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    info = json.loads(resultado.stdout)
    stream = info['streams'][0]
    width = stream['width']
    height = stream['height']
    fps_str = stream['r_frame_rate']
    if '/' in fps_str:
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 30
    else:
        fps = float(fps_str)
    return width, height, fps

# Cria um vídeo temporário a partir de uma imagem
def criar_video_temporario(imagem_path, width, height, fps, duracao=2):
    imagem_temp_path = "imagem_temp.mp4"
    comando_criar_temp = [
        "ffmpeg", "-loop", "1", "-i", imagem_path,
        "-c:v", "libx264", "-t", str(duracao),
        "-vf", f"scale={width}:{height},format=yuv420p",
        "-r", str(fps),
        "-pix_fmt", "yuv420p", "-an", imagem_temp_path,
        "-y"
    ]
    subprocess.run(comando_criar_temp, check=True)
    return imagem_temp_path


# Concatena o vídeo original com o vídeo temporário criado a partir da imagem
def concatenar_videos(video_path, imagem_temp_path, file_name, log_realtime):

    output_path = video_path + "_com_imagem.mp4"
    video_temp = "video_temp.mp4"
    subprocess.run([
        "ffmpeg", "-i", video_path, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", "-y", video_temp
    ], check=True)
    with open("inputs.txt", "w", encoding="utf-8") as f:
        f.write(f"file '{video_temp}'\n")
        f.write(f"file '{imagem_temp_path}'\n")
    comando_concat = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", "inputs.txt",
        "-c", "copy", output_path, "-y"
    ]
    rodar_ffmpeg_com_progresso(comando_concat, file_name, log_realtime)
    os.remove("inputs.txt")
    os.remove(video_temp)
    return output_path

# Função principal que processa todos os vídeos de uma pasta, limpando e melhorando os metadados
def limpar_melhorar_videos(pasta_videos, pasta_raiz, resolucao="1080x1920", imagem_path=None):
    logs = []
    processados = carregar_processados(pasta_raiz)
    ultimo_arquivo_processado = carregar_checkpoint()

    todos_videos = [os.path.join(root, file)
                    for root, dirs, files in os.walk(pasta_videos)
                    for file in files if file.endswith(".mp4")]
    total_videos = len(todos_videos)
    logs.append(f"Total de vídeos encontrados: {total_videos}")

    resultados = []
    iniciar_processamento = True
    video_atual = 0

    # Loop para processar cada vídeo encontrado
    for file_path in todos_videos:
        file_name = os.path.basename(file_path)
        video_atual += 1

        # Pula vídeos já processados
        if file_name in processados:
            msg = f"[{video_atual}/{total_videos}] {file_name} já processado. Pulando."
            logs.append(msg)
            log_realtime(msg)
            continue

        # Retoma o processamento a partir do último arquivo processado, se houver checkpoint
        if ultimo_arquivo_processado and file_name == ultimo_arquivo_processado:
            iniciar_processamento = True

        if iniciar_processamento:
            msg = f"[{video_atual}/{total_videos}] Processando: {file_name}..."
            logs.append(msg)
            log_realtime(msg)
            try:
                # Chama a função que limpa e melhora os metadados do vídeo
                resultado = limpar_melhorar_metadados(
                    file_path, resolucao, imagem_path,
                    obter_parametros_video, criar_video_temporario, concatenar_videos, log_realtime
                )
                resultados.append(resultado)
                processados.append(file_name)
                salvar_processados(pasta_raiz, processados)
                salvar_checkpoint(file_name)
                msg = f"[{video_atual}/{total_videos}] Sucesso: {file_name}"
                logs.append(msg)
                log_realtime(msg)
            except Exception as e:
                # Em caso de erro, registra no log e salva o erro nos resultados
                resultado = {
                    "arquivo": file_name,
                    "status": "Erro inesperado",
                    "erro": str(e)
                }
                msg = f"[{video_atual}/{total_videos}] ERRO ao processar {file_name}: {e}"
                logs.append(msg)
                log_realtime(msg)
                resultados.append(resultado)
        else:
            # Mensagem para arquivos pulados aguardando o checkpoint
            msg = f"[{video_atual}/{total_videos}] Pulando {file_name}, aguardando último arquivo processado."
            logs.append(msg)
            log_realtime(msg)

    # Ao final, salva os resultados em um arquivo JSON
    logs.append("Processamento de todos os vídeos finalizado.")
    log_realtime("Processamento de todos os vídeos finalizado.")
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    return "Processamento finalizado com sucesso!"
