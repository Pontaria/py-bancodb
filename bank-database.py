#!pip install mimesis numpy pandas

from mimesis import Generic
from mimesis.locales import Locale
from pathlib import Path
from datetime import date, datetime
import numpy as np
import pandas as pd
import time, re, sys

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng()
mimesis = Generic(Locale.PT_BR)


def save_file(df,format):
    
    word = re.sub(r'[^a-zA-Z0-9_-]', '', mimesis.text.word())
    timestamp = datetime.now().strftime("%H%M%S")
    filename =  f"{word}_{timestamp}"

    ext = {"excel":"xlsx","parquet":"parquet","csv":"csv"}
    
    if format not in ext:
        raise ValueError("Formato inválido")
    elif format == "excel":
        filepath = OUTPUT_DIR / f"{filename}.xlsx"
        df.to_excel(filepath, index=False)
    elif format == "parquet":
        filepath = OUTPUT_DIR / f"{filename}.parquet"
        df.to_parquet(filepath, index=False)
    else:
        filepath = OUTPUT_DIR / f"{filename}.csv"
        df.to_csv(filepath, index=False)

def textofoda(texto,velocidade_base=0.02,jitter=0.015):
    for char in texto:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(max(0.001, rng.uniform(velocidade_base - jitter, velocidade_base + jitter)))
    print()
    
def matrix_print(df, limite=1500):
    """Pega uma amostra do DataFrame e cospe no terminal pra dar o efeito Matrix"""
    # Pega só as primeiras X linhas para não travar a tela pra sempre
    amostra = df.head(limite)
    
    # Transforma em texto grudado por ' | ' direto da memória em milissegundos
    paredao = amostra.to_csv(index=False, header=False, sep='|')
    
    # Imprime tudo de uma vez.
    print(paredao)


## DONE gerar nome, cpf, dob, email e telefone de n pessoas

## gerar n numero da conta(sequencial mesmo?) DONE,tipo de conta DONE, saldo e data de abertura DONE DONE

## TODO gerar n cartões  de crédito, numero do cartão, data de validade limite e data de abertura

## gerar n transações, tipo, valor, data, hora,  conta de origem e conta de destino

#Gerando dados de clientes

def gerar_cpf():
    nums = rng.integers(0,10, size=9).tolist()
    if len(set(nums)) == 1:
        return gerar_cpf()
    d1 = (sum([nums[i] * (10-i) for i  in range(len(nums))]) * 10 % 11) % 10
    nums.append(d1)
    d2 = (sum ([nums[i] * (11-i) for i in range(len(nums))])* 10 % 11) % 10
    nums.append(d2)
    
    return ''.join(map(str,nums))
    

def gerar_clientes(n):
  names = [mimesis.person.full_name() for i in range(n)]
  cpfs = [gerar_cpf() for i in range(n)]
  dobs = [mimesis.person.birthdate(min_year=1945,max_year=2008) for i in range(n)]
  emails = [mimesis.person.email() for i in range(n)]
  phones = [mimesis.person.phone_number(mask='+55##9########') for i in range(n)]
  clients = {'nome': names,'cpf':cpfs,'data_nasc':dobs,'email':emails,'tel':phones}

  return clients

def gerar_agencias(num_agencias):
    agencia_ratios = {"enterprise":.05,"prime":.15,"regular":.8}
    
    agencias_raw = rng.integers(1000,10000,size=num_agencias)
    tipos_agencias = rng.choice(list(agencia_ratios.keys()),size=num_agencias,p=list(agencia_ratios.values()))

    dist_agencias = {}
    for num, tipo in zip(agencias_raw,tipos_agencias):
        dist_agencias.setdefault(str(tipo), []).append(int(num))
    
    return dist_agencias
    
def gerar_conta():
    nums = rng.integers(0,10, size=8).tolist()
    a = sum([nums[i] * (len(nums)+1) - i for i in range(len(nums))]) * 10 % 11 % 10
    if a == 0:
        a="X"

    return ''.join(map(str,nums)) + "-" + str(a)

def gerar_contas(num_contas,agencias_dict):
    segmentos_ratios = {"business":.05,"vip":.15,"regular":.8}
    
    segmentos = rng.choice(list(segmentos_ratios.keys()), size=num_contas,p=list(segmentos_ratios.values()))
    
    numeros_conta = [gerar_conta() for i in range(num_contas)]
    
    agencias_raw = agencias_dict.get('regular',[]) + agencias_dict.get('prime',[]) + agencias_dict.get('enterprise',[])
    
    agencias_sorteadas = rng.choice(agencias_raw, size=num_contas)
    
    saldos = np.zeros(num_contas)
    
    mask_bus = (segmentos == "business")
    mask_vip = (segmentos == "vip")
    mask_reg = (segmentos == "regular")
    
    saldos[mask_bus] = rng.uniform(50000,500000, size=mask_bus.sum())
    saldos[mask_vip] = rng.uniform(10000,100000, size=mask_vip.sum())
    saldos[mask_reg] = rng.uniform(0,5000, size=mask_reg.sum())
    
    contas = {
        "numero": numeros_conta,
        "agencia": agencias_sorteadas,
        "saldo": np.round(saldos,2),
        "modalidade": segmentos,
        "data_abertura": [mimesis.datetime.date(start=2010,end=2026) for i in range(num_contas)]
    }
    
    return contas


