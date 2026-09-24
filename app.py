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
    cartella_dati = "dati" # Il nome della cartella dove hai messo i file Excel
    
    # Cerca tutti i file che finiscono con .xlsx nella cartella
    percorso_file = os.path.join(cartella_dati, "*.xlsx")
    tutti_i_file = glob.glob(percorso_file)
    
    if not tutti_i_file:
        return pd.DataFrame() # Ritorna un dataframe vuoto se non ci sono file
        
    lista_df = []
    
    for file in tutti_i_file:
        try:
            # Leggiamo il file Excel
            df = pd.read_excel(file)
            
            # Estraiamo il nome del file (es. "GYPSUM") per capire da dove arriva il dato
            nome_macro_famiglia = os.path.basename(file).replace('.xlsx', '')
            
            # Aggiungiamo una colonna all'inizio per mostrare la Macro Famiglia
            df.insert(0, 'FILE_ORIGINE', nome_macro_famiglia)
            
            lista_df.append(df)
        except Exception as e:
            st.warning(f"Errore nella lettura del file {file}: {e}")
            
    # Uniamo tutti i file in un'unica grande tabella
    if lista_df:
        df_completo = pd.concat(lista_df, ignore_index=True)
        
        # Assicuriamoci che il CODICE ARTICOLO sia letto come testo per facilitare la ricerca
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
    # Creiamo la casella di ricerca
    ricerca = st.text_input("🔍 Inserisci il CODICE ARTICOLO da cercare:", "")
    
    # Se l'utente ha digitato qualcosa...
    if ricerca:
        # Filtriamo il dataframe (ignorando maiuscole/minuscole e valori nulli)
        # Assicuriamoci che la colonna esista per evitare crash
        if 'CODICE ARTICOLO' in dati.columns:
            risultati = dati[dati['CODICE ARTICOLO'].str.contains(ricerca, case=False, na=False)]
            
            # Mostriamo i risultati
            if not risultati.empty:
                st.success(f"Trovati {len(risultati)} risultati!")
                st.dataframe(risultati, use_container_width=True) 
            else:
                st.warning("Nessun articolo trovato con questo codice in nessuna Macro Famiglia.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")