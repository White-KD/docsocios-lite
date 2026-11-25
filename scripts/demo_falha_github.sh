#!/usr/bin/env bash
# Reproduz no GitHub Actions o ciclo: SUCESSO -> FALHA (entrega bloqueada) -> CORREÇÃO -> SUCESSO.
# Pré-requisito: o repositório já ter o remoto "origin" e a main já enviada (git push -u origin main).
# Uso: bash scripts/demo_falha_github.sh
set -euo pipefail
cd "$(dirname "$0")/.."

FIX=$(git log --format=%H --grep="^fix(repasse)" -n 1)
[ -n "$FIX" ] || { echo "Commit de correção não encontrado"; exit 1; }

git switch main
git switch -c demo/falha-pipeline

# 1) Reintroduz o erro real (taxa em % tratada como fração) desfazendo a correção
git revert --no-edit "$FIX"
git commit --amend -m "demo: reintroduz erro no cálculo do repasse (taxa 10 tratada como 1000%)"
git push -u origin demo/falha-pipeline
echo ">> Abra a aba Actions: o job 'testes' deve FALHAR e o job 'entrega' ficar SKIPPED (bloqueado)."
echo ">> (Opcional) Abra um Pull Request de demo/falha-pipeline para main e tire print do merge bloqueado."
read -rp "Pressione ENTER depois de registrar os prints da falha... "

# 2) Corrige novamente
git revert --no-edit HEAD
git commit --amend -m "fix(repasse): corrige novamente a conversão da taxa percentual"
git push
echo ">> Nova execução deve ficar VERDE nos dois jobs (testes e entrega)."
