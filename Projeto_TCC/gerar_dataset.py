import pandas as pd
import random

def gerar_fluxo_benigno():
    return {
        "Dur": round(random.uniform(0.1, 5.0), 3),
        "SrcBytes": random.randint(100, 5000),
        "DstBytes": random.randint(100, 50000),
        "SrcPkts": random.randint(5, 50),
        "DstPkts": random.randint(5, 50),
        "sTtl": random.choice([64, 128]),
        "dTtl": random.choice([64, 128]),
        "Proto": random.choice(["tcp", "udp"])
    }

def gerar_port_scan():
    return {
        "Dur": 0.0,
        "SrcBytes": 0,
        "DstBytes": 0,
        "SrcPkts": 1,
        "DstPkts": 0,
        "sTtl": 255, # O peso principal que descobrimos
        "dTtl": 0,
        "Proto": "tcp"
    }

def gerar_ddos():
    return {
        "Dur": round(random.uniform(10.0, 60.0), 3),
        "SrcBytes": random.randint(10000, 500000),
        "DstBytes": 0,
        "SrcPkts": random.randint(1000, 50000),
        "DstPkts": 0,
        "sTtl": 64,
        "dTtl": 0,
        "Proto": "udp"
    }

# Fabricar 1000 linhas
linhas = []
for _ in range(700): linhas.append(gerar_fluxo_benigno()) # 70% tráfego normal
for _ in range(150): linhas.append(gerar_port_scan())     # 15% scan
for _ in range(150): linhas.append(gerar_ddos())          # 15% DDoS

# Embaralhar para simular rede real
random.shuffle(linhas)

df = pd.DataFrame(linhas)
df.to_csv("meu_dataset_gigante.csv", index=False)
print("Sucesso! 'meu_dataset_gigante.csv' criado com 1000 fluxos de rede.")