import streamlit as st
import asyncio
import os
from gpx import * 

def main():
    # zmienne przechowywane w pamięci
    if 'client_id' not in st.session_state:
        st.session_state.client_id = ''
    if 'client_secret' not in st.session_state:
        st.session_state.client_secret = ''
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = ''
    if 'activitis' not in st.session_state:
        st.session_state.activitis = []
    if 'subm' not in st.session_state:
        st.session_state.subm = 0
    if 'subm' not in st.session_state:
        st.session_state.trasa = None

    ress_button = 0
    tab1, tab2, tab3 = st.tabs(["📁 Wgraj plik GPX", "🚴 Pobierz z Stravy", "Strava info for acces tocken"])

    with tab1:
        st.title("📍 Analiza plików GPX")
        st.write("Wgraj plik GPX, aby zobaczyć trasę na mapie oraz wykonać analizę długości i wysokości.")
        
        uploaded_file = st.file_uploader("Załaduj plik GPX", type=["gpx"])
        
        if uploaded_file is not None:
            if st.button("📊 Przelicz i wyświetl mapę"):
                display_stats(uploaded_file=uploaded_file)

    with tab2:
        if st.session_state.client_id == '' or st.session_state.client_secret == '' or st.session_state.refresh_token == '' or st.session_state.subm == 0:
            st.write("Podaj dane z aplikacji Strava i pobierz aktywność jako GPX.")         

            st.session_state.client_id = st.text_input("Client ID", value=st.session_state.client_id)
            st.session_state.client_secret = st.text_input("Client Secret", type="password",value=st.session_state.client_secret)
            st.session_state.refresh_token = st.text_input("Refresh Token", type="password",value=st.session_state.refresh_token)

            st.button("Zaloguj",on_click=change_login_status) 
     
        else:
            
            ress_button = st.button("Wyloguj", use_container_width=True)
            if st.session_state.client_id != '' and st.session_state.client_secret != '' \
                and st.session_state.refresh_token != '' and st.session_state.subm \
                and len(st.session_state.activitis)<=0:

                token = get_token(st.session_state.client_id, st.session_state.client_secret, st.session_state.refresh_token)
                if token:   
                    st.session_state.activitis = get_activitis_list(token)
                else:
                    st.write("Błędne dane logowania")

            if len(st.session_state.activitis) > 0:
                st.session_state.trasa = st.selectbox('Wybierz swoją trasę',st.session_state.activitis, format_func=format_fun_for_acrivitis, index=None)
                load_gpx = st.button("Załaduj trase", disabled=(st.session_state.trasa is None))

                if load_gpx:
                    asyncio.run(get_GPX(
                        st.session_state.client_id, 
                        st.session_state.client_secret, 
                        st.session_state.refresh_token, 
                        st.session_state.trasa['id']
                        ))

                if os.path.exists('output.gpx') and load_gpx:
                    with open("output.gpx", "r", encoding="utf-8") as f:
                        load = f.read()
                        display_stats(load)
            else:
                st.write('Brak tras')
            if ress_button:
                
                st.session_state.client_id = ''
                st.session_state.client_secret = ''
                st.session_state.refresh_token = ''
                st.session_state.activitis = []
                ress_button = 0
                st.session_state.subm = 0
                st.session_state.trasa = None
                if os.path.exists('output.gpx'):
                    os.remove('output.gpx')
                st.rerun()

    with tab3:
        st.write('https://developers.strava.com/docs/authentication/')

if __name__ == "__main__":
    main()