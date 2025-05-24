import subprocess
import os
import time
import zipfile
from flask import Flask, Response, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)
CORS(app)


@app.route('/stream')
def stream():
    def event_stream():
        with open('log_temp.txt', 'r') as f:
            f.seek(0, 2)  # Vai para o final do arquivo
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                else:
                    time.sleep(0.5)
    return Response(event_stream(), mimetype="text/event-stream")


def log_realtime(msg):
    print(msg)
    with open('log_temp.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/processados/<nome_json>')
def processados_json(nome_json):
    return send_from_directory('processados', nome_json)


@app.route('/processar', methods=['POST'])
def processar():
    open('log_temp.txt', 'w').close()
    # Crie uma pasta temporária para os vídeos recebidos
    pasta_videos = 'uploads/videos'
    os.makedirs(pasta_videos, exist_ok=True)

    pasta_raiz = request.form.get('pasta_raiz', 'videos')  # <-- Aqui!

    # Salva todos os vídeos enviados
    for file in request.files.getlist('videos'):
        caminho = os.path.join(pasta_videos, file.filename)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        file.save(caminho)

    # Salva a imagem, se enviada
    imagem_path = ''
    if 'imagem' in request.files:
        imagem = request.files['imagem']
        imagem_path = os.path.join('uploads', imagem.filename)
        imagem.save(imagem_path)

    # Chama o script Python passando os caminhos
    # (Adapte seu main.py para aceitar argumentos via sys.argv)
    import sys

    comando = [
        sys.executable, os.path.join('src', 'main.py'),
        pasta_videos,
        imagem_path,
        pasta_raiz
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    print("STDOUT do main.py:")
    print(resultado.stdout)
    print("STDERR do main.py:")
    print(resultado.stderr)
    return jsonify({'saida': resultado.stdout, 'erro': resultado.stderr})


if __name__ == '__main__':
    app.run(debug=True)
