import streamlit as st
import pandas as pd
import random
import plotly.express as px

# 1. Page Config & Minimalist Easter Egg (Req 1: 仅保留金色小字)
st.set_page_config(page_title="Konecranes OTD Optimizer", layout="wide")
st.markdown("<div style='text-align: center; color: #FFD700; font-size: 12px; font-family: monospace; letter-spacing: 2px;'>WAKANDA FOREVER</div>", unsafe_allow_html=True)

st.title("🏗️ Konecranes Supplier Risk & OTD Simulator")
st.write("Evaluating external supply chain risks utilizing Incoterms and Tiered Penalty actions.")

# 2. Setup Suppliers with varied profiles (Req 5)
supplier_profiles = [
    {"Name": "Nordic Steel Works", "Commodity": "Steel Structures", "Incoterm": "FCA", "Delay_Prob": 0.15, "Base_Fine": 600},
    {"Name": "Siemens Drives", "Commodity": "Heavy Motors", "Incoterm": "DAP", "Delay_Prob": 0.20, "Base_Fine": 800},
    {"Name": "Taiwan Semi", "Commodity": "Microchips", "Incoterm": "FCA", "Delay_Prob": 0.35, "Base_Fine": 400},
    {"Name": "Global Hydraulics", "Commodity": "Hydraulic Pumps", "Incoterm": "DDP", "Delay_Prob": 0.25, "Base_Fine": 500}
]

# 3. Base Scenarios (Req 2: Removed Internal Delays)
root_causes = [
    {"cause": "Production Capacity Issue", "type": "Supplier"},
    {"cause": "Quality QA/QC Failure", "type": "Supplier"},
    {"cause": "Raw Material Shortage (Tier 2)", "type": "Supplier"},
    {"cause": "Port Congestion / Vessel Delay", "type": "Logistics"},
    {"cause": "Customs Clearance Hold", "type": "Logistics"},
    {"cause": "Extreme Weather / Typhoon", "type": "Force Majeure"}
]

st.sidebar.header("⚙️ Simulation Params")
num_orders = st.sidebar.slider("Total Shipments", 100, 1000, 400)
run_btn = st.sidebar.button("🚀 Run Advanced Simulation")

if run_btn:
    data = []
    for i in range(num_orders):
        # Pick a random supplier
        sup = random.choice(supplier_profiles)
        
        # Check if delayed based on supplier's specific probability
        if random.random() < sup['Delay_Prob']:
            days_late = random.randint(1, 21)
            issue = random.choice(root_causes)
            
            # --- Req 4: Incoterm Logic ---
            accountable = issue['type']
            # If it's a Logistics delay, but Incoterm is DAP/DDP, Supplier is liable!
            if issue['type'] == 'Logistics' and sup['Incoterm'] in ['DAP', 'DDP']:
                accountable = 'Supplier (Transit Liability)'
            
            # --- Req 3: Tiered Penalty Logic ---
            penalty = 0
            action_tier = ""
            
            if accountable == 'Force Majeure':
                action_tier = "Exempt (Act of God)"
                penalty = 0
            elif accountable == 'Logistics' and sup['Incoterm'] == 'FCA':
                action_tier = "Konecranes Freight Forwarder Claim"
                penalty = days_late * 200 # Fixed freight penalty
            else:
                # It is a Supplier fault (either production or DAP transit)
                if days_late <= 3:
                    action_tier = "Tier 1: Warning & 8D Report"
                    penalty = 0
                elif days_late <= 14:
                    action_tier = "Tier 2: Financial Penalty"
                    penalty = days_late * sup['Base_Fine']
                else:
                    action_tier = "Tier 3: Termination Review"
                    penalty = days_late * sup['Base_Fine'] * 1.5 # Punitive multiplier
            
            data.append({
                "Order ID": f"KC-PO-{8000 + i}",
                "Supplier": sup['Name'],
                "Commodity": sup['Commodity'],
                "Incoterm": sup['Incoterm'],
                "Root Cause": issue['cause'],
                "Delay Days": days_late,
                "Final Accountability": accountable,
                "Enforcement Action": action_tier,
                "Penalty ($)": penalty
            })
            
    df = pd.DataFrame(data)

    # 4. Dashboard Visuals
    st.header("📊 External Risk & Enforcement Report")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Delayed Orders", len(df))
    col2.metric("Tier 3 Critical Breaches", len(df[df['Enforcement Action'] == 'Tier 3: Termination Review']))
    col3.metric("Total Recoverable Penalties ($)", f"${df['Penalty ($)'].sum():,.0f}")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Delays by Supplier Profile")
        fig_bar = px.histogram(df, x="Supplier", color="Enforcement Action", barmode="stack",
                               color_discrete_map={
                                   "Tier 1: Warning & 8D Report": "#FEE12B", 
                                   "Tier 2: Financial Penalty": "#FF7F50", 
                                   "Tier 3: Termination Review": "#DC143C",
                                   "Konecranes Freight Forwarder Claim": "#4169E1",
                                   "Exempt (Act of God)": "#A9A9A9"
                               })
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Accountability Impacted by Incoterms")
        fig_pie = px.pie(df, names='Final Accountability', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Enforcement Audit Log")
    st.dataframe(df, use_container_width=True)
else:
    st.info("👈 Set the number of shipments and click 'Run Advanced Simulation'.")
