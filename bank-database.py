#!pip install mimesis numpy pandas

from mimesis import Generic
from mimesis.locales import Locale
from pathlib import Path
from datetime import datetime
import argparse
import numpy as np
import pandas as pd
import time, re, sys

#bibliotecas para instalar, seguido dos imports.


#Gravando o diretório do arquivo, e salvando o caminho dos arquivos gerados para a pasta outputs.
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

#aliases do numpy e mimesis utilizando o rng padrão e a Locale brasileira.
rng = np.random.default_rng()
mimesis = Generic(Locale.PT_BR)


#Função que cuidará do salvamento dos arquivos,feita de maneira modular a fim de facilmente alternar entre formatos. Inclui qual o tipo dos dados
    #Dict com formatos aceitos e suas extensões, usando csv como extensão padrão.
    #Caso não seja passado o formato desejado usa csv.
    #Valida que o valor existe, caso contrário para o script.
    #Pega a extensão do formato e monta a função do pandas correspondente.
    #Monta o nome do arquivo, com a etapa caso provida, palavra aleatória gerada com mimesis e com acentos retirados, timestamp com hora do sistema e extensão.
    #Armazena o path do arquivo no sistema.
    #Pega a função to_... do dataframe pandas utilizando o nome do arquivo como base. Primeiros parênteses são o objeto e qual a função pegar, e os seguintes são os argumentos para passar à função e a executá-la.

def save_file(df,format="",phase=""):
    formatos_aceitos = {"excel":"xlsx","parquet":"parquet","csv":"csv"}
    VALOR_PADRAO = "csv"
    
    if format == "":
        format = VALOR_PADRAO
    if format not in formatos_aceitos:
        raise ValueError("Formato inválido")
    
    extensao = formatos_aceitos[format]
    salvar_func = f"to_{format}"
    
    prefixo = f"{phase}_" if phase else ""
    palavra = re.sub(r'[^a-zA-Z0-9_-]', '', mimesis.text.word())
    timestamp = datetime.now().strftime("%H%M%S")
    filename =  f"{prefixo}_{palavra}_{timestamp}.{extensao}"
    filepath = OUTPUT_DIR / filename
    
    getattr(df,salvar_func)(filepath,index=False)


#Função que cria o efeito de texto digitado. Recebe a string, velocidade base por caractere e o jitter, que é a variação de velocidade.
def typetext(texto,velocidade_base=0.02,jitter=0.015):
    #Para cada caractere na string:
    #Escreve o caractere no buffer do terminal, manda ele mostrar no terminal, apaga do buffer sem pular a linha e espera um tempo entre 1ms e velocidade_base+jitter. Repete até a string acabar.
    for char in texto:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(max(0.001, rng.uniform(velocidade_base - jitter, velocidade_base + jitter)))
    #pula a linha após a string acabar.
    print()
    
    
#Função que cria o efeito de paredão de texto. Recebe o DataFrame que contém as informações, limite de linhas para não demorar muito e velocidade base por linha.
    #Pega somente o que será mostrado de acordo com o limite e guarda na var amostra.
    #Para cada linha do df:
    #Pega os valores da linha i, adiciona "|" entre eles, printa a linha e espera base_vel+jitter aleatório. Repete até acabar as *limite* linhas
    
def matrix_print(df, limite=2000, base_vel=0.001):
    amostra = df.head(limite)
    for i in range(len(amostra)):
        linha_valores = amostra.iloc[i].values
        texto_tratado = " | ".join(map(str,linha_valores))
        jitter = rng.uniform(0,0.005)
        print(texto_tratado)
        time.sleep(base_vel + jitter)



#Cria um CPF aleatório válido de acordo com o algoritmo utilizado aqui <https://www.cadcobol.com.br/calcula_cpf_cnpj_caepf.htm>.
def gerar_cpf():
    nums = rng.integers(0,10, size=9).tolist()
    if len(set(nums)) == 1:
        return gerar_cpf()
    d1 = (sum([nums[i] * (10-i) for i  in range(len(nums))]) * 10 % 11) % 10
    nums.append(d1)
    d2 = (sum ([nums[i] * (11-i) for i in range(len(nums))])* 10 % 11) % 10
    nums.append(d2)
    
    return ''.join(map(str,nums))
    

