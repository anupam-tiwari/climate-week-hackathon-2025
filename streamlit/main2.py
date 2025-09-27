import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import numpy as np # Import numpy for color coding

# 1. Load Data
# Assuming the column names are 'x' for Longitude (lon) and 'y' for Latitude (lat)
try:
    cooling_locations = pd.read_csv("Cool_It__NYC_2020_-_Cooling_Sites_20250927.csv")
    cooling_locations = cooling_locations.rename(columns={"y": "lat", "x": "lon"})
    
    # 2. Add a column for marker size and color for the cooling sites (all cooling sites are 'blue')
    cooling_locations["size"] = 10  # Default size for cooling sites
    cooling_locations["color"] = [255, 0, 0, 100] # Blue/Red/Green/Alpha for cooling sites (Blue color)
    cooling_locations['source'] = 'Cooling Site'
    
except FileNotFoundError:
    st.error("Error: 'Cool_It__NYC_2020_-_Cooling_Sites_20250927.csv' not found. Please check the file path.")
    st.stop()
except KeyError as e:
    st.error(f"Error: Missing column {e} in the CSV file. Check that 'x' and 'y' columns exist.")
    st.stop()

# --- Application UI ---

st.markdown("<h4 style='color:blue;'>Heat Portal 🥵</h4>", unsafe_allow_html=True)
st.write("Fetching your location...")

# 3. Get user location
location = streamlit_geolocation()
user_lat = location.get("latitude")
user_lon = location.get("longitude")

# 4. Initialize combined DataFrame for map display
map_data = cooling_locations.copy()

# 5. Handle and Display Location
if user_lat and user_lon:
    st.markdown("<span style='color:red;'>✅ Location found.</span>", unsafe_allow_html=True)

    # Create a DataFrame for the user's location
    user_location_df = pd.DataFrame([{
        "lat": user_lat,
        "lon": user_lon,
        "size": 50,  # Larger size for user's point
        "color": [255, 0, 0, 255],  # **Bright Red** marker for the user
        'source': 'Your Location'
    }])

    # Combine user location with cooling sites for the map
    map_data = pd.concat([map_data, user_location_df], ignore_index=True)
    
    # Optional: Display a message about the heat area (can be based on actual data/zone check)
    st.markdown("<span style='color:red;'>⚠️ Looks like you may be in a heat risk area.</span>", unsafe_allow_html=True)

# 6. Display the Map
# The color column must be in a specific format for st.map to render colors.
# Since st.map defaults to a fixed size/color if not specified, it's often better
# to use st.pydeck_chart for fine-grained control over color and size.
st.map(map_data, 
       latitude="lat", 
       longitude="lon", 
       size="size", 
       color="color",
       zoom=11 if user_lat else 10) # Zoom in if user location is available

# --- Chatbot Logic ---

client = st.secrets["openai_client"] # Assuming you have a client in secrets now

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Create Dynamic System Prompt
def get_system_prompt():
    base_prompt = """
    You are a helpful and compassionate 'Heat Portal' AI assistant. Your primary function is to provide information about the nearest cooling centers based on the user's location.
    Always prioritize safety and comfort. Do not invent locations or services.
    """
    if user_lat and user_lon:
        # 8. Inject user location into the system prompt
        base_prompt += f"\n\nTHE USER'S CURRENT LOCATION IS: Latitude: {user_lat}, Longitude: {user_lon}. Use this information to guide your responses, especially for recommending nearby cooling sites from the provided data."
    else:
        base_prompt += "\n\nTHE USER'S LOCATION IS UNKNOWN. Ask the user for a street address or neighborhood to find nearby cooling sites."
    return base_prompt

if prompt := st.chat_input("Heat portal - type anything"):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages = [{"role": "system", "content": get_system_prompt()}] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    
    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})