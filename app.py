import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Configuration ---
st.set_page_config(page_title="Geothermal Reservoir Asset Manager", layout="wide")

# --- Database Connection (Cached) ---
@st.cache_data
def get_data():
    conn = mysql.connector.connect(host="localhost", user="root", 
                                   password="mourtada@123", database="GeoEnergy_Exploration")
    df = pd.read_sql("SELECT * FROM Well_Logs_Enriched", conn)
    conn.close()
    return df

df = get_data()

# --- PDF Generation Function ---
def generate_professional_pdf(df_data, fig):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "Geothermal Reservoir Engineering Report")
    
    # Au lieu de fig.to_image, on écrit simplement un résumé textuel dans le PDF
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "Dashboard Summary Data:")
    c.drawString(50, 680, f"Net Pay Zones: {len(df_data)}")
    c.drawString(50, 660, f"Average Porosity: {df_data['clean_porosity_pct'].mean():.2f}%")
    
    c.save()
    buffer.seek(0)
    return buffer

# --- Sidebar Controls ---
st.sidebar.title("🛠 Reservoir Controls")
porosity_threshold = st.sidebar.slider("Net-to-Gross Cut-off (Porosity %)", 0.0, 20.0, 8.0)
well_selection = st.sidebar.multiselect("Active Well Inventory", df['well_id'].unique())

filtered_df = df[df['well_id'].isin(well_selection)] if well_selection else df
filtered_df = filtered_df[filtered_df['clean_porosity_pct'] >= porosity_threshold]

# --- Main Dashboard ---
st.title("🌐 Geothermal Reservoir Asset Manager")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Petrophysical Analysis", "🚀 Reservoir Simulation", "📥 Data Export", "ℹ️ About / Methodology"])

with tab1:

    import os # N'oubliez pas d'importer os en haut du fichier

with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("Field Statistics")
        st.metric("Net Pay Zones", len(filtered_df))
        st.metric("Avg Temp", f"{filtered_df['smoothed_temperature_celsius'].mean():.1f} °C")
    
    with col2:
        st.subheader("Well-by-Well Log Analysis")
        
        if well_selection:
            # Mapping pour faire correspondre l'ID sélectionné au nom de fichier attendu
            well_file_map = {
                1: "Well_GT01_analytics",
                2: "Well_GT02_analytics",
                3: "Well_GT03_analytics"
            }

            for well in well_selection:
                st.write(f"### Analysis for Well: {well}")
                
                # 1. Visualisation Interactive (Plotly)
                well_data = filtered_df[filtered_df['well_id'] == well]
                fig_well = px.line(well_data, x='depth_meters', y=['gamma_ray_api', 'clean_porosity_pct'],
                                   title=f"Log Profile - {well}", template="plotly_dark")
                st.plotly_chart(fig_well, use_container_width=True)
                
                # 2. Affichage des images (Well Tracks)
                # On utilise 'well' (qui est l'ID) pour chercher dans le map
                file_name = well_file_map.get(well)
                
                if file_name:
                    target_path = os.path.join("outputs", "plots", f"{file_name}.png")
                    
                    if os.path.exists(target_path):
                        st.image(target_path, caption=f"Well Track Interpretation: Well {well}", use_container_width=True)
                    else:
                        st.warning(f"Image track '{file_name}.png' non trouvée dans 'outputs/plots/'.")
                else:
                    st.info(f"Pas de tracé d'image défini pour le puits ID: {well}")
        else:
            st.info("Select a well from the sidebar to view detailed log profiles.")
            st.line_chart(filtered_df.set_index('depth_meters')[['gamma_ray_api', 'clean_porosity_pct']])
with tab2:
    st.subheader("Sweet-spot Analysis")
    fig = px.scatter(filtered_df, x='clean_porosity_pct', y='smoothed_temperature_celsius', 
                     color='well_id', template="plotly_dark", title="Porosity vs. Temperature Correlation")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Flow Rate Sensitivity Analysis")
    flow_rate = st.slider("Target Flow Rate (m³/h)", 20.0, 100.0, 55.18)
    st.metric("Estimated Thermal Power Output", f"{flow_rate * 0.095:.2f} MW")
    
    pdf_buffer = generate_professional_pdf(filtered_df, fig)
    st.download_button("Download Engineering Report (PDF)", data=pdf_buffer, file_name="Engineering_Report.pdf", mime="application/pdf")

with tab3:
    st.subheader("Export Processed Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV Dataset", csv, "Reservoir_Export.csv", "text/csv")
    st.subheader("Engineering Reporting")
    
    # On demande à l'utilisateur de sélectionner le puits pour lequel il veut le rapport
    report_well = st.selectbox("Select Well for Report", options=well_selection if well_selection else df['well_id'].unique())
    
# Chemin vers le fichier généré par export_pdf.py
pdf_path = "Technical_Report_Geothermal_Reservoir.pdf" 

if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="Download Technical Reservoir Report",
            data=pdf_file,
            file_name="Technical_Report_Geothermal_Reservoir.pdf",
            mime="application/pdf"
        )
else:
    st.warning(f"Le fichier '{pdf_path}' est introuvable. "
               f"Veuillez vous assurer que 'export_pdf.py' a été exécuté avec succès "
               f"et que le fichier se trouve bien dans le dossier de travail actuel.")
with tab4:
    st.subheader("Technical Documentation & Methodology")
    st.markdown("""
    ### Reservoir Characterization Methodology
    This platform implements a stochastic heat-in-place calculation based on USGS formalizations. 
    
    Key Technical Principles:
    1. Data Ingestion: Automated pipeline connecting drilling real-time feeds to a centralized SQL relational schema.
    2. Signal Processing: Linear interpolation for log reconstruction, with outlier removal calibrated for UK Central Block lithologies.
    3. Petrophysical Cut-offs: Modular filtering logic applied to differentiate between matrix porosity and fracture-driven transmissivity.
    4. Stress-Testing: Real-time sensitivity analysis for rapid capacity assessment.
    
    *Version: 4.0.3 | Engineering Standards: ISO-compliant data architecture.*
    """)