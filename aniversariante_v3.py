import streamlit as st
import pandas as pd
import re
import urllib.parse
from fpdf import FPDF
from datetime import timedelta
import io

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gestão de Convites Express", layout="wide")

# --- FUNÇÃO: LIMPAR TELEFONE ---
def limpar_fone(tel):
    num = re.sub(r'\D', '', str(tel))
    if not num: return ""
    return '55' + num if not num.startswith('55') else num

# --- FUNÇÃO: RELATÓRIO FINAL (TODOS OS CONVIDADOS) ---
def gerar_relatorio_geral(lista, evento, homenageado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'RELATÓRIO FINAL DE CONVIDADOS', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Evento: {evento} - Homenageado: {homenageado}', ln=True, align='C')
    pdf.ln(10)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(80, 10, ' Nome', 1, 0, 'L', True)
    pdf.cell(60, 10, ' Telefone', 1, 0, 'L', True)
    pdf.cell(40, 10, ' Status', 1, 1, 'L', True)
    
    # Linhas da Tabela
    pdf.set_font('Arial', '', 11)
    for c in lista:
        pdf.cell(80, 10, f" {str(c['Nome'])}", 1)
        pdf.cell(60, 10, f" {str(c['Telefone'])}", 1)
        pdf.cell(40, 10, f" {str(c['Status'])}", 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# --- INICIALIZAÇÃO ---
if 'lista_convidados' not in st.session_state:
    st.session_state.lista_convidados = []

def adicionar_convidado():
    n = st.session_state.temp_nome.strip()
    f = st.session_state.temp_fone.strip()
    if n and f:
        st.session_state.lista_convidados.append({"Nome": n, "Telefone": f, "Status": "Pendente"})
        st.session_state.temp_nome = ""
        st.session_state.temp_fone = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🎨 Configuração")
    tipo_evento = st.text_input("Nome do Evento", value="Aniversário")
    homenageado = st.text_input("Homenageado", value="Luiz")
    wa_gestora = st.text_input("WhatsApp da Gestora", placeholder="55629...")
    data_evento = st.date_input("Data do Evento")
    
    st.markdown("---")
    st.subheader("📊 Finalização")
    if st.session_state.lista_convidados:
        # BOTÃO DO RELATÓRIO FINAL (O QUE VOCÊ PEDIU)
        pdf_final = gerar_relatorio_geral(st.session_state.lista_convidados, tipo_evento, homenageado)
        st.download_button(
            label="📥 BAIXAR RELATÓRIO FINAL (PDF)",
            data=pdf_final,
            file_name="relatorio_final_convidados.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    if st.button("🗑️ Limpar Lista"):
        st.session_state.lista_convidados = []
        st.rerun()

# --- TELA PRINCIPAL ---
st.title("Gestão de Convites Express")

with st.container():
    c1, c2, c3 = st.columns([2, 2, 1])
    c1.text_input("Nome do Convidado", key="temp_nome")
    c2.text_input("Telefone (com DDD)", key="temp_fone")
    c3.markdown("<br>", unsafe_allow_html=True)
    c3.button("➕ Adicionar", on_click=adicionar_convidado)

st.markdown("---")

# EXIBIÇÃO
if st.session_state.lista_convidados:
    for idx, conv in enumerate(st.session_state.lista_convidados):
        with st.expander(f"👤 {conv['Nome']}"):
            st.write(f"Telefone: {conv['Telefone']}")
            
            # Link Zap
            if wa_gestora:
                data_limite = data_evento - timedelta(days=15)
                link_confirm = f"https://wa.me/{wa_gestora}?text=Confirmado!"
                txt = (f"Olá! Convite para {tipo_evento} de {homenageado}.\n"
                       f"Data: {data_evento.strftime('%d/%m/%Y')}\n"
                       f"Confirme até {data_limite.strftime('%d/%m/%Y')} aqui: {link_confirm}")
                
                link_final = f"https://web.whatsapp.com/send?phone={limpar_fone(conv['Telefone'])}&text={urllib.parse.quote(txt)}"
                st.link_button("🚀 Enviar Convite via WhatsApp", link_final)
            
            if st.button("Remover", key=f"del_{idx}"):
                st.session_state.lista_convidados.pop(idx)
                st.rerun()
else:
    st.info("Adicione nomes para gerar o relatório.")
