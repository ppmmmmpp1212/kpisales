import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for card styling and table
st.markdown("""
    <style>
    .card-container {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5em;
        margin-bottom: 1.5em;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .card-container:hover {
        box-shadow: 0 7px 14px rgba(0,0,0,0.1), 0 3px 6px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    .card-title {
        font-size: 1.8em;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1em;
    }
    .metric-label {
        font-size: 0.9em;
        color: #6B7280;
        margin-bottom: 0.3em;
    }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1em;
        margin-bottom: 1em;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 7px 14px rgba(0,0,0,0.1), 0 3px 6px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1em;
    }
    .stDataFrame {
        width: 100%;
        font-size: 0.95em;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }
    .stDataFrame th, .stDataFrame td {
        padding: 0.8em;
        text-align: left;
        border-bottom: 1px solid #E5E7EB;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stDataFrame th {
        background-color: #F9FAFB;
        font-weight: bold;
        color: #1E3A8A;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .stDataFrame tr:hover {
        background-color: #F3F4F6;
    }
    .stDataFrame tr:nth-child(1) {
        background-color: #FEF3C7;
    }
    .stDataFrame tr:nth-child(2) {
        background-color: #E4E7EB;
    }
    .stDataFrame tr:nth-child(3) {
        background-color: #FFEDD5;
    }
    </style>
""", unsafe_allow_html=True)

