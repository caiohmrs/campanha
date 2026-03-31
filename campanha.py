import gspread
import io
from datetime import datetime
import pandas as pd
import streamlit as st
import extra_streamlit_components as stx
from streamlit_js_eval import get_geolocation
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
import xlsxwriter
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Diferenciando os tipos de credenciais
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build


# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="COMANDO 2026", 
    page_icon="🧢", 
)


# --- ESTILIZAÇÃO VISUAL UNIFICADA "COMANDO 2026" - VERSÃO FINAL CORRIGIDA ---
st.markdown(f"""
    <style>
        /* 0. CONFIGURAÇÕES TÉCNICAS E FONTES */
        @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Roboto:wght@400;700&display=swap');

        :root {{
            color-scheme: light !important;
        }}

        [data-testid="stVerticalBlock"] > div {{
            width: 100%;
            
        }}

        .stApp {{
            /* Gradiente diagonal cinza azulado premium - Opção B */
            background: linear-gradient(135deg, #E9ECEF 0%, #ADB5BD 100%) !important;
            background-attachment: fixed !important;
            color: #1D1D1B !important;
            font-family: 'Roboto', sans-serif;
        }}

        /* Transparência total dos containers para o gradiente brilhar */
        [data-testid="stAppViewContainer"], 
        [data-testid="stHeader"], 
        [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"] {{
            background-color: transparent !important;
        }}
        /* 2. SIDEBAR AMARELA */
        section[data-testid="stSidebar"] {{
            background-color: #FFEB00 !important;
            border-right: 5px solid #1D1D1B !important;
        }}

        /* 3. TÍTULOS ESTILO CARTAZ */
        h1, h2, h3 {{
            font-family: 'Archivo Black', sans-serif !important;
            text-transform: uppercase;
            font-style: italic;
            color: #1D1D1B !important;
            text-align: center;
        }}

        /* 4. PADRONIZAÇÃO TOTAL DE BOTÕES (MISSÕES + POPOVER) */
        .stButton > button, 
        div[data-testid="stPopover"] > button {{
            background-color: #E20613 !important;
            color: #FFFFFF !important;
            font-family: 'Archivo Black', sans-serif !important;
            border: 3px solid #1D1D1B !important;
            border-radius: 0px !important;
            text-transform: uppercase !important;
            box-shadow: 4px 4px 0px #1D1D1B !important;
            width: 100% !important;
            min-height: 3.5rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* 5. ABAS (TABS) - ESTILO ADESIVO URBANO (ALINHAMENTO TRAVADO) */
        
        /* Container das abas */
        div[data-baseweb="tab-list"] {{
            gap: 0px !important; /* Zerado para controlarmos via margem da aba */
            background-color: transparent !important;
            padding: 10px 0 !important;
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }}  

        /* Estilo base de cada aba (botão inativo) */
        button[data-baseweb="tab"] {{
            background-color: #FFEB00 !important; /* Amarelo */
            border: 3px solid #1D1D1B !important;
            border-radius: 0px !important;
            padding: 10px 20px !important;
            font-family: 'Archivo Black', sans-serif !important;
            text-transform: uppercase !important;
            font-style: italic !important;
            color: #1D1D1B !important;
            box-shadow: 4px 4px 0px #1D1D1B !important;
            transition: 0.2s !important;
            margin: 0 6px 10px 6px !important; /* Mantém a distância fixa entre elas */
            transform: none !important; /* Trava a posição */
        }}

        /* Aba Selecionada (Ativa) - FIXA NO LUGAR, APENAS MUDA COR */
        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: #E20613 !important; /* Vira Vermelho */
            color: #FFFFFF !important;
            box-shadow: 4px 4px 0px #1D1D1B !important; /* Mesma sombra da inativa */
            transform: none !important; /* Sem pular para o lado */
        }}

        /* Efeito de passar o mouse APENAS nas inativas */
        button[data-baseweb="tab"][aria-selected="false"]:hover {{
            transform: translate(-2px, -2px) !important;
            box-shadow: 6px 6px 0px #1D1D1B !important;
        }}

        /* Remover a linha vermelha/azul padrão embaixo das abas */
        div[data-baseweb="tab-highlight"] {{
            display: none !important;
        }}
        
        /* Ajuste de texto dentro da aba */
        button[data-baseweb="tab"] p {{
            font-size: 0.85rem !important;
            font-weight: bold !important;
            color: inherit !important;
            margin: 0 !important;
        }}

        /* 6. OUTROS COMPONENTES */
        
        div[data-testid="stExpander"], div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            border: 3px solid #1D1D1B !important;
            background-color: #F4F4F4 !important;
            box-shadow: 6px 6px 0px #FFEB00 !important;
        }}

        .stTextInput input {{
            border: 2px solid #1D1D1B !important;
            text-align: center !important;
            background-color: #FFFFFF !important;
        }}

        /* --- LIMPEZA DE INTERFACE (MANTENDO O BOTÃO DA SIDEBAR) --- */
        
        /* 1. Remove o rodapé "Made with Streamlit" */
        footer {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* 2. Remove a linha colorida no topo */
        div[data-testid="stDecoration"] {{
            display: none !important;
        }}

        /* 3. OCULTA APENAS O LADO DIREITO DO HEADER (GitHub, Fork, Deploy) */
        /* Isso preserva o lado esquerdo onde fica o botão da Sidebar */
        [data-testid="stHeaderActionElements"], .stDeployButton {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* 4. Deixa o fundo do header transparente para não parecer uma barra cinza */
        header[data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0) !important;
            color: #1D1D1B !important;
        }}

        /* 5. Ajuste de espaço para o conteúdo */
        .block-container {{
            padding-top: 2rem !important;
        }}
        /* Ajuste Mobile */
        @media (max-width: 768px) {{
            button[data-baseweb="tab"] {{
                font-size: 0.7rem !important;
                padding: 8px 10px !important;
            }}
        }}

        /* OCULTAR O BOTÃO DE FECHAR (X) DOS DIALOGS */
        button[aria-label="Close"] {{
            display: none !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Meta tag adicional para forçar Light Mode no Mobile
st.markdown('<meta name="color-scheme" content="light">', unsafe_allow_html=True)

#agora

agora = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)


# --- FUNÇÕES DE APOIO ---


# --- MODAIS DE PRESENÇA (DIALOG) ---

@st.dialog("REGISTRO DE ENTRADA")
def modal_checkin(u, agora):
    st.markdown("""
        <div style='background-color: #FFEB00; padding: 15px; border: 3px solid #1D1D1B; text-align: center; margin-bottom: 20px;'>
            <h2 style='margin:0; font-size: 1.5rem; font-style: italic; color: #1D1D1B;'>INICIAR MISSÃO</h2>
        </div>
    """, unsafe_allow_html=True)
    
    foto_in = st.camera_input("FOTO OBRIGATÓRIA", key="cam_in_dialog")
    
    if st.button("CONFIRMAR CHECK-IN AGORA", width='stretch', type="primary"):
        if foto_in:
            agora_real = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
            gps_in = st.session_state.get('last_coords', "Sem GPS")
            with st.status("🚀 PROCESSANDO REGISTRO...", expanded=True) as status:
                nome_img = f"checkin_{u['Nome']}_{agora_real.strftime('%d-%m-%Y_%H-%M')}.jpg"
                link = salvar_foto_drive(foto_in, nome_img)
                
                if link:
                    registrar_acao(u['ID_Usuario'], f"Check-in | Foto: {link}", localizacao=gps_in)
                    try:
                        horario_formatado = agora_real.strftime("%Y-%m-%d %H:%M:%S")
                        cookie_manager.set("comando2026_checkin_time", horario_formatado)
                    except Exception:
                        pass
                    
                    status.update(label="✅ ENTRADA REGISTRADA!", state="complete")
                    time.sleep(2)
                    st.rerun()
        else:
            st.error("⚠️ VOCÊ PRECISA TIRAR A FOTO!")

@st.dialog("REGISTRO DE SAÍDA")
def modal_checkout(u, agora):
    st.markdown("""
        <div style='background-color: #FFEB00; padding: 15px; border: 3px solid #1D1D1B; text-align: center; margin-bottom: 20px;'>
            <h2 style='margin:0; font-size: 1.5rem; font-style: italic; color: #1D1D1B;'>FINALIZAR MISSÃO</h2>
        </div>
    """, unsafe_allow_html=True)
    
    foto_out = st.camera_input("FOTO OBRIGATÓRIA", key="cam_out_dialog")
    st.divider()
    
    st.markdown("### 📊 RELATO DO DIA")
    clima = st.select_slider(
        "COMO FOI O TRABALHO HOJE?",
        options=["⚠️ DIFÍCIL", "😐 NORMAL", "🔥 EXCELENTE"],
        value="😐 NORMAL"
    )
    obs = st.text_area("OBSERVAÇÕES:", placeholder="Ex: chuva, falta de material...", height=80)
    
    if st.button("CONFIRMAR SAÍDA", width='stretch', type="primary"):
        if foto_out:
            agora_real = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
            gps_out = st.session_state.get('last_coords', "Sem GPS")
            
            with st.spinner("📡 ENVIANDO DADOS..."):
                nome_img = f"checkout_{u['Nome']}_{agora_real.strftime('%d-%m-%Y_%H-%M')}.jpg"
                link_drive = salvar_foto_drive(foto_out, nome_img)
                
                if link_drive:
                    # Texto da ação fica limpo
                    acao_texto = f"Check-out | Foto: {link_drive}"
                    
                    # Feedback consolidado (Clima + Obs) para a nova coluna
                    feedback_texto = f"{clima} | Obs: {obs if obs else 'Nenhuma'}"
                    
                    # Chama a função com o novo parâmetro
                    registrar_acao(u['ID_Usuario'], acao_texto, localizacao=gps_out, feedback=feedback_texto)
                    
                    try:
                        if "comando2026_checkin_time" in cookie_manager.get_all():
                            cookie_manager.delete("comando2026_checkin_time")
                    except: pass
                    
                    st.success("✅ TUDO SALVO! BOM DESCANSO.")
                    time.sleep(2)
                    st.rerun()
        else:
            st.error("⚠️ VOCÊ PRECISA TIRAR A FOTO PARA ENCERRAR!")



def _get_drive_credentials():
    """Usa OAuthCredentials (Refresh Token) para os 15GB do Drive"""
    try:
        creds_info = st.secrets["google_drive"]
        creds = OAuthCredentials(
            token=None,
            refresh_token=creds_info["refresh_token"],
            token_uri=creds_info["token_uri"],
            client_id=creds_info["client_id"],
            client_secret=creds_info["client_secret"]
        )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        return creds
    except Exception as e:
        st.error(f"Erro ao carregar credenciais do Drive: {e}")
        return None

def _get_sheets_credentials():
    """Service Account - Para o Sheets (Logs/Usuarios)"""
    try:
        creds_dict = st.secrets.get("connections", {}).get("gsheets")
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        return ServiceAccountCredentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception as e:
        st.error(f"Erro credenciais Sheets: {e}")
        return None

def _get_gspread_client():
    creds = _get_sheets_credentials()
    return gspread.authorize(creds) if creds else None

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        sheet_id = st.secrets["planilha"]["id"]
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nome_aba}"
        df = pd.read_csv(url)
        return df.astype(str).apply(lambda x: x.str.strip())
    except Exception as e:
        return None

def salvar_foto_drive(foto_arquivo, nome_arquivo):
    try:
        creds = _get_drive_credentials() 
        if not creds: return None
        drive_service = build('drive', 'v3', credentials=creds)
        id_pasta_fotos = st.secrets["google_drive"]["id_pasta_fotos"]
        file_metadata = {'name': nome_arquivo, 'parents': [id_pasta_fotos]}
        foto_bytes = io.BytesIO(foto_arquivo.getvalue())
        media = MediaIoBaseUpload(foto_bytes, mimetype='image/jpeg', resumable=False)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        drive_service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Erro no Drive: {e}")
        return None

def registrar_novo_contrato_admin(id_usuario, nome_arquivo, link_original):
    """Cria uma nova linha na aba Contratos para o colaborador assinar"""
    try:
        client = _get_gspread_client()
        if client is None: return False
        planilha_id = st.secrets["planilha"]["id"]
        aba = client.open_by_key(planilha_id).worksheet("Contratos")
        
        # Estrutura: ID_Usuario | Nome_Arquivo | Link_Original | Status | Link_Assinado
        aba.append_row([
            str(id_usuario), 
            str(nome_arquivo), 
            str(link_original), 
            "Aguardando Assinatura", 
            "" # Link_Assinado começa vazio
        ])
        return True
    except Exception as e:
        st.error(f"Erro ao registrar contrato na planilha: {e}")
        return False

def registrar_acao(id_usuario, tipo_acao, localizacao="Não informada", feedback=""):

    
    try:
        client = _get_gspread_client()
        if client is None: return
        planilha_id = st.secrets["planilha"]["id"]
        planilha = client.open_by_key(planilha_id)
        aba = planilha.worksheet("Logs")
        agora_br = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
        endereco = "Processando..."
        if "," in localizacao:
            endereco = obter_endereco_simples(localizacao)
        else:
            endereco = "Sem GPS"
        
        aba.append_row([
            agora_br.strftime("%Y%m%d%H%M%S"),
            str(id_usuario),
            str(tipo_acao),
            agora_br.strftime("%d/%m/%Y %H:%M:%S"),
            str(localizacao),
            str(endereco),
            str(feedback)
        ])
        st.toast(f"✅ Log: {tipo_acao}")
    except Exception as e:
        st.error(f"Falha ao registrar log: {e}")

def salvar_documento_drive(doc_arquivo, nome_arquivo):
    try:
        creds = _get_drive_credentials() 
        if not creds: return None
        drive_service = build('drive', 'v3', credentials=creds)
        id_pasta_contratos = st.secrets["google_drive"]["id_pasta_contratos"]
        file_metadata = {'name': nome_arquivo, 'parents': [id_pasta_contratos]}
        doc_bytes = io.BytesIO(doc_arquivo.getvalue())
        media = MediaIoBaseUpload(doc_bytes, mimetype='application/pdf', resumable=False)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        drive_service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Erro no Drive (Docs): {e}")
        return None

def atualizar_contrato_enviado(id_usuario, nome_arquivo, link_drive):
    """Atualiza o link do contrato E o status na planilha"""
    try:
        client = _get_gspread_client()
        if client is None: return False
        planilha_id = st.secrets["planilha"]["id"]
        aba = client.open_by_key(planilha_id).worksheet("Contratos")
        
        dados = aba.get_all_records()
        linha_para_atualizar = None
        
        for i, linha in enumerate(dados, start=2):
            if str(linha.get('ID_Usuario')) == str(id_usuario) and \
               str(linha.get('Nome_Arquivo')) == str(nome_arquivo):
                linha_para_atualizar = i
                break
        
        if linha_para_atualizar:
            cabecalho = aba.row_values(1)
            
            # 1. Atualiza o Link do Assinado
            if 'Link_Assinado' in cabecalho:
                col_link = cabecalho.index('Link_Assinado') + 1
                aba.update_cell(linha_para_atualizar, col_link, link_drive)
            
            # 2. Atualiza o Status para 'Enviado / Em Análise'
            if 'Status' in cabecalho:
                col_status = cabecalho.index('Status') + 1
                aba.update_cell(linha_para_atualizar, col_status, "Assinado / Em Análise")
                
            return True
        return False
    except Exception as e:
        st.error(f"Falha ao atualizar contrato: {e}")
        return False

def sanitize_whatsapp(v: str) -> str:
    """Limpa o número, corrige erro de float (.0) e garante o formato 55 + DDD + 9 + Número"""
    if v is None or str(v).lower() == "nan" or str(v).strip() == "":
        return ""
    
    # 1. Transforma em string e remove o ".0" que o Excel/Pandas coloca em números
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    
    # 2. Mantém apenas os dígitos (remove +, -, espaços e parênteses)
    nums = "".join(filter(str.isdigit, s))
    
    # 3. CORREÇÃO DE ERRO DE FLOAT (O zero extra no final)
    # Se o número tem 12 dígitos, termina em 0 e NÃO começa com 55, 
    # é quase certeza que o zero final é o ".0" que virou "0".
    if len(nums) == 12 and nums.endswith("0") and not nums.startswith("55"):
        nums = nums[:-1]

    # 4. GARANTIR O 55 (BRASIL) E O 9 (CELULAR)
    # Se o número tem 11 dígitos (DDD + 9 + 8 dígitos), só adiciona o 55
    if len(nums) == 11:
        return "55" + nums
    
    # Se o número tem 10 dígitos (DDD + 8 dígitos), falta o 55 e o 9
    if len(nums) == 10:
        return "55" + nums[:2] + "9" + nums[2:]
    
    # Se o número já começa com 55
    if nums.startswith("55"):
        # Se tem 12 dígitos (55 + DDD + 8 dígitos), falta o 9
        if len(nums) == 12:
            return "55" + nums[2:4] + "9" + nums[4:]
        return nums

    return nums

def obter_endereco_simples(coords_str):
    """Converte 'lat, lon' em um endereço curto (Rua ou Bairro)"""
    if not coords_str or "GPS" in coords_str or "," not in coords_str:
        return "Local não identificado"
    
    try:
        geolocator = Nominatim(user_agent="comando2026_geocoder")
        location = geolocator.reverse(coords_str, timeout=10)
        address = location.raw.get('address', {})
        
        # Tenta pegar as informações mais relevantes (Rua, Bairro ou Cidade)
        rua = address.get('road', '')
        bairro = address.get('suburb', '')
        cidade = address.get('city', address.get('town', ''))
        
        if rua:
            return f"{rua}, {bairro}".strip(", ")
        return f"{bairro}, {cidade}".strip(", ")
    except:
        return "Endereço indisponível"


# --- LOGICA DE COOKIES ---
cookie_manager = stx.CookieManager()
todos_os_cookies = cookie_manager.get_all()

# --- ESTADO DE LOGIN ---
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "logout_em_andamento" not in st.session_state:
    st.session_state["logout_em_andamento"] = False

if "mensagem_exibida" not in st.session_state:
    st.session_state["mensagem_exibida"] = False

# Autologin via Cookie (Só tenta se não estiver saindo)
if todos_os_cookies and not st.session_state["logout_em_andamento"]:
    user_id_cookie = todos_os_cookies.get("comando2026_user_id")
    
    if user_id_cookie and st.session_state["usuario_logado"] is None:
        df_usuarios = carregar_dados("Usuarios")
        if df_usuarios is not None:
            user_match = df_usuarios[df_usuarios['ID_Usuario'].str.lower() == user_id_cookie.lower().strip()]
            if not user_match.empty:
                st.session_state["usuario_logado"] = user_match.iloc[0].to_dict()
                st.rerun()

# --- TELA DE LOGIN ---
if st.session_state["usuario_logado"] is None:
    # Reseta o sinal de logout para permitir novo login
    st.session_state["logout_em_andamento"] = False
    
    # Criamos um espaço no topo para centralizar verticalmente
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    
    with col_l2:
        # TÍTULO ESTILIZADO (Igual às artes)
        st.markdown("""
            <h1 style='text-align: center; font-size: 4rem; line-height: 0.9; margin-bottom: 20px; margin-top: -100px'>
                Max Maciel<br><span style='color: #E20613;'>🧢 2026</span>
            </h1>
        """, unsafe_allow_html=True)
        
# CONTAINER DE LOGIN (Estilo Card Amarelo Centralizado)
        with st.container():
            st.markdown("""
                <div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 10px 10px 0px #1D1D1B; text-align: center;'>
                    <h2 style='margin-top: 0; font-size: 1.5rem; font-family: "Archivo Black", sans-serif; font-style: italic; text-transform: uppercase; color: #1D1D1B;'>
                        Faça seu login abaixo:
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            # Espaço entre o título e o input
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            
            # O input e o botão herdarão o estilo centralizado se estiverem dentro de colunas ou se o CSS global permitir
            # Mas para garantir o visual dentro da caixa, costumamos usar este truque de CSS:
            email_input = st.text_input("ID DE USUÁRIO (E-MAIL)", placeholder="seu@email.com", label_visibility="collapsed")
            
            if st.button("ENTRAR NO PAINEL", width='stretch', type="primary"):
                with st.spinner("VALIDANDO..."):
                    df_usuarios = carregar_dados("Usuarios")
                    if df_usuarios is not None:
                        user_match = df_usuarios[df_usuarios['ID_Usuario'].str.lower() == email_input.lower().strip()]
                        if not user_match.empty:
                            st.session_state["usuario_logado"] = user_match.iloc[0].to_dict()
                            cookie_manager.set("comando2026_user_id", email_input.lower().strip(), key="set_user_cookie")
                            st.rerun()
                        else:
                            st.error("❌ ID NÃO ENCONTRADO")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Primeiro acesso? Solicite seu ID ao seu supervisor.")

    st.stop()

# --- VARIÁVEIS DO USUÁRIO (SÓ APÓS LOGIN) ---
u = st.session_state["usuario_logado"]
cargo_limpo = str(u['Cargo']).strip().lower()

# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Perfil")
    st.write(f"Olá, **{u['Nome'].split()[0]}**")
    st.caption(f"Cargo: {u['Cargo']}")
    
    # --- BOTÃO DE ATUALIZAR ---
    if st.button("🔄 ATUALIZAR PAINEL", width="stretch"):
        with st.spinner("Buscando dados..."):
            st.cache_data.clear() # Limpa o cache para forçar nova leitura da planilha
            st.rerun()

    if st.button("Sair / Trocar Conta", width='stretch'):
        # 1. Sinaliza que o logout começou (bloqueia auto-login)
        st.session_state["logout_em_andamento"] = True
        st.session_state["usuario_logado"] = None
        st.session_state["mensagem_exibida"] = False 
        
        # 2. Tenta deletar os cookies com chaves únicas
        try:
            cookie_manager.delete("comando2026_user_id", key="del_user")
        except:
            pass
            
        try:
            cookie_manager.delete("comando2026_checkin_time", key="del_check")
        except:
            pass

        st.success("Saindo e limpando dados...")
        
        # 3. Limpa as memórias da sessão e os caches de dados
        st.session_state.clear()
        st.cache_data.clear()
        
        # 4. Pausa crucial para o navegador apagar os cookies de fato
        import time
        time.sleep(2)
        
        # 5. Recarrega a página, voltando para o login
        st.rerun()

        
# --- CABEÇALHO BEM-VINDO (VERSÃO SEM QUEBRA DE LINHA) ---
nome_primeiro = u['Nome'].split()[0].upper()


st.markdown(f"""
    <div style='
        background-color: #FFEB00; 
        padding: 15px; 
        border: 4px solid #1D1D1B; 
        box-shadow: 8px 8px 0px #1D1D1B; 
        text-align: center;
        width: 90%;
        margin: 10px auto 25px auto;
    '>
        <h3 style='
            margin: 0; 
            font-size: 1.5rem; 
            font-family: "Archivo Black", sans-serif; 
            font-style: italic; 
            color: #1D1D1B;
            line-height: 1;
        '>
            BEM-VINDO,
        </h3>
        <h1 style='
            margin: 0; 
            font-size: 2.2rem; 
            font-family: "Archivo Black", sans-serif; 
            font-style: italic; 
            text-transform: uppercase; 
            color: #E20613;
            line-height: 1.1;
            white-space: nowrap;  
            overflow: hidden;     
            text-overflow: clip; 
            margin-top: -30px;
        '>
            {nome_primeiro}
        </h1>
    </div>
""", unsafe_allow_html=True)


# --- VISÃO: COLABORADOR ---
if cargo_limpo == "colaborador":
    
    # 1. CARREGAMENTO PRÉVIO DA MENSAGEM (Define 'm' logo no início)
    df_msgs = carregar_dados("Mensagens")
    df_usuarios = carregar_dados("Usuarios")
    df_logs = carregar_dados("Logs")
    m = None 

# --- NOVO: RESUMO PESSOAL (ESTILO FAIXA CLEAN) ---
    hoje_str = agora.strftime("%d/%m/%Y")
    meus_logs_hoje = df_logs[(df_logs['ID_Usuario'] == u['ID_Usuario']) & (df_logs['Data_Hora'].str.contains(hoje_str))]
    qtd_acoes_hoje = len(meus_logs_hoje)
    
    st.markdown(f"""
        <div style='
            background-color: #FFEB00;
            border-top: 2px solid #1D1D1B;
            border-bottom: 2px solid #1D1D1B;
            padding: 6px 0;
            margin: 10px 0 25px 0;
            display: flex;
            justify-content: center;
            gap: 40px;
            font-family: "Archivo Black", sans-serif;
            text-transform: uppercase;
            font-style: italic;
        '>
            <span style='color: #1D1D1B; font-size: 0.9rem;'>
                <span style='color: #E20613;'>●</span> AÇÕES HOJE: {qtd_acoes_hoje}
            </span>
            <span style='color: #1D1D1B; font-size: 0.9rem;'>
                <span style='color: #E20613;'>●</span> STATUS: {'ATIVO' if qtd_acoes_hoje > 0 else 'OFF'}
            </span>
        </div>
    """, unsafe_allow_html=True)

    if df_msgs is not None and not df_msgs.empty:
        # Filtra pelo ID do Grupo
        msg_grupo = df_msgs[df_msgs['ID_Alvo'].astype(str).str.strip() == str(u['ID_Grupo']).strip()]
        
        if not msg_grupo.empty:
            m = msg_grupo.iloc[-1]
            
            # --- LÓGICA DE TELA DE BLOQUEIO (SPLASH SCREEN) ---
            if not st.session_state["mensagem_exibida"]:
                st.markdown(f"""
                    <div style='background-color: #FFEB00; padding: 40px 20px; border: 5px solid #1D1D1B; 
                                box-shadow: 10px 10px 0px #1D1D1B; text-align: center; margin-top: 20px;'>
                        <h1 style='font-family: "Archivo Black", sans-serif; font-style: italic; color: #1D1D1B; font-size: 2.5rem;'>
                            COMANDO 2026<br><span style='color: #E20613;'>INFORME DO DIA</span>
                        </h1>
                        <hr style='border: 2px solid #1D1D1B; margin: 20px 0;'>
                        <p style='font-size: 1.4rem; font-weight: bold; color: #1D1D1B; line-height: 1.4;'>
                            {m['Mensagem_Inicial']}
                        </p>
                    </div>
                    <br>
                """, unsafe_allow_html=True)
                
                if st.button("✅ LI AS INSTRUÇÕES E QUERO ENTRAR", width='stretch', type="primary"):
                    st.session_state["mensagem_exibida"] = True
                    st.rerun()
                st.stop()

    # 3. CAPTURA DE GPS COMPACTA
    location_data = get_geolocation()
    col_status, col_btn = st.columns([3, 1])
    with col_status:
        if location_data:
            try:
                lat = location_data['coords']['latitude']
                lon = location_data['coords']['longitude']
                st.session_state['last_coords'] = f"{lat},{lon}"
                st.markdown("🟢 **GPS ATIVO**")
            except:
                st.session_state['last_coords'] = "Erro GPS"
                st.markdown("🔴 **ERRO GPS**")
        else:
            st.session_state['last_coords'] = "Aguardando..."
            st.markdown("🟡 **BUSCANDO SINAL...**")
    with col_btn:
        if st.button("🔄", help="Atualizar GPS"):
            st.rerun()

    # 4. ABAS DE CONTEÚDO
    tab_missoes, tab_contratos = st.tabs(["🚀 Missões e Presença", "📄 Meus Contratos"])

    with tab_missoes:
        # --- REGISTRO DE PRESENÇA ---
        st.divider()
        st.markdown("""
            <div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 8px 8px 0px #1D1D1B; text-align: center; margin-bottom: 25px;'>
                <h2 style='margin:0; font-size: 1.8rem; font-style: italic; color: #1D1D1B;'>REGISTRO DE PRESENÇA</h2>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏁 ENTRADA (CHECK-IN)", width='stretch', key="btn_modal_in"):
                modal_checkin(u, agora)
        with c2:
            if st.button("🏁 SAÍDA (CHECK-OUT)", width='stretch', key="btn_modal_out"):
                modal_checkout(u, agora)

        # --- SEÇÃO DE MISSÕES ---
        st.divider()
        st.markdown("""
            <div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 8px 8px 0px #1D1D1B; text-align: center; margin-bottom: 25px;'>
                <h2 style='margin:0; font-size: 1.8rem; font-style: italic; color: #1D1D1B;'>🚀 MISSÕES DIÁRIAS</h2>
            </div>
        """, unsafe_allow_html=True)

        # Lógica de extração segura da tarefa
        t_txt = ""
        if m is not None:
            val_planilha = str(m.get('Tarefa_Direcionada', '')).strip()
            if val_planilha.lower() != 'nan' and val_planilha != "":
                t_txt = val_planilha.upper()

        if not t_txt:
            t_txt = "MOBILIZAÇÃO GERAL E PANFLETAGEM"

        with st.container(border=True): 
            st.markdown(f"<h3 style='text-align: center; color: #1D1D1B; margin-bottom: 10px;'>🚩 MISSÃO PRIORITÁRIA</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-weight: bold; font-size: 1.1rem; color: #E20613;'>{t_txt}</p>", unsafe_allow_html=True)
            
            if st.button(f"CONCLUIR MISSÃO DE HOJE", width='stretch', key="btn_tarefa_fixa"):
                registrar_acao(u['ID_Usuario'], f"CONCLUIU: {t_txt}", localizacao=st.session_state.get('last_coords'))
                st.success("MISSÃO REGISTRADA COM SUCESSO!")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- AÇÕES DE REDE ---
        st.markdown("<h3 style='font-size: 1.2rem;'>📲 AÇÕES DE REDE</h3>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            if st.button("📸 CURTA, COMENTE E COMPARTILHE NOSSO ÚLTIMO POST!", width='stretch', key="fixo_insta"):
                registrar_acao(u['ID_Usuario'], "AÇÃO: INTERAÇÃO INSTAGRAM", localizacao=st.session_state.get('last_coords'))
                st.markdown(f"""
                    <a href="https://www.instagram.com/maxmacieldf/" target="_blank">
                        <div style='background-color: #1D1D1B; color: #FFEB00; text-align: center; padding: 10px; border: 2px solid #FFEB00; font-weight: bold; font-size: 0.8rem;'>
                            ABRIR PERFIL DO MAX ↗️
                        </div>
                    </a>
                """, unsafe_allow_html=True)

        with col_m2:
            if st.button("💬 TRAGA UM NOVO AMIGO PARA SER COLABORADOR!", width='stretch', key="fixo_whats"):
                registrar_acao(u['ID_Usuario'], "AÇÃO: TRAZER NOVO COLABORADOR!", localizacao=st.session_state.get('last_coords'))
                mensagem_pronta = "Salve! Já acompanha o trabalho do Max Maciel pelo DF?? Sou colaborador dele e estou muito feliz com o trabalho que estamos fazendo. Vamos juntos nessa campanha? 🚀 https://forms.gle/NzJy6NEynbaPyD6w6"
                msg_url = urllib.parse.quote(mensagem_pronta)
                st.markdown(f"""
                    <a href="https://wa.me/?text={msg_url}" target="_blank">
                        <div style='background-color: #1D1D1B; color: #FFEB00; text-align: center; padding: 10px; border: 2px solid #FFEB00; font-weight: bold; font-size: 0.8rem;'>
                            ESCOLHER AMIGO ↗️
                        </div>
                    </a>
                """, unsafe_allow_html=True)

        with tab_contratos:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                
                # --- NOVO: BLOCO DE SOLICITAÇÃO DE CONTRATO ---
                st.markdown("""
                    <div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 8px 8px 0px #1D1D1B; text-align: center; margin-bottom: 20px;'>
                        <h2 style='margin:0; font-size: 1.3rem; font-family: "Archivo Black", sans-serif; font-style: italic; color: #1D1D1B;'>📝 NOVO CONTRATO</h2>
                        <p style='margin:5px 0 0 0; font-size: 0.9rem; font-weight: bold;'>VOCÊ AINDA NÃO GEROU SEU CONTRATO?</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Link para o formulário (Substitua o link abaixo pelo seu link real)
                url_formulario = "https://forms.gle/9fqxvN8XfCmTRh9EA" 
                
                st.link_button("📋 PREENCHER DADOS PARA GERAR CONTRATO", url_formulario, width='stretch', type="primary")
                
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                st.divider()
        
                st.subheader("📄 Meus Documentos")
                df_contratos = carregar_dados("Contratos")
                if df_contratos is not None:
                    meus_docs = df_contratos[df_contratos['ID_Usuario'].astype(str) == str(u['ID_Usuario'])]
                    if not meus_docs.empty:
                        for _, doc in meus_docs.iterrows():
                            with st.container(border=True):
                                st.write(f"**Doc:** {doc['Nome_Arquivo']}")
                                st.link_button("📥 Baixar Original", doc['Link_Original'], width='stretch')
                                arq = st.file_uploader("Upload Assinado (PDF)", type=['pdf'], key=f"up_{doc['Nome_Arquivo']}")
                                if st.button("Confirmar Envio", key=f"btn_{doc['Nome_Arquivo']}", width='stretch', type="primary"):
                                    if arq:
                                        with st.spinner("Enviando..."):
                                            link = salvar_documento_drive(arq, f"ASSINADO_{u['Nome']}_{doc['Nome_Arquivo']}")
                                            if link and atualizar_contrato_enviado(u['ID_Usuario'], doc['Nome_Arquivo'], link):
                                                st.success("Enviado com sucesso!")
                                                time.sleep(1)
                                                st.rerun()
                    else:
                        st.info("Nenhum contrato pendente.")

    # --- RODAPÉ DE SUPORTE (FORA DAS ABAS) ---
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h3 style='font-size: 1.2rem; text-align: left;'>🆘 PRECISA DE AJUDA?</h3>", unsafe_allow_html=True)

    col_sup1, col_sup2 = st.columns(2)
    id_supervisor_dele = str(u.get('ID_Supervisor', '')).strip().lower()
    dados_supervisor = df_usuarios[df_usuarios['ID_Usuario'].str.lower().str.strip() == id_supervisor_dele] if df_usuarios is not None else pd.DataFrame()

    with col_sup1:
        if not dados_supervisor.empty:
            whats_sup = sanitize_whatsapp(dados_supervisor.iloc[0]['WhatsApp'])
            nome_sup = dados_supervisor.iloc[0]['Nome'].split()[0].upper()
            msg_sup = f"Olá {nome_sup}! Sou colaborador da sua equipe e preciso de ajuda."
            st.link_button(f"👤 FALAR COM {nome_sup}", f"https://wa.me/{whats_sup}?text={urllib.parse.quote(msg_sup)}", width='stretch')
        else:
            st.button("👤 SUPERVISOR NÃO ENCONTRADO", disabled=True, width='stretch')

    with col_sup2:
        whats_tecnico = "5561998788292"
        msg_tecnica = "Olá! Estou tendo dificuldades técnicas com o aplicativo Comando 2026."
        st.link_button("🛠️ SUPORTE DO APP", f"https://wa.me/{whats_tecnico}?text={urllib.parse.quote(msg_tecnica)}", width='stretch')

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)


# --- VISÃO: SUPERVISOR --- 
elif cargo_limpo == "supervisor":

    # 1. CARREGAMENTO PRÉVIO DE DADOS (Igual ao Colaborador)
    df_msgs = carregar_dados("Mensagens")
    df_usuarios = carregar_dados("Usuarios")
    df_logs = carregar_dados("Logs")
    m = None 

    if df_msgs is not None and not df_msgs.empty:
        # Filtra pelo grupo do Supervisor para as diretrizes dele
        msg_grupo = df_msgs[df_msgs['ID_Alvo'].astype(str).str.strip() == str(u['ID_Grupo']).strip()]
        if not msg_grupo.empty:
            m = msg_grupo.iloc[-1]
            # Splash Screen inicial
            if not st.session_state["mensagem_exibida"]:
                st.markdown(f"""
                    <div style='background-color: #FFEB00; padding: 40px 20px; border: 5px solid #1D1D1B; 
                                box-shadow: 10px 10px 0px #1D1D1B; text-align: center; margin-top: 20px;'>
                        <h1 style='font-family: "Archivo Black", sans-serif; font-style: italic; color: #1D1D1B; font-size: 2.5rem;'>
                            COMANDO 2026<br><span style='color: #E20613;'>DIRETRIZES DE LIDERANÇA</span>
                        </h1>
                        <hr style='border: 2px solid #1D1D1B; margin: 20px 0;'>
                        <p style='font-size: 1.4rem; font-weight: bold; color: #1D1D1B; line-height: 1.4;'>{m['Mensagem_Inicial']}</p>
                    </div><br>
                """, unsafe_allow_html=True)
                if st.button("✅ CIENTE DAS DIRETRIZES", width='stretch', type="primary"):
                    st.session_state["mensagem_exibida"] = True
                    st.rerun()
                st.stop()

    # 2. CAPTURA DE GPS COMPACTA (Sempre visível no topo)
    location_data = get_geolocation()
    col_status, col_btn = st.columns([3, 1])
    with col_status:
        if location_data:
            try:
                lat, lon = location_data['coords']['latitude'], location_data['coords']['longitude']
                st.session_state['last_coords'] = f"{lat},{lon}"
                st.markdown("🟢 **GPS ATIVO**")
            except: st.markdown("🔴 **ERRO GPS**")
        else: st.markdown("🟡 **BUSCANDO SINAL...**")
    with col_btn:
        if st.button("🔄", help="Atualizar GPS"): st.rerun()

    # 3. SISTEMA DE ABAS DO SUPERVISOR
    tab_missoes, tab_contratos, tab_equipe = st.tabs([
        "🚀 MISSÕES E PRESENÇA", "📄 MEUS CONTRATOS", "📈 ACOMPANHAMENTO"
    ])

    # ==========================================
    # ABA 1: MISSÕES (IDÊNTICA AO COLABORADOR)
    # ==========================================
    with tab_missoes:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        # Registro de Presença
        st.markdown("<div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 8px 8px 0px #1D1D1B; text-align: center; margin-bottom: 25px;'><h2 style='margin:0; font-size: 1.8rem; font-style: italic; color: #1D1D1B;'>MEU REGISTRO</h2></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏁 ENTRADA (CHECK-IN)", width='stretch', key="sup_in"): modal_checkin(u, agora)
        with c2:
            if st.button("🏁 SAÍDA (CHECK-OUT)", width='stretch', key="sup_out"): modal_checkout(u, agora)

        # Missões Diárias
        st.divider()
        st.markdown("<div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 8px 8px 0px #1D1D1B; text-align: center; margin-bottom: 25px;'><h2 style='margin:0; font-size: 1.8rem; font-style: italic; color: #1D1D1B;'>🚀 MISSÕES DIÁRIAS</h2></div>", unsafe_allow_html=True)
        
        t_txt = str(m.get('Tarefa_Direcionada', 'MISSÃO GERAL')).upper() if m is not None else "MISSÃO GERAL"
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align: center; color: #1D1D1B; margin-bottom: 10px;'>🚩 MISSÃO PRIORITÁRIA</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-weight: bold; font-size: 1.1rem; color: #E20613;'>{t_txt}</p>", unsafe_allow_html=True)
            if st.button("CONCLUIR MISSÃO DE HOJE", width='stretch', key="sup_task_done"):
                registrar_acao(u['ID_Usuario'], f"CONCLUIU: {t_txt}", localizacao=st.session_state.get('last_coords'))
                st.success("MISSÃO REGISTRADA!")

        # Ações de Rede
        st.markdown("<h3 style='font-size: 1.2rem;'>📲 AÇÕES DE REDE</h3>", unsafe_allow_html=True)
        cm1, cm2 = st.columns(2)
        with cm1:
            if st.button("📸 INSTAGRAM", width='stretch', key="sup_insta"):
                registrar_acao(u['ID_Usuario'], "AÇÃO: INTERAÇÃO INSTAGRAM", localizacao=st.session_state.get('last_coords'))
                st.markdown(f"<a href='https://www.instagram.com/maxmacieldf/' target='_blank'><div style='background-color: #1D1D1B; color: #FFEB00; text-align: center; padding: 10px; font-weight: bold; font-size: 0.8rem;'>ABRIR PERFIL ↗️</div></a>", unsafe_allow_html=True)
        with cm2:
            if st.button("💬 WHATSAPP", width='stretch', key="sup_whats"):
                registrar_acao(u['ID_Usuario'], "AÇÃO: MOBILIZAÇÃO WHATSAPP", localizacao=st.session_state.get('last_coords'))
                msg_zap = urllib.parse.quote("Salve! Vamos juntos com Max Maciel 🚀 https://www.instagram.com/maxmacieldf/")
                st.markdown(f"<a href='https://wa.me/?text={msg_zap}' target='_blank'><div style='background-color: #1D1D1B; color: #FFEB00; text-align: center; padding: 10px; font-weight: bold; font-size: 0.8rem;'>ENVIAR P/ AMIGO ↗️</div></a>", unsafe_allow_html=True)

        with tab_contratos:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                
                # --- NOVO: BLOCO DE SOLICITAÇÃO DE CONTRATO ---
                st.markdown("""
                    <div style='background-color: #FFEB00; padding: 15px; border: 4px solid #1D1D1B; box-shadow: 8px 8px 0px #1D1D1B; text-align: center; margin-bottom: 20px;'>
                        <h2 style='margin:0; font-size: 1.3rem; font-family: "Archivo Black", sans-serif; font-style: italic; color: #1D1D1B;'>📝 NOVO CONTRATO</h2>
                        <p style='margin:5px 0 0 0; font-size: 0.9rem; font-weight: bold;'>VOCÊ AINDA NÃO GEROU SEU CONTRATO?</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Link para o formulário (Substitua o link abaixo pelo seu link real)
                url_formulario = "https://forms.gle/9fqxvN8XfCmTRh9EA" 
                
                st.link_button("📋 PREENCHER DADOS PARA GERAR CONTRATO", url_formulario, width='stretch', type="primary")
                
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                st.divider()
        
                st.subheader("📄 Meus Documentos")
                df_contratos = carregar_dados("Contratos")
                if df_contratos is not None:
                    meus_docs = df_contratos[df_contratos['ID_Usuario'].astype(str) == str(u['ID_Usuario'])]
                    if not meus_docs.empty:
                        for _, doc in meus_docs.iterrows():
                            with st.container(border=True):
                                st.write(f"**Doc:** {doc['Nome_Arquivo']}")
                                st.link_button("📥 Baixar Original", doc['Link_Original'], width='stretch')
                                arq = st.file_uploader("Upload Assinado (PDF)", type=['pdf'], key=f"up_{doc['Nome_Arquivo']}")
                                if st.button("Confirmar Envio", key=f"btn_{doc['Nome_Arquivo']}", width='stretch', type="primary"):
                                    if arq:
                                        with st.spinner("Enviando..."):
                                            link = salvar_documento_drive(arq, f"ASSINADO_{u['Nome']}_{doc['Nome_Arquivo']}")
                                            if link and atualizar_contrato_enviado(u['ID_Usuario'], doc['Nome_Arquivo'], link):
                                                st.success("Enviado com sucesso!")
                                                time.sleep(1)
                                                st.rerun()
                    else:
                        st.info("Nenhum contrato pendente.")
    # ==========================================
    # ABA 3: ACOMPANHAMENTO (LOGICA ANTERIOR DO SUPERVISOR)
    # ==========================================
    with tab_equipe:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if df_usuarios is not None and df_logs is not None:
            minha_equipe = df_usuarios[df_usuarios['ID_Supervisor'].astype(str) == str(u['ID_Usuario'])]
            
            # Métricas da Equipe
            espaco_metricas = st.empty()
            
            # Filtro de Data
            c_data, _ = st.columns([1.5, 1])
            with c_data:
                data_sel = st.date_input("📅 DATA DE ANÁLISE", datetime.now(timezone.utc) - timedelta(hours=3))
            d_str = data_sel.strftime("%d/%m/%Y")

            # Cálculos de Equipe
            logs_dia = df_logs[df_logs['Data_Hora'].str.contains(d_str)]
            ativos_dia = logs_dia[logs_dia['ID_Usuario'].isin(minha_equipe['ID_Usuario'])]
            total_vol = len(minha_equipe)
            num_ativos = ativos_dia[ativos_dia['Tipo_Acao'].str.contains("Check-in")]['ID_Usuario'].nunique()
            total_acoes = len(ativos_dia)

            espaco_metricas.markdown(f"""
                <div style="display: flex; justify-content: space-between; gap: 5px; width: 100%; margin-bottom: 15px;">
                    <div style="flex: 1; background: #FFF; border: 2px solid #1D1D1B; box-shadow: 3px 3px 0px #1D1D1B; text-align: center; padding: 5px;">
                        <p style="margin: 0; font-size: 0.6rem; font-family: 'Archivo Black'; color: #666;">EQUIPE</p>
                        <p style="margin: 0; font-size: 1.2rem; font-family: 'Archivo Black'; color: #1D1D1B;">{total_vol}</p>
                    </div>
                    <div style="flex: 1; background: #FFF; border: 2px solid #1D1D1B; box-shadow: 3px 3px 0px #1D1D1B; text-align: center; padding: 5px;">
                        <p style="margin: 0; font-size: 0.6rem; font-family: 'Archivo Black'; color: #666;">ATIVOS</p>
                        <p style="margin: 0; font-size: 1.2rem; font-family: 'Archivo Black'; color: #E20613;">{num_ativos}</p>
                    </div>
                    <div style="flex: 1; background: #FFF; border: 2px solid #1D1D1B; box-shadow: 3px 3px 0px #1D1D1B; text-align: center; padding: 5px;">
                        <p style="margin: 0; font-size: 0.6rem; font-family: 'Archivo Black'; color: #666;">AÇÕES</p>
                        <p style="margin: 0; font-size: 1.2rem; font-family: 'Archivo Black'; color: #1D1D1B;">{total_acoes}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<h3 style='font-size: 1.1rem; text-align: left; margin-top: -15px;'>📋 STATUS DA EQUIPE ({d_str[:5]})</h3>", unsafe_allow_html=True)

            for _, vol in minha_equipe.iterrows():
                logs_vol = df_logs[(df_logs['ID_Usuario'] == vol['ID_Usuario']) & (df_logs['Data_Hora'].str.contains(d_str))]
                
                tem_in = not logs_vol[logs_vol['Tipo_Acao'].str.contains("Check-in")].empty
                tem_net = not logs_vol[logs_vol['Tipo_Acao'].str.contains("AÇÃO:")].empty
                tem_ok = not logs_vol[logs_vol['Tipo_Acao'].str.contains("CONCLUIU:")].empty
                
                if tem_in and tem_ok: label = "🔥 COMPLETO"
                elif tem_in: label = "🟢 EM CAMPO"
                elif tem_net: label = "🟡 REDES"
                else: label = "⚪ OFF"

                with st.expander(f"{label} | {vol['Nome'].upper()}"):
                    if not logs_vol.empty:
                        feed_html = ""
                        for _, row in logs_vol.tail(5)[::-1].iterrows():
                            acao_txt = str(row['Tipo_Acao']).split("|")[0].split("Foto:")[0].strip().upper()
                            hora_txt = row['Data_Hora'].split()[-1][:5]
                            # Clima
                            fb = str(row.get('Feedback', '')).strip()
                            badge = f"<span style='background-color:#FFEB00; border:1px solid #000; padding:1px 4px; font-size:0.5rem; margin-left:8px;'>{fb.split('|')[0]}</span>" if "Check-out" in row['Tipo_Acao'] and fb and fb != "nan" else ""
                            
                            feed_html += f"<div style='background-color:#F4F4F4; border:2px solid #1D1D1B; padding:10px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; box-shadow:3px 3px 0px #1D1D1B;'><div style='text-align:left;'><span style='font-family:Archivo Black; font-size:0.8rem;'>{acao_txt}</span>{badge}<br><span style='font-size:0.7rem; color:#666; font-weight:bold;'>🕒 {hora_txt}</span></div>"
                            if "," in str(row['Localização']):
                                feed_html += f"<div><a href='https://www.google.com/maps?q={row['Localização']}' target='_blank' style='background-color:#E20613; color:#FFF; padding:3px 6px; border:1px solid #000; font-size:0.5rem; text-decoration:none; font-family:Archivo Black;'>📍 MAPA</a></div>"
                            feed_html += "</div>"
                        st.markdown(feed_html, unsafe_allow_html=True)
                    
                    st.divider()
                    w_vol = sanitize_whatsapp(vol['WhatsApp'])
                    p_vol = vol['Nome'].split()[0]
                    c_w1, c_w2 = st.columns(2)
                    with c_w1:
                        if tem_in: b_n, b_m = "💪 MOTIVAR", f"Bora {p_vol}! Pra cima! 🚀"
                        elif tem_net: b_n, b_m = "⚡ REFORÇAR", f"Boa {p_nome}! Não esquece o check-in na rua! 💪"
                        else: b_n, b_m = "⚠️ COBRAR", f"Fala {p_vol}! Algum problema? Não vi suas ações hoje."
                        st.link_button(b_n, f"https://api.whatsapp.com/send?text={urllib.parse.quote(b_m)}&phone={w_vol}", width='stretch', type="primary")
                    with c_w2:
                        st.link_button("💬 CHAT", f"https://wa.me/{w_vol}", width='stretch')

            # Relatório Geral para Coordenador
            st.markdown("<br>", unsafe_allow_html=True)
            rel_txt = f"📊 *RELATÓRIO {d_str}*\n👤 Sup: {nome_primeiro}\n👥 Equipe: {total_vol}\n🔥 Ativos: {num_ativos}\n🎯 Ações: {total_acoes}"
            st.link_button("📲 ENVIAR RELATÓRIO P/ COORDENAÇÃO", f"https://api.whatsapp.com/send?text={urllib.parse.quote(rel_txt)}", width='stretch', type="primary")

    # Rodapé de Suporte do Supervisor (Pode falar com o Admin/Suporte técnico)
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h3 style='font-size: 1.2rem; text-align: left;'>🛠️ SUPORTE DE LIDERANÇA</h3>", unsafe_allow_html=True)
    st.link_button("🛠️ REPORTAR ERRO NO APP", "https://wa.me/5561998788292?text=Erro no Painel de Supervisor", width='stretch')


# --- PERFIL: ADMIN (COORDENAÇÃO) ---
elif cargo_limpo == "admin":
    
    # 0. CSS EXCLUSIVO DO ADMIN (Tamanho Máximo e Fontes Grandes)
    st.markdown("""
        <style>
            .block-container {
                max-width: 1100px !important; 
                padding-top: 2rem !important;
            }
            /* Aumenta a fonte de todas as abas no PC */
            button[data-baseweb="tab"] p {
                font-size: 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    agora_br = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
    hoje_str = agora_br.strftime("%d/%m/%Y")

    df_usuarios = carregar_dados("Usuarios")
    df_logs = carregar_dados("Logs")

# --- TICKER DE OPERAÇÕES ANIMADO (VERSÃO NOME REAL) ---
    if not df_logs.empty:
        # 1. Pega os últimos 10 logs
        ultimos_logs_raw = df_logs.tail(10)

        # 2. Faz o cruzamento (merge) para buscar o Nome real do voluntário
        # df_usuarios já deve estar carregado no seu bloco de Admin
        df_ticker = pd.merge(ultimos_logs_raw, df_usuarios[['ID_Usuario', 'Nome']], on='ID_Usuario', how='left')
        
        # 3. Fallback: se não encontrar o nome na planilha, usa o ID (e-mail)
        df_ticker['Nome'] = df_ticker['Nome'].fillna(df_ticker['ID_Usuario'])

        # 4. Monta a frase usando o primeiro nome de cada um
        frase_ticker = "  ///  ".join([
            f"⚡ {str(row['Nome']).split()[0].upper()}: {str(row['Tipo_Acao']).split('|')[0].strip().upper()}"
            for _, row in df_ticker[::-1].iterrows()
        ])
        
        conteudo_duplicado = f"{frase_ticker} /// {frase_ticker}"

        st.markdown(f"""
            <style>
                @keyframes scroll {{
                    0% {{ transform: translateX(0); }}
                    100% {{ transform: translateX(-50%); }}
                }}
                .ticker-container {{
                    width: 100%;
                    overflow: hidden;
                    background: #FFEB00;
                    border-top: 3px solid #1D1D1B;
                    border-bottom: 3px solid #1D1D1B;
                    padding: 8px 0;
                    margin-bottom: 25px;
                    white-space: nowrap;
                    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                }}
                .ticker-content {{
                    display: inline-block;
                    animation: scroll 45s linear infinite;
                    font-family: 'Archivo Black', sans-serif;
                    font-size: 0.9rem;
                    color: #1D1D1B;
                    font-style: italic;
                    text-transform: uppercase;
                }}
                .ticker-content:hover {{
                    animation-play-state: paused;
                }}
            </style>
            <div class="ticker-container">
                <div class="ticker-content">
                    {conteudo_duplicado}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 2. ABAS DE GESTÃO
    tab_hierarquia, tab_logs, tab_mapa, tab_mensagens, tab_cadastro, tab_contratos = st.tabs([
        "👥 EQUIPES", "📊 DASHBOARD", "🗺️ MAPA", "📝 MISSÕES", "➕ CADASTRO", "📄 CONTRATOS"
    ])

# ==========================================
    # ABA 1: ESTRUTURA DE EQUIPES (GRID DESKTOP CORRIGIDO)
    # ==========================================
    with tab_hierarquia:
        st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 25px; font-size: 2rem;'>ESTRUTURA DE EQUIPES</h2>", unsafe_allow_html=True)
        
        df_usuarios = carregar_dados("Usuarios")
        df_logs = carregar_dados("Logs")
        df_grupos_info = carregar_dados("Grupos")

        if df_usuarios is not None and df_grupos_info is not None:
            df_gerencial = pd.merge(df_usuarios, df_grupos_info, on='ID_Grupo', how='left')
            df_gerencial['Macro_Grupo'] = df_gerencial['Macro_Grupo'].fillna("GERAL")

            # Filtro de Macro Região
            macros_existentes = sorted(df_gerencial['Macro_Grupo'].unique().tolist())
            st.markdown("<p style='font-family: \"Archivo Black\", sans-serif; font-size: 0.9rem; margin-bottom: 5px;'>📍 SELECIONE A MACRO REGIÃO:</p>", unsafe_allow_html=True)
            macro_selecionada = st.selectbox("FILTRO_MACRO", ["TODAS AS REGIÕES"] + macros_existentes, label_visibility="collapsed")

            if macro_selecionada == "TODAS AS REGIÕES":
                df_f_admin = df_gerencial.copy()
            else:
                df_f_admin = df_gerencial[df_gerencial['Macro_Grupo'] == macro_selecionada]
            
            supervisores = df_f_admin[df_f_admin['Cargo'].str.lower().str.strip() == "supervisor"]
            
            if supervisores.empty:
                st.warning("Nenhum supervisor nesta região.")
            else:
                # 1. CRIAMOS AS COLUNAS TOTAIS DO MONITOR
                col_sup1, col_sup2 = st.columns(2, gap="large")
                
                for i, (_, sup) in enumerate(supervisores.iterrows()):
                    # Escolhe a coluna da vez
                    col_alvo = col_sup1 if i % 2 == 0 else col_sup2
                    
                    # --- TUDO A PARTIR DAQUI PRECISA ESTAR DENTRO DO 'WITH COL_ALVO' ---
                    with col_alvo:
                        equipe = df_f_admin[df_f_admin['ID_Supervisor'].astype(str).str.strip() == str(sup['ID_Usuario']).strip()]
                        qtd_equipe = len(equipe)
                        
                        # Ativos hoje
                        logs_eq = df_logs[(df_logs['ID_Usuario'].isin(equipe['ID_Usuario'])) & (df_logs['Data_Hora'].str.contains(hoje_str))]
                        ativos_hoje = logs_eq[logs_eq['Tipo_Acao'].str.contains("Check-in")]['ID_Usuario'].nunique()
                        cor_ativos = "#E20613" if ativos_hoje > 0 else "#666666"

                        # A. CARD HTML (Título, Grupo e Números)
                        card_html = f"""
                            <div style='background-color: #FFFFFF; border: 4px solid #1D1D1B; box-shadow: 6px 6px 0px #1D1D1B; padding: 20px; margin-bottom: 12px;'>
                                <div style='border-bottom: 3px solid #1D1D1B; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;'>
                                    <div>
                                        <h3 style='margin: 0; font-family: "Archivo Black", sans-serif; font-size: 1.5rem; color: #E20613; text-transform: uppercase;'>{sup['Nome']}</h3>
                                        <span style='font-size: 0.8rem; color: #666; font-weight: bold;'>MACRO: {sup['Macro_Grupo']}</span>
                                    </div>
                                    <span style='background-color: #FFEB00; border: 2px solid #1D1D1B; padding: 4px 10px; font-family: "Archivo Black", sans-serif; font-size: 0.8rem;'>{sup['ID_Grupo']}</span>
                                </div>
                                <div style='display: flex; gap: 15px;'>
                                    <div style='flex: 1; background-color: #F4F4F4; border: 2px solid #1D1D1B; padding: 12px; text-align: center;'>
                                        <div style='font-family: "Archivo Black", sans-serif; font-size: 0.85rem; color: #666;'>EQUIPE</div>
                                        <div style='font-family: "Archivo Black", sans-serif; font-size: 2.2rem; color: #1D1D1B; line-height: 1; margin-top: 5px;'>{qtd_equipe}</div>
                                    </div>
                                    <div style='flex: 1; background-color: #F4F4F4; border: 2px solid #1D1D1B; padding: 12px; text-align: center;'>
                                        <div style='font-family: "Archivo Black", sans-serif; font-size: 0.85rem; color: #666;'>ATIVOS</div>
                                        <div style='font-family: "Archivo Black", sans-serif; font-size: 2.2rem; color: {cor_ativos}; line-height: 1; margin-top: 5px;'>{ativos_hoje}</div>
                                    </div>
                                </div>
                            </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # B. BOTÕES LADO A LADO (CHAT E GRUPO)
                        w_sup = sanitize_whatsapp(sup['WhatsApp'])
                        link_grp = str(sup.get('Link_Grupo', '')).strip()
                        
                        c_wa1, c_wa2 = st.columns(2)
                        with c_wa1:
                            st.link_button(f"👤 CHAT: {sup['Nome'].split()[0].upper()}", f"https://wa.me/{w_sup}", width="stretch")
                        with c_wa2:
                            if link_grp and "chat.whatsapp" in link_grp:
                                st.link_button("📢 GRUPO", f"{link_grp}#{sup['ID_Usuario']}", width="stretch")
                            else:
                                st.button("🚫 SEM LINK", disabled=True, width="stretch", key=f"no_link_{sup['ID_Usuario']}")

                        # C. EXPANDER DE INTEGRANTES (DENTRO DA COLUNA)
                        with st.expander(f"👥 LISTA DE INTEGRANTES ({qtd_equipe})"):
                            if not equipe.empty:
                                for _, vol in equipe.iterrows():
                                    w_vol = sanitize_whatsapp(vol['WhatsApp'])
                                    st.markdown(f"""
                                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding: 8px 0;">
                                            <span style="font-size: 0.9rem; font-weight: bold; color: #1D1D1B;">{vol['Nome'].upper()}</span>
                                            <a href="https://wa.me/{w_vol}" target="_blank" style="background-color: #25D366; color: #FFFFFF; font-size: 0.7rem; padding: 4px 10px; border: 2px solid #1D1D1B; text-decoration: none; font-weight: bold; white-space: nowrap;">CHAMAR</a>
                                        </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.caption("Sem voluntários.")
                        
                        st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
    # ABA 2: MENSAGENS E MISSÕES (AJUSTADO P/ 4 COLUNAS)
    # ==========================================
    with tab_mensagens:
        st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 25px; font-size: 2rem;'>DIRETRIZES DO DIA</h2>", unsafe_allow_html=True)
        
        st.markdown("""
            <style>
                div[data-testid="stForm"] label p { font-size: 1.6rem !important; font-family: 'Archivo Black' !important; font-style: italic; }
                div[data-testid="stForm"] textarea, div[data-testid="stForm"] input { font-size: 1.4rem !important; font-weight: bold !important; border: 3px solid #1D1D1B !important; }
            </style>
        """, unsafe_allow_html=True)
        
        try:
            client = _get_gspread_client()
            aba_msg = client.open_by_key(st.secrets["planilha"]["id"]).worksheet("Mensagens")
            # Puxa os dados
            dados_msg = aba_msg.get_all_records()
            df_msg = pd.DataFrame(dados_msg)

            # Lista de alvos únicos
            lista_alvos = df_msg["ID_Alvo"].unique().tolist() if not df_msg.empty else []
            alvo_selecionado = st.selectbox("1. SELECIONE O GRUPO:", ["Novo..."] + lista_alvos)

            with st.form("form_admin_msg"):
                if alvo_selecionado == "Novo...": 
                    id_alvo, msg_i, tar = "", "", ""
                else:
                    # Filtra a linha do grupo selecionado
                    d = df_msg[df_msg["ID_Alvo"] == alvo_selecionado].iloc[-1]
                    id_alvo = d.get("ID_Alvo", "")
                    msg_i = d.get("Mensagem_Inicial", "")
                    tar = d.get("Tarefa_Direcionada", "")

                f_id = st.text_input("ID DO GRUPO (IGUAL AO CADASTRADO):", value=id_alvo)
                f_msg = st.text_area("MENSAGEM NO POP-UP (BOAS-VINDAS):", value=msg_i, height=150)
                f_tar = st.text_area("MISSÃO DE RUA (TAREFA PRINCIPAL):", value=tar, height=100)

                if st.form_submit_button("🚀 ATUALIZAR DIRETRIZES", type="primary", width='stretch'):
                    if f_id:
                        data_auto = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)).strftime("%d/%m/%Y")
                        
                        # SÃO APENAS ESSES 4 VALORES:
                        # A=ID_Alvo, B=Mensagem_Inicial, C=Tarefa_Direcionada, D=Data_Referencia
                        nova_linha = [f_id, f_msg, f_tar, data_auto]
                        
                        if alvo_selecionado != "Novo...":
                            try:
                                cell = aba_msg.find(str(alvo_selecionado))
                                if cell:
                                    aba_msg.delete_rows(cell.row)
                            except:
                                pass
                        
                        aba_msg.append_row(nova_linha) # Salva exatamente nas colunas A, B, C, D
                        st.success("✅ ATUALIZADO!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("O ID DO GRUPO É OBRIGATÓRIO")
        except Exception as e:
            st.error(f"Erro na conexão: {e}")

# ==========================================
# ABA 3: DASHBOARD GERAL (VISÃO COORDENAÇÃO)
# ==========================================
    with tab_logs:
        st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 25px; font-size: 2rem;'>ESTATÍSTICAS DO COMANDO</h2>", unsafe_allow_html=True)
        
        # 1. TRATAMENTO DE DADOS
        if 'Localização' not in df_logs.columns: df_logs['Localização'] = "Sem GPS"
        if 'Endereço' not in df_logs.columns: df_logs['Endereço'] = "Não identificado"
        if 'Feedback' not in df_logs.columns: df_logs['Feedback'] = "Nenhum"

        df_logs['Data_Hora_DT'] = pd.to_datetime(df_logs['Data_Hora'], dayfirst=True, errors='coerce')
        df_logs['Data_Filtro'] = df_logs['Data_Hora'].str.split().str[0]
        
        datas_disponiveis = sorted(
            [d for d in df_logs['Data_Filtro'].unique().tolist() if isinstance(d, str) and "/" in d], 
            key=lambda x: datetime.strptime(x, "%d/%m/%Y"), 
            reverse=True
        )

        # 2. ÁREA DE FILTROS LADO A LADO (PC-FIRST)
        c_f1, c_f2 = st.columns([1, 1])
        with c_f1:
            periodo_selecionado = st.selectbox("📅 FILTRAR POR DATA:", ["Histórico Completo"] + datas_disponiveis)
        with c_f2:
            # Sugestão Adicional: Filtro por Supervisor
            lista_sups = ["TODOS"] + df_usuarios[df_usuarios['Cargo'].str.lower() == "supervisor"]['Nome'].unique().tolist()
            sup_filtro = st.selectbox("👤 FILTRAR POR SUPERVISOR:", lista_sups)

        # Merge para análise
        df_completo = pd.merge(df_logs, df_usuarios[['ID_Usuario', 'Nome', 'ID_Supervisor', 'ID_Grupo']], on='ID_Usuario', how='left')
        df_completo = pd.merge(df_completo, df_usuarios[['ID_Usuario', 'Nome']].rename(columns={'Nome': 'Supervisor_Nome', 'ID_Usuario': 'ID_Supervisor'}), on='ID_Supervisor', how='left')
        df_completo['Nome'] = df_completo['Nome'].fillna(df_completo['ID_Usuario'])

        # Aplicação dos Filtros
        df_f = df_completo.copy()
        if periodo_selecionado != "Histórico Completo":
            df_f = df_f[df_f['Data_Filtro'] == periodo_selecionado]
        if sup_filtro != "TODOS":
            df_f = df_f[df_f['Supervisor_Nome'] == sup_filtro]

        # 3. CARDS DE IMPACTO
        total_acoes = len(df_f)
        ativos_unicos = df_f['ID_Usuario'].nunique()
        checkins_total = len(df_f[df_f['Tipo_Acao'].str.contains("Check-in", case=False)])

        st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 30px;">
        <div style="flex: 1; background: #FFF; border: 4px solid #1D1D1B; padding: 20px; text-align: center; box-shadow: 6px 6px 0px #1D1D1B;">
            <div style="font-family: 'Archivo Black'; font-size: 0.9rem; color: #666;">AÇÕES NO PERÍODO</div>
            <div style="font-family: 'Archivo Black'; font-size: 3rem; color: #1D1D1B; line-height: 1; margin-top: 10px;">{total_acoes}</div>
        </div>
        <div style="flex: 1; background: #FFF; border: 4px solid #1D1D1B; padding: 20px; text-align: center; box-shadow: 6px 6px 0px #1D1D1B;">
            <div style="font-family: 'Archivo Black'; font-size: 0.9rem; color: #666;">MEMBROS ATIVOS</div>
            <div style="font-family: 'Archivo Black'; font-size: 3rem; color: #E20613; line-height: 1; margin-top: 10px;">{ativos_unicos}</div>
        </div>
        <div style="flex: 1; background: #FFF; border: 4px solid #1D1D1B; padding: 20px; text-align: center; box-shadow: 6px 6px 0px #1D1D1B;">
            <div style="font-family: 'Archivo Black'; font-size: 0.9rem; color: #666;">PRESENÇA FÍSICA</div>
            <div style="font-family: 'Archivo Black'; font-size: 3rem; color: #1D1D1B; line-height: 1; margin-top: 10px;">{checkins_total}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

        # 4. RESUMO DE PERFORMANCE POR EQUIPE (Sugestão de "outra coisa")
        if not df_f.empty:
            st.markdown("<h3 style='font-family: \"Archivo Black\", sans-serif; font-size: 1.4rem; text-align: left;'>🏆 RANKING POR EQUIPE</h3>", unsafe_allow_html=True)
            # Agrupamento para ver produtividade por supervisor
            df_rank = df_f.groupby('Supervisor_Nome').agg({
                'Tipo_Acao': 'count',
                'ID_Usuario': 'nunique'
            }).reset_index().rename(columns={'Supervisor_Nome': 'Supervisor', 'Tipo_Acao': 'Total de Ações', 'ID_Usuario': 'Colaboradores na Rua'})
            
            st.dataframe(df_rank.sort_values(by='Total de Ações', ascending=False), use_container_width=True, hide_index=True)

        st.divider()

        # 5. TABELA DE LOGS COMPLETA (ADICIONADA COLUNA FEEDBACK)
        st.markdown("<h3 style='font-family: \"Archivo Black\", sans-serif; font-size: 1.4rem; text-align: left;'>📄 DETALHAMENTO DAS MISSÕES</h3>", unsafe_allow_html=True)
        
        # Adicionada a coluna Feedback na visualização
        df_visual = df_f.sort_values(by="Data_Hora_DT", ascending=False)
        
        st.dataframe(
            df_visual[['Nome', 'Tipo_Acao', 'Data_Hora', 'Feedback', 'Endereço']], 
            column_config={
                "Nome": "Colaborador", 
                "Tipo_Acao": "Ação", 
                "Data_Hora": "Horário",
                "Feedback": "📣 Relato/Clima",
                "Endereço": "📍 Local"
            }, 
            width='stretch', 
            hide_index=True
        )

        # 6. EXPORTAÇÃO PARA EXCEL (Relatório Gerencial)
        if not df_f.empty:
            try:
                df_excel = df_visual[['Nome', 'Supervisor_Nome', 'ID_Grupo', 'Tipo_Acao', 'Data_Hora', 'Feedback', 'Endereço', 'Localização']].copy()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_excel.to_excel(writer, index=False, sheet_name='Relatorio_Completo')
                    worksheet = writer.sheets['Relatorio_Completo']
                    for idx, col in enumerate(df_excel.columns):
                        max_len = max(df_excel[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(idx, idx, max_len)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label=f"📊 BAIXAR RELATÓRIO COMPLETO EM EXCEL ({periodo_selecionado})",
                    data=buffer.getvalue(),
                    file_name=f'comando2026_relatorio_{sup_filtro}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    width='stretch',
                    type="primary"
                )
            except Exception as e:
                st.error(f"Erro ao gerar Excel: {e}")


# ==========================================
    # ABA 4: GESTÃO DE ACESSOS E GRUPOS
    # ==========================================
    with tab_cadastro:
        # 1. Carregamos as listas atualizadas
        df_usuarios = carregar_dados("Usuarios")
        df_grupos_master = carregar_dados("Grupos") # Nova aba
        
        if df_usuarios is not None and df_grupos_master is not None:
            lista_supervisores = df_usuarios[df_usuarios['Cargo'].str.lower().str.strip() == "supervisor"]['ID_Usuario'].unique().tolist()
            lista_grupos = sorted(df_grupos_master['ID_Grupo'].unique().tolist())
            
# --- SEÇÃO 1: NOVO INTEGRANTE ---
            st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 20px; font-size: 1.8rem;'>👤 NOVO INTEGRANTE</h2>", unsafe_allow_html=True)
            
            # Criamos um mapeamento: "NOME (ID)" -> "ID"
            df_sup_only = df_usuarios[df_usuarios['Cargo'].str.lower().str.strip() == "supervisor"]
            
            # Criamos uma lista formatada para o dropdown e um dicionário para busca
            # Exemplo: "JOÃO SILVA (joao@email.com)"
            mapeamento_sup = {
                f"{row['Nome'].upper()} ({row['ID_Usuario'].lower()})": row['ID_Usuario'] 
                for _, row in df_sup_only.iterrows()
            }
            lista_nomes_exibicao = sorted(mapeamento_sup.keys())

            with st.container(border=True):
                with st.form("form_novo_user_v2", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**DADOS PESSOAIS**")
                        n_id = st.text_input("ID / E-MAIL (LOGIN):").strip().lower()
                        n_nome = st.text_input("NOME COMPLETO:")
                        n_whats = st.text_input("WHATSAPP (DDD + NÚMERO):")
                    with c2:
                        st.markdown("**VÍNCULO NO COMANDO**")
                        n_cargo = st.selectbox("CARGO:", ["Colaborador", "Supervisor", "Admin"])
                        n_grupo = st.selectbox("GRUPO / TERRITÓRIO:", options=lista_grupos)
                        
                        # O dropdown agora mostra os nomes formatados
                        n_sup_selecionado_display = st.selectbox(
                            "SUPERVISOR RESPONSÁVEL:", 
                            options=["NENHUM / PRÓPRIO SUPERVISOR"] + lista_nomes_exibicao
                        )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("✅ CADASTRAR INTEGRANTE", type="primary", width='stretch'):
                        if n_id and n_nome and n_whats:
                            try:
                                client = _get_gspread_client()
                                aba_u = client.open_by_key(st.secrets["planilha"]["id"]).worksheet("Usuarios")
                                
                                # Lógica para recuperar o ID real do supervisor selecionado
                                if n_sup_selecionado_display == "NENHUM / PRÓPRIO SUPERVISOR":
                                    id_supervisor_final = ""
                                else:
                                    id_supervisor_final = mapeamento_sup[n_sup_selecionado_display]

                                # Colunas: ID_Usuario | Nome | WhatsApp | Cargo | ID_Grupo | ID_Supervisor
                                aba_u.append_row([
                                    n_id, 
                                    n_nome.upper(), # Salva em maiúsculo para padronizar
                                    n_whats, 
                                    n_cargo, 
                                    n_grupo, 
                                    id_supervisor_final
                                ])
                                
                                st.success(f"🚀 {n_nome.upper()} CADASTRADO!")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"Erro: {e}")
                        else: st.error("⚠️ PREENCHA TODOS OS CAMPOS!")

# --- SEÇÃO 2: NOVO GRUPO ---
            st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 20px; font-size: 1.8rem;'>🚩 CRIAR NOVO GRUPO</h2>", unsafe_allow_html=True)
            
            with st.container(border=True):
                # Formulário com rótulos ocultos para controle total do alinhamento
                with st.form("form_novo_grupo_v2", clear_on_submit=True):
                    
                    c_g1, c_g2 = st.columns(2, gap="medium")
                    
                    with c_g1:
                        st.markdown("<p style='font-family: \"Archivo Black\", sans-serif; font-size: 0.9rem; margin-bottom: 8px; color: #1D1D1B;'>NOME DO MICRO-GRUPO (EX: PSUL):</p>", unsafe_allow_html=True)
                        g_nome = st.text_input("NOME_OCULTO", placeholder="DIGITE O NOME", label_visibility="collapsed")
                    
                    with c_g2:
                        st.markdown("<p style='font-family: \"Archivo Black\", sans-serif; font-size: 0.9rem; margin-bottom: 8px; color: #1D1D1B;'>MACRO GRUPO (REGIÃO):</p>", unsafe_allow_html=True)
                        opcoes_macro = [
                            "CEILÂNDIA/SOL NASCENTE",
                            "TAGUATINGA/SAMAMBAIA",
                            "GAMA/SANTA MARIA",
                            "PLANALTINA / LADO NORTE",
                            "PLANO/UNB",
                            "GABINETE",
                            "MOVIMENTOS",
                            "VOLUNTÁRIOS"
                        ]
                        g_macro = st.selectbox("MACRO_OCULTO", options=opcoes_macro, label_visibility="collapsed")
                    
                    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                    
                    # Botão com estilo de impacto
                    if st.form_submit_button("➕ REGISTRAR GRUPO NO SISTEMA", width='stretch', type="primary"):
                        if g_nome:
                            try:
                                client = _get_gspread_client()
                                plan = client.open_by_key(st.secrets["planilha"]["id"])
                                plan.worksheet("Grupos").append_row([g_nome.upper(), g_macro])
                                
                                # Linha de boas-vindas na aba Mensagens
                                data_atual_msg = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)).strftime("%d/%m/%Y")
                                plan.worksheet("Mensagens").append_row([g_nome.upper(), "BEM-VINDO AO COMANDO!", "MISSÃO INICIAL DE RUA", data_atual_msg])
                                
                                st.success(f"✅ GRUPO {g_nome.upper()} CRIADO!")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: 
                                st.error(f"Erro: {e}")
                        else:
                            st.error("⚠️ DIGITE O NOME DO MICRO-GRUPO!")
# ==========================================
    # ABA 5: MAPA DE OPERAÇÕES (SELETOR INDEPENDENTE)
    # ==========================================
    with tab_mapa:
        st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 25px; font-size: 2rem;'>🗺️ MAPA DE OPERAÇÕES</h2>", unsafe_allow_html=True)
        
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import MarkerCluster

        # 1. SELETOR DE DATA EXCLUSIVO PARA O MAPA
        # Extraímos as datas disponíveis nos logs (reutilizando a lógica da aba anterior)
        df_logs['Data_Filtro'] = df_logs['Data_Hora'].str.split().str[0]
        datas_mapa = sorted(
            [d for d in df_logs['Data_Filtro'].unique().tolist() if isinstance(d, str) and "/" in d], 
            key=lambda x: datetime.strptime(x, "%d/%m/%Y"), 
            reverse=True
        )

        c_map_filtro, _ = st.columns([1.5, 2])
        with c_map_filtro:
            periodo_mapa = st.selectbox("📍 FILTRAR LOCALIZAÇÕES POR DATA:", ["Histórico Completo"] + datas_mapa, key="filtro_mapa_indep")

        # 2. FILTRAGEM DOS DADOS
        if periodo_mapa == "Histórico Completo":
            df_m = df_completo.copy()
        else:
            df_m = df_completo[df_completo['Data_Filtro'] == periodo_mapa].copy()

        # 3. TRATAMENTO DE COORDENADAS (LAT/LON)
        def extrair_lat_lon(pos):
            try:
                if pos and "," in str(pos):
                    lat, lon = str(pos).split(",")
                    return float(lat), float(lon)
            except:
                return None, None
            return None, None

        df_m['lat'], df_m['lon'] = zip(*df_m['Localização'].apply(extrair_lat_lon))
        # Removemos logs que não possuem GPS válido
        df_geo = df_m.dropna(subset=['lat', 'lon'])

        # 4. RENDERIZAÇÃO DO MAPA
        if not df_geo.empty:
            # Centraliza o mapa na média dos pontos encontrados
            m = folium.Map(location=[df_geo['lat'].mean(), df_geo['lon'].mean()], zoom_start=12, tiles="OpenStreetMap")
            
            # Cluster para agrupar pontos próximos (melhora visual no PC)
            marker_cluster = MarkerCluster().add_to(m)

            for _, row in df_geo.iterrows():
                # Pop-up no estilo da Campanha
                popup_content = f"""
                <div style="font-family: sans-serif; min-width: 180px; border: 2px solid #1D1D1B; padding: 10px; background-color: #FFF;">
                    <b style="color: #E20613; text-transform: uppercase; font-size: 14px;">{row['Nome']}</b><br>
                    <div style="margin: 5px 0; border-top: 1px solid #000;"></div>
                    <b>Ação:</b> {str(row['Tipo_Acao']).split('|')[0]}<br>
                    <b>Hora:</b> {row['Data_Hora'].split()[-1][:5]}<br>
                    <small style="color: #666;">{row['Endereço']}</small>
                </div>
                """
                
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(marker_cluster)

            # Exibe o mapa ocupando a largura disponível
            st_folium(m, width=1200, height=600, returned_objects=[])
            
            st.markdown(f"💡 **Exibindo {len(df_geo)} registros geolocalizados.** Clique nos círculos para expandir as regiões.")
        else:
            with st.container(border=True):
                st.warning(f"⚠️ NENHUM DADO DE GPS ENCONTRADO PARA: {periodo_mapa}")
                st.info("Somente ações realizadas com GPS ativo no celular aparecem neste mapa.")

# ==========================================
    # ABA 5: GESTÃO DE CONTRATOS (ADMIN)
    # ==========================================
    with tab_contratos:
        st.markdown("<h2 style='font-family: \"Archivo Black\", sans-serif; color: #1D1D1B; margin-bottom: 25px; font-size: 2rem;'>📄 GESTÃO DE CONTRATOS</h2>", unsafe_allow_html=True)
        
        col_envio, col_status = st.columns([1.2, 2], gap="large")

        with col_envio:
            st.markdown("### 📤 ENVIAR PARA INTEGRANTE")
            with st.container(border=True):
                with st.form("form_admin_envia_contrato", clear_on_submit=True):
                    # --- MELHORIA: LISTA DETALHADA PARA SELEÇÃO ---
                    # Criamos uma lista formatada: "JOÃO SILVA | SUPERVISOR | CEILÂNDIA"
                    # Filtrando para não aparecer o próprio Admin na lista de envios
                    df_destinatarios = df_usuarios[df_usuarios['Cargo'].str.lower() != "admin"]
                    
                    mapeamento_dest = {
                        f"{row['Nome'].upper()} | {row['Cargo'].upper()} | {row['ID_Grupo']}": row['ID_Usuario'] 
                        for _, row in df_destinatarios.iterrows()
                    }
                    lista_nomes_contrato = sorted(mapeamento_dest.keys())
                    
                    user_selecionado_display = st.selectbox("PARA QUEM É O CONTRATO?", options=lista_nomes_contrato)
                    
                    n_doc = st.text_input("NOME DO DOCUMENTO:", placeholder="Ex: Contrato_NomeSobrenome_Data")
                    arq_pdf = st.file_uploader("ARQUIVO PDF:", type=['pdf'])
                    
                    if st.form_submit_button("🚀 ENVIAR AGORA", width='stretch', type="primary"):
                        if arq_pdf and n_doc and user_selecionado_display:
                            # Recupera o ID real (e-mail) do mapeamento
                            u_destino = mapeamento_dest[user_selecionado_display]
                            
                            with st.spinner("Subindo para o Drive..."):
                                # 1. Salva no Google Drive (na sua pasta de contratos do secrets)
                                link_gerado = salvar_documento_drive(arq_pdf, f"ORIGINAL_{n_doc}_{u_destino}")
                                
                                if link_gerado:
                                    # 2. Cria a linha na planilha 'Contratos'
                                    if registrar_novo_contrato_admin(u_destino, n_doc, link_gerado):
                                        st.success(f"✅ DOCUMENTO ENVIADO COM SUCESSO!")
                                        st.cache_data.clear()
                                        time.sleep(1)
                                        st.rerun()
                        else:
                            st.error("Preencha o nome do doc e selecione o PDF.")
        with col_status:
            st.markdown("### 📋 MONITORAMENTO")
            df_cont = carregar_dados("Contratos")
            
            if df_cont is not None and not df_cont.empty:
                # Cruzamos os dados para mostrar o Nome e não o e-mail
                df_view = pd.merge(df_cont, df_usuarios[['ID_Usuario', 'Nome']], on='ID_Usuario', how='left')
                df_view['Nome'] = df_view['Nome'].fillna(df_view['ID_Usuario']) # Fallback se não achar nome

                # Tabela de Resumo
                st.dataframe(
                    df_view[['Nome', 'Nome_Arquivo', 'Status']],
                    column_config={
                        "Nome": "Integrante",
                        "Nome_Arquivo": "Documento",
                        "Status": "Situação"
                    },
                    width="stretch",
                    hide_index=True
                )
                
                # Detalhes com botões
                with st.expander("🔍 VER LINKS E ARQUIVOS", expanded=True):
                    for _, row in df_view.iterrows():
                        c_info, c_links = st.columns([2, 1.5])
                        
                        with c_info:
                            # Mostra o nome em destaque
                            st.markdown(f"**{row['Nome'].upper()}**")
                            st.caption(f"Arquivo: {row['Nome_Arquivo']}")
                        
                        with c_links:
                            # Botões lado a lado menores
                            sub_c1, sub_c2 = st.columns(2)
                            sub_c1.link_button("📄 ORIG", row['Link_Original'], width='stretch', help="Baixar original enviado")
                            
                            link_assin = str(row.get('Link_Assinado', ''))
                            if link_assin.startswith("http"):
                                sub_c2.link_button("✍️ ASSIN", link_assin, width='stretch', type="primary", help="Ver assinado pelo integrante")
                            else:
                                sub_c2.button("⏳ PEND", disabled=True, width='stretch')
                        st.divider()
