# Guia para Criar e Usar um Ambiente Virtual (venv) no Python

Este guia contém os passos necessários para criar e ativar um ambiente virtual (venv) no Python em sistemas Windows e Unix (Linux/macOS).

## Passos para Criar o Ambiente Virtual:

### 1. Abrir o Terminal ou Prompt de Comando

- **No Windows**: Abra o **Prompt de Comando** ou **PowerShell** como administrador.
- **No Linux/macOS**: Abra o terminal normalmente.

### 2. Navegar até o Diretório Desejado

Use o comando `cd` para navegar até o diretório onde você deseja criar o ambiente virtual. Exemplo:

```bash
cd /e/shoppe/script-remocao-metadados
```
### 3. Criar o Ambiente Virtual

```bash
python -m venv venv

```

### 4. Ativar o Ambiente Virtual

```bash
source venv/Scripts/activate
```



### 5. Instalar Pacotes no Ambiente Virtual

```bash
pip install -r requirements.txt

```


### 6. Rodar a aplicação

```bash
python main.py
```

### 7. Colar o caminho dos videos/subpastas

```bash
E:\shoppe\Eduzz\videos\PACK-700-SHOPEE\VIDEOS 600-900
```

### 8. Terminou de usar | Deletar ambiente .venv

```bash
rm -rf .venv

```

