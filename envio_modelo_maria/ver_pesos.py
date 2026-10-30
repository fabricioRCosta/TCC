import joblib
import pandas as pd

# Carregar o ficheiro do modelo na memória
modelo = joblib.load('catboos_model.joblib')

# Extrair as métricas internas da Árvore de Decisão (CatBoost)
pesos = modelo.feature_importances_
nomes = modelo.feature_names_

# Estruturar os dados numa tabela ordenada
df_pesos = pd.DataFrame({'Atributo': nomes, 'Impacto_na_Decisao_(%)': pesos})
df_pesos = df_pesos.sort_values(by='Impacto_na_Decisao_(%)', ascending=False)

# Formatar para exibição limpa no terminal
df_pesos['Impacto_na_Decisao_(%)'] = df_pesos['Impacto_na_Decisao_(%)'].round(4).astype(str) + ' %'

print("\n=== RAIOS-X DO MODELO MARIA ===")
print("Peso estatístico de cada coluna para detetar anomalias:\n")
print(df_pesos.to_string(index=False))
print("===============================\n")