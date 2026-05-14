import streamlit as st
import pandas as pd
import re
import urllib.parse
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Convites Express", layout="wide")

# --- ESTILIZAÇÃO CSS (PALETA DESIGNER) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1a2a6c; font-weight: 800; font-size: 35px; }
    .stButton>button { background-color: #b21f1f; color: white; border-radius: 8px; }
    .pdf-button>button { background-color: #1a2a6c !important; border: 2px solid #fdbb2d !important; }
    </style>
    """, unsafe_allow_html=True)

def limpar_fone(tel):
    num = re.sub(r'\D', '', str(tel))
    return '55' + num if not num.startswith('55') else num

# --- FUNÇÃO GERADORA DE PDF ---
def exportar_pdf(df, evento, homenageado, data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Estilizado
    pdf.set_fill_color(26, 42, 108) 
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_font('Arial', 'B', 22)
    pdf.set_text_color(253, 187, 45) 
    pdf.cell(0, 15, 'GESTÃO DE CONVITES EXPRESS', ln=True, align='C')
    
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'Relatório Profissional: {evento}', ln=True, align='C')
    pdf.cell(0, 10, f'Homenageado: {homenageado} | Data: {data}', ln=True, align='C')
    
    pdf.ln(30)
    
    # Tabela de Conferência
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(85, 10, 'Convidado', 1, 0, 'C', True)
    pdf.cell(55, 10, 'Telefone', 1, 0, 'C', True)
    pdf.cell(50, 10, 'Status de Envio', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 10)
    for _, row in df.iterrows():
        pdf.cell(85, 10, str(row[0])[:40], 1)
        pdf.cell(55, 10, str(row[1]), 1)
        pdf.cell(50, 10, str(row['Status']), 1)
        pdf.ln()
        
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f'Documento gerado por Vivianne Gomes - Design Criativo em {datetime.now().strftime("%d/%m/%Y")}', align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- CONTEÚDO PRINCIPAL ---
st.markdown('<p class="main-title">Gestão de Convites Express</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 Identidade")
    tipo_evento = st.text_input("Qual é o evento?", value="Homenagem")
    homenageado = st.text_input("Homenageado", value="Luiz")
    wa_gestora = st.text_input("WhatsApp da Gestora")
    data_evento = st.date_input("Data do Evento")
    arquivo_pdf_convite = st.file_uploader("📥 Convite (PDF)", type=["pdf"])

arquivo_csv = st.file_uploader("📊 Carregue a Lista de Convidados (CSV)", type=["csv"])

if arquivo_csv and wa_gestora:
    if 'df_express' not in st.session_state:
        df_base = pd.read_csv(arquivo_csv, sep=None, engine='python', dtype=str)
        df_base['Status'] = "Pendente"
        st.session_state.df_express = df_base

    df_atual = st.session_state.df_express
    
    # DASHBOARD DE CONTROLE
    col_met1, col_met2, col_pdf = st.columns([1, 1, 2])
    col_met1.metric("Pendentes", len(df_atual[df_atual['Status'] == "Pendente"]))
    col_met2.metric("Enviados", len(df_atual[df_atual['Status'] == "Enviado"]))
    
    with col_pdf:
        st.markdown('<div class="pdf-button">', unsafe_allow_html=True)
        # Gerar e disponibilizar PDF
        data_str = data_evento.strftime('%d/%m/%Y')
        pdf_bin = exportar_pdf(df_atual, tipo_evento, homenageado, data_str)
        st.download_button(
            label="📄 DESCARREGAR RELATÓRIO PDF",
            data=pdf_bin,
            file_name=f"Relatorio_{homenageado}_Express.pdf",
            mime="application/pdf"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # LISTA PARA DISPARO MANUAL
    for idx, linha in df_atual.iterrows():
        nome = str(linha.iloc[0]).strip()
        fone = limpar_fone(linha.iloc[1])
        status = linha['Status']
        
        with st.container():
            c_st, c_nm, c_ac = st.columns([0.5, 3, 2])
            c_st.write("🔴" if status == "Pendente" else "🟢")
            c_nm.markdown(f"**{nome}** \n\n {fone}")
            
            with c_ac:
                txt_conf = urllib.parse.quote(f"Olá! Confirmo presença no {tipo_evento} de {homenageado}. Atenciosamente, {nome}")
                link_wa = f"https://web.whatsapp.com/send?phone={fone}&text={urllib.parse.quote(f'Olá {nome}! Segue o convite para o evento de {homenageado}. Confirme aqui: https://wa.me/{wa_gestora}?text={txt_conf}')}"
                
                ca1, ca2 = st.columns(2)
                ca1.link_button("🚀 Abrir", link_wa)
                if status == "Pendente" and ca2.button("Check", key=f"btn_{idx}"):
                    st.session_state.df_express.at[idx, 'Status'] = "Enviado"
                    st.rerun()

    if st.button("Resetar Lista"):
        st.session_state.df_express['Status'] = "Pendente"
        st.rerun()