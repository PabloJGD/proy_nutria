import streamlit as st
import requests
import json
from PIL import Image
import io

# Backend API URL
API_URL = "http://localhost:8000/recommend"

st.set_page_config(page_title="AI Chef Assistant", page_icon="🍳", layout="wide")

st.title("🍳 AI Chef & Nutritionist Agent")
st.markdown("Upload usage photo of your ingredients or list them, and I'll recommend the best healthy recipes for you!")

# Sidebar - User Profile
with st.sidebar:
    st.header("👤 Your Profile")
    name = st.text_input("Name", "User")
    # Soporta decimales para bebés (ej. 0.5 años)
    age = st.number_input("Age", min_value=0.0, max_value=120.0, value=30.0, step=0.1)
    
    st.subheader("Health Goals")
    goals = st.text_area("Your Goals (e.g., Lose weight, build muscle)", "Eat healthy")
    
    st.subheader("Dietary Restrictions")
    diet_options = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Low-Carb", "Keto", "Paleo"]
    selected_diets = st.multiselect("Select Diets", diet_options)
    
    allergies = st.text_input("Allergies (comma separated)", "")
    
    # Store profile in session state
    user_profile = {
        "name": name,
        "age": age,
        "health_goals": goals,
        "dietary_restrictions": selected_diets,
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()]
    }

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 Step 1: Add Ingredients")
    
    tabs = st.tabs(["Upload Image", "Take Photo", "Text Input"])
    
    image_file = None
    text_input = None
    
    with tabs[0]:
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            image_file = uploaded_file

    with tabs[1]:
        camera_file = st.camera_input("Take a picture")
        if camera_file:
            image = Image.open(camera_file)
            st.image(image, caption='Captured Image', use_column_width=True)
            image_file = camera_file

    with tabs[2]:
        text_input = st.text_area("Or type ingredients here (optional if image provided)", height=100)

    if st.button("🔍 Find Recipes", type="primary", use_container_width=True):
        if not image_file and not text_input:
            st.error("Please provide an image or text description!")
        else:
            with st.spinner("Analyzing ingredients and finding recipes..."):
                # Prepare payload
                files = {}
                if image_file:
                    # Reset pointer
                    image_file.seek(0)
                    files = {"image": ("image.jpg", image_file, "image/jpeg")}
                
                data = {
                    "text_description": text_input if text_input else "",
                    "user_profile": json.dumps(user_profile)
                }
                
                try:
                    # Send request to backend
                    response = requests.post(API_URL, data=data, files=files if files else None)
                    response.raise_for_status()
                    result = response.json()
                    
                    if "recommendation" in result:
                        st.session_state['result'] = result['recommendation']
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to backend. Is 'main.py' running?")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with col2:
    st.header("🍽️ Recommendations")
    
    if 'result' in st.session_state:
        st.success("Here are my suggestions!")
        st.markdown(st.session_state['result'])
    else:
        st.info("Recommendations will appear here after you submit.")
