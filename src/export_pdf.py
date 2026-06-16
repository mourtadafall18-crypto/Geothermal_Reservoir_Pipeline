import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line

# =========================================================================
# IMAGE SEARCH FUNCTION (MAINTAINED PIPELINE PATHS)
# =========================================================================
def find_image_file(pattern, default_filenames):
    """Searches for images in the pipeline output directories."""
    target_folders = [
        os.path.join("outputs", "plots"), # For Well Tracks
        "output", # For 2D cross-section
        os.path.join("output", "plots"),
        "outputs",
        os.path.join("outpouts", "plots"), 
        os.path.join("outpout", "plots"),
        "outpouts",
        "outpout"
    ]
    
    def clean(text):
        return text.lower().replace('-', '').replace('_', '').replace(' ', '')

    clean_pattern = clean(pattern)

    # Step 1: Exact filename match search
    for folder in target_folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            for filename in default_filenames:
                full_path = os.path.join(folder, filename)
                if os.path.exists(full_path):
                    print(f"✅ [FOUND] Image detected (Exact name): {full_path}")
                    return full_path

    # Step 2: Keyword fallback search
    for folder in target_folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            try:
                for f in os.listdir(folder):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                        if clean_pattern in clean(f):
                            full_path = os.path.join(folder, f)
                            print(f"🎯 [FOUND VIA KEYWORD] '{pattern}' associated with -> {full_path}")
                            return full_path
            except Exception as e:
                print(f"⚠️ Unable to read directory {folder}: {e}")
                
    print(f"❌ [ALERT] No image containing '{pattern}' found in directories.")
    return None

# =========================================================================
# 1. CUSTOM CANVAS CLASS: DYNAMIC PAGE NUMBERING & DECORATIONS
# =========================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        if not hasattr(self, '_saved_page_states'):
            self._saved_page_states = []

    def showPage(self):
        if not hasattr(self, '_saved_page_states'):
            self._saved_page_states = []
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states) if hasattr(self, '_saved_page_states') else 0
        if num_pages > 0:
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        width, height = self._pagesize
        
        # ---------------- RUNNING HEADER ----------------
        self.setStrokeColor(colors.HexColor("#2B6CB0"))
        self.setLineWidth(1)
        self.line(36, height - 45, width - 36, height - 45)
        
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(36, height - 35, "GEOENERGY EXPLORATION LTD. | TECHNICAL EXPERTISE REPORT")
        
        # ---------------- RUNNING FOOTER ----------------
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 50, width - 36, 50)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 35, "Ref: GEO-UK-2026-REP-004 | Classification: Reservoir Confidential")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(width - 36, 35, page_str)
        
        self.restoreState()

