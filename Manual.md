# Manual de Execução e Estrutura do Projeto — TCC (Otimização Projeto MARIA)
 
Este guia resume a estrutura de pastas e arquivos do diretório `TCC`, explica a função de cada script Python e apresenta a ordem exata de execução no terminal do VS Code (Linux).
 
---
 
## 1. Como Preparar o Terminal e Rodar (Passo a Passo)
 
1. Abra o terminal integrado no VS Code (`Ctrl + '`) na raiz da pasta `TCC`.
2. Ative o ambiente virtual isolado (`.venv`) e entre na pasta dos códigos principais (`Projeto_TCC`):
```bash
source .venv/bin/activate
cd Projeto_TCC
```
 
   > Confirme se `(.venv)` apareceu no início da linha do terminal.
 
3. Ordem de execução dos scripts (caso precise reproduzir todo o pipeline do zero):
```bash
# Passo 1: Organiza os TXTs brutos do NSL-KDD em CSVs com cabeçalho e adapta ao formato MARIA
python3 preparar_base.py
 
# Passo 2: Extrai os pesos (Feature Importance) do modelo original da autora
python3 ver_pesos.py
 
# Passo 3: Testa o modelo original (catboos_model.joblib) sobre o NSL-KDD adaptado e calcula métricas
python3 avaliar_maria_nslkdd.py
 
# Passo 4: Limpa o NSL-KDD, ranqueia as 40 features e testa o CatBoost reduzindo colunas (40 -> 15 -> 10 -> 6)
python3 otimizar_colunas_catboost.py
```
 
---
 
## 2. Estrutura de Pastas e Arquivos da Raiz (`TCC/`)
 
| Item | Descrição |
|------|-----------|
| `.venv/` | Ambiente virtual Python isolado com todas as bibliotecas instaladas (`catboost`, `pandas`, `scikit-learn`, `joblib`, `numpy`). |
| `envio_modelo_maria/` | Arquivos originais enviados pela autora do projeto MARIA (mantidos intactos como referência). |
| `Projeto_TCC/` | Diretório principal de desenvolvimento com nossos scripts, datasets e resultados. |
| `Projeto MARIA.pdf` | Artigo base do projeto original utilizado como referência teórica. |
| `relatorio15.11.md` | Relatório técnico completo documentando os experimentos com NSL-KDD e a redução de colunas. |
| `reunioes-tarefas` | Histórico cronológico das decisões e metas definidas nas reuniões de orientação. |
| `requirements.txt` | Lista de dependências Python do projeto. |
| `.gitignore` | Configurado para impedir o envio do `.venv` e arquivos pesados/temporários ao GitHub. |
 
---
 
## 3. Manual dos Scripts e Arquivos (`Projeto_TCC/`)
 
### 3.1 Scripts Python (`.py`)
 
#### `preparar_base.py`
 
**O que faz:** Lê os arquivos brutos sem cabeçalho (`KDDTrain+.txt` e `KDDTest+.txt`) dentro de `datasets/`, insere os nomes oficiais das 43 colunas do NSL-KDD e salva os CSVs completos. Também gera a versão adaptada para as 8 entradas do modelo original (`kdd_remap_para_maria.csv`), preenchendo os campos ausentes (`SrcPkts`, `DstPkts`, `sTtl`, `dTtl`) com valores padrão neutros (`1` e `64`).
 
#### `ver_pesos.py`
 
**O que faz:** Carrega o modelo pré-treinado original (`catboos_model.joblib`) e extrai a importância estatística (*Feature Importance*) de cada atributo, mostrando quais colunas mais pesam na decisão da IA.
 
#### `exemplo_predicao.py`
 
**O que faz:** Script de inferência adaptado do original para testar predições individuais ou em lote usando o `catboos_model.joblib`.
 
#### `gerar_dataset.py`
 
**O que faz:** Gera fluxos de rede sintéticos (benignos e ataques simulados como *Port Scan*) para testar o comportamento e os limites de detecção do modelo original.
 
#### `avaliar_maria_nslkdd.py`
 
**O que faz:** Executa o modelo pré-treinado original (`catboos_model.joblib`) sobre o conjunto de teste do NSL-KDD adaptado (`kdd_remap_para_maria.csv`), salva as predições em `resultado_nslkdd.csv` e cruza com o gabarito real (`KDDTest_completo.csv`) para calcular Acurácia, Precisão, Recall, F1-Score e Matriz de Confusão.
 
#### `otimizar_colunas_catboost.py`
 
**O que faz:** Script principal de otimização. Remove colunas mortas/constantes do NSL-KDD (`num_outbound_cmds`), treina um CatBoost completo (40 colunas) para ranquear os atributos mais relevantes (`ranking_catboost_nslkdd.csv`) e realiza o benchmark comparando acurácia, precisão, recall, F1-score e tempo de inferência ao cortar as features para 15, 10 e 6 colunas.
 
### 3.2 Modelos, Dados e Saídas Geradas
 
| Item | Descrição |
|------|-----------|
| `datasets/` | Subpasta contendo os arquivos brutos (`.txt`) e tratados (`KDDTrain_completo.csv`, `KDDTest_completo.csv`) do NSL-KDD. |
| `catboos_model.joblib` | Arquivo binário do modelo CatBoost pré-treinado original do projeto MARIA. |
| `kdd_remap_para_maria.csv` | Base de teste NSL-KDD formatada com as 8 colunas esperadas pelo modelo original. |
| `resultado_nslkdd.csv` | Saída contendo as predições geradas pelo modelo original sobre o NSL-KDD. |
| `ranking_catboost_nslkdd.csv` | Tabela gerada com o peso percentual de importância de cada uma das 40 colunas úteis do NSL-KDD no CatBoost. |
| `catboost_info/` | Pasta de logs internos gerada automaticamente pela biblioteca CatBoost durante o treinamento. |
 
