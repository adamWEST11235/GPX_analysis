import gpxpy
import folium
from geopy.distance import geodesic
from streamlit_folium import folium_static
from strava2gpx import strava2gpx
from datetime import datetime
import streamlit as st
import pandas as pd
import requests
from gpx import * 

def parse_gpx(file):
    #przetwarzanie pliku GPX
    gpx = gpxpy.parse(file)
    points = []
    elevations = []
    speeds = []
    times = []
    total_distance = 0.0
    total_up = 0.0
    total_down = 0.0
    
    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                points.append((point.latitude, point.longitude))
                elevations.append(point.elevation)
                times.append(point.time)
                
                if i > 0:
                    prev_point = segment.points[i - 1]
                    dist = geodesic((prev_point.latitude, prev_point.longitude), (point.latitude, point.longitude)).km
                    total_distance += dist

                    elevation_change = point.elevation - prev_point.elevation
                    if elevation_change > 0:
                        total_up += elevation_change
                    else:
                        total_down += abs(elevation_change)
                    
                    time_diff = (point.time - prev_point.time).total_seconds() / 3600.0
                    if time_diff > 0:
                        speeds.append(dist / time_diff)
                    else:
                        speeds.append(0)
                else:
                    speeds.append(0)
    
    start_time = times[0] if times else None
    end_time = times[-1] if times else None
    duration = (end_time - start_time).total_seconds() / 3600.0 if start_time and end_time else 0
    avg_speed = total_distance / duration if duration > 0 else 0

    return points, elevations, speeds, total_distance, total_up, total_down, start_time, end_time, duration, avg_speed

def reduce_data(data, max_points=2000):
    #uśrednianie wartości w zbierze 
    if len(data) <= max_points:
        return data
    ratio = len(data) / max_points
    reduced = []
    for i in range(max_points):
        start = int(i * ratio)
        end = int((i + 1) * ratio)
        chunk = data[start:end]
        if isinstance(chunk[0], tuple):
            avg_point = (
                sum(p[0] for p in chunk) / len(chunk),
                sum(p[1] for p in chunk) / len(chunk)
            )
            reduced.append(avg_point)
        else:
            reduced.append(sum(chunk) / len(chunk))
    return reduced


def plot_map(points):
    #rysowanie wykresu
    if not points:
        return None
    
    start_location = points[0]
    my_map = folium.Map(location=start_location, zoom_start=12)
    folium.PolyLine(points, color="blue", weight=5, opacity=0.7).add_to(my_map)
    folium.Marker(points[0], popup="Start", icon=folium.Icon(color="green")).add_to(my_map)
    folium.Marker(points[-1], popup="Meta", icon=folium.Icon(color="red")).add_to(my_map)
    return my_map

async def get_GPX(client_id, client_secret, refresh_token, id):
    #pobieranie wskazanego pliku GPX z strawa
    s2g = strava2gpx(client_id, client_secret, refresh_token)
    await s2g.connect()
    await s2g.write_to_gpx(id, "output")
    return 1



def get_token(client_id, client_secret,refresh_token):
    #pobieranie access token
    url = f"https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token"
    response = requests.post(url)
    if response.status_code == 200:
        return response.json()['access_token']


def get_activitis_list(token):
    #pobieranie informacji o trasach
    url = f'https://www.strava.com/api/v3/athlete/activities?access_token={token}'
    get_act = requests.get(url).json()
    return [{'id': x['id'],'distance': x['distance'], 'start_date':x['start_date_local']} for x in get_act]

def change_login_status():
    #zmiana statusu zalogowania
    st.session_state.subm = 1

def format_fun_for_acrivitis(trasa):
    dt = datetime.strptime(trasa["start_date"], "%Y-%m-%dT%H:%M:%SZ")
    dystans_km = trasa["distance"] / 1000
    return f"Trasa z dnia: {dt.strftime('%Y-%m-%d %H:%M:%S')} , dystans: {dystans_km:.2f} km"

def display_stats(uploaded_file):
    # Wyświetlanie mapy 

    points, elevations, speeds, total_distance, total_up, total_down, start_time, end_time, duration, avg_speed = parse_gpx(uploaded_file)

    points = reduce_data(points)
    elevations = reduce_data(elevations)
    speeds = reduce_data(speeds,200)
                
    # Tworzenie mapy
    my_map = plot_map(points)
    if my_map:
        folium_static(my_map)
                
    # Analiza trasy
    st.subheader("📈 Analiza trasy")
    st.write(f"**Długość trasy:** {total_distance:.2f} km")
    st.write(f"🔼 **Przewyższenie w górę:** {total_up:.2f} m")
    st.write(f"🔽 **Przewyższenie w dół:** {total_down:.2f} m")
    st.write(f"🕒 **Czas trwania:** {duration:.2f} godz.")
    st.write(f"🚀 **Średnia prędkość:** {avg_speed:.2f} km/h")
    st.write(f"📅 **Start:** {start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else 'Brak danych'}")
    st.write(f"📅 **Koniec:** {end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else 'Brak danych'}")

    # Wysokość
    elevation_df = pd.DataFrame({
        "Punkt": list(range(len(elevations))),
        "Wysokość (m)": elevations
    })
    st.line_chart(elevation_df.set_index("Punkt"))

    # Prędkość
    speed_df = pd.DataFrame({
        "Punkt": list(range(len(speeds))),
        "Prędkość (km/h)": speeds
    })
    st.line_chart(speed_df.set_index("Punkt"))    
