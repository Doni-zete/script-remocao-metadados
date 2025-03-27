import os
import subprocess
import json
from pymediainfo import MediaInfo

# Função para ler os vídeos processados da pasta específica
def carregar_processados(pasta_videos):
    nome_pasta = os.path.basename(pasta_videos)
    caminho_json = os.path.join(
        "processados", f"{nome_pasta}_processados.json")

    if os.path.exists(caminho_json):
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Função para salvar os vídeos processados na pasta específica
def salvar_processados(pasta_videos, processados):
    nome_pasta = os.path.basename(pasta_videos)
    caminho_json = os.path.join(
        "processados", f"{nome_pasta}_processados.json")

    os.makedirs("processados", exist_ok=True)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(processados, f, ensure_ascii=False, indent=4)

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

# Função para criar um vídeo temporário a partir da imagem
def criar_video_temporario(imagem_path, duracao=2):
    imagem_temp_path = "imagem_temp.mp4"
    comando_criar_temp = [
        "ffmpeg", "-loop", "1", "-i", imagem_path, "-c:v", "libx264", "-t", str(
            duracao),
        # Não redimensiona a imagem
        "-vf", "scale=iw:ih,format=yuv420p", "-pix_fmt", "yuv420p", "-an", imagem_temp_path
    ]
    subprocess.run(comando_criar_temp, check=True)
    return imagem_temp_path

# Função para concatenar vídeos (garantir que o vídeo e a imagem sejam combinados corretamente)
def concatenar_videos(video_path, imagem_temp_path):
    output_path = video_path + "_com_imagem.mp4"

    # Criação do arquivo de entrada para concatenação
    with open("inputs.txt", "w", encoding="utf-8") as f:
        f.write(f"file '{video_path}'\n")  # Primeiro o vídeo
        f.write(f"file '{imagem_temp_path}'\n")  # Depois a imagem

    comando_concat = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", "inputs.txt", "-c:v", "libx264", "-c:a", "aac", output_path
    ]
    subprocess.run(comando_concat, check=True)
    os.remove("inputs.txt")
    return output_path

# Função para melhorar e redimensionar os vídeos para formato vertical (9:16) para plataformas como Instagram, TikTok e YouTube Shorts
# Alterado para 1080x1920 (vertical)
def limpar_melhorar_videos(pasta_videos, resolucao="1080x1920", imagem_path=None):
    # Carrega os vídeos já processados (salvando apenas o nome do arquivo)
    processados = carregar_processados(pasta_videos)

    # Carrega o último arquivo processado
    ultimo_arquivo_processado = carregar_checkpoint()

    resultados = []
    iniciar_processamento = True  # Controla se devemos começar o processamento

    for root, dirs, files in os.walk(pasta_videos):
        for file in files:
            if file.endswith(".mp4"):
                file_path = os.path.join(root, file)
                # Pega apenas o nome do arquivo
                file_name = os.path.basename(file_path)

                # Se o vídeo já foi processado, pula para o próximo
                if file_name in processados:
                    print(
                        f"Pulo o arquivo {file_name} pois já foi processado.")
                    continue

                # Inicia o processamento a partir do último arquivo, ou começa do primeiro vídeo
                if ultimo_arquivo_processado and file_name == ultimo_arquivo_processado:
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
                                f"Metadados limpos com sucesso e qualidade melhorada para {file_name}")
                        else:
                            resultado = {
                                "arquivo": file_path,
                                "status": "Falha ao limpar metadados",
                                "metadados_restantes": track,
                                "metadados_antes": metadados_antes,
                                "metadados_depois": metadados_depois
                            }
                            print(
                                f"Falha ao limpar metadados para {file_name}")
                            print(f"Metadados restantes: {track}")

                        resultados.append(resultado)

                        # Juntar vídeo com imagem
                        if imagem_path:
                            imagem_temp_path = criar_video_temporario(
                                imagem_path)
                            output_path = concatenar_videos(
                                file_path, imagem_temp_path)
                            # Remover o vídeo temporário
                            os.remove(imagem_temp_path)
                            # Substituir o vídeo original pelo vídeo com imagem
                            os.replace(output_path, file_path)
                            print(
                                f"Imagem juntada ao vídeo e salvo em: {file_name}")

                        # Adiciona o nome do vídeo processado à lista de processados (apenas o nome)
                        processados.append(file_name)
                        salvar_processados(pasta_videos, processados)

                        # Salva o checkpoint a cada vídeo processado com sucesso
                        salvar_checkpoint(file_name)

                    except Exception as e:
                        resultado = {
                            "arquivo": file_path,
                            "status": "Erro inesperado",
                            "erro": str(e)
                        }
                        print(
                            f"Erro inesperado ao processar '{file_name}': {e}")
                        resultados.append(resultado)

                else:
                    print(
                        f"Pulando o arquivo {file_name}, pois ainda não foi atingido o último arquivo processado")

    # Salvar os resultados em um arquivo JSON
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)


# Solicita o caminho da pasta ao usuário
if __name__ == "__main__":
    pasta_videos = input(
        "Digite o caminho da pasta raiz contendo os vídeos: ").strip()
    imagem_path = input("Digite o caminho da imagem (opcional): ").strip()
    if imagem_path and not os.path.exists(imagem_path):
        print("Imagem não encontrada. Processamento sem imagem.")
        imagem_path = None

    limpar_melhorar_videos(pasta_videos, imagem_path=imagem_path)