def gerar_cartoes(num_contas,df_contas):
    qtd_cartoes = int(num_contas*1.2)
    numeros = [mimesis.payment.credit_card_number() for i in range(qtd_cartoes)]
    validades = [mimesis.datetime.date(start=2027,end=2030)for i in range(qtd_cartoes)]
    limites = rng.uniform(800,50000, size=qtd_cartoes)
    aberturas =[validades[i].replace(year=validades[i].year - 8) for i in range(qtd_cartoes)]
    ids = rng.choice(df_contas["numero"].values, size=qtd_cartoes)
    
    df_cartoes = pd.DataFrame({
        "numero_cartao": numeros,
        "validade": validades,
        "limite": limites,
        "data_abertura": aberturas,
        "id_conta": ids
    })
    
    return df_cartoes

def gerar_transacoes_batch(num_transacoes,df_contas):
    tipos_transacoes = ["SQ","DP","TR"]
    dist_transacoes = [.3,.4,.3]
    tipos = rng.choice(tipos_transacoes, size=num_transacoes, p=dist_transacoes)
    ids_contas_origem = rng.choice(df_contas.index,size=num_transacoes)
    ids_contas_destino = rng.choice(df_contas.index,size=num_transacoes)
    origens = df_contas["numero"].values[ids_contas_origem]
    destinos = df_contas["numero"].values[ids_contas_destino]
    segmentos = df_contas["modalidade"].values[ids_contas_origem]
    
    valores = np.zeros(num_transacoes)
    
    mask_bus = (segmentos == "business")
    mask_vip = (segmentos == "vip")
    mask_reg = (segmentos == "regular")
    
    valores[mask_bus] = rng.uniform(10000,200000, size=mask_bus.sum())
    valores[mask_vip] = rng.uniform(5000,100000, size=mask_vip.sum())
    valores[mask_reg] = rng.uniform(15,5000, size=mask_reg.sum())
    
    df_batch = pd.DataFrame({
        "tipo": tipos,
        "valor": valores,
        "origem": origens,
        "destino": destinos,
        "timestamp": [mimesis.datetime.datetime() for i in range(num_transacoes)]
    })
    
    df_batch.loc[df_batch["tipo"] == "SQ", "destino"] = None
    df_batch.loc[df_batch["tipo"] == "DP", "origem"] = None
    
    mask_iguais = (df_batch["tipo"] == "TR") & (df_batch["origem"] == df_batch["destino"])
    
    df_batch.loc[mask_iguais, "destino"] = rng.choice(df_contas["numero"].values,size=mask_iguais.sum())
    
    return df_batch


if __name__ == "__main__":
    
    COM_EMOCAO = True
    if COM_EMOCAO:
        textofoda("GERADOR DE DATABASE - BANCO V0.9")
    else: print("GERADOR DE DATABASE - BANCO V0.9")
    
    
    if COM_EMOCAO:
        textofoda("Digite um número desejado de clientes (Min:100/Máx recomendado: 300000)")
    else: print("Digite um número desejado de clientes (Min:100/Máx recomendado: 300000)")
    
    numero_tr_pedidas = input()
    
    if COM_EMOCAO:
        textofoda("GERANDO - AGUARDE")
    else: print("GERANDO - AGUARDE")
    time.sleep(3)
    
    BASE_CLIENTES = int(numero_tr_pedidas)
    NUM_AGENCIAS = 150
    NUM_CLIENTES = BASE_CLIENTES
    
    NUM_CONTAS = int(NUM_CLIENTES*1.1)
    NUM_TRANSACOES = int(NUM_CONTAS*4.5)
    
    if COM_EMOCAO:
        textofoda("1/5 - GERANDO AGÊNCIAS...")
        time.sleep(1)
        
    else: print("1/5 - GERANDO AGÊNCIAS...")
    agencias = gerar_agencias(NUM_AGENCIAS)
    
    if COM_EMOCAO:
        textofoda("FEITO! CONTINUANDO...")
        time.sleep(.5)
    
    
    if COM_EMOCAO:
        textofoda("2/5 - GERANDO CLIENTES...")
        time.sleep(2)
        
    else: print("2/5 - GERANDO CLIENTES...")
    clientes = gerar_clientes(NUM_CLIENTES)
    df_clientes = pd.DataFrame(clientes)
    save_file(df_clientes,"csv")
    
    if COM_EMOCAO:
        matrix_print(df_clientes,limite=2000)
        textofoda("FEITO! CONTINUANDO...")
        time.sleep(.5)

    if COM_EMOCAO:
        textofoda("3/5 - GERANDO CONTAS...")
        time.sleep(2)
    
    else: print("3/5 - GERANDO CONTAS...")
    contas = gerar_contas(NUM_CONTAS,agencias)
    df_contas = pd.DataFrame(contas)
    save_file(df_contas, "csv")
    
    if COM_EMOCAO:
        matrix_print(df_contas,limite=2000)
        textofoda("FEITO! CONTINUANDO...")
        time.sleep(.5)
    
    #TODO Cartoes
    
    if COM_EMOCAO:
        textofoda("4/5 - GERANDO CARTÕES...")
        time.sleep(2)
    else: print("4/5 - GERANDO CARTÕES...")
    
    cartoes = gerar_cartoes(NUM_CONTAS,df_contas)
    save_file(cartoes,"csv")
    
    if COM_EMOCAO:
        matrix_print(cartoes,limite=2000)
        textofoda("FEITO! CONTINUANDO...")
        time.sleep(.5)
    
    
    if COM_EMOCAO:
        textofoda("5/5 - GERANDO TRANSAÇÕES...")
        time.sleep(2)
    else: print("5/5 - GERANDO TRANSAÇÕES...")
    transacoes = gerar_transacoes_batch(NUM_TRANSACOES,df_contas)
    save_file(transacoes,"csv")
    
    if COM_EMOCAO:
        matrix_print(transacoes,limite=2000)
        textofoda("FEITO! Finalizando")
        time.sleep(.5)
        
    if COM_EMOCAO:
        textofoda("Geração terminada! os arquivos estão na pasta /output.")