import os
import subprocess
import json
from pymediainfo import MediaInfo

# Função para ler o checkpoint e determinar onde retomar
def carregar_checkpoint():
    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
            return checkpoint.get("ultimo_arquivo", None)
    return None

# Função para salvar o checkpoint do último arquivo processado
def salvar_checkpoint(ultimo_arquivo):
    checkpoint = {"ultimo_arquivo": ultimo_arquivo}
    with open("checkpoint.json", "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=4)

# Função para carregar o histórico de vídeos processados
def carregar_historico():
    if os.path.exists("historico_processados.json"):
        with open("historico_processados.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Função para salvar o histórico de vídeos processados
def salvar_historico(historico):
    with open("historico_processados.json", "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

# Função para melhorar e redimensionar os vídeos para formato vertical (9:16) para plataformas como Instagram, TikTok e YouTube Shorts
# Alterado para 1080x1920 (vertical)
def limpar_melhorar_videos(pasta_videos, resolucao="1080x1920"):
    # Carrega o último arquivo processado
    ultimo_arquivo_processado = carregar_checkpoint()

    # Carrega o histórico dos vídeos processados
    historico_processados = carregar_historico()

    resultados = []
    iniciar_processamento = True  # Controla se devemos começar o processamento

    for root, dirs, files in os.walk(pasta_videos):
        for file in files:
            if file.endswith(".mp4"):
                file_path = os.path.join(root, file)

                # Verifica se o nome do arquivo já foi processado, se sim, ignora
                if file in historico_processados:
                    print(f"Vídeo '{file}' já processado. Pulando...")
                    continue

                # Inicia o processamento a partir do último arquivo, ou começa do primeiro vídeo
                if ultimo_arquivo_processado and file_path == ultimo_arquivo_processado:
                    iniciar_processamento = True

                # Se o processamento já foi iniciado, ou é o primeiro vídeo, processa o arquivo
                if iniciar_processamento:
                    try:
                        # Verificação dos metadados antes da limpeza
                        media_info_before = MediaInfo.parse(file_path)
                        metadados_antes = media_info_before.to_data()

                        # Comando para limpar metadados, melhorar a qualidade e redimensionar a resolução para formato vertical
                        temp_file_path = file_path + ".temp"
                        comando_ffmpeg = [
                            "ffmpeg", "-i", file_path, "-map_metadata", "-1",
                            "-c:v", "libx264", "-crf", "18", "-preset", "slow",  # Melhora a qualidade do vídeo
                            "-c:a", "aac", "-b:a", "192k",  # Melhora a qualidade do áudio
                            # Redimensiona e ajusta o vídeo para 1080x1920
                            "-vf", f"scale={resolucao}:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                            "-f", "mp4", temp_file_path,
                            "-metadata", "title=", "-metadata", "author=", "-metadata", "comment=", "-metadata", "description=", "-metadata", "creation_time=",
                            "-metadata:s:v", "title=", "-metadata:s:v", "comment=", "-metadata:s:a", "title=", "-metadata:s:a", "comment="
                        ]
                        subprocess.run(comando_ffmpeg, check=True)

                        # Substituir o arquivo original pelo arquivo temporário
                        os.replace(temp_file_path, file_path)

                        # Verificação dos metadados após a limpeza
                        media_info_after = MediaInfo.parse(file_path)
                        metadados_depois = media_info_after.to_data()
                        metadados_removidos = True

                        # Verifica se os metadados específicos foram removidos
                        for track in metadados_depois['tracks']:
                            if track['track_type'] == 'General':
                                if any(key in track for key in ['title', 'author', 'comment', 'description', 'creation_time']):
                                    metadados_removidos = False
                                    break

                        if metadados_removidos:
                            resultado = {
                                "arquivo": file_path,
                                "status": "Metadados limpos com sucesso e qualidade melhorada",
                                "metadados_antes": metadados_antes,
                                "metadados_depois": metadados_depois
                            }
                            print(
                                f"Metadados limpos com sucesso e qualidade melhorada para {file_path}")
                        else:
                            resultado = {
                                "arquivo": file_path,
                                "status": "Falha ao limpar metadados",
                                "metadados_restantes": track,
                                "metadados_antes": metadados_antes,
                                "metadados_depois": metadados_depois
                            }
                            print(
                                f"Falha ao limpar metadados para {file_path}")
                            print(f"Metadados restantes: {track}")

                        resultados.append(resultado)

                        # Adiciona o vídeo ao histórico
                        historico_processados.append(file)

                        # Salva o checkpoint e o histórico
                        salvar_checkpoint(file_path)
                        salvar_historico(historico_processados)

                    except Exception as e:
                        resultado = {
                            "arquivo": file_path,
                            "status": "Erro inesperado",
                            "erro": str(e)
                        }
                        print(
                            f"Erro inesperado ao processar '{file_path}': {e}")
                        resultados.append(resultado)

                else:
                    print(
                        f"Pulando o arquivo {file_path}, pois ainda não foi atingido o último arquivo processado")

    # Exibe o último vídeo processado
    if resultados:
        ultimo_video = resultados[-1]
        print("\nÚltimo vídeo processado:")
        print(f"Arquivo: {ultimo_video['arquivo']}")
        print(f"Status: {ultimo_video['status']}")

    # Salvar os resultados em um arquivo JSON
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)


# Solicita o caminho da pasta ao usuário
if __name__ == "__main__":
    pasta_videos = input(
        "Digite o caminho da pasta raiz contendo os vídeos: ").strip()
    limpar_melhorar_videos(pasta_videos)
