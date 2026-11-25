#!/usr/bin/env bash
# Reproduz localmente as mesmas etapas do .github/workflows/ci.yml.
# Uso: bash scripts/pipeline_local.sh
set -u
cd "$(dirname "$0")/.."

echo "== PIPELINE LOCAL DocSocios Lite =="
echo "commit: $(git rev-parse --short HEAD 2>/dev/null)  branch: $(git branch --show-current 2>/dev/null)"
echo

echo "## JOB testes"
echo "-> Verificar sintaxe"
if ! python3 -m compileall -q app tests run.py; then
  echo "RESULTADO: FALHA na verificação de sintaxe"; echo "## JOB entrega: BLOQUEADO (skipped)"; exit 1
fi
echo "-> Executar testes automatizados"
mkdir -p reports
if ! python3 -m pytest -v --junitxml=reports/junit.xml; then
  echo
  echo "RESULTADO JOB testes: FALHA"
  echo "## JOB entrega: BLOQUEADO (skipped) - pacote NÃO foi gerado"
  exit 1
fi
echo "RESULTADO JOB testes: SUCESSO"
echo

echo "## JOB entrega"
mkdir -p dist
VERSAO="$(date +%Y.%m.%d)-$(git rev-parse --short=7 HEAD 2>/dev/null || echo local)"
echo "$VERSAO" > VERSION
python3 - "$VERSAO" <<'PY'
import sys, zipfile, pathlib
v = sys.argv[1]
out = pathlib.Path("dist") / f"docsocios-lite-{v}.zip"
with zipfile.ZipFile(out, "w") as z:
    for p in ["run.py", "requirements.txt", "README.md", "VERSION"]:
        if pathlib.Path(p).exists():
            z.write(p)
    for f in pathlib.Path("app").rglob("*"):
        if f.is_file() and "__pycache__" not in f.parts:
            z.write(f)
print(f"pacote gerado: {out}")
PY
rm -f VERSION
echo "RESULTADO JOB entrega: SUCESSO"
