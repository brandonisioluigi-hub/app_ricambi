import streamlit as st
import pandas as pd
import os
import glob

# Imposta la pagina
st.set_page_config(layout="wide", page_title="Ricerca Ricambi", page_icon="⚙️")

st.header("⚙️ Ricerca Ricambi - Archivio Globale")
st.write("Cerca il **Codice Articolo** attraverso tutte le Macro Famiglie per trovare immediatamente il ricambio corretto.")
st.divider()

def formatta_data_it(valore):
    """Formatta la data in gg-mm-aaaa rimuovendo l'ora."""
    if pd.isna(valore) or str(valore).strip() == "" or str(valore).strip() == "N/D":
        return ""
    try:
        data_pulita = pd.to_datetime(valore, dayfirst=True)
        return data_pulita.strftime('%d-%m-%Y')
    except:
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
        ricerca = st.text_input("🔍 INSERISCI IL CODICE ARTICOLO:", "", placeholder="Es. 9040")
    
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
                        
                        # 1. CERCA AUTOMATICAMENTE TUTTE LE REVISIONI (CE 1, CE 2, CE 3...)
                        revisioni_trovate = []
                        for col in row.index:
                            if "CODICE RICAMBIO CE" in col:
                                rev_num = col.replace("CODICE RICAMBIO CE", "").strip() # Estrae il numero "1", "2" ecc.
                                val = str(row[col]).strip()
                                # Registra la revisione solo se esiste un codice ricambio valido
                                if val and val != "N/D":
                                    revisioni_trovate.append(rev_num)
                        
                        revisioni_trovate.sort() # Ordina logicamente 1, 2, 3...

                        if revisioni_trovate:
                            # 2. CREA LE "TABS" (SCHEDE NAVIGABILI) PER OGNI REVISIONE TROVATA
                            tabs = st.tabs([f"🔄 Revisione CE {rev}" for rev in revisioni_trovate])
                            
                            for idx, rev in enumerate(revisioni_trovate):
                                with tabs[idx]:
                                    # Ricambio Principale
                                    cod_principale = str(row.get(f'CODICE RICAMBIO CE {rev}', '')).strip()
                                    st.code(cod_principale, language="text")
                                    
                                    # Date
                                    col_d1, col_d2 = st.columns(2)
                                    data_att = str(row.get(f'DATA ATTIVAZIONE CE {rev}', '')).strip()
                                    if data_att:
                                        col_d1.write(f"**🟢 Attivazione:** {data_att}")
                                        
                                    data_sos = str(row.get(f'DATA SOSPENSIONE CE {rev}', '')).strip()
                                    if data_sos:
                                        col_d2.write(f"**🔴 Sospensione:** {data_sos}")
                                        
                                    # 3. RICERCA DINAMICA DI COLONNE FUTURE PER QUESTA STESSA REVISIONE
                                    # Cerca qualsiasi altra colonna che finisca per "CE 1" (o la revisione corrente)
                                    altri_dati = {}
                                    for col in row.index:
                                        if f"CE {rev}" in col or f"CE{rev}" in col:
                                            # Escludiamo le tre colonne che abbiamo già stampato qui sopra
                                            if col not in [f'CODICE RICAMBIO CE {rev}', f'DATA ATTIVAZIONE CE {rev}', f'DATA SOSPENSIONE CE {rev}']:
                                                val = str(row[col]).strip()
                                                if val and val != "N/D":
                                                    altri_dati[col] = val
                                                    
                                    # Se trova altri ricambi/dati per questa revisione, li stampa in un elenco puntato
                                    if altri_dati:
                                        st.markdown("---") # Linea di separazione
                                        st.markdown(f"**📌 Altri componenti (Revisione CE {rev}):**")
                                        for k, v in altri_dati.items():
                                            # Pulisce il nome della colonna per togliere "CE 1" e renderlo leggibile
                                            nome_pulito = k.replace(f"CE {rev}", "").replace(f"CE{rev}", "").strip().title()
                                            st.write(f"- **{nome_pulito}:** {v}")

                        else:
                            st.info("Nessun ricambio assegnato a questo articolo.")
                        
                        # Espansore dati grezzi
                        with st.expander("Mostra tutti i dati della riga"):
                            row_filtrata = row[row != ""]
                            st.dataframe(pd.DataFrame(row_filtrata).T, hide_index=True)
                            
            else:
                st.warning("Nessun articolo trovato con questo codice.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")
