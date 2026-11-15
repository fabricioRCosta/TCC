# Relatório Técnico — Experimentos NSL-KDD e Otimização do Modelo CatBoost

**Projeto:** Evolução do Sistema MARIA (Detecção e Prevenção de Intrusões)  
**Etapa:** Análise da Base NSL-KDD, Teste de Compatibilidade no Modelo Original e Redução de Dimensionalidade (*Feature Selection*)

---

## 1. Contexto e Objetivo da Etapa

Com base nas diretrizes definidas nas reuniões de orientação (`10/11` e `13/11`), o foco técnico desta etapa foi direcionado para a **otimização do modelo preditivo**, buscando **reduzir o número de colunas do arquivo `.csv` de entrada mantendo (ou superando) a precisão original**, antes de prosseguir para o desenvolvimento da API em FastAPI.

Para embasar e validar a técnica de seleção de atributos em um benchmark consolidado da literatura, adotou-se a base de dados **NSL-KDD** (Tavallaee et al., 2009), que corrige o viés estatístico do KDD'99 original ao eliminar **78,05%** de registros duplicados no conjunto de treino e **75,15%** no conjunto de teste.

---

## 2. Organização da Estrutura do Projeto

Para manter a rastreabilidade entre os arquivos originais fornecidos pela autora do projeto MARIA e os novos scripts desenvolvidos para o TCC, o diretório local foi estruturado em duas frentes isoladas:

* `envio_modelo_maria/`: Arquivos originais intactos (`exemplo_predicao.py`, `exemplo_fluxos.csv`, `exemplo_fluxo_ataque.csv`, `README.md`, `SHA256SUMS.txt`).
* `Projeto_TCC/`:
  * `datasets/`: Bases brutas e processadas (`KDDTrain+.txt`, `KDDTest+.txt`, `KDDTrain_completo.csv`, `KDDTest_completo.csv`, `meu_dataset_IA.csv`).
  * Scripts de processamento, avaliação e otimização (`preparar_base.py`, `avaliar_maria_nslkdd.py`, `otimizar_colunas_catboost.py`, `ver_pesos.py`, `gerar_dataset.py`).
  * Artefatos gerados (`catboos_model.joblib`, `nslkdd_para_maria.csv`, `resultado_nslkdd.csv`, `ranking_catboost_nslkdd.csv`).

---

## 3. Aquisição e Transformação da Base NSL-KDD

### 3.1. Download dos Arquivos Oficiais
Foram obtidos os dois conjuntos completos oficiais do NSL-KDD em formato texto bruto (sem cabeçalho):
* **`KDDTrain+.txt`**: 125.973 registros (conjunto de treinamento).
* **`KDDTest+.txt`**: 22.544 registros (conjunto de teste).

### 3.2. Estruturação e Inclusão de Cabeçalhos (`preparar_base.py`)
Os arquivos brutos possuem **43 colunas** (41 atributos de rede + `label` indicando o tipo de tráfego/ataque + `difficulty_level` de 0 a 21). Foi desenvolvido o script `preparar_base.py` para atribuir os nomes oficiais de cada coluna e converter ambos os arquivos para o formato `.csv` estruturado:
* `datasets/KDDTrain_completo.csv` `(125.973 x 43)`
* `datasets/KDDTest_completo.csv` `(22.544 x 43)`

---

## 4. Teste de Compatibilidade no Modelo Original MARIA

### 4.1. Análise de Lacuna de Atributos (*Feature Gap*)
O modelo original do MARIA (`catboos_model.joblib`) foi treinado sobre fluxos de rede IoT (IoT-23 + 5G-NIDD) e exige exatamente **8 colunas de entrada** (`Dur`, `SrcBytes`, `DstBytes`, `SrcPkts`, `DstPkts`, `sTtl`, `dTtl`, `Proto`).

Ao mapear o NSL-KDD para o esquema do MARIA, identificou-se uma divergência estrutural causada pelas diferentes ferramentas de captura de pacotes utilizadas na criação de cada base:

| Coluna MARIA | Coluna NSL-KDD | Status no NSL-KDD | Peso no `catboos_model.joblib` |
| :--- | :--- | :--- | :---: |
| **`Dur`** | `duration` | Mapeamento direto | 19,46% |
| **`SrcBytes`** | `src_bytes` | Mapeamento direto | 16,98% |
| **`DstBytes`** | `dst_bytes` | Mapeamento direto | 4,36% |
| **`Proto`** | `protocol_type` | Mapeamento direto (`tcp`, `udp`, `icmp`) | ~11,11% |
| **`SrcPkts`** | *Inexistente* | **Ausente** (preenchido com `1`) | 21,05% |
| **`DstPkts`** | *Inexistente* | **Ausente** (preenchido com `1`) | 1,50% |
| **`sTtl`** | *Inexistente* | **Ausente** (preenchido com `64`) | 16,95% |
| **`dTtl`** | *Inexistente* | **Ausente** (preenchido com `64`) | 8,60% |

> **Observação Crítica:** As 4 colunas ausentes no NSL-KDD (`SrcPkts`, `DstPkts`, `sTtl`, `dTtl`) somam **48,10% do peso de decisão** do modelo pré-treinado da autora.

### 4.2. Execução e Avaliação (`avaliar_maria_nslkdd.py`)
Para testar empiricamente o comportamento do modelo original diante do NSL-KDD, gerou-se o arquivo `nslkdd_para_maria.csv` (preenchendo as lacunas com valores padrão neutros) e executou-se a inferência sobre todos os 22.544 fluxos de teste, salvando as predições em `resultado_nslkdd.csv` e comparando-as com o gabarito binário (`0 = Benigno`, `1 = Ataque`).

#### Resultados Obtidos (Modelo Original MARIA no `KDDTest+`):
* **Acurácia (Accuracy):** `43,08%`
* **Precisão (Precision):** `0,00%`
* **Recall (Taxa de Detecção):** `0,00%`
* **F1-Score:** `0,00%`

#### Matriz de Confusão:
* **Verdadeiros Benignos (VN):** `9.711` | **Falsos Alarmes (FP):** `0`
* **Ataques Perdidos (FN):** `12.833` | **Ataques Detectados (VP):** `0`

#### Diagnóstico Técnico:
O modelo original classificou **100% dos 22.544 registros como `Benign`**. A acurácia de 43,08% corresponde apenas à proporção natural de tráfego normal presente na base de teste ($9.711 / 22.544$). Isso comprova empiricamente dois pontos fundamentais para o TCC:
1. O modelo pré-treinado original é altamente dependente de métricas de camada de rede (`sTtl` e `SrcPkts`) para identificar assinaturas de ataque.
2. Devido à diferença de domínio (*Domain Shift*) e de atributos entre bases IoT e bases corporativas clássicas, não basta adaptar o CSV de entrada — é necessário realizar a limpeza e o retreinamento do algoritmo CatBoost diretamente sobre os atributos da base alvo.

---

## 5. Limpeza de Dados e Seleção de Atributos (*Feature Selection*)

Com o script `otimizar_colunas_catboost.py`, realizou-se o processo de limpeza e engenharia de atributos sobre o conjunto `KDDTrain_completo.csv` (mantendo o `KDDTest_completo.csv` estritamente isolado para evitar vazamento de dados / *Data Leakage*):

1. **Remoção de Metadados:** Exclusão da coluna `difficulty_level` (índice interno de benchmark, inexistente em tráfego real).
2. **Remoção de Colunas Constantes (Variância Zero):** Identificação e exclusão automática da coluna `num_outbound_cmds`, que apresenta valor `0` em 100% dos registros, restando **40 atributos úteis**.
3. **Extração de Importância (*Feature Importance*):** Treinamento de um modelo CatBoost baseline (300 iterações) com todas as 40 colunas úteis para ranquear o peso estatístico de cada atributo.

### Top 15 Colunas Mais Relevantes no NSL-KDD (CatBoost)