#Gera n clientes usando listas que são retornadas em um dict.
    #Gera n nomes completos utilizando mimesis, destaque para que, como declaramos previamente a Locale PT_BR os nomes virão como nomes típicos Brasileiros.
    #Gera n cpfs utilizando a função criada anteriormente.
    #Gera n datas utilizando mimesis, com ano mínimo de 1945 e máximo de 2008.
    #Gera n telefones utilizando mimesis, utilizando como máscara o padrão brasileiro.
    #Cria o dict com as informações para fácil criação do DataFrame, e o retorna.
def gerar_clientes(n):
    names = [mimesis.person.full_name() for i in range(n)]
    cpfs = [gerar_cpf() for i in range(n)]
    dobs = [mimesis.person.birthdate(min_year=1945,max_year=2008) for i in range(n)]
    emails = [mimesis.person.email() for i in range(n)]
    phones = [mimesis.person.phone_number(mask='+55##9########') for i in range(n)]
    clients = {'nome': names,'cpf':cpfs,'data_nasc':dobs,'email':emails,'tel':phones}

    return clients


#Gera *num_agencias* agências, as separando entre agências empresariais, "premium" ou normais para uso futuro.
    #Gera *num_agencias* agências com 4 dígitos acima do número 1000.
    #Separa as agências por segmento, sorteando números e colocando-os usando a razão do dict.
def gerar_agencias(num_agencias):
    agencia_ratios = {"enterprise":.05,"prime":.15,"regular":.8}
    agencias_raw = rng.integers(1000,10000,size=num_agencias)
    tipos_agencias = rng.choice(list(agencia_ratios.keys()),size=num_agencias,p=list(agencia_ratios.values()))
    dist_agencias = {}
    for num, tipo in zip(agencias_raw,tipos_agencias):
        dist_agencias.setdefault(str(tipo), []).append(int(num))
    
    return dist_agencias
    
#Gera uma conta com 8 números, com dígito verificador também válido de acordo com o algoritmo Módulo 11.
def gerar_conta():
    nums = rng.integers(0,10, size=8).tolist()
    a = sum([nums[i] * (len(nums)+1) - i for i in range(len(nums))]) * 10 % 11 % 10
    if a == 0:
        a="X"

    return ''.join(map(str,nums)) + "-" + str(a)


#Gera *num_contas* contas. Separa elas por segmento, cria o número, atribui uma agência de acordo com o segmento,
    #Cria uma lista com *num_contas* valores para usar como balanço, cria máscaras de acordo com os segmentos e atribui um balanço condizente para cada segmento(>50K para empresas, <100K para VIP's e <5K para Normais).
    #Retorna um dict contendo as informações + data de abertura gerada com mimesis para montagem de um DataFrame.
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
        "data_abertura": [mimesis.datetime.date(start=2010,end=2025) for i in range(num_contas)]
    }
    
    return contas

#Gera *qtd_cartoes* cartões, simulando mais de um cartão por conta. Gera os números utilizando mimesis, suas validades começando pelo ano de 2027,
    # os limites de maneira aleatória com numpy, a data de abertura subtraindo 8 anos da data de vencimento e finalmente seleciona uma conta pelos id's do DataFrame contas.
    # Retorna um dict com informações para uso em um DataFrame.
def gerar_cartoes(qtd_cartoes,df_contas):
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


#Gera *num_transacoes* de transações, separadas entre Saques(SQ), Depósitos)(DP) e Transferências(TR) distribuidas usando os valores *dist_transacoes*.
    #Cria uma lista de *num_transacoes* escolhendo aleatóriamente os tipos.
    #Escolhe contas aleatórias como origem usando o DataFrame contas.
    #Escolhe contas aleatórias como destino usando o mesmo DataFrame.
    #Puxa os segmentos das contas para usar como mask na hora de atribuir o valor da operação.
    #cria um array com *num_transacoes* zeros, atribui o valor de cada transação aleatóiriamente usando RNG + máscara para definir o range do valor. 

    #Monta um dataframe com tipo, valor, origem, destino e timestamp aleatória.
    #Retira Destinos de Saques e Origens de Depósitos, substituindo por Nan para melhor compatibilidade com bancos de dados.
    #Checa se há operações com origens e destinos iguais, caso haja sorteia um novo destino.
    #Retorna o DataFrame tratado.
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
    valores = valores.round(decimals=2)
    
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



