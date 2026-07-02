import streamlit as st
import pandas as pd
import re
import os
import unicodedata
import zipfile
import tempfile
import itertools
from datetime import datetime
from io import BytesIO
import json

# Configuração inicial da página
st.set_page_config(page_title="SearchCRT - Busca e Comparativo de Dados", layout="wide")

# Tema seletor
col_vazia, col_seletor = st.columns([5.2, 1.8])
with col_seletor:
    tema_selecionado = st.radio(
        "Visualização",
        options=["Modo Claro", "Modo Escuro"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

# Definição de estilo baseada no tema
if tema_selecionado == "Modo Claro":
    bg_principal = "#FFFFFF"
    texto_principal = "#333333"
    bg_sidebar = "#F4F6F9"
    texto_sidebar = "#1B365D"
    borda_sidebar = "#E0E0E0"
    card_bg = "#F8F9FA"
    titulo_cor = "#1B365D"
else:
    bg_principal = "#0E1117"
    texto_principal = "#E0E0E0"
    bg_sidebar = "#1E222B"
    texto_sidebar = "#E0E0E0"
    borda_sidebar = "#2D3139"
    card_bg = "#1A1C23"
    titulo_cor = "#4A90E2"

# CSS customizado
st.markdown(f"""
    <style>
    .main {{
        background-color: {bg_principal} !important;
        color: {texto_principal} !important;
    }}
    .main .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 3rem;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    .main p, .main span, .main label, .main [data-testid="stMarkdownContainer"] p {{
        color: {texto_principal} !important;
    }}
    h1, h2, h3, h4 {{
        color: {titulo_cor} !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {borda_sidebar} !important;
    }}
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h3 {{
        color: {texto_sidebar} !important;
    }}
    div.stButton > button {{
        background-color: #1B365D !important;
        border: 1px solid #1B365D !important;
        border-radius: 4px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 13px !important;
        letter-spacing: 0.5px;
        color: #FFFFFF !important;
    }}
    div.stButton > button:hover {{
        background-color: #F2A900 !important;
        border: 1px solid #F2A900 !important;
        color: #1B365D !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Banner de Cabeçalho
st.markdown("""
    <div style="background-color: #1B365D; padding: 25px; border-bottom: 6px solid #F2A900; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-family: Arial, sans-serif; font-size: 24px; font-weight: 700; letter-spacing: 0.5px; line-height: 1.2;">
            🔍 SearchCRT - Sistema de Busca e Comparativo de Dados
        </h1>
        <p style="color: #F2A900; margin: 6px 0 0 0; font-family: Arial, sans-serif; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
            Análise Avançada • Comparativo Inteligente • Busca Localizada
        </p>
    </div>
""", unsafe_allow_html=True)

# Inicializar session_state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_results' not in st.session_state:
    st.session_state.last_results = None

# Funções auxiliares
def extrair_nomes(texto):
    """Extrai e normaliza nomes"""
    if not texto or str(texto).lower() == 'nan':
        return []
    nfkd = unicodedata.normalize('NFKD', str(texto))
    limpo = re.sub(r'[^a-zA-Z\s]', '', u"".join([c for c in nfkd if not unicodedata.combining(c)]))
    limpo = " ".join(limpo.split()).upper()
    return [limpo] if len(limpo) > 2 else []

def is_cpf_valido(cpf):
    """Valida CPF com dígitos verificadores"""
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = 11 - (soma % 11)
    if int(cpf[9]) != (0 if d1 >= 10 else d1):
        return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = 11 - (soma % 11)
    if int(cpf[10]) != (0 if d2 >= 10 else d2):
        return False
    return True

def extrair_cpfs_validos(texto):
    """Extrai e valida CPFs"""
    cpfs = set()
    for match in re.finditer(r'(?:\d[^\d]{0,2}){10}\d', str(texto)):
        possivel = re.sub(r'\D', '', match.group(0))
        if len(possivel) == 11 and is_cpf_valido(possivel):
            cpfs.add(f"{possivel[:3]}.{possivel[3:6]}.{possivel[6:9]}-{possivel[9:]}")
    return list(cpfs)

def extrair_telefones(texto):
    """Extrai telefones"""
    telefones = set()
    for match in re.finditer(r'(?:\+?55\s?)?\(?0?[1-9]{2}\)?[\s\-]*(?:9[\s\-]?)?\d{4}[\s\-]?\d{4}', str(texto)):
        num = re.sub(r'\D', '', match.group(0))
        if num.startswith('55') and len(num) >= 12:
            num = num[2:]
        if num.startswith('0') and len(num) >= 11:
            num = num[1:]
        if len(num) in [10, 11]:
            telefones.add(num)
    return list(telefones)

def extrair_emails(texto):
    """Extrai e-mails"""
    emails = set()
    for match in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(texto)):
        emails.add(match.group(0).lower())
    return list(emails)

def processar_arquivo(caminho, campos_selecionados):
    """Processa arquivo e extrai dados"""
    dados = {}
    ext = os.path.splitext(caminho)[1].lower()
    nome_arquivo = os.path.basename(caminho)
    
    try:
        if ext == '.txt':
            with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
                for linha in f:
                    linha_str = str(linha).strip()
                    if not linha_str:
                        continue
                    chaves = set()
                    if 'Nome' in campos_selecionados:
                        nomes = extrair_nomes(linha_str)
                        chaves.update(nomes)
                    if 'CPF' in campos_selecionados:
                        cpfs = extrair_cpfs_validos(linha_str)
                        chaves.update(cpfs)
                    if 'Telefone' in campos_selecionados:
                        tels = extrair_telefones(linha_str)
                        chaves.update(tels)
                    if 'E-mail' in campos_selecionados:
                        emails = extrair_emails(linha_str)
                        chaves.update(emails)
                    
                    for chave in chaves:
                        if chave not in dados:
                            dados[chave] = []
                        dados[chave].append({'arquivo': nome_arquivo, 'dados': linha_str})
        
        elif ext in ['.xlsx', '.xls']:
            xls = pd.ExcelFile(caminho)
            for aba in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=aba)
                df.dropna(how='all', inplace=True)
                
                for idx, row in df.iterrows():
                    linha_str = ' '.join(str(v) for v in row if v and str(v) != 'nan')
                    if not linha_str.strip():
                        continue
                    
                    chaves = set()
                    if 'Nome' in campos_selecionados:
                        nomes = extrair_nomes(linha_str)
                        chaves.update(nomes)
                    if 'CPF' in campos_selecionados:
                        cpfs = extrair_cpfs_validos(linha_str)
                        chaves.update(cpfs)
                    if 'Telefone' in campos_selecionados:
                        tels = extrair_telefones(linha_str)
                        chaves.update(tels)
                    if 'E-mail' in campos_selecionados:
                        emails = extrair_emails(linha_str)
                        chaves.update(emails)
                    
                    for chave in chaves:
                        if chave not in dados:
                            dados[chave] = []
                        dados[chave].append({'arquivo': nome_arquivo, 'aba': aba, 'dados': linha_str})
        
        elif ext == '.csv':
            df = pd.read_csv(caminho)
            for idx, row in df.iterrows():
                linha_str = ' '.join(str(v) for v in row if v and str(v) != 'nan')
                if not linha_str.strip():
                    continue
                
                chaves = set()
                if 'Nome' in campos_selecionados:
                    nomes = extrair_nomes(linha_str)
                    chaves.update(nomes)
                if 'CPF' in campos_selecionados:
                    cpfs = extrair_cpfs_validos(linha_str)
                    chaves.update(cpfs)
                if 'Telefone' in campos_selecionados:
                    tels = extrair_telefones(linha_str)
                    chaves.update(tels)
                if 'E-mail' in campos_selecionados:
                    emails = extrair_emails(linha_str)
                    chaves.update(emails)
                
                for chave in chaves:
                    if chave not in dados:
                        dados[chave] = []
                    dados[chave].append({'arquivo': nome_arquivo, 'dados': linha_str})
    
    except Exception as e:
        st.error(f"Erro ao processar {nome_arquivo}: {str(e)}")
        return None
    
    return dados

# Menu lateral
st.sidebar.markdown("<h3 style='margin-top:0;'>Navegação</h3>", unsafe_allow_html=True)
area_selecionada = st.sidebar.radio(
    "Selecione a funcionalidade:",
    ["1. Comparativo de Dados", "2. Busca Localizada", "3. Histórico de Buscas"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido com ❤️ por bikopv09")

# AREA 1: COMPARATIVO DE DADOS
if area_selecionada == "1. Comparativo de Dados":
    st.subheader("🔄 Comparativo Avançado de Dados")
    st.write("Compare múltiplos arquivos e identifique padrões e duplicatas entre fontes diferentes.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Campos a Comparar")
        usar_nome = st.checkbox("Nome", value=True)
        usar_cpf = st.checkbox("CPF")
        usar_tel = st.checkbox("Telefone")
        usar_email = st.checkbox("E-mail")
    
    with col2:
        st.markdown("### Configurações")
        min_fontes = st.slider("Mínimo de fontes para ocorrência", 2, 10, 2)
    
    campos_selecionados = []
    if usar_nome:
        campos_selecionados.append("Nome")
    if usar_cpf:
        campos_selecionados.append("CPF")
    if usar_tel:
        campos_selecionados.append("Telefone")
    if usar_email:
        campos_selecionados.append("E-mail")
    
    st.markdown("### Upload de Arquivos")
    arquivos_upload = st.file_uploader(
        "Selecione os arquivos (XLSX, XLS, CSV, TXT)",
        type=["xlsx", "xls", "csv", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("🔍 Processar Arquivos"):
        if not arquivos_upload:
            st.error("Por favor, selecione pelo menos um arquivo.")
        elif not campos_selecionados:
            st.error("Por favor, selecione pelo menos um campo para comparar.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            todos_dados = {}
            mapa_arquivos = {}
            
            for idx, uploaded_file in enumerate(arquivos_upload):
                status_text.text(f"Processando arquivo {idx+1}/{len(arquivos_upload)}...")
                
                # Salvar arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                
                try:
                    dados_arquivo = processar_arquivo(tmp_path, campos_selecionados)
                    if dados_arquivo:
                        for chave, ocorrencias in dados_arquivo.items():
                            if chave not in todos_dados:
                                todos_dados[chave] = []
                                mapa_arquivos[chave] = set()
                            todos_dados[chave].extend(ocorrencias)
                            mapa_arquivos[chave].add(idx)
                finally:
                    os.unlink(tmp_path)
                
                progress_bar.progress((idx + 1) / len(arquivos_upload))
            
            status_text.text("Filtrando resultados...")
            
            # Filtrar por mínimo de fontes
            resultados = {
                chave: dados for chave, dados in todos_dados.items()
                if len(mapa_arquivos[chave]) >= min_fontes
            }
            
            if not resultados:
                st.warning(f"Nenhum resultado encontrado com mínimo de {min_fontes} fontes.")
            else:
                st.success(f"✅ Encontrados {len(resultados)} registros!")
                
                # Exibir resultados
                st.markdown("### Resultados da Comparação")
                
                resultado_df = []
                for chave in sorted(resultados.keys()):
                    qtd_ocorrencias = len(mapa_arquivos[chave])
                    arquivos_encontrados = [arquivos_upload[i].name for i in sorted(mapa_arquivos[chave])]
                    resultado_df.append({
                        "Chave": chave,
                        "Ocorrências": qtd_ocorrencias,
                        "Arquivos": ", ".join(arquivos_encontrados)
                    })
                
                df_resultados = pd.DataFrame(resultado_df)
                st.dataframe(df_resultados, use_container_width=True)
                
                # Salvar estado para download
                st.session_state.last_results = {
                    'resultados': resultados,
                    'mapa_arquivos': {k: sorted(list(v)) for k, v in mapa_arquivos.items()},
                    'arquivos': [f.name for f in arquivos_upload]
                }
                
                # Botão de exportação
                if st.button("📥 Exportar Relatório (ZIP)"):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Criar arquivos de exportação
                        txt_path = os.path.join(tmpdir, "relatorio.txt")
                        csv_path = os.path.join(tmpdir, "relatorio.csv")
                        
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write("=== RELATÓRIO DE COMPARATIVO ===\n")
                            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                            f.write(f"Arquivos processados: {len(arquivos_upload)}\n")
                            f.write(f"Campos: {', '.join(campos_selecionados)}\n")
                            f.write(f"Total de registros encontrados: {len(resultados)}\n\n")
                            
                            for chave in sorted(resultados.keys()):
                                f.write(f"\n[{chave}]\n")
                                f.write(f"Ocorrências: {len(mapa_arquivos[chave])}\n")
                                for ocorrencia in resultados[chave]:
                                    f.write(f"  - {ocorrencia['arquivo']}: {ocorrencia['dados']}\n")
                        
                        df_resultados.to_csv(csv_path, index=False, encoding='utf-8')
                        
                        # Criar ZIP
                        zip_path = os.path.join(tmpdir, "Relatorio_SearchCRT.zip")
                        with zipfile.ZipFile(zip_path, 'w') as zf:
                            zf.write(txt_path, os.path.basename(txt_path))
                            zf.write(csv_path, os.path.basename(csv_path))
                        
                        with open(zip_path, 'rb') as f:
                            st.download_button(
                                label="📥 Download Relatório",
                                data=f.read(),
                                file_name=f"Relatorio_SearchCRT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip"
                            )

# AREA 2: BUSCA LOCALIZADA
elif area_selecionada == "2. Busca Localizada":
    st.subheader("🎯 Busca Localizada")
    st.write("Localize registros específicos em suas planilhas.")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_busca = st.selectbox(
            "Tipo de busca:",
            ["Nome", "CPF", "Telefone", "E-mail", "Texto Livre"]
        )
    
    with col2:
        termo_busca = st.text_input("Digite o termo a buscar:")
    
    arquivo_busca = st.file_uploader(
        "Selecione a planilha para busca:",
        type=["xlsx", "xls", "csv"]
    )
    
    if st.button("🔎 Buscar"):
        if not arquivo_busca:
            st.error("Por favor, selecione um arquivo.")
        elif not termo_busca:
            st.error("Por favor, digite um termo para buscar.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo_busca.name)[1]) as tmp:
                tmp.write(arquivo_busca.getbuffer())
                tmp_path = tmp.name
            
            try:
                resultados_busca = []
                
                ext = os.path.splitext(tmp_path)[1].lower()
                if ext in ['.xlsx', '.xls']:
                    xls = pd.ExcelFile(tmp_path)
                    for aba in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name=aba)
                        df_str = df.astype(str)
                        
                        for idx, row in df_str.iterrows():
                            encontrado = False
                            if tipo_busca == "Nome":
                                for val in row:
                                    if termo_busca.upper() in extrair_nomes(val):
                                        encontrado = True
                                        break
                            elif tipo_busca == "CPF":
                                cpfs_busca = extrair_cpfs_validos(termo_busca)
                                if cpfs_busca:
                                    for val in row:
                                        if cpfs_busca[0] in extrair_cpfs_validos(val):
                                            encontrado = True
                                            break
                            elif tipo_busca == "Telefone":
                                tels_busca = extrair_telefones(termo_busca)
                                if tels_busca:
                                    for val in row:
                                        if tels_busca[0] in extrair_telefones(val):
                                            encontrado = True
                                            break
                            elif tipo_busca == "E-mail":
                                emails_busca = extrair_emails(termo_busca)
                                if emails_busca:
                                    for val in row:
                                        if emails_busca[0] in extrair_emails(val):
                                            encontrado = True
                                            break
                            else:  # Texto Livre
                                for val in row:
                                    if termo_busca.lower() in str(val).lower():
                                        encontrado = True
                                        break
                            
                            if encontrado:
                                dados_linha = {f"Col_{i}": v for i, v in enumerate(row)}
                                dados_linha["Aba"] = aba
                                resultados_busca.append(dados_linha)
                
                elif ext == '.csv':
                    df = pd.read_csv(tmp_path)
                    df_str = df.astype(str)
                    
                    for idx, row in df_str.iterrows():
                        encontrado = False
                        if tipo_busca == "Texto Livre":
                            for val in row:
                                if termo_busca.lower() in str(val).lower():
                                    encontrado = True
                                    break
                        else:
                            for val in row:
                                if termo_busca.lower() in str(val).lower():
                                    encontrado = True
                                    break
                        
                        if encontrado:
                            resultados_busca.append(dict(row))
                
                if not resultados_busca:
                    st.warning(f"Nenhum resultado encontrado para '{termo_busca}'.")
                else:
                    st.success(f"✅ Encontrados {len(resultados_busca)} registros!")
                    
                    df_busca = pd.DataFrame(resultados_busca)
                    st.dataframe(df_busca, use_container_width=True)
                    
                    # Download dos resultados
                    csv_data = df_busca.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="📥 Download Resultados (CSV)",
                        data=csv_data,
                        file_name=f"busca_{tipo_busca}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            finally:
                os.unlink(tmp_path)

# AREA 3: HISTÓRICO
elif area_selecionada == "3. Histórico de Buscas":
    st.subheader("📋 Histórico de Operações")
    st.write("Visualize e gerencie seu histórico de buscas e comparativos.")
    
    if st.session_state.last_results:
        st.markdown("### Último Resultado")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Registros Encontrados", len(st.session_state.last_results['resultados']))
        with col2:
            st.metric("Arquivos Processados", len(st.session_state.last_results['arquivos']))
        with col3:
            st.metric("Timestamp", datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        st.markdown("### Arquivos Processados")
        for arq in st.session_state.last_results['arquivos']:
            st.write(f"• {arq}")
    else:
        st.info("Nenhuma busca realizada ainda. Execute uma busca para visualizar o histórico.")

st.markdown("---")
st.caption("🔒 SearchCRT v1.0 - Análise de Dados Confidencial | Desenvolvido em Streamlit")
