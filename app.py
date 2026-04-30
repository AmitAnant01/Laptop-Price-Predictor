import streamlit as st
import numpy as np
import pandas as pd
import pickle

# ── Page config ─────────────────────────────────────────
st.set_page_config(page_title="Laptop Price Predictor", layout="centered")

st.title("Laptop Price Predictor")
st.markdown("Enter laptop specs to estimate price")

# ── Load model ─────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    model = pickle.load(open("laptop_model.pkl", "rb"))
    columns = pickle.load(open("feature_columns.pkl", "rb"))
    return model, columns

model, feature_columns = load_artifacts()

# ── Inputs ─────────────────────────────────────────
st.subheader("Enter Specifications")

col1, col2 = st.columns(2)

with col1:
    company = st.selectbox("Brand", ["Dell","HP","Lenovo","Asus","Acer","MSI","Apple"])
    type_name = st.selectbox("Type", ["Notebook","Gaming","Ultrabook","Workstation"])
    ram = st.selectbox("RAM (GB)", [4,8,16,32,64])
    weight = st.number_input("Weight (kg)", 0.5, 5.0, 2.0)

with col2:
    cpu = st.selectbox("CPU", ["Intel i3","Intel i5","Intel i7","AMD Ryzen 5","AMD Ryzen 7"])
    gpu = st.selectbox("GPU", ["Intel","Nvidia","AMD"])
    storage = st.selectbox("Storage", ["256 SSD","512 SSD","1TB HDD","1TB SSD"])
    os = st.selectbox("OS", ["Windows","Mac","Linux"])

col3, col4 = st.columns(2)

with col3:
    inches = st.selectbox("Screen Size", [13.3,14,15.6,17.3])
    ips = st.radio("IPS", ["Yes","No"])

with col4:
    touchscreen = st.radio("Touchscreen", ["Yes","No"])
    resolution = st.selectbox("Resolution", ["1366x768","1920x1080","2560x1600"])

# ── Feature Engineering ─────────────────────────────────

# Resolution split
x_res = int(resolution.split("x")[0])
y_res = int(resolution.split("x")[1])

ppi = ((x_res**2 + y_res**2)**0.5) / inches

# CPU brand extraction
if "Intel" in cpu:
    cpu_brand = "Intel"
else:
    cpu_brand = "AMD"

# Storage split
if "SSD" in storage:
    memory_type = "SSD"
else:
    memory_type = "HDD"

memory_gb = int(storage.split()[0].replace("TB","000"))

# ── Build Input ─────────────────────────────────
def build_input():
    data = {
        "Inches": inches,
        "Ram": ram,
        "Weight": weight,
        "Cpu_Speed": 2.5,  # default (or improve if in dataset)
        "X_res": x_res,
        "Y_res": y_res,
        "PPI": ppi,
        "IPS": 1 if ips=="Yes" else 0,
        "Touchscreen": 1 if touchscreen=="Yes" else 0,
        "Memory_GB": memory_gb
    }

    # categorical mapping
    categories = {
        "Company": company,
        "TypeName": type_name,
        "Cpu_Brand": cpu_brand,
        "Gpu_Brand": gpu,
        "Memory_Type": memory_type,
        "OS": os
    }

    for key, value in categories.items():
        col_name = f"{key}_{value}"
        if col_name in feature_columns:
            data[col_name] = 1

    df = pd.DataFrame([data])

    # align columns
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    return df[feature_columns]

# ── Prediction ─────────────────────────────────
st.markdown("---")

if st.button("Predict Price"):
    input_df = build_input()
    log_price = model.predict(input_df)[0]
    price = int(np.exp(log_price))

    st.success(f"Estimated Price: ₹{price:,}")

    # Smart category
    if price < 40000:
        st.info("Budget Laptop")
    elif price < 80000:
        st.info("Mid-range Laptop")
    else:
        st.info("High-end Laptop")

    st.caption("Prediction may vary based on market trends.")

    st.markdown("### Specification Summary")

summary = {
    "Brand": company,
    "Type": type_name,
    "RAM": f"{ram} GB",
    "Storage": f"{memory_gb} GB ({memory_type})",
    "CPU": cpu,
    "GPU": gpu,
    "Screen": f"{inches} inch | IPS: {ips} | Touch: {touchscreen}",
    "OS": os,
    "Weight": f"{weight} kg",
}

st.success("Prediction based on the following configuration:")

st.table(pd.DataFrame(summary.items(), columns=["Specification", "Value"]))
