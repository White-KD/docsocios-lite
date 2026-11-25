# DocSócios Lite
## Rafael Cegatti RA: 2337576


Versão didática e simplificada do **DocSócios**, um gestor de escalas de plantões médicos.
Projeto acadêmico para demonstrar controle de versão, integração contínua, testes automatizados
e entrega com bloqueio em caso de falha.

## Funcionalidades

| # | Funcionalidade | Regra de negócio |
|---|----------------|------------------|
| 1 | **Cadastro de médicos** | Nome obrigatório; CRM no formato `12345-PR` (normaliza `12345/pr`); CRM não pode repetir |
| 2 | **Escala de plantões** | Data, turno (D/N) e valor; **bloqueia conflito** (mesma data e turno já ocupados); filtro por mês |
| 3 | **Repasse mensal** | Soma os plantões do mês por médico e desconta a taxa administrativa (padrão 10%) |

## Como executar

Requisitos: Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Abra http://127.0.0.1:5000 no navegador. Os dados ficam em `docsocios.db` (SQLite, criado automaticamente).

### API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/saude` | Verificação de saúde |
| GET/POST | `/api/medicos` | Lista / cadastra médico `{"nome","crm"}` |
| GET/POST | `/api/plantoes?mes=AAAA-MM` | Lista / registra plantão `{"medico_id","data","turno","valor"}` |
| GET | `/api/repasse?mes=AAAA-MM&taxa=10` | Repasse do mês por médico |

## Testes automatizados

```bash
python -m pytest -v
```

11 testes em `tests/` (médicos, plantões, repasse, saúde/interface).

## Pipeline CI/CD (`.github/workflows/ci.yml`)

Disparado em todo `push`, em `pull_request` para `main` e manualmente.

1. **testes** — instala dependências, verifica sintaxe (`compileall`) e roda o `pytest` (gera `junit.xml`).
2. **entrega** — `needs: testes`: só executa se todos os testes passarem. Gera o pacote
   `docsocios-lite-<data>-<sha>.zip` e publica como artefato. Na `main`, se o segredo
   `RENDER_DEPLOY_HOOK` existir, dispara o deploy no Render.

Se um teste falhar, o job **entrega fica _skipped_**: nenhum pacote é gerado (entrega bloqueada).

Para rodar as mesmas etapas localmente: `bash scripts/pipeline_local.sh`.

## Fluxo de branches

`main` protegida; cada funcionalidade em `feature/*`, integrada por merge (`--no-ff`) após o pipeline verde:
`feature/cadastro-medicos` → `feature/escala-plantoes` → `feature/repasse-medicos` → `feature/interface-web`.

Na `feature/repasse-medicos` ocorreu uma falha real: a taxa de 10 foi usada como fração
(`bruto * (1 - 10)`), gerando repasse negativo (−R$ 18.000 em vez de R$ 1.800). O teste
`test_repasse_soma_plantoes_do_mes_e_desconta_taxa_de_10_porcento` detectou o erro, a entrega
foi bloqueada e o commit `fix(repasse)` corrigiu. Logs em `evidencias/`.

### Reproduzir a falha no GitHub Actions

```bash
git remote add origin https://github.com/<usuario>/docsocios-lite.git
git push -u origin --all
bash scripts/demo_falha_github.sh
```
