# Modelo treinado do trabalho MARIA

Este pacote disponibiliza o modelo para inferência. A base de treinamento ainda não está pública e não está incluída. O nome original `catboos_model.joblib` foi preservado.

## Execução

Ambiente de referência: Python 3.10.7. As versões diretas das bibliotecas estão fixadas em `requirements.txt`.

Extraia o ZIP, abra o terminal na pasta extraída e execute:

```bash
python -m venv .venv
```

Ative o ambiente no Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências e execute o exemplo:

```bash
python -m pip install -r requirements.txt
python exemplo_predicao.py
python exemplo_predicao.py --entrada meus_fluxos.csv --saida predicoes.csv
```

O script imprime JSON no terminal; `--saida` também grava um CSV. O modelo e o CSV de exemplo são localizados em relação ao script. Caminhos fornecidos como argumentos são relativos ao diretório de execução.

## Dados de entrada

Use CSV separado por vírgulas, com cabeçalho e ponto como separador decimal. Cada linha representa um fluxo de rede. O arquivo `exemplo_fluxos.csv` contém somente dois registros sintéticos, sem rótulos esperados; não é uma amostra da base e não serve para medir acurácia.

| Campo | Conteúdo |
| --- | --- |
| `Dur` | Duração do fluxo; o coletor local do projeto usa segundos. |
| `SrcBytes` | Quantidade de bytes no sentido de origem. |
| `DstBytes` | Quantidade de bytes no sentido de resposta. |
| `SrcPkts` | Quantidade de pacotes no sentido de origem. |
| `DstPkts` | Quantidade de pacotes no sentido de resposta. |
| `sTtl` | TTL associado à origem. |
| `dTtl` | TTL associado à resposta. |
| `Proto` | `icmp`, `ipv6-icmp`, `llc`, `lldp`, `sctp`, `tcp` ou `udp`. |

Os valores numéricos devem ser finitos e não negativos; bytes, pacotes e TTL devem ser inteiros, e TTL deve estar entre 0 e 255. Dados ausentes e protocolos fora da lista são rejeitados. Colunas extras são preservadas na saída, mas não entram no modelo. IPs e rótulos não são necessários para a inferência.

O script converte `Proto` em sete indicadores 0/1 e organiza as 14 colunas na ordem registrada no próprio modelo. Não aplica normalização nem ajusta imputação nos dados de teste. Não foram encontrados no repositório um pipeline de treinamento ou estatísticas de imputação persistidas; por isso, o exemplo exige entradas completas e segue a estrutura de inferência da API local para esses valores. Não substitua valores desconhecidos por zero sem uma justificativa metodológica.

A correspondência dos nomes das colunas não garante equivalência dos dados: confira unidades, contagem de bytes, direção do fluxo, janela de agregação e forma de obter o TTL antes de comparar resultados. O treinamento completo não foi reproduzido a partir deste pacote.

## Saída e integração

As classes foram conferidas no arquivo do modelo: `Benign`, `DDoS`, `HTTPFlood`, `Okiru`, `PartOfAHorizontalPortScan` e `UDPFlood`. A saída inclui `Predicao` e uma coluna `Prob_<classe>` para cada classe. As probabilidades não constituem garantia de acerto ou medida validada de confiança.

Para incorporar ao seu código, carregue o modelo uma vez e reutilize a função:

```python
import joblib
import pandas as pd
from exemplo_predicao import predizer

modelo = joblib.load('catboos_model.joblib')
fluxos = pd.read_csv('meus_fluxos.csv')
resultado = predizer(modelo, fluxos)
print(resultado['Predicao'].tolist())
```

A função é síncrona. Na arquitetura assíncrona, execute a inferência em workers com concorrência limitada para não ocupar o loop de eventos. O exemplo usa uma thread por chamada do CatBoost e faz chamadas separadas para classe e probabilidades; considere esse custo ao medir latência. Meça carregamento, preparação e inferência separadamente, faça aquecimento e registre hardware, versões, tamanho dos lotes e concorrência.

O exemplo realiza classificação local. A implementação e avaliação de resposta ativa ficam a cargo da integração do aluno. Para avaliar qualidade de classificação são necessários dados rotulados representativos; para novo treinamento é necessária uma base de treinamento.

Carregue arquivos `.joblib` apenas de origem confiável, pois a desserialização pode executar código. O arquivo `SHA256SUMS.txt` registra o hash do modelo para conferir a integridade da cópia.

Ao usar este material no TCC ou em publicações, cite o artigo MARIA.
