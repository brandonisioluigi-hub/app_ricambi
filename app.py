import streamlit as st
import pandas as pd
import os
import glob

# Imposta la pagina
st.set_page_config(layout="wide", page_title="Ricerca Ricambi", page_icon="⚙️")

st.header("⚙️ Ricerca Ricambi - Archivio Globale")
st.write("Cerca il **Codice Articolo** attraverso tutte le Macro Famiglie per trovare immediatamente il ricambio corretto.")
st.divider()

# --- NUOVA FUNZIONE PER FORMATTARE LE DATE ---
def formatta_data_it(valore):
    """Formatta la data in gg-mm-aaaa rimuovendo l'ora. Ignora i testi."""
    if pd.isna(valore) or str(valore).strip() == "" or str(valore).strip() == "N/D":
        return ""
    try:
        # Tenta di convertire in data. dayfirst=True assicura che 10/11 sia letto come 10 Novembre.
        data_pulita = pd.to_datetime(valore, dayfirst=True)
        return data_pulita.strftime('%d-%m-%Y')
    except:
        # Se non è una data (es. c'è scritto testo), lascia il testo e rimuove orari finti.
        return str(valore).replace(" 00:00:00", "").strip()

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
            
            # --- APPLICHIAMO LA FORMATTAZIONE DELLE DATE ---
            # Cerchiamo tutte le colonne che contengono la parola "DATA" e le formattiamo
            for col in df.columns:
                if 'DATA' in col:
                    df[col] = df[col].apply(formatta_data_it)
                    
            nome_macro_famiglia = os.path.basename(file).replace('.xlsx', '')
            df.insert(0, 'FILE_ORIGINE', nome_macro_famiglia)
            lista_df.append(df)
        except Exception as e:
            st.warning(f"Errore nella lettura del file {file}: {e}")
            
    if lista_df:
        df_completo = pd.concat(lista_df, ignore_index=True)
        if 'CODICE ARTICOLO' in df_completo.columns:
            df_completo['CODICE ARTICOLO'] = df_completo['CODICE ARTICOLO'].astype(str)
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
                        
                        st.markdown(f"**🏷️ Articolo: {row.get('CODICE ARTICOLO', '')}**")
                        st.caption(f"📁 Macro Famiglia: **{row['FILE_ORIGINE']}** | 🗂️ Famiglia: {row.get('FAMIGLIA', '')}")
                        
                        col_r1, col_r2 = st.columns(2)
                        
                        # Blocco CE 1
                        with col_r1:
                            cod_ce1 = str(row.get('CODICE RICAMBIO CE 1', '')).strip()
                            if cod_ce1 and cod_ce1 != "N/D":
                                st.markdown("**🛠️ Ricambio CE 1**")
                                st.code(cod_ce1, language="text")
                                
                                data_att_ce1 = str(row.get('DATA ATTIVAZIONE CE 1', '')).strip()
                                if data_att_ce1:
                                    st.write(f"**Dal:** {data_att_ce1}")
                                    
                                data_sos_ce1 = str(row.get('DATA SOSPENSIONE CE 1', '')).strip()
                                if data_sos_ce1:
                                    st.write(f"**Al:** {data_sos_ce1}")
                            
                        # Blocco CE 2
                        with col_r2:
                            cod_ce2 = str(row.get('CODICE RICAMBIO CE 2', '')).strip()
                            if cod_ce2 and cod_ce2 != "N/D":
                                st.markdown("**🔧 Ricambio CE 2**")
                                st.code(cod_ce2, language="text")
                                
                                data_att_ce2 = str(row.get('DATA ATTIVAZIONE CE 2', '')).strip()
                                if data_att_ce2:
                                    st.write(f"**Dal:** {data_att_ce2}")
                                    
                                data_sos_ce2 = str(row.get('DATA SOSPENSIONE CE 2', '')).strip()
                                if data_sos_ce2:
                                    st.write(f"**Al:** {data_sos_ce2}")
                        
                        # Espansore dati grezzi
                        with st.expander("Mostra tutti i dati della riga"):
                            row_filtrata = row[row != ""]
                            st.dataframe(pd.DataFrame(row_filtrata).T, hide_index=True)
                            
            else:
                st.warning("Nessun articolo trovato con questo codice.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")
