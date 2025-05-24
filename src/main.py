import os
import sys
import json
from processamento import limpar_melhorar_videos


# Ponto de entrada do script, trata argumentos de linha de comando ou entrada manual
if __name__ == "__main__":
    if len(sys.argv) > 1:
        pasta_videos = sys.argv[1]
        imagem_path = sys.argv[2] if len(sys.argv) > 2 else None
        pasta_raiz = sys.argv[3]
        logs = limpar_melhorar_videos(
            pasta_videos, pasta_raiz, imagem_path=imagem_path)
        print(logs)
    else:
        pasta_videos = input(
            "Digite o caminho da pasta raiz contendo os vídeos: ").strip()
        imagem_path = input("Digite o caminho da imagem (opcional): ").strip()
        if imagem_path and not os.path.exists(imagem_path):
            print("Imagem não encontrada. Processamento sem imagem.")
            imagem_path = None
        limpar_melhorar_videos(pasta_videos, imagem_path=imagem_path)
        print("Processamento concluído.")
