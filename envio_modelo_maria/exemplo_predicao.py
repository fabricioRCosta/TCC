"""Inferencia local com o modelo MARIA; execute --help para ver as opcoes."""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


PASTA = Path(__file__).resolve().parent
NUMERICAS = ['Dur', 'SrcBytes', 'DstBytes', 'SrcPkts', 'DstPkts', 'sTtl', 'dTtl']
PROTOCOLOS = ['icmp', 'ipv6-icmp', 'llc', 'lldp', 'sctp', 'tcp', 'udp']
ATRIBUTOS = NUMERICAS + [f'Proto_{p}' for p in PROTOCOLOS]


def preparar_entrada(dados, modelo):
    """Converte fluxos com Proto textual para os 14 atributos do modelo."""
    faltantes = set(NUMERICAS + ['Proto']) - set(dados.columns)
    if faltantes:
        raise ValueError(f'Colunas obrigatorias ausentes: {sorted(faltantes)}')
    if dados.empty:
        raise ValueError('O CSV precisa conter ao menos um fluxo.')
    if list(modelo.feature_names_) != ATRIBUTOS:
        raise ValueError('O modelo informado tem atributos diferentes dos esperados.')
    numericos = dados[NUMERICAS].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(numericos.to_numpy(dtype=float)).all():
        raise ValueError('Preencha todos os campos numericos com valores finitos.')
    if (numericos < 0).any().any():
        raise ValueError('Os campos numericos nao podem ser negativos.')
    contagens = numericos[NUMERICAS[1:]]
    if (contagens % 1 != 0).any().any():
        raise ValueError('Bytes, pacotes e TTL devem ser inteiros.')
    if (numericos[['sTtl', 'dTtl']] > 255).any().any():
        raise ValueError('TTL deve estar entre 0 e 255.')
    protocolos = dados['Proto'].astype('string').str.strip().str.lower()
    if not protocolos.isin(PROTOCOLOS).all():
        raise ValueError(f'Proto deve ser um destes valores: {PROTOCOLOS}')
    entrada = numericos.copy()
    for protocolo in PROTOCOLOS:
        entrada[f'Proto_{protocolo}'] = (protocolos == protocolo).astype(int)
    return entrada.loc[:, modelo.feature_names_]


def predizer(modelo, dados):
    """Reutilize o modelo carregado para classificar um lote de fluxos."""
    entrada = preparar_entrada(dados, modelo)
    classes = np.asarray(modelo.predict(entrada, thread_count=1)).reshape(-1)
    probabilidades = modelo.predict_proba(entrada, thread_count=1)
    resultado = dados.reset_index(drop=True).copy()
    resultado['Predicao'] = classes
    for indice, classe in enumerate(modelo.classes_):
        resultado[f'Prob_{classe}'] = probabilidades[:, indice]
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo', type=Path, default=PASTA / 'catboos_model.joblib')
    parser.add_argument('--entrada', type=Path, default=PASTA / 'exemplo_fluxo_ataque.csv')
    parser.add_argument('--saida', type=Path, help='CSV opcional com classes e probabilidades')
    args = parser.parse_args()
    try:
        # Carregue apenas arquivos joblib de uma origem confiavel.
        modelo = joblib.load(args.modelo)
        dados = pd.read_csv(args.entrada)
        resultado = predizer(modelo, dados)
        if args.saida:
            resultado.to_csv(args.saida, index=False)
        print(json.dumps(resultado.to_dict(orient='records'), ensure_ascii=True, indent=2))
    except (OSError, ValueError, TypeError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
