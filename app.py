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
    if pd.isna(valore) or str(valore).strip() == "" or str(valore).strip().upper() in ["N/D", "NAN"]:
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
            # AGGIUNTA FONDAMENTALE: dtype=str
            # Forza Python a leggere le celle esattamente come sono scritte in Excel (come Testo), 
            # evitando che trasformi i codici in numeri decimali (.0) e che si mangi gli zeri iniziali!
            df = pd.read_excel(file, dtype=str)
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
            
            # Pulizia per rimuovere i "nan" (testuali) generati dalla lettura forzata come stringa
            df_completo = df_completo.fillna("")
            df_completo = df_completo.replace("nan", "")
            
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
                        
                        # 1. CERCA AUTOMATICAMENTE TUTTE LE REVISIONI
                        revisioni_trovate = []
                        for col in row.index:
                            if "CODICE RICAMBIO CE" in col:
                                rev_num = col.replace("CODICE RICAMBIO CE", "").strip() 
                                val = str(row[col]).strip()
                                if val and val.upper() not in ["N/D", "NAN", ""]:
                                    revisioni_trovate.append(rev_num)
                        
                        revisioni_trovate.sort() 

                        if revisioni_trovate:
                            # 2. CREA LE TABS
                            tabs = st.tabs([f"🔄 Revisione CE {rev}" for rev in revisioni_trovate])
                            
                            for idx, rev in enumerate(revisioni_trovate):
                                with tabs[idx]:
                                    # Ricambio Principale
                                    cod_principale = str(row.get(f'CODICE RICAMBIO CE {rev}', '')).strip()
                                    # Ulteriore sicurezza per eliminare eventuali vecchi ".0" residui
                                    if cod_principale.endswith(".0"):
                                        cod_principale = cod_principale[:-2]
                                    st.code(cod_principale, language="text")
                                    
                                    # Date
                                    col_d1, col_d2 = st.columns(2)
                                    data_att = str(row.get(f'DATA ATTIVAZIONE CE {rev}', '')).strip()
                                    if data_att and data_att.upper() not in ["N/D", "NAN"]:
                                        col_d1.write(f"**🟢 Attivazione:** {data_att}")
                                        
                                    data_sos = str(row.get(f'DATA SOSPENSIONE CE {rev}', '')).strip()
                                    if data_sos and data_sos.upper() not in ["N/D", "NAN"]:
                                        col_d2.write(f"**🔴 Sospensione:** {data_sos}")
                                        
                                    # 3. RICERCA DINAMICA DI ALTRI COMPONENTI
                                    altri_dati = {}
                                    for col in row.index:
                                        if f"CE {rev}" in col or f"CE{rev}" in col:
                                            if col not in [f'CODICE RICAMBIO CE {rev}', f'DATA ATTIVAZIONE CE {rev}', f'DATA SOSPENSIONE CE {rev}']:
                                                val = str(row[col]).strip()
                                                if val.endswith(".0") and val.replace(".", "").isdigit():
                                                    val = val[:-2]
                                                if val and val.upper() not in ["N/D", "NAN", ""]:
                                                    altri_dati[col] = val
                                                    
                                    if altri_dati:
                                        st.markdown("---") 
                                        st.markdown(f"**📌 Altri componenti (Revisione CE {rev}):**")
                                        for k, v in altri_dati.items():
                                            nome_pulito = k.replace(f"CE {rev}", "").replace(f"CE{rev}", "").strip().title()
                                            st.write(f"- **{nome_pulito}:** {v}")

                        else:
                            st.info("Nessun ricambio assegnato a questo articolo.")
                        
                        # Espansore dati grezzi
                        with st.expander("Mostra tutti i dati della riga"):
                            row_filtrata = row[(row != "") & (row != "nan")]
                            st.dataframe(pd.DataFrame(row_filtrata).T, hide_index=True)
                            
            else:
                st.warning("Nessun articolo trovato con questo codice.")
        else:
            st.error("Errore: La colonna 'CODICE ARTICOLO' non è stata trovata nei tuoi file Excel.")
