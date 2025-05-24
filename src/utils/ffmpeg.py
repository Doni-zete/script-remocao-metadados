import subprocess
import re

# Obtém os parâmetros do vídeo (largura, altura, fps) usando ffprobe
def obter_parametros_video(video_path):
    import json
    comando = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "json", video_path
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if not resultado.stdout:
        raise Exception(
            f"ffprobe não retornou saída para o vídeo: {video_path}")
    info = json.loads(resultado.stdout)
    stream = info['streams'][0]
    width = stream['width']
    height = stream['height']
    fps_str = stream['r_frame_rate']
    # Calcula o fps corretamente, tratando casos de fração
    if '/' in fps_str:
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 30
    else:
        fps = float(fps_str)
    return width, height, fps

# Cria um vídeo temporário a partir de uma imagem, com resolução e fps definidos
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


def rodar_ffmpeg_com_progresso(comando, file_name, log_realtime):
    import subprocess
    process = subprocess.Popen(
        comando,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    total_duration = None
    duration_pattern = re.compile(r'Duration: (\d+):(\d+):(\d+).(\d+)')
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
    last_percent = -1

    for line in process.stderr:
        # Descobre a duração total do vídeo
        if total_duration is None:
            match = duration_pattern.search(line)
            if match:
                h, m, s, ms = map(int, match.groups())
                total_duration = h * 3600 + m * 60 + s + ms / 100
        # Descobre o tempo atual processado
        match = time_pattern.search(line)
        if match and total_duration:
            h, m, s, ms = map(int, match.groups())
            current = h * 3600 + m * 60 + s + ms / 100
            percent = int((current / total_duration) * 100)
            if percent != last_percent:
                log_realtime(f"Processando {file_name}: {percent}%")
                last_percent = percent
    process.wait()
    if process.returncode != 0:
        raise Exception("Erro no ffmpeg")

# Concatena o vídeo original com o vídeo temporário criado a partir da imagem
def concatenar_videos(video_path, imagem_temp_path, file_name, log_realtime):
    import os
    output_path = video_path + "_com_imagem.mp4"
    video_temp = "video_temp.mp4"
    # Converte o vídeo original para um formato temporário compatível
    subprocess.run([
        "ffmpeg", "-i", video_path, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", "-y", video_temp
    ], check=True)
    # Cria o arquivo de inputs para concatenação
    with open("inputs.txt", "w", encoding="utf-8") as f:
        f.write(f"file '{video_temp}'\n")
        f.write(f"file '{imagem_temp_path}'\n")
    comando_concat = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", "inputs.txt",
        "-c", "copy", output_path, "-y"
    ]
    # Executa a concatenação dos vídeos
    rodar_ffmpeg_com_progresso(comando_concat, file_name, log_realtime)
    # Remove arquivos temporários
    os.remove("inputs.txt")
    os.remove(video_temp)
    return output_path
