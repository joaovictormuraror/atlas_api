# ATLAS API

API em Flask que gera roteiros personalizados com Gemini e mantém um pequeno CRUD local de roteiros salvos em `roteiros.json`.

## Pré-requisitos
- Python 3.10+ (recomendado virtualenv)
- Conta Google AI Studio com chave de API do Gemini (modelo default `models/gemini-2.0-flash`)
- Sistema compatível com `python3 -m venv`

## Passo a passo para rodar localmente
1. **Clone / atualize o projeto**
   ```bash
   git clone <repo-url>
   cd atlas_api
   ```
2. **Crie e ative o ambiente**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Instale as dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Configure variáveis de ambiente** (arquivo `.env` na raiz):
   ```ini
   GEMINI_API_KEY=coloque_sua_chave_aqui
   # Opcional: GEMINI_MODEL=models/gemini-2.0-flash
   ```
   O arquivo é lido automaticamente por `python-dotenv`. Sem a chave o endpoint de IA falha.
5. **Execute a API**
   ```bash
   python app.py
   ```
   O servidor sobe em `http://0.0.0.0:8080` com reload e logs em modo debug.

## Estrutura relevante
```
app.py          # Flask + chamadas Gemini + CRUD arquivo
requirements.txt
roteiros.json   # Banco local (JSON)
requests.http   # Exemplos de requisições (VS Code / REST Client)
```

## Endpoints

### `GET /`
Retorna `{ "status": "API funcionando!" }` para verificação de saúde.

### `POST /gerar-roteiro`
Gera um roteiro entre `dataInicio` e `dataFim` usando o modelo Gemini e devolve JSON já pronto para consumo.

**Body esperado**
```json
{
  "nome": "Férias no Rio",
  "destino": "Rio de Janeiro",
  "dataInicio": "2025-02-10",
  "dataFim": "2025-02-14",
  "observacoes": "Trilho leve e restaurantes"
}
```
**Erros comuns**
- Campos obrigatórios ausentes → `400`
- Falha na chamada do modelo → resposta padrão com `_raw` contendo o texto retornado.

### `POST /roteiros`
Salva um roteiro customizado no arquivo `roteiros.json`.

**Body**
```json
{
  "title": "Rio express",
  "destination": "Rio de Janeiro",
  "duration": "4 dias",
  "content": { "...": "..." },
  "createdAt": "2025-02-01T10:00:00Z"
}
```
O backend gera um `id` UUID e retorna `201` com o objeto salvo.

### `GET /roteiros`
Lista todos os registros presentes em `roteiros.json`.

### `DELETE /roteiros/<id>`
Remove o roteiro cujo `id` corresponda à rota. Retorna `{ "ok": true }` independente de o registro existir ou não.

## Testando requisições
- **REST Client / VS Code**: use o arquivo `requests.http` já configurado.
- **cURL**:
  ```bash
  curl -X POST http://localhost:8080/gerar-roteiro \
    -H "Content-Type: application/json" \
    -d '{ "nome": "João", "destino": "Lisboa", "dataInicio": "2025-03-01", "dataFim": "2025-03-05" }'
  ```

## Persistência local
- `roteiros.json` é criado automaticamente caso não exista.
- Como é armazenamento em arquivo, o app precisa de permissão de escrita no diretório.
- Para limpar dados basta excluir o arquivo com a API parada (não há migrações).

## Dicas de produção
- Configure variáveis de ambiente no serviço escolhido (Render, Railway, etc.).
- Use `gunicorn` apontando para `app:app` e um reverso com HTTPS.
- Proteja o endpoint de geração (rate limiting / chave interna) se o front for público para evitar abuso e custos.

Boa viagem! ✈️
