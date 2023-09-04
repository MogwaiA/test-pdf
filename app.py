import streamlit as st
from tab_eventid import carte_par_eventid
from tab_rapportseismes import rapports_seismes


st.set_page_config(
    page_title="Carte de Sismicité",
    page_icon=":earthquake:",
    layout="wide",  # Utiliser une mise en page plus large
    initial_sidebar_state="expanded",  # Barre latérale ouverte par défaut
)

tabs = {
      "Rapports": rapports_seismes,
      "Carte par séisme": carte_par_eventid      
}

# Afficher les onglets
selected_tab = st.sidebar.radio("Sélectionnez un onglet", list(tabs.keys()))
tabs[selected_tab]()


