import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# 1. Carrega o modelo e o CSV adaptado (ambos na pasta atual Projeto_TCC)
modelo = joblib.load("catboos_model.joblib")
df_entrada = pd.read_csv("nslkdd_para_maria.csv")

# 2. Aplica o mesmo pré-processamento do script original (One-Hot Encoding em Proto)
X = pd.get_dummies(df_entrada, columns=["Proto"])
for col in modelo.feature_names_:
    if col not in X.columns:
        X[col] = 0
X = X[modelo.feature_names_]

# 3. Executa a predição e salva o resultado_nslkdd.csv
predicoes = modelo.predict(X).ravel()
df_saida = df_entrada.copy()
df_saida["Predicao"] = predicoes
df_saida.to_csv("resultado_nslkdd.csv", index=False)
print("Arquivo 'resultado_nslkdd.csv' gerado com sucesso!")

# 4. Carrega o gabarito real dentro da subpasta datasets/
df_real = pd.read_csv("datasets/KDDTest_completo.csv")

# 5. Converte para classificação binária: 0 = Benigno, 1 = Ataque
y_true = (df_real["label"].str.strip().str.lower() != "normal").astype(int)
y_pred = (pd.Series(predicoes).astype(str).str.strip().str.lower() != "benign").astype(int)

# 6. Calcula e exibe as métricas
cm = confusion_matrix(y_true, y_pred)

print("\n=== RESULTADOS: MODELO MARIA ORIGINAL NO NSL-KDD ===")
print(f"Acurácia  (Accuracy) : {accuracy_score(y_true, y_pred) * 100:.2f}%")
print(f"Precisão  (Precision): {precision_score(y_true, y_pred, zero_division=0) * 100:.2f}%")
print(f"Recall    (Detecção) : {recall_score(y_true, y_pred, zero_division=0) * 100:.2f}%")
print(f"F1-Score             : {f1_score(y_true, y_pred, zero_division=0) * 100:.2f}%")

print("\n--- Distribuição das Classes Previstas pelo MARIA ---")
print(pd.Series(predicoes).value_counts())

print("\n--- Matriz de Confusão ---")
print(f"Verdadeiros Benignos (VN): {cm[0][0]} | Falsos Alarmes (FP): {cm[0][1]}")
print(f"Ataques Perdidos     (FN): {cm[1][0]} | Ataques Detectados (VP): {cm[1][1]}")

print("\n--- Relatório Detalhado ---")
print(classification_report(y_true, y_pred, target_names=["Benigno (0)", "Ataque (1)"], zero_division=0))