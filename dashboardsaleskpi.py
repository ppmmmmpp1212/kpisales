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

# Custom CSS (unchanged)
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

# Function to create sales scorecard
def sales_scorecard(name, cluster, kode_sf, kode_sap, gmail):
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
            <div style='font-size: 0.95em; color: #6B7280;'>🔢 Kode SF: <b>{kode_sf}</b></div>
            <div style='font-size: 0.95em; color: #6B7280;'>🔢 Kode SAP: <b>{kode_sap}</b></div>
            <div style='font-size: 0.95em; color: #6B7280;'>📧 Gmail: <b>{gmail}</b></div>
        </div>
    </div>
    """

# Function to create styled progress info
def styled_progress_info(title, actual, target, unit="hari"):
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
    actual_num = pd.to_numeric(actual, errors='coerce')
    target_num = pd.to_numeric(target, errors='coerce')
    percent = min(actual_num / target_num if target_num and pd.notnull(target_num) and target_num != 0 else 0, 1.0)
    return st.progress(percent)

# Load Data from Google Sheets
@st.cache_data
def load_data_from_gsheet():
    sheet_id = "1f9faUw7p9nhh3flE_EogTLi-64AMvzPMLHKNBcsr19o"
    sheet_name = "KPI"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url, parse_dates=["tanggal"])
        required_columns = [
            'tanggal', 'Cluster', 'nama_sales', 'kode_sf', 'kode_sap', 'gmail',
            'absensi', 'target_absen', '%absen',
            'target_sa', 'aktual_sa', '%SA', 'target_fv', 'aktual_fv', '%VF',
            'total_outlet_bulan', 'jumlah_kunjungan_outlet', '%kunjungan',
            'Target_outletbaru', 'total_outlet_baru', '%outletbaru',
            'skor_total', 'target_skor', 'reward'
        ]
        available_columns = [col for col in required_columns if col in df.columns]
        if len(available_columns) < len(required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            st.warning(f"Missing columns in data: {missing}")
        df = df[available_columns]
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data_from_gsheet()

# Sidebar
with st.sidebar:
    st.image("mmpp.png", caption="Sales Dashboard Logo")
    st.title("📈 Sales Performance")
    st.markdown("---")
    
    page = "Individual Dashboard"
    
    # Date filter for selecting month and year
    if not df.empty and 'tanggal' in df.columns:
        # Extract unique months and years from 'tanggal' column
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        df['month_year'] = df['tanggal'].dt.strftime('%Y-%m')
        unique_months = sorted(df['month_year'].dropna().unique(), reverse=True)
        
        # Map months to Indonesian names
        month_map = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }
        period_options = [
            f"{month_map[month.split('-')[1]]} {month.split('-')[0]}" 
            for month in unique_months
        ]
        
        # Set default to current month and year
        current_month_year = datetime.now().strftime('%Y-%m')
        current_month = month_map[current_month_year.split('-')[1]]
        default_period = f"{current_month} {current_month_year.split('-')[0]}"
        
        # Ensure default period is in period_options, else select the most recent
        default_index = period_options.index(default_period) if default_period in period_options else 0
        selected_period = st.selectbox("Select Period", period_options, index=default_index)
        
        # Filter data by selected period
        selected_month, selected_year = selected_period.split()
        selected_month_num = list(month_map.keys())[list(month_map.values()).index(selected_month)]
        selected_month_year = f"{selected_year}-{selected_month_num}"
        filtered_df = df[df['month_year'] == selected_month_year]
    else:
        st.warning("No valid date data available for filtering.")
        filtered_df = df
        selected_period = f"Juli {datetime.now().year}"
    
    # Gmail search input
    search_gmail = st.text_input("Search by Gmail", placeholder="Enter Gmail address...")
    
    st.markdown("---")
    st.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main Content
if page == "Individual Dashboard":
    # Main Dashboard Title
    st.markdown('<div class="main-title">Sales Performance Dashboard</div>', unsafe_allow_html=True)
    
    # Filter data by Gmail if provided
    if search_gmail:
        filtered_df = filtered_df[filtered_df['gmail'].str.lower() == search_gmail.lower()]
        
        if not filtered_df.empty:
            row = filtered_df.iloc[0]
            with st.container():
                # Pass additional fields to sales_scorecard
                kode_sf = row['kode_sf'] if 'kode_sf' in row and pd.notnull(row['kode_sf']) else '-'
                kode_sap = row['kode_sap'] if 'kode_sap' in row and pd.notnull(row['kode_sap']) else '-'
                gmail = row['gmail'] if 'gmail' in row and pd.notnull(row['gmail']) else '-'
                st.markdown(sales_scorecard(row['nama_sales'], row['Cluster'], row['kode_sf'], row['kode_sap'], row['gmail']), unsafe_allow_html=True)
                
                # Assign variables with proper column checks
                absensi = row['absensi'] if 'absensi' in row else 0
                absen_target = row['target_absen'] if 'target_absen' in row else 1
                target_sa = row['target_sa'] if 'target_sa' in row and pd.notnull(row['target_sa']) and row['target_sa'] != 0 else 1
                aktual_sa = row['aktual_sa'] if 'aktual_sa' in row else 0
                target_fv = row['target_fv'] if 'target_fv' in row and pd.notnull(row['target_fv']) and row['target_fv'] != 0 else 1
                aktual_fv = row['aktual_fv'] if 'aktual_fv' in row else 0
                total_outlet_bulan = row['total_outlet_bulan'] if 'total_outlet_bulan' in row and pd.notnull(row['total_outlet_bulan']) and row['total_outlet_bulan'] != 0 else 1
                jumlah_kunjungan_outlet = row['jumlah_kunjungan_outlet'] if 'jumlah_kunjungan_outlet' in row else 0
                Target_outletbaru = row['Target_outletbaru'] if 'Target_outletbaru' in row and pd.notnull(row['Target_outletbaru']) and row['Target_outletbaru'] != 0 else 1
                total_outlet_baru = row['total_outlet_baru'] if 'total_outlet_baru' in row else 0
                skor_total = row['skor_total'] if 'skor_total' in row else 0
                target_skor = row['target_skor'] if 'target_skor' in row and pd.notnull(row['target_skor']) and row['target_skor'] != 0 else 1
                reward = row['reward'] if 'reward' in row else 0
                
                st.markdown("---")
                st.markdown("<h3 style='text-align: center;'>🎯 Pencapaian Parameter</h3>", unsafe_allow_html=True)
                st.markdown("")
                st.markdown("")
                
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(styled_progress_info("Absensi", absensi, absen_target, "hari"), unsafe_allow_html=True)
                    custom_progress_bar("Absensi", absensi, absen_target)
                    st.markdown(styled_progress_info("SA Achievement", aktual_sa, target_sa, "unit"), unsafe_allow_html=True)
                    custom_progress_bar("SA Achievement", aktual_sa, target_sa)
                    st.markdown(styled_progress_info("VF Achievement", aktual_fv, target_fv, "unit"), unsafe_allow_html=True)
                    custom_progress_bar("VF Achievement", aktual_fv, target_fv)
                
                with col2:
                    st.markdown(styled_progress_info("Kunjungan Outlet", jumlah_kunjungan_outlet, total_outlet_bulan, "outlet"), unsafe_allow_html=True)
                    custom_progress_bar("Kunjungan Outlet", jumlah_kunjungan_outlet, total_outlet_bulan)
                    st.markdown(styled_progress_info("Outlet Baru", total_outlet_baru, Target_outletbaru, "outlet"), unsafe_allow_html=True)
                    custom_progress_bar("Outlet Baru", total_outlet_baru, Target_outletbaru)
                            
                st.markdown("---")
                st.markdown("<h3 style='text-align: center;'>🎯 Skor Total & Reward</h3>", unsafe_allow_html=True)
                
                # Calculate percentage for progress bar
                skor_num = pd.to_numeric(skor_total, errors='coerce')
                target_skor_num = pd.to_numeric(target_skor, errors='coerce')
                percent = (skor_num / target_skor_num * 100 if target_skor_num and pd.notnull(target_skor_num) and target_skor_num != 0 else 0)
                percent_display = min(percent, 100)  # For display purposes (in %)
                percent_progress = min(percent / 100, 1.0)  # For st.progress (0.0 to 1.0)
                
                # Display styled progress info
                st.markdown(styled_progress_info("Skor Total", skor_total, target_skor, "poin"), unsafe_allow_html=True)
                
                # Display reward and date
                st.write(f"Reward: **Rp {reward if pd.notnull(reward) else 0:,.0f}**".replace(",", "."))
                tanggal_str = str(row['tanggal']) if pd.notnull(row['tanggal']) else '-'
                try:
                    tanggal_dt = pd.to_datetime(tanggal_str)
                    tanggal_formatted = tanggal_dt.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    tanggal_formatted = tanggal_str
                st.markdown(f"📅 Periode Akhir Tanggal: **{tanggal_formatted}**")
        else:
            st.warning("No sales person found with the provided Gmail for the selected period.")
    else:
        st.info("Masukkan gmail anda yang terdaftar di aplikasi TALENTA untuk melihat progress anda.")
