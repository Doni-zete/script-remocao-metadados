let processados = [];

// Mostra logs coloridos em tempo real no front
function iniciarStreamLogs() {
  const logMsg = document.getElementById('logMsg');
  // Remova ou comente a linha abaixo para não apagar os logs anteriores
  // logMsg.innerHTML = '';
  const eventSource = new EventSource('/stream');
  eventSource.onmessage = function (event) {
    let line = event.data;

    if (line.includes('%')) {
      // Exemplo: "Processando WhatsApp Video ...: 37%"
      document.getElementById('progresso').innerHTML = `<span style="color:#1976d2;">${line}</span>`;
      return;
    }

    // Verde para sucesso
    if (line.includes('Sucesso:')) {
      line = `<span style="color:#388e3c;">${line}</span>`;
    }
    // Laranja para processando
    else if (line.includes('Processando:')) {
      line = `<span style="color:#ff9800;">${line}</span>`;
    }
    // Vermelho para erro
    else if (line.includes('ERRO')) {
      line = `<span style="color:#d32f2f;">${line}</span>`;
    }
    // Azul para o resto
    else {
      line = `<span style="color:#1892f5;">${line}</span>`;
    }

    logMsg.innerHTML += line + '<br>';
    logMsg.scrollTop = logMsg.scrollHeight;
  };
  eventSource.onerror = function () {
    eventSource.close();
  };
}

// Chame iniciarStreamLogs() logo antes de enviar os arquivos
function enviar() {
  iniciarStreamLogs();
  const formData = new FormData();
  const videoFolder = document.getElementById('videoFolder');
  const imageFile = document.getElementById('imageFile');
  const progresso = document.getElementById('progresso');
  const logMsg = document.getElementById('logMsg');

  logMsg.innerHTML = '<span class="status">Enviando arquivos e processando, aguarde...</span><br>';
  progresso.innerHTML = '';

  for (const file of videoFolder.files) {
    formData.append('videos', file, file.webkitRelativePath);
  }
  if (imageFile.files.length > 0) {
    formData.append('imagem', imageFile.files[0]);
  }

  // ADICIONE ESTE BLOCO AQUI, ANTES DO fetch:
  if (videoFolder.files.length > 0) {
    // Pega o nome da pasta raiz selecionada
    const rootFolder = videoFolder.files[0].webkitRelativePath.split('/')[0];
    formData.append('pasta_raiz', rootFolder);
  }

  fetch('/processar', { method: 'POST', body: formData })
    .then(r => r.json().catch(() => ({ erro: 'Resposta inválida do servidor' })))
    .then(data => {
      if (data.erro) {
        logMsg.innerHTML += `<span class="status erro">Erro: ${data.erro}</span>`;
        progresso.innerHTML = '';
      } else {
        logMsg.innerHTML += `<span class="status sucesso">Processamento finalizado!</span>`;
        progresso.innerHTML = '';
      }
    })
    .catch(() => {
      logMsg.innerHTML += `<span class="status erro">Erro inesperado ao enviar ou processar os arquivos.</span>`;
      progresso.innerHTML = '';
    });

}

