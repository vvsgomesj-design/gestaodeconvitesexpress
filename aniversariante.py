import streamlit as st
import pandas as pd
import re
import urllib.parse
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gestão de Convites Express", layout="wide")

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1a2a6c; font-weight: 800; font-size: 32px; }
    .card { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #1a2a6c; margin-bottom: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .btn-convite { background-color: #fdbb2d !important; color: #1a2a6c !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA GERAR O CONVITE INDIVIDUAL (PDF) ---
def gerar_convite_individual(nome_convidado, evento, homenageado, data):
    pdf = FPDF()
    pdf.add_page()
    # Design Simples do Convite
    pdf.set_fill_color(26, 42, 108)
    pdf.rect(5, 5, 200, 287, 'D')
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(26, 42, 108)
    pdf.ln(50)
    pdf.cell(0, 20, evento.upper(), ln=True, align='C')
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
    pdf.cell(0, 10, "Sua presença é fundamental!", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- INICIALIZAÇÃO ---
if 'lista_convidados' not in st.session_state:
    st.session_state.lista_convidados = []

def adicionar_convidado():
    if st.session_state.temp_nome and st.session_state.temp_fone:
        st.session_state.lista_convidados.append({
            "Nome": st.session_state.temp_nome,
            "Telefone": st.session_state.temp_fone,
            "Status": "Pendente"
        })
        st.session_state.temp_nome = ""
        st.session_state.temp_fone = ""

def limpar_fone(tel):
    num = re.sub(r'\D', '', str(tel))
    return '55' + num if not num.startswith('55') else num

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎨 Configuração")
    tipo_evento = st.text_input("Evento", value="Aniversário")
    homenageado = st.text_input("Homenageado", value="", placeholder="Ex: Luiz")
    wa_gestora = st.text_input("WhatsApp da Gestora", placeholder="55629...")
    data_evento = st.date_input("Data do Evento")

# --- TELA PRINCIPAL ---
st.markdown('<p class="main-title">Gestão de Convites Express</p>', unsafe_allow_html=True)

# Bloco de Digitação
with st.container():
    col1, col2, col3 = st.columns([2, 2, 1])
    col1.text_input("Nome do Convidado", key="temp_nome")
    col2.text_input("Telefone com DDD", key="temp_fone")
    col3.markdown("<br>", unsafe_allow_html=True)
    col3.button("➕ Adicionar", on_click=adicionar_convidado)

st.markdown("---")

# --- EXIBIÇÃO DA LISTA ---
if st.session_state.lista_convidados:
    for idx, convidado in enumerate(st.session_state.lista_convidados):
        with st.container():
            status_cor = "🔴" if convidado['Status'] == "Pendente" else "🟢"
            st.markdown(f"""<div class="card"><b>{status_cor} {convidado['Nome']}</b></div>""", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
            
            # 1. Gerar e baixar o convite individual
            if homenageado:
                pdf_convite = gerar_convite_individual(
                    convidado['Nome'], tipo_evento, homenageado, data_evento.strftime('%d/%m/%Y')
                )
                c1.download_button(f"📥 Baixar Convite", data=pdf_convite, file_name=f"Convite_{convidado['Nome']}.pdf", key=f"pdf_{idx}")
            
            # 2. Link WhatsApp
            if homenageado and wa_gestora:
                txt_c = urllib.parse.quote(f"Confirmado no {tipo_evento} de {homenageado}. Assinado: {convidado['Nome']}")
                msg = f"Olá! Segue o seu convite. Confirme aqui: https://wa.me/{wa_gestora}?text={txt_c}"
                link = f"https://web.whatsapp.com/send?phone={limpar_fone(convidado['Telefone'])}&text={urllib.parse.quote(msg)}"
                c2.link_button("🚀 Enviar Zap", link)
            
            # 3. Check e Excluir
            if convidado['Status'] == "Pendente":
                if c3.button("✔", key=f"chk_{idx}"):
                    st.session_state.lista_convidados[idx]['Status'] = "Enviado"
                    st.rerun()
            if c4.button("🗑", key=f"del_{idx}"):
                st.session_state.lista_convidados.pop(idx)
                st.rerun()
else:
    st.info("Digite os dados acima para gerar os convites!")