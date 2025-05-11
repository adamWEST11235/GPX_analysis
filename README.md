# Analizator Tras GPX

Aplikacja webowa do analizy tras GPX, która umożliwia:
- Wgrywanie i analizę plików GPX
- Pobieranie tras z konta Strava
- Wyświetlanie statystyk i map tras

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/adamWEST11235/GPX_analysis.git
```

2. Zainstaluj wymagane zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

Aby uruchomić aplikację, wykonaj:
```bash
streamlit run main.py
```

## Funkcjonalności

- 📁 Wgrywanie plików GPX
- 🚴 Pobieranie tras z konta Strava
- 📊 Analiza długości i wysokości trasy
- 🗺️ Wyświetlanie trasy na mapie

## Konfiguracja Strava API

Aby korzystać z funkcji pobierania tras ze Stravy, należy:
1. Utworzyć aplikację na [Strava API](https://developers.strava.com/)
2. Uzyskać Client ID, Client Secret i Refresh Token
3. Wprowadzić te dane w odpowiedniej zakładce aplikacji 
