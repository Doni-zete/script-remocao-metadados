# Remover Metadados

Este projeto é uma aplicação Python destinada a processar vídeos, removendo metadados indesejados e melhorando a qualidade dos arquivos. O foco principal é adaptar vídeos para formatos compatíveis com plataformas de mídia social, como Instagram, TikTok e YouTube Shorts.

## Estrutura do Projeto

O projeto é organizado da seguinte forma:

```
remover-metadados
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── processamento.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── arquivos.py
│   │   ├── ffmpeg.py
│   │   └── metadados.py
│   └── types
│       └── index.py
├── requirements.txt
└── README.md
```

## Instalação

Para instalar as dependências do projeto, execute o seguinte comando:


### 1. Criar o Ambiente Virtual
```bash
python -m venv venv

```

### 2. Ativar o Ambiente Virtual

```bash
source venv/Scripts/activate
```

### 3. Instalar Pacotes no Ambiente Virtual

```
pip install -r requirements.txt
```

## Uso

Para executar a aplicação, utilize o seguinte comando:

```
python src/server.py 
```
````bash
http://127.0.0.1:5000/
````

### 4. Terminou de usar | Deletar ambiente .venv

```bash
rm -rf .venv

```


## Funcionalidades

- Carregamento de vídeos de uma pasta específica.
- Remoção de metadados indesejados dos vídeos.
- Melhoria da qualidade e redimensionamento dos vídeos para formato vertical (9:16).
- Adição de uma imagem aos vídeos processados.
- Registro de logs e checkpoints para monitoramento do progresso.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.

