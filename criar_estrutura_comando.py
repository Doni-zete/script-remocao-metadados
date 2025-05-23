import os

estrutura = [
    "src/__init__.py",
    "src/main.py",
    "src/processamento.py",
    "src/utils/__init__.py",
    "src/utils/arquivos.py",
    "src/utils/ffmpeg.py",
    "src/utils/metadados.py",
    "src/types/index.py",
    "requirements.txt",
    "README.md"
]

for caminho in estrutura:
    dir_path = os.path.dirname(caminho)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if not os.path.exists(caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            if caminho.endswith("__init__.py"):
                f.write("# Pacote Python\n")
            elif caminho.endswith(".md"):
                f.write("# Projeto remover-metadados\n")
            else:
                f.write("")

print("Estrutura criada com sucesso!")