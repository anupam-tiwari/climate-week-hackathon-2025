from openai import OpenAI
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
from io import StringIO



lol = """
Status,FeatureType,PropertyName,SubPropertyName,GISPropNum,OMPPropID,Borough,District,x,y
Activated,Misting Station,Newtown Barge Playground,,B135,B135,Brooklyn,B-01,-73.959782702112,40.7359820507185
Activated,Hydrant Spray Cap,Randall's Island Park,,M107,M107,Manhattan,M-11R,-73.934913286427,40.7836316072814
Activated,Hydrant Spray Cap,Randall's Island Park,,M107,M107,Manhattan,M-11R,-73.9341482801174,40.7833712248471
Activated,Misting Station,Rockaway Beach Boardwalk,,Q163,Q163,Queens,Q-14,-73.8298133948064,40.5793258574036
"""

# read the CSV string into a DataFrame
cooling_locations = pd.read_csv(StringIO(lol))

st.markdown("<h4 style='color:blue;'>Heat Portal</h4>", unsafe_allow_html=True)
# Get user location
location = streamlit_geolocation()

# Display map if location available
if location and location.get("latitude") and location.get("longitude"):
    # Create DataFrame with correct column names
    df = pd.DataFrame([{
        "lat": location["latitude"],
        "lon": location["longitude"]
    }])
    st.map(df)
    
    st.markdown("<span style='color:red;'>looks like you are in a heat wave area., here are few recomendations</span>", unsafe_allow_html=True)
    
    df = pd.DataFrame({
        "lat": cooling_locatios["x"][:2],
        "lon": cooling_locatios["y"][:2]
    })
    st.map(df[:3])
    st.write(cooling_locatios[:3])
    
    df = pd.DataFrame(cooling_locatios)
    
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def recommendation_system_prompt():
    if location and location.get("latitude") and location.get("longitude"):
        return {1}
    return

system_prompt = """
return these location always: 

POPS - 120 Park Avenue ♂
Indoor - Other Indoor Cool Option
0.03 mi
120 PARK AVENUE
Open • Closes 9:30 PM • Privately Owned Public Space. Hours are subject to change.

Stavros Niarchos Foundation Library (SNFL). ♂
Indoor - Cooling Center
0.16 mi
455 5 AVENUE
Open • Closes 6:00 PM • (212) 340-0863

Stephen A Schwarzman Building ♂
Indoor - Cooling Center
0.21 mi
476 5 AVENUE
Open • Closes 6:00 PM • (917) 275-6975
"""

if prompt := st.chat_input("Heat portal - type anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
