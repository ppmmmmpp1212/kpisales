import streamlit as st
import pandas as pd
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
    # Safely convert to numeric for calculation, keeping original data intact
    actual_num = pd.to_numeric(actual, errors='coerce')
    target_num = pd.to_numeric(target, errors='coerce')
    percent = (actual_num / target_num * 100 if target_num and pd.notnull(target_num) and target_num != 0 else 0)
    color = "#10B981" if percent >= 100 else "#3B82F6"
    return f"""
    <div style='margin-bottom: 0.5em;'>
        <div style='font-size: 1.1em; font-weight: bold; color: #1E3A8A;'>{title}</div>
        <div style='font-size: 0.95em; color: #374151;'>
            <span style='font-weight: 600; color: {color};'>{actual if pd.notnull(actual) else 0}</span> dari <b>{target if pd.notnull(target) else 0}</b> {unit} 
            <span style='float: right; color: {color};'>({percent:.2f}%)</span>
        </div>
    </div>
    """

# Function to create custom progress bar
def custom_progress_bar(label, actual, target, emoji="🚶"):
    # Safely convert to numeric for calculation
    actual_num = pd.to_numeric(actual, errors='coerce')
    target_num = pd.to_numeric(target, errors='coerce')
    percent = min(actual_num / target_num * 100 if target_num and pd.notnull(target_num) and target_num != 0 else 0, 100)
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
    sheet_name = "KPI"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url, parse_dates=["tanggal"])
        # Select only the required columns without manipulation
        required_columns = [
            'tanggal', 'Cluster', 'nama_sales', 'absensi', 'target_absen', '%absen',
            'target_sa', 'aktual_sa', '%SA', 'target_fv', 'aktual_fv', '%VF',
            'total_outlet_bulan', 'jumlah_kunjungan_outlet', '%kunjungan',
            'Target_outletbaru', 'total_outlet_baru', '%outletbaru',
            'skor_total', 'target_skor', 'reward'
        ]
        available_columns = [col for col in required_columns if col in df.columns]
        df = df[available_columns]
        # Display raw data for verification
        st.write("Raw Data Sample:", df.head())
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
    
    # Page selection with only Individual Dashboard
    page = "Individual Dashboard"
    
    cluster_options = ['All Clusters'] + sorted(df['Cluster'].unique().tolist() if not df.empty else [])
    selected_cluster = st.selectbox("Filter by Cluster", cluster_options)
    
    # Filter sales names based on selected cluster
    if selected_cluster != 'All Clusters':
        filtered_df = df[df['Cluster'] == selected_cluster]
    else:
        filtered_df = df
    sales_options = sorted(filtered_df['nama_sales'].unique().tolist() if not filtered_df.empty else [])
    selected_sales = st.selectbox("Select Sales Person", sales_options if sales_options else ["No data available"])
    
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
            
            # Data Processing (using raw values)
            absensi = row['absensi']
            absen_target = row['target_absen']
            target_sa = row['target_sa'] if pd.notnull(row['target_sa']) and row['target_sa'] != 0 else 1
            aktual_sa = row['aktual_sa']
            target_fv = row['target_fv'] if pd.notnull(row['target_fv']) and row['target_fv'] != 0 else 1
            aktual_fv = row['aktual_fv']
            total_outlet = row['total_outlet_bulan'] if pd.notnull(row['total_outlet_bulan']) and row['total_outlet_bulan'] != 0 else 1
            jumlah_kunjungan = row['jumlah_kunjungan_outlet']
            target_outlet_baru = row['Target_outletbaru'] if pd.notnull(row['Target_outletbaru']) and row['Target_outletbaru'] != 0 else 1
            outlet_baru = row['total_outlet_baru']
            skor_total = row['skor_total']
            target_skor = row['target_skor'] if pd.notnull(row['target_skor']) and row['target_skor'] != 0 else 1
            reward = row['reward']
            
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>🎯 Pencapaian Parameter</h3>", unsafe_allow_html=True)
            st.markdown("")
            st.markdown("")
            
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(styled_progress_info("Absensi", absensi, target_absen, "hari"), unsafe_allow_html=True)
                st.progress(min(pd.to_numeric(absensi, errors='coerce') / pd.to_numeric(target_absen, errors='coerce') if pd.to_numeric(target_absen, errors='coerce') and pd.notnull(pd.to_numeric(target_absen, errors='coerce')) and pd.to_numeric(target_absen, errors='coerce') != 0 else 0, 1.0) if pd.notnull(pd.to_numeric(absensi, errors='coerce')) and pd.notnull(pd.to_numeric(target_absen, errors='coerce')) else 0)
                st.markdown(styled_progress_info("SA Achievement", aktual_sa, target_sa, "unit"), unsafe_allow_html=True)
                st.progress(min(pd.to_numeric(aktual_sa, errors='coerce') / pd.to_numeric(target_sa, errors='coerce') if pd.to_numeric(target_sa, errors='coerce') and pd.notnull(pd.to_numeric(target_sa, errors='coerce')) and pd.to_numeric(target_sa, errors='coerce') != 0 else 0, 1.0) if pd.notnull(pd.to_numeric(aktual_sa, errors='coerce')) and pd.notnull(pd.to_numeric(target_sa, errors='coerce')) else 0)
                st.markdown(styled_progress_info("FV Achievement", aktual_fv, target_fv, "unit"), unsafe_allow_html=True)
                st.progress(min(pd.to_numeric(aktual_fv, errors='coerce') / pd.to_numeric(target_fv, errors='coerce') if pd.to_numeric(target_fv, errors='coerce') and pd.notnull(pd.to_numeric(target_fv, errors='coerce')) and pd.to_numeric(target_fv, errors='coerce') != 0 else 0, 1.0) if pd.notnull(pd.to_numeric(aktual_fv, errors='coerce')) and pd.notnull(pd.to_numeric(target_fv, errors='coerce')) else 0)
            
            with col2:
                st.markdown(styled_progress_info("Kunjungan Outlet", jumlah_kunjungan_outlet, total_outlet, "outlet"), unsafe_allow_html=True)
                st.progress(min(pd.to_numeric(jumlah_kunjungan_outlet, errors='coerce') / pd.to_numeric(total_outlet, errors='coerce') if pd.to_numeric(total_outlet, errors='coerce') and pd.notnull(pd.to_numeric(total_outlet, errors='coerce')) and pd.to_numeric(total_outlet, errors='coerce') != 0 else 0, 1.0) if pd.notnull(pd.to_numeric(jumlah_kunjungan_outlet, errors='coerce')) and pd.notnull(pd.to_numeric(total_outlet, errors='coerce')) else 0)
                st.markdown(styled_progress_info("Outlet Baru", total_outlet_baru, Target_outletbaru, "outlet"), unsafe_allow_html=True)
                st.progress(min(pd.to_numeric(total_outlet_baru, errors='coerce') / pd.to_numeric(Target_outletbaru, errors='coerce') if pd.to_numeric(Target_outletbaru, errors='coerce') and pd.notnull(pd.to_numeric(Target_outletbaru, errors='coerce')) and pd.to_numeric(Target_outletbaru, errors='coerce') != 0 else 0, 1.0) if pd.notnull(pd.to_numeric(total_outlet_baru, errors='coerce')) and pd.notnull(pd.to_numeric(Target_outletbaru, errors='coerce')) else 0)
            
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>🎯 Skor Total & Reward</h3>", unsafe_allow_html=True)
            st.write(f"Skor: **{skor_total if pd.notnull(skor_total) else 0}** dari target **{target_skor if pd.notnull(target_skor) else 0}**")
            st.markdown(custom_progress_bar("Total Skor", skor_total, target_skor, emoji="🚶"), unsafe_allow_html=True)
            st.write(f"Reward: **Rp {reward if pd.notnull(reward) else 0:,.0f}**".replace(",", "."))
            # Safely format date without assuming datetime object
            tanggal_str = str(row['tanggal']) if pd.notnull(row['tanggal']) else '-'
            try:
                tanggal_dt = pd.to_datetime(tanggal_str)
                tanggal_formatted = tanggal_dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                tanggal_formatted = tanggal_str
            st.markdown(f"📅 Data Tanggal: **{tanggal_formatted}**")
    else:
        st.warning("No data available for the selected filters.")