#Usa o __main__ para executar o script.
    #Adiciona os launch args --quiet e --clientes para geração rápida. 
    #Usa 150 agências como base, 1.1 contas por cliente, 4.5 transações por conta e 1.3 cartões por conta.
    #Caso FANCY_VISUAL estiver em True mostra o "processo" no terminal, caso contrário só gera os dados.
    #Salva usando a função save_file.
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="GERADOR DE DATABASE - BANCO V0.9")
    
    parser.add_argument("--quiet","-q", action="store_true",help="Desativa o modo FANCY_VISUAL e roda silencioso.")
    
    parser.add_argument("--clientes", "-c",type=int,help="Define o número de clientes e pula o Input.")
    
    args = parser.parse_args()
    
    FANCY_VISUAL = not args.quiet
    
    if FANCY_VISUAL:
        typetext("GERADOR DE DATABASE - BANCO V0.9")
    else: print("GERADOR DE DATABASE - BANCO V0.9")
    
    if args.clientes:
        BASE_CLIENTES = args.clientes
        print(f"Configuração recebida via argumento: {BASE_CLIENTES} clientes.")
    else:
        
        if FANCY_VISUAL:
            typetext("Digite um número desejado de clientes (Min:100/Máx recomendado: 300000)")
        else: print("Digite um número desejado de clientes (Min:100/Máx recomendado: 300000)")
        
        try:
            numero_clientes = input()
            BASE_CLIENTES = int(numero_clientes)
        except ValueError:
            print("Valor inválido! Usando padrão de 100 clientes.")
            BASE_CLIENTES = 100
            
    if FANCY_VISUAL:
        typetext("GERANDO - AGUARDE")
    else: print("GERANDO - AGUARDE")
    time.sleep(3)
    
    BASE_CLIENTES = int(numero_clientes)
    NUM_AGENCIAS = 150
    NUM_CLIENTES = BASE_CLIENTES
    
    NUM_CONTAS = int(NUM_CLIENTES*1.1)
    NUM_TRANSACOES = int(NUM_CONTAS*4.5)
    NUM_CARTOES = int(NUM_CONTAS*1.3)
    
    if FANCY_VISUAL:
        typetext("1/5 - GERANDO AGÊNCIAS...")
        time.sleep(1)
        
    else: print("1/5 - GERANDO AGÊNCIAS...")
    agencias = gerar_agencias(NUM_AGENCIAS)
    
    if FANCY_VISUAL:
        typetext("FEITO! CONTINUANDO...")
        time.sleep(.5)
    
    
    if FANCY_VISUAL:
        typetext("2/5 - GERANDO CLIENTES...")
        time.sleep(1)
        
    else: print("2/5 - GERANDO CLIENTES...")
    clientes = gerar_clientes(NUM_CLIENTES)
    df_clientes = pd.DataFrame(clientes)
    save_file(df_clientes,"csv")
    
    if FANCY_VISUAL:
        matrix_print(df_clientes,limite=2000)
        typetext("FEITO! CONTINUANDO...")
        time.sleep(.5)

    if FANCY_VISUAL:
        typetext("3/5 - GERANDO CONTAS...")
        time.sleep(1)
    
    else: print("3/5 - GERANDO CONTAS...")
    contas = gerar_contas(NUM_CONTAS,agencias)
    df_contas = pd.DataFrame(contas)
    save_file(df_contas, "csv")
    
    if FANCY_VISUAL:
        matrix_print(df_contas,limite=2000)
        typetext("FEITO! CONTINUANDO...")
        time.sleep(.5)
    
    #TODO Cartoes
    
    if FANCY_VISUAL:
        typetext("4/5 - GERANDO CARTÕES...")
        time.sleep(1)
    else: print("4/5 - GERANDO CARTÕES...")
    
    cartoes = gerar_cartoes(NUM_CARTOES,df_contas)
    save_file(cartoes,"csv")
    
    if FANCY_VISUAL:
        matrix_print(cartoes,limite=2000)
        typetext("FEITO! CONTINUANDO...")
        time.sleep(.5)
    
    
    if FANCY_VISUAL:
        typetext("5/5 - GERANDO TRANSAÇÕES...")
        time.sleep(1)
    else: print("5/5 - GERANDO TRANSAÇÕES...")
    transacoes = gerar_transacoes_batch(NUM_TRANSACOES,df_contas)
    save_file(transacoes,"csv")
    
    if FANCY_VISUAL:
        matrix_print(transacoes,limite=2000)
        typetext("FEITO! Finalizando")
        time.sleep(.5)
        
    if FANCY_VISUAL:
        typetext("Geração terminada! os arquivos estão na pasta /output.")