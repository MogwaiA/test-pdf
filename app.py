import streamlit as st
from tab_rapportseismes import rapports_seismes


st.set_page_config(
    page_title="Carte de Sismicité",
    page_icon=":earthquake:",
    layout="wide",  # Utiliser une mise en page plus large !
    initial_sidebar_state="expanded",  # Barre latérale ouverte par défaut
)

rapports_seismes()
