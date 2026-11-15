import pandas as pd

# Nomes oficiais das 43 colunas do NSL-KDD
colunas_nsl = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_diff_src_port_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty_level"
]

# 1. Processa e salva as bases completas com cabeçalho
df_train = pd.read_csv("KDDTrain.txt", names=colunas_nsl)
df_test = pd.read_csv("KDDTest.txt", names=colunas_nsl)

df_train.to_csv("KDDTrain_completo.csv", index=False)
df_test.to_csv("KDDTest_completo.csv", index=False)
print(f"Treino salvo: {df_train.shape} | Teste salvo: {df_test.shape}")

# 2. Adapta o conjunto de teste para o esquema de colunas do modelo MARIA
df_maria = pd.DataFrame({
    "Dur": df_test["duration"],
    "SrcBytes": df_test["src_bytes"],
    "DstBytes": df_test["dst_bytes"],
    "SrcPkts": 1,   # Atributo ausente no NSL-KDD (preenchimento padrão)
    "DstPkts": 1,   # Atributo ausente no NSL-KDD (preenchimento padrão)
    "sTtl": 64,     # Atributo ausente no NSL-KDD (TTL padrão)
    "dTtl": 64,     # Atributo ausente no NSL-KDD (TTL padrão)
    "Proto": df_test["protocol_type"].str.lower()
})

df_maria.to_csv("nslkdd_para_maria.csv", index=False)
print("Arquivo 'nslkdd_para_maria.csv' gerado com sucesso!")