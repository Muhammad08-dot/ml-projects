import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
from sklearn.impute import SimpleImputer
from kaggle.api.kaggle_api_extended import KaggleApi 
import glob

# --- Page Config ---
st.set_page_config(page_title="AI Data Hunter", layout="wide")
st.title("🤖 AI Data Hunter (Hard Reset Version)")
st.markdown("### 🔍 Search -> Select -> Download -> Analyze")

# --- Session State Setup ---
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'dataset_options' not in st.session_state:
    st.session_state['dataset_options'] = {}

# --- SIDEBAR ---
st.sidebar.header("1. Data Source")
data_source = st.sidebar.radio("Select Source:", ["Upload CSV", "Smart Search (Kaggle)"])

# --- OPTION A: UPLOAD ---
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        st.session_state['df'] = pd.read_csv(uploaded_file)
        st.sidebar.success("✅ File Uploaded!")

# --- OPTION B: KAGGLE SEARCH ---
elif data_source == "Smart Search (Kaggle)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌍 Find Datasets")
    
    # 1. Search Box
    search_query = st.sidebar.text_input("Enter Topic", "Iris")
    
    # 2. Search Button (THE FIX IS HERE)
    if st.sidebar.button("🔎 Search New Data"):
        # --- MEMORY WIPE ---
        st.session_state['dataset_options'] = {}  # Dropdown saaf
        st.session_state['df'] = None             # Purana Table screen se gayab! (Important)
        
        try:
            with st.spinner(f"Searching for '{search_query}'..."):
                api = KaggleApi()
                api.authenticate()
                
                # Strict Search (No sorting by votes to get exact matches)
                datasets = api.dataset_list(search=search_query, max_size=50000000)
                
                st.session_state['dataset_options'] = {d.title: d.ref for d in datasets[:15]}
                
                if not st.session_state['dataset_options']:
                    st.sidebar.error(f"❌ '{search_query}' ka koi data nahi mila.")
                else:
                    st.sidebar.success(f"✅ {len(st.session_state['dataset_options'])} Datasets Found!")
                    st.rerun() # Page refresh to clear old table
                    
        except Exception as e:
            st.sidebar.error(f"Search Error: {e}")

    # 3. Dropdown & Download
    if st.session_state['dataset_options']:
        selected_title = st.sidebar.selectbox("Select Dataset:", list(st.session_state['dataset_options'].keys()))
        
        if st.sidebar.button("⬇️ Download & Load"):
            dataset_ref = st.session_state['dataset_options'][selected_title]
            
            try:
                with st.spinner("Deleting old files & Downloading new..."):
                    # --- FILE SYSTEM CLEANUP ---
                    # Purani files delete karna bohot zaroori hai
                    for f in glob.glob("*.csv"):
                        try:
                            os.remove(f)
                        except:
                            pass
                    
                    # Download New Data
                    api = KaggleApi()
                    api.authenticate()
                    api.dataset_download_files(dataset_ref, path=".", unzip=True)
                    
                    # Find New CSV
                    csv_files = glob.glob("*.csv")
                    if csv_files:
                        # Ab jo file milegi wo confirm nayi hogi
                        latest_file = max(csv_files, key=os.path.getctime)
                        st.session_state['df'] = pd.read_csv(latest_file)
                        st.success(f"✅ Loaded: {latest_file}")
                        st.rerun()
                    else:
                        st.error("❌ Download hua par CSV file nahi mili.")
                        
            except Exception as e:
                st.error(f"Download Error: {e}")

# --- MAIN DISPLAY AREA ---
# Agar DF None hai (Search button dabane ke baad), to kuch show nahi hoga
if st.session_state['df'] is not None:
    df = st.session_state['df']
    
    st.markdown("---")
    st.subheader(f"📊 Active Dataset: {df.shape[0]} Rows, {df.shape[1]} Columns")
    st.dataframe(df, height=300)

    # --- Data Health ---
    st.markdown("### 🏥 Data Stats")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows", df.shape[0])
    c2.metric("Missing Values", df.isnull().sum().sum())
    c3.metric("Columns", df.shape[1])

    # --- Visuals ---
    st.markdown("### 📈 Visual Check")
    num_cols = df.select_dtypes(include=np.number).columns
    if len(num_cols) > 0:
        col_to_plot = st.selectbox("Select Column to Plot:", num_cols)
        fig, ax = plt.subplots(figsize=(6,3))
        sns.histplot(df[col_to_plot], kde=True, ax=ax)
        st.pyplot(fig)
    else:
        st.info("No numeric columns to plot.")

    # --- Cleaning & Download ---
    st.markdown("---")
    c_btn1, c_btn2 = st.columns(2)
    
    with c_btn1:
        if st.button("🚀 Auto-Clean Data"):
            num_cols = df.select_dtypes(include=np.number).columns
            cat_cols = df.select_dtypes(include='object').columns
            
            if len(num_cols) > 0:
                df[num_cols] = SimpleImputer(strategy='mean').fit_transform(df[num_cols])
            if len(cat_cols) > 0:
                df[cat_cols] = df[cat_cols].astype(str)
                df[cat_cols] = SimpleImputer(strategy='most_frequent').fit_transform(df[cat_cols])
            
            st.session_state['df'] = df
            st.success("✨ Data Cleaned!")
            st.rerun()
            
    with c_btn2:
        st.download_button("📥 Download Final CSV", df.to_csv(index=False).encode('utf-8'), "cleaned_data.csv")