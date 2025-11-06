from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
from uuid import uuid4

#   CONFIG .env + Gemini
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

print("✅ GEMINI_API_KEY lida:", os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

#   ROTA: GERAR ROTEIRO COM IA
@app.route("/gerar-roteiro", methods=["POST"])
def gerar_roteiro():
    import json, re
    try:
        data = request.json

        nome = data.get("nome")
        destino = data.get("destino")
        dataInicio = data.get("dataInicio")
        dataFim = data.get("dataFim")
        observacoes = data.get("observacoes", "")

        if not nome or not destino or not dataInicio or not dataFim:
            return jsonify({"erro": "Campos obrigatórios: nome, destino, dataInicio, dataFim"}), 400

        prompt = f"""
Crie um roteiro de viagem **em JSON puro** (sem textos fora do JSON).

Dados do usuário:
- Nome do roteiro: {nome}
- Destino: {destino}
- Data de início: {dataInicio}
- Data de término: {dataFim}
- Observações: {observacoes}

Regras:
- Divida por dias, com a data de cada dia entre {dataInicio} e {dataFim}.
- >= 3 atividades/dia, com hora aproximada e pequena descrição.
- Otimize deslocamentos (lugares próximos no mesmo dia).
- Se exigir reserva/ingresso, indique.
- No fim, inclua um resumo com custo estimado por pessoa (BRL), transporte sugerido e dicas práticas.

Formato **OBRIGATÓRIO** (JSON):
{{
  "nome": "{nome}",
  "destino": "{destino}",
  "dias": [
    {{
      "data": "YYYY-MM-DD",
      "atividades": [
        {{ "hora": "HH:MM", "descricao": "Atividade" }}
      ]
    }}
  ],
  "resumo": {{
    "custoEstimado": "R$ valor",
    "transporte": "texto",
    "dicas": "texto"
  }}
}}
"""

        model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        modelo = genai.GenerativeModel(model_name)

        try:
            resposta = modelo.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
        except Exception:
            resposta = modelo.generate_content(prompt)

        raw = getattr(resposta, "text", "") or ""

        print("\n--- GEMINI RAW (primeiros 500 chars) ---\n", raw[:500], "\n----------------------------------------\n")

        def extract_json(s: str):
            try:
                return json.loads(s)
            except Exception:
                pass

            fence = re.search(r"```json(.*?)```", s, flags=re.S|re.I)
            if fence:
                try:
                    return json.loads(fence.group(1).strip())
                except Exception:
                    pass

            braces = re.search(r"\{.*\}", s, flags=re.S)
            if braces:
                candidate = braces.group(0)
                candidate = re.sub(r",\s*([\]\}])", r"\1", candidate)
                try:
                    return json.loads(candidate)
                except Exception:
                    pass

            return None

        parsed = extract_json(raw)

        if not parsed or not isinstance(parsed, dict):
            parsed = {
                "nome": nome,
                "destino": destino,
                "dias": [],
                "resumo": {
                    "custoEstimado": "Não informado",
                    "transporte": "Não informado",
                    "dicas": "Nenhuma dica disponível"
                },
                "_raw": raw  
            }

        parsed.setdefault("nome", nome)
        parsed.setdefault("destino", destino)
        parsed.setdefault("dias", [])
        parsed.setdefault("resumo", {})
        parsed["resumo"].setdefault("custoEstimado", "Não informado")
        parsed["resumo"].setdefault("transporte", "Não informado")
        parsed["resumo"].setdefault("dicas", "Nenhuma dica disponível")

        return jsonify(parsed)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

#   ROTAS: SALVAR / LISTAR / EXCLUIR ROTEIROS
ROTEIROS_FILE = "roteiros.json"

def carregar_roteiros():
    if not os.path.exists(ROTEIROS_FILE):
        with open(ROTEIROS_FILE, "w") as f:
            json.dump([], f)
    with open(ROTEIROS_FILE, "r") as f:
        return json.load(f)

def salvar_roteiros(lista):
    with open(ROTEIROS_FILE, "w") as f:
        json.dump(lista, f, indent=4)

@app.route("/roteiros", methods=["POST"])
def salvar_roteiro():
    data = request.json
    roteiros = carregar_roteiros()

    novo = {
        "id": str(uuid4()),
        "title": data.get("title"),
        "destination": data.get("destination"),
        "duration": data.get("duration"),
        "content": data.get("content"),
        "createdAt": data.get("createdAt"),
    }

    roteiros.append(novo)
    salvar_roteiros(roteiros)

    return jsonify({"ok": True, "roteiro": novo}), 201


@app.route("/roteiros", methods=["GET"])
def listar_roteiros():
    roteiros = carregar_roteiros()
    return jsonify(roteiros), 200


@app.route("/roteiros/<id>", methods=["DELETE"])
def excluir_roteiro(id):
    roteiros = carregar_roteiros()
    roteiros = [r for r in roteiros if r["id"] != id]
    salvar_roteiros(roteiros)
    return jsonify({"ok": True}), 200



#   STATUS
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "API funcionando!"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)