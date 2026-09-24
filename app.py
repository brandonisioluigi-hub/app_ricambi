import streamlit as st
import pandas as pd
import os
import glob

# Imposta la pagina
st.set_page_config(layout="wide", page_title="Ricerca Ricambi", page_icon="⚙️")

# Titoli rimpiccioliti (usiamo un header più piccolo invece del title)
st.header("⚙️ Ricerca Ricambi - Archivio Globale")
st.write("Cerca il **Codice Articolo** attraverso tutte le Macro Famiglie per trovare immediatamente il ricambio corretto.")
st.divider()

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
            # Invece di "N/D", questa volta manteniamo i valori vuoti per gestirli dopo
            df_completo = df_completo.fillna("") 
        return df_completo
    else:
        return pd.DataFrame()

dati = load_all_data()

if dati.empty:
    st.error("Nessun dato trovato nella cartella 'dati'.")
else:
    # Barra di ricerca
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ricerca = st.text_input("🔍 INSERISCI IL CODICE ARTICOLO:", "", placeholder="Es. 60990")
    
    st.write("") 

    if ricerca:
        if 'CODICE ARTICOLO' in dati.columns:
            risultati = dati[dati['CODICE ARTICOLO'].str.contains(ricerca, case=False, na=False)]
            
            if not risultati.empty:
                st.success(f"Trovati {len(risultati)} risultati per '{ricerca}'")
                
                for index, row in risultati.iterrows():
                    with st.container(border=True): 
                        
                        # Intestazione della scheda (rimpicciolita con markdown)
                        st.markdown(f"**🏷️ Articolo: {row.get('CODICE ARTICOLO', '')}**")
                        st.caption(f"📁 Macro Famiglia: **{row['FILE_ORIGINE']}** | 🗂️ Famiglia: {row.get('FAMIGLIA', '')}")
                        
                        col_r1, col_r2 = st.columns(2)
                        
                        # Blocco CE 1
                        with col_r1:
                            cod_ce1 = str(row.get('CODICE RICAMBIO CE 1', '')).strip()
                            # Controlliamo se c'è un ricambio valido (diverso da vuoto o "N/D")
                            if cod_ce1 and cod_ce1 != "N/D":
                                st.markdown("**🛠️ Ricambio CE 1**")
                                st.code(cod_ce1, language="text")
                                
                                # Mostriamo le date solo se esistono
                                data_att_ce1 = str(row.get('DATA ATTIVAZIONE CE 1', '')).strip()
                                if data_att_ce1 and data_att_ce1 != "N/D":
                                    st.write(f"**Dal:** {data_att_ce1}")
                                    
                                data_sos_ce1 = str(row.get('DATA SOSPENSIONE CE 1', '')).strip()
                                if data_sos_ce1 and data_sos_ce1 != "N/D":
                                    st.write(f"**Al:** {data_sos_ce1}")
                            
                        # Blocco CE 2 (si vede SOLO se esiste il ricambio)
                        with col_r2:
                            cod_ce2 = str(row.get('CODICE RICAMBIO CE 2', '')).strip()
                            if cod_ce2 and cod_ce2 != "N/D":
                                st.markdown("**🔧 Ricambio CE 2**")
                                st.code(cod_ce2, language="text")
                                
                                data_att_ce2 = str(row.get('DATA ATTIVAZIONE CE 2', '')).strip()
                                if data_att_ce2 and data_att_ce2 != "N/D":
                                    st.write(f"**Dal:** {data_att_ce2}")
                                    
                                data_sos_ce2 = str(row.get('DATA SOSPENSIONE CE 2', '')).strip()
                                if data_sos_ce2 and data_sos_ce2 != "N/D":
                                    st.write(f"**Al:** {data_sos_ce2}")
                        
                        # Espansore per i dati grezzi
                        with st.expander("Mostra tutti i dati della riga"):
                            # Filtriamo solo le colonne che non sono vuote
                            row_filtrata = row[row != ""]
                            st.dataframe(pd.DataFrame(row_filtrata).T, hide_index=True)
                            
            else:
                st.warning("Nessun articolo trovato con questo codice.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")
