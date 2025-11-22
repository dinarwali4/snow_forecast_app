import xarray as xr
import matplotlib.pyplot as plt
import streamlit as st

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("❄️ Probabilistic Snowfall Forecast for KP")
st.header("Winter 2025-2026 (from Oct 2025 Forecast)")

FREEZING_POINT = 273.15

# --- Data Loading Functions ---
@st.cache_data
def load_data(filename):
    print(f"Loading data from: {filename}")
    try:
        data = xr.open_dataset(filename, decode_times=False)
        return data
    except Exception as e:
        st.error(f"Error loading {filename}: {e}. Make sure it's on your Desktop.")
        return None

# --- Calculation Function ---
# THIS IS THE FIX: 'data' is changed to '_data'
@st.cache_data
def get_snow_forecast(_data): # <--- FIX IS HERE
    if _data is None:
        return None, None
    print("Calculating forecast...")
    temp = _data['t2m']
    precip = _data['tprate']
    
    snowfall_all_members = precip.where(temp < FREEZING_POINT)
    mean_snowfall = snowfall_all_members.mean(dim='number')
    snow_occurs = (snowfall_all_members > 1e-9)
    probability_of_snow = snow_occurs.mean(dim='number') * 100
    
    return mean_snowfall, probability_of_snow

# --- Plotting Function ---
@st.cache_data
def create_plots(_mean_snowfall, _probability_of_snow): # <-- Also fixed here
    if _mean_snowfall is None:
        return None
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Mean
    _mean_snowfall.isel(forecast_reference_time=0).plot(ax=ax1, cmap='viridis')
    ax1.set_title("1. Mean 'Most Likely' Snowfall Forecast")
    
    # Plot 2: Probability
    _probability_of_snow.isel(forecast_reference_time=0).plot(ax=ax2, cmap='Blues', vmin=0, vmax=100)
    ax2.set_title("2. Probability of Any Snowfall (%)")
    
    plt.tight_layout()
    return fig

# --- Main App ---
st.tabs(["December 2025", "January 2026", "February 2026"])
dec_tab, jan_tab, feb_tab = st.tabs(["December 2025", "January 2026", "February 2026"])

# --- December Tab ---
with dec_tab:
    st.subheader("Forecast for December 2025")
    dec_data = load_data("kp_december_2025_forecast.nc")
    dec_mean, dec_prob = get_snow_forecast(dec_data)
    st.pyplot(create_plots(dec_mean, dec_prob))

# --- January Tab ---
with jan_tab:
    st.subheader("Forecast for January 2026")
    jan_data = load_data("kp_january_2026_forecast.nc")
    jan_mean, jan_prob = get_snow_forecast(jan_data)
    st.pyplot(create_plots(jan_mean, jan_prob))

# --- February Tab ---
with feb_tab:
    st.subheader("Forecast for February 2026")
    feb_data = load_data("kp_february_2026_forecast.nc")
    feb_mean, feb_prob = get_snow_forecast(feb_data)
    st.pyplot(create_plots(feb_mean, feb_prob))

st.subheader("About this Data")
st.write("""
This forecast shows the 'most likely' snowfall (left) and the 'confidence' (probability) of any snow (right) for each month. 
This is based on the 51-member ECMWF seasonal forecast made in October 2025.
""")
# ---------------------------------------------------------
# PASTE THIS AT THE BOTTOM OF calculate_PROBABILITY.py
# ---------------------------------------------------------
import os # Make sure this is imported at the top, or add it here

st.markdown("---") # A visual line separator
st.header("📆 Daily Snow Forecast: December 2025")
st.write("Use the slider below to view the high-resolution forecast for specific days.")

# 1. Create the Slider
day = st.slider("Select a Day in December", min_value=1, max_value=31, value=1)

# 2. Define the File Path (pointing to your clean 'data' folder)
# The f-string inserts the slider number into the filename
file_path = f"data/december_day_{day}.nc"

# 3. Load and Visualize
if os.path.exists(file_path):
    try:
        # Open the NetCDF file
        with xr.open_dataset(file_path) as ds:
            
            # Automatically grab the main data variable (usually 'precip' or 'snow')
            var_name = list(ds.data_vars)[0]
            data_variable = ds[var_name]

            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 5))
            data_variable.plot(ax=ax, cmap='Blues', add_colorbar=True)
            
            # Customize the title
            ax.set_title(f"Snowfall Intensity - December {day}, 2025", fontsize=12)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")

            # Display in Streamlit
            st.pyplot(fig)
            
            # Optional: Show specific values if needed
            with st.expander(f"View Raw Data for Dec {day}"):
                st.write(ds)

    except Exception as e:
        st.error(f"An error occurred reading the file: {e}")
else:
    st.warning(f"Forecast data for December {day} is not available yet.")
