import time
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 1. Carrega treino e teste completos do NSL-KDD
df_train = pd.read_csv("datasets/KDDTrain_completo.csv")
df_test = pd.read_csv("datasets/KDDTest_completo.csv")

# 2. Limpeza básica: remove metadado 'difficulty_level' e colunas constantes (variância zero)
df_train = df_train.drop(columns=["difficulty_level"])
df_test = df_test.drop(columns=["difficulty_level"])

colunas_constantes = [c for c in df_train.columns if df_train[c].nunique() <= 1]
print(f"Colunas constantes removidas ({len(colunas_constantes)}): {colunas_constantes}")

df_train = df_train.drop(columns=colunas_constantes)
df_test = df_test.drop(columns=colunas_constantes)

# 3. Define alvo binário (0 = Benigno, 1 = Ataque) e features
y_train = (df_train["label"].str.strip().str.lower() != "normal").astype(int)
y_test = (df_test["label"].str.strip().str.lower() != "normal").astype(int)

X_train = df_train.drop(columns=["label"])
X_test = df_test.drop(columns=["label"])

cat_cols = ["protocol_type", "service", "flag"]

# 4. Treina o CatBoost completo (todas as 40 colunas úteis) para obter o ranking de pesos
print("\nTreinando CatBoost completo (40 colunas)...")
cb_full = CatBoostClassifier(iterations=300, random_seed=42, verbose=0)
cb_full.fit(X_train, y_train, cat_features=cat_cols)

ranking = pd.DataFrame({
    "Coluna": X_train.columns,
    "Peso (%)": cb_full.get_feature_importance()
}).sort_values(by="Peso (%)", ascending=False)

ranking.to_csv("ranking_catboost_nslkdd.csv", index=False)
print("\n=== TOP 15 COLUNAS NO CATBOOST ===")
print(ranking.head(15).to_string(index=False))

# 5. Benchmark: testa a precisão e o tempo de inferência reduzindo as colunas
print("\n=== COMPARATIVO DE REDUÇÃO DE COLUNAS (TESTE NO KDDTest+) ===")
print(f"{'Qtd Colunas':<13} | {'Acurácia':<10} | {'Precisão':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Tempo Pred (ms)':<15}")
print("-" * 80)

for k in [len(X_train.columns), 15, 10, 6]:
    top_cols = ranking["Coluna"].head(k).tolist()
    top_cats = [c for c in top_cols if c in cat_cols]
    
    modelo = CatBoostClassifier(iterations=300, random_seed=42, verbose=0)
    modelo.fit(X_train[top_cols], y_train, cat_features=top_cats)
    
    t0 = time.perf_counter()
    preds = modelo.predict(X_test[top_cols])
    tempo_ms = (time.perf_counter() - t0) * 1000
    
    acc = accuracy_score(y_test, preds) * 100
    prec = precision_score(y_test, preds) * 100
    rec = recall_score(y_test, preds) * 100
    f1 = f1_score(y_test, preds) * 100
    
    print(f"{k:<13} | {acc:>8.2f}% | {prec:>8.2f}% | {rec:>8.2f}% | {f1:>8.2f}% | {tempo_ms:>12.2f} ms")