# Function to create a metric card
def metric_card(label, value, trend):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div style="font-size: 1.5em; font-weight: bold; color: #1E3A8A;">{value}</div>
        <div style="font-size: 0.9em; color: #6B7280;">{trend}</div>
    </div>
    """

def sales_scorecard(name, cluster):
    return f"""
    <div style='
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.2em 1.5em;
        margin-bottom: 1em;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
    '>
        <div style='flex-grow: 1;'>
            <div style='font-size: 1.3em; font-weight: 700; color: #1E3A8A;'>👤 {name}</div>
            <div style='font-size: 0.95em; color: #6B7280;'>📍 Cluster: <b>{cluster}</b></div>
        </div>
    </div>
    """

# Function to create styled progress info
def styled_progress_info(title, actual, target, unit="hari"):
    percent = actual / target * 100 if target != 0 else 0
    color = "#10B981" if percent >= 100 else "#3B82F6"
    return f"""
    <div style='margin-bottom: 0.5em;'>
        <div style='font-size: 1.1em; font-weight: bold; color: #1E3A8A;'>{title}</div>
        <div style='font-size: 0.95em; color: #374151;'>
            <span style='font-weight: 600; color: {color};'>{actual:.1f}</span> dari <b>{target:.0f}</b> {unit} 
            <span style='float: right; color: {color};'>({percent:.2f}%)</span>
        </div>
    </div>
    """

# Function to create custom progress bar
def custom_progress_bar(label, actual, target, emoji="🚶"):
    percent = min(actual / target * 100 if target != 0 else 0, 100)
    color = "#3B82F6"
    return f"""
    <div style="margin-bottom: 1em;">
        <div style="display: flex; align-items: center; margin-bottom: 0.3em;">
            <span style="font-size: 1.1em; margin-right: 0.4em;">{emoji}</span>
            <span style="font-size: 1em; font-weight: 600; color: #1E3A8A;">{label} ({percent:.2f}%)</span>
        </div>
        <div style="background-color: #E5E7EB; border-radius: 10px; height: 18px; width: 100%;">
            <div style="height: 100%; width: {percent}%; background-color: {color}; border-radius: 10px;"></div>
        </div>
    </div>
    """

# Load Data from Google Sheets
@st.cache_data
def load_data_from_gsheet():
    sheet_id = "1f9faUw7p9nhh3flE_EogTLi-64AMvzPMLHKNBcsr19o"
    sheet_name = "Sheet7"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url, parse_dates=["tanggal"])
        numeric_columns = ['Cluster','absensi', 'target_sa', 'aktual_sa', 'target_fv', 'aktual_fv', 
                           'total_outlet_bulan', 'jumlah_kunjungan_outlet', 'Target_outletbaru', 
                           'total_outlet_baru', 'skor_total', 'target_skor', 'reward', 
                           '%absen', '%SA', '%VF', '%kunjungan', '%outletbaru']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data_from_gsheet()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="Sales Dashboard Logo")
    st.title("📈 Sales Performance")
    st.markdown("---")
    
    # Page selection with Leaderboard as default
    page = st.selectbox("Select Page", ["Individual Dashboard", "Leaderboard"], index=1)
    
    if page == "Individual Dashboard":
        cluster_options = ['All Clusters'] + sorted(df['Cluster'].unique().tolist() if not df.empty else [])
        selected_cluster = st.selectbox("Filter by Cluster", cluster_options)
        
        # Filter sales names based on selected cluster
        if selected_cluster != 'All Clusters':
            filtered_df = df[df['Cluster'] == selected_cluster]
        else:
            filtered_df = df
        sales_options = sorted(filtered_df['nama_sales'].unique().tolist() if not filtered_df.empty else [])
        selected_sales = st.selectbox("Select Sales Person", sales_options if sales_options else ["No data available"])
    
    elif page == "Leaderboard":
        cluster_options = ['All Clusters'] + sorted(df['Cluster'].unique().tolist() if not df.empty else [])
        selected_cluster = st.selectbox("Filter by Cluster", cluster_options)
    
    st.markdown("---")
    st.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**Data Source:** Google Sheets")
    st.markdown("**Developed by:** Your Team Name")

# Main Content
if page == "Individual Dashboard":
    # Filter data by cluster and sales person
    if selected_cluster != 'All Clusters':
        df = df[df['Cluster'] == selected_cluster]
    df = df[df['nama_sales'] == selected_sales]
    
    # Main Dashboard
    st.markdown('<div class="main-title">Sales Performance Dashboard</div>', unsafe_allow_html=True)
    
    if not df.empty:
        row = df.iloc[0]
        with st.container():
            st.markdown(sales_scorecard(row['nama_sales'], row['Cluster']), unsafe_allow_html=True)
            
            # Data Processing
            absensi = float(row['absensi']) if pd.notnull(row['absensi']) else 0
            absen_target = 27
            target_sa = float(row['target_sa']) if pd.notnull(row['target_sa']) and float(row['target_sa']) != 0 else 1
            aktual_sa = float(row['aktual_sa']) if pd.notnull(row['aktual_sa']) else 0
            target_fv = float(row['target_fv']) if pd.notnull(row['target_fv']) and float(row['target_fv']) != 0 else 1
            aktual_fv = float(row['aktual_fv']) if pd.notnull(row['aktual_fv']) else 0
            total_outlet = float(row['total_outlet_bulan']) if pd.notnull(row['total_outlet_bulan']) and float(row['total_outlet_bulan']) != 0 else 1
            jumlah_kunjungan = float(row['jumlah_kunjungan_outlet']) if pd.notnull(row['jumlah_kunjungan_outlet']) else 0
            target_outlet_baru = float(row['Target_outletbaru']) if pd.notnull(row['Target_outletbaru']) and float(row['Target_outletbaru']) != 0 else 1
            outlet_baru = float(row['total_outlet_baru']) if pd.notnull(row['total_outlet_baru']) else 0
            skor_total = float(row['skor_total']) if pd.notnull(row['skor_total']) else 0
            target_skor = float(row['target_skor']) if pd.notnull(row['target_skor']) and float(row['target_skor']) != 0 else 1
            
            # Calculate reward based on skor_total percentage
            skor_percent = (skor_total / target_skor * 100) if target_skor != 0 else 0
            if skor_percent >= 100:
                reward = 600000
            elif 90 <= skor_percent < 100:
                reward = 400000
            elif 80 <= skor_percent < 90:
                reward = 300000
            else:
                reward = 0
            
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>🎯 Pencapaian Parameter</h3>", unsafe_allow_html=True)
            st.markdown("")
            st.markdown("")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(styled_progress_info("Absensi", absensi, absen_target, "hari"), unsafe_allow_html=True)
                st.progress(min(absensi / absen_target, 1.0))
                st.markdown(styled_progress_info("SA Achievement", aktual_sa, target_sa, "unit"), unsafe_allow_html=True)
                st.progress(min(aktual_sa / target_sa, 1.0))
                st.markdown(styled_progress_info("FV Achievement", aktual_fv, target_fv, "unit"), unsafe_allow_html=True)
                st.progress(min(aktual_fv / target_fv, 1.0))
            
            with col2:
                st.markdown(styled_progress_info("Kunjungan Outlet", jumlah_kunjungan, total_outlet, "outlet"), unsafe_allow_html=True)
                st.progress(min(jumlah_kunjungan / total_outlet, 1.0))
                st.markdown(styled_progress_info("Outlet Baru", outlet_baru, target_outlet_baru, "outlet"), unsafe_allow_html=True)
                st.progress(min(outlet_baru / target_outlet_baru, 1.0))
            
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>🎯 Skor Total & Reward</h3>", unsafe_allow_html=True)
            st.write(f"Skor: **{skor_total:.2f}** dari target **{target_skor:.0f}**")
            st.markdown(custom_progress_bar("Total Skor", skor_total, target_skor, emoji="🚶"), unsafe_allow_html=True)
            st.write(f"Reward: **Rp {reward:,.0f}**".replace(",", "."))
            st.markdown(f"📅 Data Tanggal: **{row['tanggal']:%Y-%m-%d}**")
    else:
        st.warning("No data available for the selected filters.")

elif page == "Leaderboard":
    st.markdown('<div class="main-title">Sales Leaderboard</div>', unsafe_allow_html=True)
    
    # Filter data by cluster
    if selected_cluster != 'All Clusters':
        leaderboard_df = df[df['Cluster'] == selected_cluster].copy()
    else:
        leaderboard_df = df.copy()
    
    if not leaderboard_df.empty:
        # Add rank based on skor_total
        leaderboard_df['Rank'] = leaderboard_df['skor_total'].rank(ascending=False, method='min').astype(int)
        leaderboard_df = leaderboard_df.sort_values('skor_total', ascending=False).reset_index(drop=True)
        
        # Select columns for display
        display_columns = ['Rank', 'tanggal', 'Cluster', 'nama_sales', '%absen', '%SA', '%VF', '%kunjungan', '%outletbaru', 'skor_total']
        leaderboard_df = leaderboard_df[display_columns]
        
        # Format the dataframe for display
        formatted_df = leaderboard_df.copy()
        formatted_df['tanggal'] = formatted_df['tanggal'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else '-')
        formatted_df['%absen'] = (formatted_df['%absen'] * 100).round(2).apply(lambda x: f"{x:.2f}%")
        formatted_df['%SA'] = (formatted_df['%SA'] * 100).round(2).apply(lambda x: f"{x:.2f}%")
        formatted_df['%VF'] = (formatted_df['%VF'] * 100).round(2).apply(lambda x: f"{x:.2f}%")
        formatted_df['%kunjungan'] = (formatted_df['%kunjungan'] * 100).round(2).apply(lambda x: f"{x:.2f}%")
        formatted_df['%outletbaru'] = (formatted_df['%outletbaru'] * 100).round(2).apply(lambda x: f"{x:.2f}%")
        formatted_df['skor_total'] = formatted_df['skor_total'].apply(lambda x: f"{x:.2f}")
        
        # Rename columns for better display
        formatted_df.columns = ['Rank', 'Tanggal', 'Cluster', 'Nama Sales', '% Absen', '% SA', '% VF', '% Kunjungan', '% Outlet Baru', 'Skor Total']
        
        # Display the table in a container
        with st.container():
            st.dataframe(
                formatted_df,
                use_container_width=True,
                height=600,  # Adjust height to show more rows without scrolling
                column_config={
                    'Rank': st.column_config.NumberColumn(width="small"),
                    'Tanggal': st.column_config.TextColumn(width="medium"),
                    'Cluster': st.column_config.TextColumn(width="medium"),
                    'Nama Sales': st.column_config.TextColumn(width="medium"),
                    '% Absen': st.column_config.TextColumn(width="small"),
                    '% SA': st.column_config.TextColumn(width="small"),
                    '% VF': st.column_config.TextColumn(width="small"),
                    '% Kunjungan': st.column_config.TextColumn(width="small"),
                    '% Outlet Baru': st.column_config.TextColumn(width="small"),
                    'Skor Total': st.column_config.TextColumn(width="small")
                }
            )
    else:
        st.warning("No data available for the selected cluster.")
