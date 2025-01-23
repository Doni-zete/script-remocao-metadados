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

# Função principal para limpar e melhorar os vídeos


def limpar_e_melhorar_videos(pasta_videos):
    # Carrega o último arquivo processado
    ultimo_arquivo_processado = carregar_checkpoint()

    resultados = []
    iniciar_processamento = True  # Controla se devemos começar o processamento

    for root, dirs, files in os.walk(pasta_videos):
        for file in files:
            if file.endswith(".mp4"):
                file_path = os.path.join(root, file)

                # Inicia o processamento a partir do último arquivo, ou começa do primeiro vídeo
                if ultimo_arquivo_processado and file_path == ultimo_arquivo_processado:
                    iniciar_processamento = True

                # Se o processamento já foi iniciado, ou é o primeiro vídeo, processa o arquivo
                if iniciar_processamento:
                    try:
                        # Verificação dos metadados antes da limpeza
                        media_info_before = MediaInfo.parse(file_path)
                        metadados_antes = media_info_before.to_data()

                        # Comando para limpar metadados e melhorar a qualidade usando ffmpeg
                        temp_file_path = file_path + ".temp"
                        comando_ffmpeg = [
                            "ffmpeg", "-i", file_path, "-map_metadata", "-1",
                            "-c:v", "libx264", "-crf", "18", "-preset", "slow",  # Melhora a qualidade do vídeo
                            "-c:a", "aac", "-b:a", "192k",  # Melhora a qualidade do áudio
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

                        # Salva o checkpoint a cada vídeo processado com sucesso
                        salvar_checkpoint(file_path)

                    except Exception as e:
                        resultado = {
                            "arquivo": file_path,
                            "status": "Erro inesperado",
                            "erro": str(e)
                        }
                        print(
                            f"Erro inesperado ao processar '{file_path}': {e}")
                        resultados.append(resultado)

                    # Após processar o vídeo, continuar para o próximo
                else:
                    print(
                        f"Pulando o arquivo {file_path}, pois ainda não foi atingido o último arquivo processado")

    # Salvar os resultados em um arquivo JSON
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)


# Solicita o caminho da pasta ao usuário
if __name__ == "__main__":
    pasta_videos = input(
        "Digite o caminho da pasta raiz contendo os vídeos: ").strip()
    limpar_e_melhorar_videos(pasta_videos)
