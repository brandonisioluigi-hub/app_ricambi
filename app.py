import streamlit as st
import pandas as pd
import os
import glob

# Imposta la pagina per essere più larga
st.set_page_config(layout="wide")

st.title("Ricerca Ricambi - Archivio Globale")
st.write("Cerca il Codice Articolo attraverso tutte le Macro Famiglie.")

# Funzione per caricare tutti i file Excel da una cartella
@st.cache_data
def load_all_data():
    cartella_dati = "dati" 
    
    percorso_file = os.path.join(cartella_dati, "*.xlsx")
    tutti_i_file = glob.glob(percorso_file)
    
    if not tutti_i_file:
        return pd.DataFrame() 
        
    lista_df = []
    
    for file in tutti_i_file:
        try:
            df = pd.read_excel(file)
            
            # NOVITÀ: Trasformiamo tutti i nomi delle colonne in MAIUSCOLO e togliamo gli spazi vuoti
            # Questo evita problemi se un file ha "Codice articolo" e un altro "CODICE ARTICOLO"
            df.columns = [str(col).strip().upper() for col in df.columns]
            
            nome_macro_famiglia = os.path.basename(file).replace('.xlsx', '')
            df.insert(0, 'FILE_ORIGINE', nome_macro_famiglia)
            
            lista_df.append(df)
        except Exception as e:
            st.warning(f"Errore nella lettura del file {file}: {e}")
            
    if lista_df:
        df_completo = pd.concat(lista_df, ignore_index=True)
        
        if 'CODICE ARTICOLO' in df_completo.columns:
            df_completo['CODICE ARTICOLO'] = df_completo['CODICE ARTICOLO'].astype(str)
            
        return df_completo
    else:
        return pd.DataFrame()

# Esecuzione principale dell'app
dati = load_all_data()

if dati.empty:
    st.error("Nessun dato trovato. Assicurati di aver inserito i file Excel nella cartella 'dati'.")
else:
    ricerca = st.text_input("🔍 Inserisci il CODICE ARTICOLO da cercare:", "")
    
    if ricerca:
        if 'CODICE ARTICOLO' in dati.columns:
            risultati = dati[dati['CODICE ARTICOLO'].str.contains(ricerca, case=False, na=False)]
            
            if not risultati.empty:
                st.success(f"Trovati {len(risultati)} risultati!")
                st.dataframe(risultati, use_container_width=True) 
            else:
                st.warning("Nessun articolo trovato con questo codice in nessuna Macro Famiglia.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")
