from pymediainfo import MediaInfo
import subprocess
import os
from utils.ffmpeg import rodar_ffmpeg_com_progresso

def limpar_melhorar_metadados(file_path, resolucao, imagem_path, obter_parametros_video, criar_video_temporario, concatenar_videos, log_realtime):
    # Verificação dos metadados antes da limpeza
    media_info_before = MediaInfo.parse(file_path)
    metadados_antes = media_info_before.to_data()

    temp_file_path = file_path + ".temp"
    comando_ffmpeg = [
        "ffmpeg", "-i", file_path, "-map_metadata", "-1",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-c:a", "aac", "-b:a", "192k",
        "-vf", f"scale={resolucao}:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-f", "mp4", temp_file_path,
        "-metadata", "title=", "-metadata", "author=", "-metadata", "comment=", "-metadata", "description=", "-metadata", "creation_time=",
        "-metadata:s:v", "title=", "-metadata:s:v", "comment=", "-metadata:s:a", "title=", "-metadata:s:a", "comment="
    ]
    rodar_ffmpeg_com_progresso(
        comando_ffmpeg, os.path.basename(file_path), log_realtime)
    os.replace(temp_file_path, file_path)

    media_info_after = MediaInfo.parse(file_path)
    metadados_depois = media_info_after.to_data()
    metadados_removidos = True

    for track in metadados_depois['tracks']:
        if track['track_type'] == 'General':
            if any(key in track for key in ['title', 'author', 'comment', 'description', 'creation_time']):
                metadados_removidos = False
                break

    resultado = {
        "arquivo": file_path,
        "status": "Metadados limpos com sucesso e qualidade melhorada" if metadados_removidos else "Falha ao limpar metadados",
        "metadados_antes": metadados_antes,
        "metadados_depois": metadados_depois
    }

    # Juntar vídeo com imagem, se necessário
    if imagem_path:
        width, height, fps = obter_parametros_video(file_path)
        imagem_temp_path = criar_video_temporario(
            imagem_path, width, height, fps)
        # Corrigido: passando file_name e log_realtime
        output_path = concatenar_videos(
            file_path, imagem_temp_path, os.path.basename(file_path), log_realtime)
        os.remove(imagem_temp_path)
        os.replace(output_path, file_path)
        # if log_realtime:
        #    log_realtime(
        #        f"Imagem juntada ao vídeo e salvo em: {os.path.basename(file_path)}")

    return resultado
