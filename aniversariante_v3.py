import streamlit as st
import pandas as pd
import re
import urllib.parse
from fpdf import FPDF
from datetime import timedelta

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gestão de Convites Express", layout="wide")

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1a2a6c; font-weight: 800; font-size: 32px; }
    .card { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #1a2a6c; margin-bottom: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE SUPORTE ---
def limpar_fone(tel):
    num = re.sub(r'\D', '', str(tel))
    if not num: return ""
    return '55' + num if not num.startswith('55') else num

def gerar_convite_individual(nome_convidado, evento, homenageado, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(26, 42, 108)
    pdf.rect(5, 5, 200, 287, 'D')
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(26, 42, 108)
    pdf.ln(50)
    pdf.cell(0, 20, str(evento).upper(), ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 20, f"de {homenageado}", ln=True, align='C')
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 25)
    pdf.set_text_color(178, 31, 31)
    pdf.cell(0, 20, f"Para: {nome_convidado}", ln=True, align='C')
    pdf.ln(30)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Data: {data}", ln=True, align='C')
    pdf.cell(0, 10, "Sua presenca e fundamental!", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- INICIALIZAÇÃO DO ESTADO ---
if 'lista_convidados' not in st.session_state:
    st.session_state.lista_convidados = []

def adicionar_convidado():
    nome = st.session_state.temp_nome.strip()
    fone = st.session_state.temp_fone.strip()
    if nome and fone:
        st.session_state.lista_convidados.append({"Nome": nome, "Telefone": fone, "Status": "Pendente"})
        st.session_state.temp_nome = ""
        st.session_state.temp_fone = ""
    else:
        st.error("Preencha Nome e Telefone!")

def processar_csv(arquivo):
    try:
        df = pd.read_csv(arquivo, sep=None, engine='python')
        if 'Nome' in df.columns and 'Telefone' in df.columns:
            for _, row in df.iterrows():
                st.session_state.lista_convidados.append({"Nome": str(row['Nome']), "Telefone": str(row['Telefone']), "Status": "Pendente"})
            st.success(f"{len(df)} convidados importados!")
        else:
            st.error("O CSV deve ter as colunas 'Nome' e 'Telefone'")
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎨 Configuração")
    tipo_evento = st.text_input("Evento", value="Aniversário")
    homenageado = st.text_input("Homenageado", value="Luiz")
    wa_gestora = st.text_input("WhatsApp da Gestora (DDD+Número)", placeholder="Ex: 55629...")
    data_evento = st.date_input("Data do Evento")
    
    # Cálculo da data limite (15 dias antes)
    data_limite = data_evento - timedelta(days=15)
    
    st.markdown("---")
    st.header("📂 Importar Lista")
    arquivo_csv = st.file_uploader("Arquivo CSV", type=["csv"])
    if arquivo_csv and st.button("Carregar CSV"):
        processar_csv(arquivo_csv)
    
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.lista_convidados = []
        st.rerun()

# --- TELA PRINCIPAL ---
st.markdown('<p class="main-title">Gestão de Convites Express</p>', unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns([2, 2, 1])
    col1.text_input("Nome do Convidado", key="temp_nome")
    col2.text_input("Telefone (com DDD)", key="temp_fone")
    col3.markdown("<br>", unsafe_allow_html=True)
    col3.button("➕ Adicionar", on_click=adicionar_convidado)

st.markdown("---")

# --- LISTAGEM ---
if st.session_state.lista_convidados:
    for idx, convidado in enumerate(st.session_state.lista_convidados):
        with st.container():
            status_cor = "🔴" if convidado['Status'] == "Pendente" else "🟢"
            st.markdown(f'<div class="card"><b>{status_cor} {convidado["Nome"]}</b> - {convidado["Telefone"]}</div>', unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
            
            # PDF
            pdf_bytes = gerar_convite_individual(convidado['Nome'], tipo_evento, homenageado, data_evento.strftime('%d/%m/%Y'))
            c1.download_button("📥 PDF", pdf_bytes, file_name=f"Convite_{convidado['Nome']}.pdf", key=f"p_{idx}")
            
            # WhatsApp com a frase solicitada
            if wa_gestora:
                # Texto de confirmação que o convidado enviará para a gestora
                confirm_link_text = urllib.parse.quote(f"Olá! Gostaria de confirmar minha presença no {tipo_evento} de {homenageado}. Nome: {convidado['Nome']}")
                link_confirmacao = f"https://wa.me/{wa_gestora}?text={confirm_link_text}"
                
                # Mensagem principal que você enviará para o convidado
                texto_whatsapp = (
                    f"Você está convidado para o \"{tipo_evento}\" de \"{homenageado}\".\n\n"
                    f"📅 Data do evento: {data_evento.strftime('%d/%m/%Y')}\n"
                    f"⚠️ Peço que confirme com a gestão de eventos no link abaixo até o dia {data_limite.strftime('%d/%m/%Y')}:\n\n"
                    f"{link_confirmacao}"
                )
                
                link_final_zap = f"https://web.whatsapp.com/send?phone={limpar_fone(convidado['Telefone'])}&text={urllib.parse.quote(texto_whatsapp)}"
                c2.link_button("🚀 Enviar Zap", link_final_zap)
            
            if convidado['Status'] == "Pendente" and c3.button("✔", key=f"ok_{idx}"):
                st.session_state.lista_convidados[idx]['Status'] = "Enviado"
                st.rerun()
                
            if c4.button("🗑", key=f"del_{idx}"):
                st.session_state.lista_convidados.pop(idx)
                st.rerun()
else:
    st.info("Adicione convidados para começar.")