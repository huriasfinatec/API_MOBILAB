# Arquivo: importar_dados.py (Versão Final)

import pandas as pd
import os
from sqlalchemy import create_engine
import sys
from urllib.parse import quote_plus

# --- CONFIGURAÇÕES IMPORTANTES ---
DB_USER = "mobilabfinatec"
DB_PASS = "Finatec_25"          # A senha correta que você definiu
DB_HOST = "localhost"           # Mantenha 'localhost', pois usamos o túnel SSH do DBeaver
DB_PORT = 3306                  # Porta padrão do MySQL
DB_NAME = "bd_semob"            # O nome correto do banco de dados
TABLE_NAME = "fluxo_veiculos"   # Nome da tabela que vamos criar
PASTA_EXCEL = 'fluxo'           # A pasta onde estão os arquivos Excel
# --- FIM DAS CONFIGURAÇÕES ---

def conectar_db():
    """Cria a engine de conexão com o banco de dados MySQL."""
    try:
        # Codificamos a senha para lidar com quaisquer caracteres especiais
        senha_codificada = quote_plus(DB_PASS)
        
        engine = create_engine(
            f'mysql+pymysql://{DB_USER}:{senha_codificada}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
        engine.connect()
        print("✅ Conexão com o banco de dados MySQL bem-sucedida!")
        return engine
    except Exception as e:
        print(f"\n❌ ERRO: Não foi possível conectar ao banco de dados.")
        print(f"   Detalhes: {e}")
        print("\n   Por favor, verifique se:")
        print("   1. O DBeaver está com a conexão e o túnel SSH ativos.")
        print("   2. Os dados de usuário, senha, host e nome do banco estão corretos no script.")
        sys.exit(1)

def processar_arquivos_excel(caminho_pasta):
    """Lê todos os arquivos Excel de uma pasta e os consolida em um DataFrame."""
    lista_dfs = []
    print(f"\n▶️ Lendo arquivos da pasta '{caminho_pasta}'...")
    
    if not os.path.isdir(caminho_pasta):
        print(f"❌ ERRO: A pasta '{caminho_pasta}' não foi encontrada. Verifique se ela foi criada no lugar certo.")
        sys.exit(1)

    arquivos_encontrados = [f for f in os.listdir(caminho_pasta) if f.endswith('.xlsx')]
    if not arquivos_encontrados:
        print(f"❌ ERRO: Nenhum arquivo .xlsx encontrado na pasta '{caminho_pasta}'.")
        sys.exit(1)

    for nome_arquivo in arquivos_encontrados:
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        print(f"   Processando: {nome_arquivo}")
        try:
            df_temp = pd.read_excel(caminho_completo)
            df_temp['nome_arquivo_origem'] = nome_arquivo
            lista_dfs.append(df_temp)
        except Exception as e:
            print(f"     -> Aviso: Erro ao ler o arquivo {nome_arquivo}. Ignorando. Detalhe: {e}")

    if not lista_dfs:
        print("❌ ERRO: Nenhum arquivo Excel pôde ser lido com sucesso.")
        sys.exit(1)
    else:
        return pd.concat(lista_dfs, ignore_index=True)

def limpar_e_transformar_dados(df):
    """Limpa e transforma os dados para o formato do banco de dados."""
    print("\n▶️ Limpando e transformando dados...")
    
    df.rename(columns={
        'Grupo': 'grupo', 'Endereço': 'endereco', 'Intervalo': 'intervalo',
        'Data': 'data', 'porte': 'porte', 'fluxo': 'fluxo'
    }, inplace=True)
    
    df['hora_inicio'] = df['intervalo'].astype(str).str.split(' - ').str[0]
    
    df['data_hora_inicio'] = pd.to_datetime(
        df['data'].astype(str) + ' ' + df['hora_inicio'], 
        dayfirst=True, errors='coerce'
    )
    
    df.dropna(subset=['data_hora_inicio'], inplace=True)
    df['fluxo'] = pd.to_numeric(df['fluxo'], errors='coerce').fillna(0).astype(int)
    
    colunas_finais = [
        'grupo', 'endereco', 'data_hora_inicio', 
        'porte', 'fluxo', 'nome_arquivo_origem'
    ]
    
    for col in colunas_finais:
        if col not in df.columns:
            df[col] = None

    df_final = df[colunas_finais]
    
    print(f"   {len(df_final)} registros prontos para serem inseridos.")
    print("   Amostra dos dados transformados:")
    print(df_final.head())
    return df_final

def inserir_dados_no_db(df, engine, nome_tabela):
    """Insere o DataFrame no banco de dados MySQL."""
    print(f"\n▶️ Iniciando inserção de dados na tabela '{nome_tabela}'...")
    try:
        # if_exists='replace': Apaga a tabela se ela já existir e cria uma nova.
        # Use 'append' se no futuro quiser adicionar mais dados sem apagar os antigos.
        df.to_sql(nome_tabela, con=engine, if_exists='replace', index=False)
        print(f"✅ Dados inseridos com sucesso na tabela '{nome_tabela}'!")
    except Exception as e:
        print(f"❌ ERRO durante a inserção de dados: {e}")

if __name__ == "__main__":
    db_engine = conectar_db()
    df_bruto = processar_arquivos_excel(PASTA_EXCEL)
    df_limpo = limpar_e_transformar_dados(df_bruto)
    inserir_dados_no_db(df_limpo, db_engine, TABLE_NAME)
    print("\n🎉 Processo concluído! 🎉")