| Posição | Coluna | Peso (%) | Descrição do Atributo |
| :---: | :--- | :---: | :--- |
| **1** | `src_bytes` | 29,49% | Quantidade de bytes enviados da origem para o destino |
| **2** | `dst_bytes` | 10,43% | Quantidade de bytes retornados do destino para a origem |
| **3** | `service` | 9,96% | Serviço de rede na porta destino (`http`, `private`, `dns`, etc.) |
| **4** | `protocol_type` | 8,01% | Protocolo da camada de transporte (`tcp`, `udp`, `icmp`) |
| **5** | `srv_count` | 6,63% | Conexões para o mesmo serviço nos últimos 2 segundos |
| **6** | `count` | 6,12% | Conexões para o mesmo host destino nos últimos 2 segundos |
| **7** | `dst_host_srv_count` | 3,75% | Conexões acumuladas para o mesmo host destino e serviço |
| **8** | `dst_host_same_srv_rate` | 3,61% | Taxa de conexões no mesmo serviço do host destino |
| **9** | `dst_host_diff_srv_rate` | 3,35% | Taxa de conexões em serviços diferentes (indicador de *Port Scan*) |
| **10** | `same_srv_rate` | 2,86% | Proporção de conexões no mesmo serviço na janela de 2s |
| **11** | `dst_host_same_src_port_rate` | 2,33% | Taxa de conexões originadas da mesma porta de origem |
| **12** | `dst_host_srv_serror_rate` | 2,19% | Taxa de erros de sincronização (SYN) no mesmo serviço |
| **13** | `hot` | 2,16% | Indicadores de ações sensíveis na sessão (acesso a diretórios/programas) |
| **14** | `dst_host_rerror_rate` | 1,84% | Taxa de conexões rejeitadas (`REJ`) pelo host destino |
| **15** | `dst_host_count` | 1,70% | Total de conexões destinadas ao mesmo host na janela histórica |

---

## 6. Resultados do Benchmark de Redução de Colunas

Foram treinados e avaliados quatro modelos CatBoost com diferentes cortes de dimensionalidade (`40`, `15`, `10` e `6` colunas) para medir o impacto na qualidade da classificação e na latência de inferência sobre os 22.544 registros do `KDDTest+`:

| Qtd. Colunas | Redução de Atributos | Acurácia | Precisão | Recall | F1-Score | Tempo de Predição (22.544 fluxos) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **40 (Completo)** | 0% (Baseline) | 77,24% | 96,76% | 62,10% | 75,65% | 73,67 ms |
| **15 (Top 15)** | **-62,5%** | **79,60%** | **96,77%** | 66,37% | **78,74%** | 76,75 ms |
| **10 (Top 10)** | **-75,0%** | 78,59% | 96,70% | 64,60% | 77,45% | **17,44 ms** |
| **6 (Top 6)** | **-85,0%** | 78,21% | 92,60% | **67,08%** | 77,80% | 23,14 ms |

### Conclusões Extraídas do Experimento
1. **Aumento de Precisão com Menos Colunas:** O corte das 25 colunas de menor peso (de 40 para 15 atributos) eliminou ruído e reduziu o *overfitting*, elevando a acurácia de **77,24% para 79,60%** (+2,36%) e o F1-Score de **75,65% para 78,74%** (+3,09%).
2. **Ganho Expressivo de Desempenho (Latência):** Com apenas **10 colunas** (redução de 75% do tamanho do CSV), o modelo manteve a acurácia acima do baseline completo (**78,59%**) e reduziu o tempo total de inferência de **73,67 ms para 17,44 ms** (ganho de **4,2x em velocidade**), tornando-o altamente viável para operação em tempo real na futura API FastAPI.
3. **Resiliência com Atributos Mínimos:** Mesmo operando com apenas **6 colunas** básicas de tráfego, o modelo alcançou o maior índice de **Recall (67,08%)** entre todos os cenários testados.

---

## 7. Próximos Passos Planejados

* **Persistência do Modelo Otimizado:** Exportar o novo modelo CatBoost reduzido (15 ou 10 colunas) em formato `.joblib` e gerar os respectivos datasets enxutos (`KDDTrain_reduzido.csv` e `KDDTest_reduzido.csv`).
* **Avaliação junto ao Orientador (Reunião de Sexta-feira):** Apresentar a tabela comparativa de redução de dimensionalidade e validar a escolha final do conjunto de atributos (15 colunas para máxima acurácia vs. 10 colunas para menor latência), além de avaliar a replicação dessa mesma metodologia em uma amostra das bases originais do MARIA (IoT-23 + 5G-NIDD).
* **Desenvolvimento da API / IPS:** Integrar o modelo otimizado final a um microsserviço de alta performance em **FastAPI** para detecção e bloqueio ativo de intrusões.