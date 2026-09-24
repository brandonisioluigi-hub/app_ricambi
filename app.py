import streamlit as st
import pandas as pd
import os
import glob

# Imposta la pagina e un po' di CSS personalizzato per le "Card"
st.set_page_config(layout="wide", page_title="Ricerca Ricambi", page_icon="⚙️")

st.title("⚙️ Ricerca Ricambi - Archivio Globale")
st.markdown("Cerca il **Codice Articolo** attraverso tutte le Macro Famiglie per trovare immediatamente il ricambio corretto.")
st.divider() # Aggiunge una linea orizzontale per separare il titolo

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
            # Riempiamo i campi vuoti con "N/D" per una migliore estetica
            df_completo = df_completo.fillna("N/D")
        return df_completo
    else:
        return pd.DataFrame()

dati = load_all_data()

if dati.empty:
    st.error("Nessun dato trovato nella cartella 'dati'.")
else:
    # Mettiamo la barra di ricerca in evidenza
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ricerca = st.text_input("🔍 INSERISCI IL CODICE ARTICOLO:", "", placeholder="Es. 60990")
    
    st.write("") # Spazio vuoto

    if ricerca:
        if 'CODICE ARTICOLO' in dati.columns:
            # Ricerca esatta o parziale
            risultati = dati[dati['CODICE ARTICOLO'].str.contains(ricerca, case=False, na=False)]
            
            if not risultati.empty:
                st.success(f"Trovati {len(risultati)} risultati per '{ricerca}'")
                
                # Invece della tabella, creiamo delle schede per ogni risultato
                for index, row in risultati.iterrows():
                    with st.container(border=True): # Crea un box con bordo per ogni risultato
                        
                        # Intestazione della scheda
                        st.subheader(f"🏷️ Articolo: {row.get('CODICE ARTICOLO', 'N/D')}")
                        st.caption(f"📁 Macro Famiglia: **{row['FILE_ORIGINE']}** | 🗂️ Famiglia: {row.get('FAMIGLIA', 'N/D')}")
                        
                        # Creiamo delle colonne interne per i dettagli dei ricambi
                        col_r1, col_r2, col_r3 = st.columns(3)
                        
                        # Blocco CE 1
                        with col_r1:
                            st.markdown("### 🛠️ Ricambio CE 1")
                            cod_ce1 = row.get('CODICE RICAMBIO CE 1', 'N/D')
                            if cod_ce1 != "N/D":
                                st.code(cod_ce1, language="text") # Evidenzia il codice
                            else:
                                st.write("Nessun ricambio")
                            st.write(f"**Dal:** {row.get('DATA ATTIVAZIONE CE 1', 'N/D')}")
                            st.write(f"**Al:** {row.get('DATA SOSPENSIONE CE 1', 'N/D')}")
                            
                        # Blocco CE 2 (se esiste)
                        with col_r2:
                            st.markdown("### 🔧 Ricambio CE 2")
                            cod_ce2 = row.get('CODICE RICAMBIO CE 2', 'N/D')
                            if cod_ce2 != "N/D" and str(cod_ce2).strip() != "":
                                st.code(cod_ce2, language="text")
                            else:
                                st.write("Nessun ricambio")
                            st.write(f"**Dal:** {row.get('DATA ATTIVAZIONE CE 2', 'N/D')}")
                            st.write(f"**Al:** {row.get('DATA SOSPENSIONE CE 2', 'N/D')}")
                            
                        # Puoi aggiungere un terzo blocco col_r3 per altre info (es. note) se vuoi!
                        
                        # Se l'utente vuole comunque vedere la tabella grezza di questo singolo articolo
                        with st.expander("Mostra tutti i dati grezzi dell'articolo"):
                            # Filtriamo solo le colonne che non sono N/D per pulire la vista
                            row_filtrata = row[row != "N/D"]
                            st.dataframe(pd.DataFrame(row_filtrata).T, hide_index=True)
                            
            else:
                st.warning("Nessun articolo trovato con questo codice.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")
