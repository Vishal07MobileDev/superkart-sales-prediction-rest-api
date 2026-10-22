import streamlit as st
import requests
import pandas as pd
import json

# Set page configuration
st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")

# Configure Flask API URL (configured to access the backend container directly in Docker network)
BACKEND_URL = "http://backend:7860"

st.title("🛒 SuperKart Store Sales Forecast Dashboard")
st.write("This interactive interface allows you to predict sales totals for individual products or perform batch forecasting using our tuned machine learning models.")

tab1, tab2 = st.tabs(["🎯 Single Product Sales Forecast", "📁 Batch Forecast Upload"])

with tab1:
    st.header("Single Product Sales Forecast")
    st.write("Please select the product and store attributes below to estimate sales.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_id_char = st.selectbox("Product ID Prefix", options=["FD", "DR", "NC"], help="FD = Food, DR = Drink, NC = Non-Consumable")
        product_weight = st.number_input("Product Weight", min_value=1.0, max_value=50.0, value=12.5, step=0.1)
        product_sugar_content = st.selectbox("Sugar Content", options=["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input("Allocated Area Ratio", min_value=0.0, max_value=1.0, value=0.05, format="%.4f")
        product_mrp = st.number_input("Product Maximum Retail Price (MRP)", min_value=10.0, max_value=500.0, value=145.0, step=0.5)
        
    with col2:
        product_type_category = st.selectbox("Product Category", options=["Non Perishables", "Perishables", "Non-Consumables"])
        store_size = st.selectbox("Store Size", options=["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("Store City Tier", options=["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", options=["Food Mart", "Departmental Store", "Supermarket Type1", "Supermarket Type2"])
        store_age_years = st.slider("Store Age (Years)", min_value=1, max_value=50, value=15)
        
    if st.button("Predict Sales"):
        payload = {
            "Product_Weight": float(product_weight),
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": float(product_allocated_area),
            "Product_MRP": float(product_mrp),
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age_years),
            "Product_Type_Category": product_type_category
        }
        
        try:
            with st.spinner("Calculating sales forecast..."):
                response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)
                if response.status_code == 200:
                    prediction = response.json().get("Product_Store_Sales_Total")
                    st.success(f"### Predicted Product Store Sales Total: **${prediction:,.2f}**")
                else:
                    st.error(f"API Error: {response.json().get('error', 'Unknown Error')}")
        except Exception as e:
            st.error(f"Unable to connect to prediction API: {str(e)}")

with tab2:
    st.header("Bulk Forecast Upload")
    st.write("Upload a CSV file containing multiple product and store features to generate predictions in batches.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        # Read and preview data
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.write("### File Preview")
            st.dataframe(preview_df.head())
            
            # Reset the file pointer to allow uploading again
            uploaded_file.seek(0)
            
            if st.button("Generate Batch Predictions"):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                with st.spinner("Processing batch predictions..."):
                    response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files)
                    
                    if response.status_code == 200:
                        preds_dict = response.json()
                        preds_series = pd.Series(preds_dict).sort_index(key=lambda x: x.astype(int))
                        
                        # Add predictions as a column to the preview dataframe
                        preview_df['Predicted_Sales_Total'] = preds_series.values
                        
                        st.success("🎉 Batch predictions successfully generated!")
                        st.dataframe(preview_df)
                        
                        # Option to download the prediction CSV
                        csv = preview_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Prediction Output CSV",
                            data=csv,
                            file_name="SuperKart_Sales_Predictions.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(f"Batch API Error: {response.json().get('error', 'Unknown Error')}")
        except Exception as e:
            st.error(f"Error processing batch file: {str(e)}")
