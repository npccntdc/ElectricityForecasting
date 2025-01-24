import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Function to fetch weather data
def get_weather_data(api_key, latitude, longitude, num_days=3):
    location = f"{latitude},{longitude}"
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={num_days}&tp=15"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve data: {response.status_code}")
        return None

# Function to process weather data
def process_weather_data(weather_data, city_name):
    all_weather_data = []
    if weather_data:
        for day in weather_data['forecast']['forecastday']:
            for hour in day['hour']:
                record = {
                    'City': city_name,
                    'Date': day['date'],
                    'Time': hour['time'],
                    'Wind Gust (mph)': hour['gust_mph'],
                    'Wind Gust (kph)': hour['gust_kph'],
                    'Temperature (°C)': hour['temp_c'],
                    'Chance of Rain (%)': hour['chance_of_rain']
                }
                all_weather_data.append(record)
    return pd.DataFrame(all_weather_data)

# Streamlit App
def main():
    st.title("Pakistan Wind Gust & Electricity Demand Impact")
    st.sidebar.header("Settings")

    # Inputs
    api_key = st.sidebar.text_input("Weather API Key", type="password")
    num_days = st.sidebar.slider("Forecast Days", 1, 3, 3)
    gust_threshold = st.sidebar.slider("Wind Gust Threshold (mph)", 20, 30, 40, 50)

    cities = {
        "Karachi": (24.8607, 67.0011),
        "Lahore": (31.5497, 74.3436),
        "Islamabad": (33.6844, 73.0479),
        "Quetta": (30.1798, 66.975),
        "Peshawar": (34.0151, 71.5249)
    }

    if api_key:
        st.sidebar.success("API Key Entered")
        
        # Fetch data for each city
        city_weather_data = []
        for city, coords in cities.items():
            weather_data = get_weather_data(api_key, coords[0], coords[1], num_days)
            if weather_data:
                city_df = process_weather_data(weather_data, city)
                city_weather_data.append(city_df)
        
        if city_weather_data:
            df = pd.concat(city_weather_data, ignore_index=True)
            
            # Highlight areas with high wind gusts
            high_gust_df = df[df['Wind Gust (mph)'] >= gust_threshold]
            st.header("Wind Gust Alerts")
            if not high_gust_df.empty:
                st.warning(f"{len(high_gust_df)} high wind gust events detected across Pakistan!")
                st.dataframe(high_gust_df)
            else:
                st.success("No high wind gust events detected.")

            # Visualize data
            st.header("Wind Gust Forecast Across Pakistan")
            fig = px.line(df, x='Time', y='Wind Gust (mph)', color='City', title="Wind Gusts Over Time")
            st.plotly_chart(fig, use_container_width=True)

            # Estimate electricity demand impact
            st.header("Impact on Electricity Demand")
            # Hypothetical demand reduction formula
            df['Estimated Demand Reduction (%)'] = df['Wind Gust (mph)'].apply(lambda x: min(max((x - gust_threshold) * 0.5, 0), 10))
            demand_impact_df = df.groupby('City')['Estimated Demand Reduction (%)'].mean().reset_index()
            st.bar_chart(demand_impact_df.set_index('City'))
            
            st.write("The above bar chart shows the estimated reduction in electricity demand (%) for each city due to wind gust effects.")

    else:
        st.warning("Please enter your Weather API key to get started.")

if __name__ == "__main__":
    main()