# =========================================================================
# 2. MAIN REPORT GENERATION FUNCTION
# =========================================================================
def generate_expert_report():
    pdf_filename = "Technical_Report_Geothermal_Reservoir.pdf"
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=75,
        bottomMargin=75
    )
    
    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1A365D")   
    secondary_color = colors.HexColor("#2B6CB0") 
    text_color = colors.HexColor("#2D3748")      
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=primary_color, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=16, textColor=secondary_color, spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=primary_color, spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=secondary_color, spaceBefore=10, spaceAfter=6, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=14, textColor=text_color, spaceAfter=8, alignment=4
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom', parent=body_style, leftIndent=15, firstLineIndent=-10, spaceAfter=4
    )
    italic_style = ParagraphStyle(
        'Italic_Custom', parent=body_style, fontName='Helvetica-Oblique', textColor=colors.HexColor("#4A5568"), leftIndent=15
    )
    caption_style = ParagraphStyle(
        'Caption_Custom', parent=styles['Normal'], fontName='Helvetica-BoldOblique', fontSize=8.5, leading=12, textColor=colors.HexColor("#4A5568"), alignment=1, spaceBefore=8, spaceAfter=14
    )
    table_text = ParagraphStyle(
        'TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=text_color, alignment=1
    )
    table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=1
    )

    story = []

    # DOCUMENT HEADER
    story.append(Paragraph("TECHNICAL EXPERTISE AND RESERVOIR SYNTHESIS REPORT", title_style))
    story.append(Paragraph("<b>Integrated Evaluation of the Hydrothermal Potential of the UK Central Bloc</b>", subtitle_style))
    meta_text = (
        "<b>Compilation Date:</b> June 5, 2026 | <b>Author:</b> MOURTADA FALL<br/>"
        "<b>Status:</b> Final (V1.1) | <b>Data Sciences & Data Engineering :</b> Version 4.0.2 (Automated Core Engine)"
    )
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 5))

    # SECTION 1
    story.append(Paragraph("1. Introduction, Geodynamic Context & Project Objectives", h1_style))
    story.append(Paragraph(
        "This technical evaluation delivers a comprehensive appraisal of the deep hydrothermal potential within the "
        "'UK Central Bloc'. Aligned with the UK’s strategic decarbonization goals for urban district heating and industrial "
        "processes, this study aims to de-risk subsurface exploration by transitioning from legacy empirical "
        "extrapolations to a fully deterministic, data-driven framework. The target area presents a complex polyphase "
        "structural setting, characterized by a Permo-Triassic syn-to-post-rift sedimentary prism unconformably overlying "
        "a folded and faulted Paleozoic Variscan basement. The ultimate objective of this digital evaluation campaign is "
        "to replace classic uncertainties with an automated, auditable reservoir engineering pipeline. Connected directly "
        "to wireline log databases via MySQL Workbench, this analytical engine precisely quantifies the productive net "
        "thickness (Net Pay), models dynamic petrophysical properties, estimates the Heat In Place (HIP) using the USGS "
        "stochastic formalism, and dimensions the hydraulic architecture of production wellbores. The final goal is to secure "
        "the geothermal doublet asset by identifying the optimal compartment capable of sustaining a stable commercial "
        "production flow rate over a nominal 30-year operational lifetime.", body_style
    ))

    # SECTION 2
    story.append(Paragraph("2. Digital Architecture, Data Science & Evaluation Methodology", h1_style))
    story.append(Paragraph(
        "The evaluation relies on an automated protocol guaranteeing strict reproducibility of all calculations, from raw "
        "drilling data down to the final engineering indicator. The approach interconnects a SQL relational database, a "
        "geophysical data processing engine (Data Science), and a specialized reservoir engineering module.", body_style
    ))
    
    story.append(Paragraph("The pipeline processes three primary categories of data extracted in real time from MySQL:", body_style))
    story.append(Paragraph("• <b>Wireline Log Data (Well Logs):</b> Continuous records as a function of depth including Gamma Ray (GR) for lithology, deep resistivity (Rt) for fluid evaluation, formation density (Rhob), and neutron porosity (NPHI).", bullet_style))
    story.append(Paragraph("• <b>Structural & Geometric Data:</b> Formation gross thickness maps, localization, and displacements of major faults impacting reservoir compartmentalization.", bullet_style))
    story.append(Paragraph("• <b>Dynamic & Thermal Data:</b> Stabilized bottom-hole temperatures (BHT), reservoir pressures, and historical thermal anomalies related to fluid circulation of hydrothermal origin.", bullet_style))
    story.append(Spacer(1, 5))

    # --- ADVANCED FIGURE 1: DETAILED & EXPANDED PIPELINE FLOWCHART ---
    story.append(Paragraph("<b>Figure 1: Detailed Operational Architecture of the Automated Reservoir Pipeline</b>", caption_style))
    dwg = Drawing(523, 105) 
    steps = [
        {"title": "1. INGESTION", "desc1": "MySQL Workbench DB", "desc2": "Automated Core Parsing", "x": 2},
        {"title": "2. DATA SCIENCE", "desc1": "Despiking & Cleaning", "desc2": "Linear Interpolation", "x": 108},
        {"title": "3. PETROPHYSICS", "desc1": "Vsh, Phi, Sw Filters", "desc2": "Net Pay Extraction", "x": 214},
        {"title": "4. VOLUMETRICS", "desc1": "USGS HIP Formalism", "desc2": "Stochastic Power calculation", "x": 320},
        {"title": "5. HYDRAULICS", "desc1": "ESP Sizing Layout", "desc2": "Critical Flow Rate (m³/h)", "x": 426}
    ]
    for i, step in enumerate(steps):
        box_color = colors.HexColor("#1A365D") if i < 3 else colors.HexColor("#C53030")
        dwg.add(Rect(step["x"], 5, 94, 90, fillColor=box_color, strokeColor=colors.HexColor("#1A202C"), strokeWidth=1.2, rx=5, ry=5))
        dwg.add(String(step["x"] + 47, 76, step["title"], textAnchor="middle", fontSize=8.5, fillColor=colors.white, fontName="Helvetica-Bold"))
        dwg.add(Line(step["x"] + 10, 68, step["x"] + 84, 68, strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.5))
        dwg.add(String(step["x"] + 47, 46, step["desc1"], textAnchor="middle", fontSize=7, fillColor=colors.HexColor("#E2E8F0"), fontName="Helvetica-Oblique"))
        dwg.add(String(step["x"] + 47, 24, step["desc2"], textAnchor="middle", fontSize=7, fillColor=colors.HexColor("#E2E8F0"), fontName="Helvetica"))
        if i < len(steps) - 1:
            next_x = steps[i+1]["x"]
            dwg.add(Line(step["x"] + 94, 50, next_x, 50, strokeColor=colors.HexColor("#4A5568"), strokeWidth=1.5))
    story.append(dwg)
    story.append(Spacer(1, 10))

    # SECTION 2.2 
    story.append(Paragraph("2.2 Data Simulation, Synthetic Generation & Preprocessing", h2_style))
    story.append(Paragraph(
        "<b>Data Generation & Simulation:</b> To ensure the robustness of our reservoir engineering pipeline, we implement a "
        "synthetic data generation engine. This module creates high-fidelity, realistic well log suites (Gamma Ray, Resistivity, "
        "Density, Neutron Porosity) that mimic complex geological conditions. Crucially, the simulation injects controlled, "
        "non-linear signal artifacts such as borehole washouts, tool noise, and cycle-skipping phenomena. This 'stress-testing' "
        "approach allows us to calibrate our automated correction algorithms (despiking, normalization) against ground-truth "
        "models before processing real-world field data.", body_style
    ))
    story.append(Paragraph(
        "<b>Signal Conditioning & Despiking:</b> Upon generation, the pipeline applies a series of corrective filters to "
        "these synthetic datasets. Sensor failures and borehole artifacts are isolated and corrected utilizing a bounded "
        "linear interpolation algorithm. Unphysical outliers (e.g., negative porosities or water saturations exceeding 100%) "
        "are systematically clipped and regularized by the analytical engine.", body_style
    ))
    story.append(Paragraph("2.3 Data Lineage & Assurance Qualité", h2_style))
    story.append(Paragraph(
        "Le pipeline applique un algorithme de détection d'aberrations (Z-score > 3σ) pour filtrer les artefacts de logging "
        "avant toute interpolation. Ce processus garantit que la simulation thermique n'est pas biaisée par des données erronées.", body_style))
    story.append(Paragraph(
        "<b>Productive Reservoir Discrimination (Net Pay):</b> Once conditioned, the engine applies three cumulative "
        "petrophysical cut-off filters to the continuous log tracks to isolate Net Pay:", body_style
    ))
    story.append(Paragraph("• Shale volume (Vsh) derived from the Gamma Ray index: <i>Vsh &lt; 30%</i>", bullet_style))
    story.append(Paragraph("• Effective intergranular or fracture porosity: <i>Phi &gt; 10%</i>", bullet_style))
    story.append(Paragraph("• Mobile water saturation (active hydrothermal circulation): <i>Sw &gt; 50%</i>", bullet_style))
    story.append(Paragraph("Only intervals simultaneously meeting these criteria are qualified as 'Net Pay' and will contribute to volumetric and power calculations.", body_style))
    
    story.append(Paragraph("2.4 Analyse de Sensibilité", h2_style))
    story.append(Paragraph("Les seuils de coupure pétrophysiques ont été calibrés par analogie avec les gisements du Royaume-Uni.", body_style))
    
    # Table des seuils
    data = [["Formation", "Gamma Ray (API)", "Porosité (%)", "Fractures (/m)", "Analogie"],
            ["Trias (Matrice)", "< 65", "> 8", "N/A", "Bassin Wessex"],
            ["Carbonifère (Faille)", "< 70", "N/A", "> 12", "N. Pennines"]]
    t = Table(data, colWidths=[100, 80, 80, 80, 100])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    story.append(t)
    story.append(Spacer(1, 10))
    
    # SECTION 3
    story.append(Paragraph("3. Synthesis of Petrophysical and Reservoir Properties", h1_style))
    story.append(Paragraph("The table below groups the exact metrics extracted from the database after executing the petrophysical filters from Step 2.", body_style))
    
    raw_data = [
        [Paragraph("Well ID", table_header), Paragraph("Target Formation", table_header), Paragraph("Gross Thickness (m)", table_header), Paragraph("Net Pay (m)", table_header), Paragraph("N-to-G (%)", table_header), Paragraph("Temp. (°C)", table_header), Paragraph("HIP (PJ)", table_header), Paragraph("Required Flow (m³/h)", table_header)],
        [Paragraph("GT-01", table_text), Paragraph("Sherwood Sandstone (Triassic)", table_text), Paragraph("699", table_text), Paragraph("594", table_text), Paragraph("84.98%", table_text), Paragraph("21.99", table_text), Paragraph("0.00", table_text), Paragraph("0.00", table_text)],
        [Paragraph("GT-02", table_text), Paragraph("Carboniferous (Fault Zone)", table_text), Paragraph("999", table_text), Paragraph("150", table_text), Paragraph("15.02%", table_text), Paragraph("53.74", table_text), Paragraph("5.28", table_text), Paragraph("55.18", table_text)],
        [Paragraph("GT-03", table_text), Paragraph("Triassic Onlap / Variscan Basement", table_text), Paragraph("499", table_text), Paragraph("0", table_text), Paragraph("0.00%", table_text), Paragraph("0.00", table_text), Paragraph("0.00", table_text), Paragraph("0.00", table_text)]
    ]
    t = Table(raw_data, colWidths=[45, 138, 60, 50, 50, 50, 50, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Paragraph("<b>Table 1: Validated geophysical and dynamic parameters per well</b>", caption_style))

    # MAXIMIZED GRAPHICS INJECTIONS
    perf_img_path = find_image_file("performance", ["Synthese_Performances_Puits.png"])
    if perf_img_path:
        perf_box = []
        perf_box.append(Image(perf_img_path, width=523, height=220))
        perf_box.append(Paragraph("<b>Figure 2: Comparative synthesis of production performance and critical required flow rates per well.</b>", caption_style))
        story.append(KeepTogether(perf_box))

    # SECTION 4
    story.append(Paragraph("4. Detailed Compartment Analysis and Well Evaluation", h1_style))
    
    # 4.1 GT-01 + Well Track
    story.append(Paragraph("4.1 Well GT-01: Eastern Matrix Basin Compartment (Sherwood Sandstone)", h2_style))
    story.append(Paragraph(
        "The vertical well GT-01 penetrates a thick sedimentary series of fluvio-lacustrine origin belonging to the Sherwood "
        "Sandstone Group (Triassic). Gamma Ray and Density-Porosity logs reveal an excellent, homogeneous matrix reservoir, "
        "characterized by an exceptional Net-to-Gross of 84.98% and a gross sedimentary thickness of 699 meters. However, "
        "thermal analysis indicates a stabilized bottom-hole temperature (BHT) of only 21.99°C, reflecting a structural high "
        "or a locally deficient geothermal gradient. Its usable Hydrothermal Heat In Place (HIP) relative to the industrial "
        "plant rejection baseline is null (0 PJ), excluding GT-01 as a direct producer asset.", body_style
    ))
    gt01_track = find_image_file("GT01", ["Well_GT01_Tracks.png", "well_track_GT-01.png"])
    if gt01_track:
        track_box = []
        track_box.append(Image(gt01_track, width=523, height=240))
        track_box.append(Paragraph("<b>Figure 3: Composite logs (Well Tracks) for well GT-01.</b>", caption_style))
        story.append(KeepTogether(track_box))

    # 4.2 GT-02 + Well Track
    story.append(Paragraph("4.2 Well GT-02: Major Fault Zone and Carboniferous Fractured Reservoir", h2_style))
    story.append(Paragraph(
        "Well GT-02 targets a major structural anomaly manifested as a sub-vertical fault corridor cutting through the deep "
        "Carboniferous Limestones. The total drilled gross interval is 999 meters. The productive net interval (Net Pay) is "
        "strictly restricted to 150 meters (Net-to-Gross of 15.02%), corresponding to intensely fractured zones. The primary "
        "thermodynamic interest of GT-02 lies in its hydrodynamic behavior: the fault acts as a highly transmissive vertical "
        "conduit, forcing deep hyperthermal fluids upward to an exceptional stabilized temperature of 53.74°C. The USGS volumetric "
        "calculation confirms a Heat In Place (HIP) of 5.28 PetaJoules (PJ) confined within the fracture network.", body_style
    ))
    gt02_track = find_image_file("GT02", ["Well_GT02_Tracks.png", "well_track_GT-02.png"])
    if gt02_track:
        track_box = []
        track_box.append(Image(gt02_track, width=523, height=240))
        track_box.append(Paragraph("<b>Figure 4: Composite logs (Well Tracks) for well GT-02.</b>", caption_style))
        story.append(KeepTogether(track_box))

    # 4.3 GT-03 + Well Track
    story.append(Paragraph("4.3 Well GT-03: Western Margin and Stratigraphic Pinch-out (Onlap)", h2_style))
    story.append(Paragraph(
        "The exploratory well GT-03 documents the western closure of the sedimentary system. It highlights a distinct "
        "stratigraphic pinch-out where porous sandstone formations lap onto the paleo-relief of the tight, compacted Variscan "
        "basement. The application of petrophysical cut-offs isolates a Net Pay strictly equal to 0 meters. The absence of an open "
        "fracture network combined with the destruction of matrix porosity by early mechanical diagenesis eliminates all "
        "fluid productivity.", body_style
    ))
    gt03_track = find_image_file("GT03", ["Well_GT03_Tracks.png", "well_track_GT-03.png"])
    if gt03_track:
        track_box = []
        track_box.append(Image(gt03_track, width=523, height=240))
        track_box.append(Paragraph("<b>Figure 5: Composite logs (Well Tracks) for well GT-03.</b>", caption_style))
        story.append(KeepTogether(track_box))

    # 4.4 Lithostratigraphic Cross-Section
    img_coupe = find_image_file("coupe", ["coupe_lithostratigraphique_2D.png"])
    if img_coupe:
        section_img = []
        section_img.append(Spacer(1, 5))
        section_img.append(Paragraph("4.4 Cross-Sectional Bloc Synthesis (Real Modeled Cross-Section)", h2_style))
        section_img.append(Paragraph(
            "The two-dimensional geometric synthesis highlights the graben structure of the sedimentary sector. "
            "Polyphase tectonic activity generated the eastern downfaulted compartment (GT-01), while the uplift of the western "
            "block causes a distinct stratigraphic pinch-out visible at well GT-03. The central fault acts as a structural boundary "
            "and a thermal conduit for the fractured reservoir of GT-02.", body_style
        ))
        section_img.append(Image(img_coupe, width=523, height=280))
        section_img.append(Paragraph("<b>Figure 6: Interpolated West-East lithostratigraphic cross-section (Real data from MySQL Workbench).</b>", caption_style))
        story.append(KeepTogether(section_img))

    # SECTION 5
    story.append(Paragraph("5. Physical and Mathematical Foundations & Reservoir Equations", h1_style))
    story.append(Paragraph("The technical validation of the exploitable power relies on two core pillars of porous media physics:", body_style))
    
    story.append(Paragraph("<b>1. Global Volumetric Energy Equation (USGS Formalism):</b>", h2_style))
    formule_hip = "<font face='Courier' size='9.5'><b>Q_HIP = A × h × [((1 - Phi) × Rhome × Cme) + (Phi × Rhof × Cf)] × (Tr - Tref)</b></font>"
    story.append(Paragraph(formule_hip, italic_style))
    story.append(Paragraph("Where Rhome = 2650 kg/m³, Cme = 850 J/kg/°C, Cf = 4184 J/kg/°C, and Tref (plant rejection baseline) = 40°C.", body_style))
    
    story.append(Paragraph("<b>2. Hydraulic Sizing of the Critical Flow Rate:</b>", h2_style))
    formule_prod = "<font face='Courier' size='9.5'><b>Q_production = P_thermal / [Rhof × Cf × (Tr - Tref)]</b></font>"
    story.append(Paragraph(formule_prod, italic_style))
    story.append(Paragraph("The numerical application for GT-02 yields a required extraction flow rate of 15.33 L/s (equivalent to 55.18 m³/h).", body_style))

    # SECTION 6
    story.append(Paragraph("6. Strategic Recommendations and Production Engineering Layout", h1_style))
    story.append(Paragraph("Based on the synthesized results, Management issues the following directives:", body_style))
    
    story.append(Paragraph(
        "<b>1. Selective Completion Strategy for GT-02:</b> Prioritize an open-hole completion or premium slotted liners across "
        "the limestone fractures to avoid skin damage and preserve natural reservoir permeability.", body_style
    ))
    story.append(Paragraph(
        "<b>2. Electrical Submersible Pump (ESP) Specifications:</b> Nominal flow rate of 50 to 65 m³/h set at approximately "
        "350 m depth. Metallurgy must strictly specify Super-Duplex steel or Nickel alloy (Inconel 625) due to dissolved CO2 corrosion risks.", body_style
    ))
    story.append(Paragraph(
        "<b>3. GT-01 Asset Repurposing (ATES):</b> Repurpose this non-productive 'cold' wellbore into an Aquifer Thermal Energy "
        "Storage (ATES) system to capture and store seasonal surface industrial excess heat during summer periods for winter peak shaving.", body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"🎉 Engineering technical report successfully generated with enhanced flowchart and data lineage details: {pdf_filename}")

if __name__ == "__main__":
    generate_expert_report()
