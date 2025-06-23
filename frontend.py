import streamlit as st
import pandas as pd
import re
from io import BytesIO
import base64

st.markdown("""
<style>
:root {
  --primary: #2563eb;
  --secondary: #1d4ed8;
  --accent: #3b82f6;
  --dark: #1e293b;
  --light: #f8fafc;
  --card-bg: #ffffff;
  --text-dark: #1e293b;
  --text-light: #f8fafc;
  --bg-primary: #ffffff;
  --bg-secondary: #f1f5f9;
  --border: #e2e8f0;
}

html, body, .stApp {
  background: var(--bg-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--text-dark);
  line-height: 1.6;
}

section[data-testid="stSidebar"] {
  background: var(--dark);
  color: var(--text-light);
  padding: 2rem 1.5rem;
  border-right: 1px solid var(--border);
}

h1, h2, h3, h4, h5, h6 {
  color: var(--text-dark);
  font-weight: 700;
}

h1 {
  font-size: 2.5rem;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
}

.stButton > button {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white !important;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  transition: all 0.2s ease;
}

.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stTextInput>div>div>input,
.stSelectbox>div>div>select,
.stTextArea>div>div>textarea {
  background: var(--card-bg) !important;
  color: var(--text-dark) !important;
  border: 2px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 0.75rem !important;
}

.stDataFrame {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  background: var(--card-bg) !important;
}

.stDataFrame th {
  background: linear-gradient(to right, var(--primary), var(--secondary)) !important;
  color: white !important;
}

.candidate-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stMetric {
  background: var(--card-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 1rem !important;
}

.stSlider .st-b7 {
  background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
}

@media (max-width: 768px) {
  h1 {
    font-size: 2rem;
  }
  
  .stButton > button {
    padding: 1rem !important;
  }
}

.stDownloadButton {text-align: center;}
.stDownloadButton > button {
    background: linear-gradient(90deg, var(--primary), var(--accent));
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}
.stDownloadButton > button:hover {
    background: linear-gradient(90deg, var(--secondary), var(--primary));
    transform: translateY(-1px);
}
.stButton {text-align: center;}
.stButton > button {
    background: linear-gradient(90deg, var(--primary), var(--accent));
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}
.stButton > button:hover {
    background: linear-gradient(90deg, var(--secondary), var(--primary));
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

if 'filtered' not in st.session_state:
    st.session_state.filtered = False
if 'df' not in st.session_state:
    st.session_state.df = None

st.markdown("<h1>🎯 Candidate Filter Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Filter and rank job candidates with precision</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: white;'>📁 Data Upload</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx"], label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.df = df

            if "Experience" in df.columns:
                df['Experience_Value'] = df['Experience'].apply(
                    lambda x: int(re.search(r'\d+', str(x)).group()) if pd.notnull(x) and re.search(r'\d+', str(x)) else 0
                )
            else:
                df['Experience_Value'] = 0

            st.success("✅ File successfully loaded")

            st.markdown("<h2 style='color: white; margin-top: 1.5rem;'>🔍 Filter Controls</h2>", unsafe_allow_html=True)
            min_exp = st.slider("Minimum Experience (years)", 0, 30, 0)

            if 'Qualifications' in df.columns:
                qualifications = st.multiselect(
                    "Qualifications",
                    options=sorted(df['Qualifications'].dropna().unique()),
                    default=[]
                )
            else:
                st.warning("No qualifications data found")
                qualifications = []

            work_type = st.multiselect(
                "Employment Type",
                options=["Full-time", "Part-time", "Intern", "Contract"],
                default=["Full-time", "Part-time", "Intern"]
            )

            job_title_contains = st.text_input("Job Title Keywords") if 'Job_Title' in df.columns else ""
            role_contains = st.text_input("Role Keywords") if 'Role' in df.columns else ""
            location_contains = st.text_input("Location Keywords") if 'location' in df.columns else ""

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Apply Filters", type="primary"):
                    st.session_state.filtered = True
                    st.rerun()
            with col2:
                if st.button("Reset Filters"):
                    st.session_state.filtered = False
                    st.rerun()

        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        st.warning("Please upload a data file to begin")
        st.stop()

if st.session_state.filtered and st.session_state.df is not None:
    df = st.session_state.df.copy()

    df = df[df['Experience_Value'] >= min_exp]

    if qualifications and 'Qualifications' in df.columns:
        df = df[df['Qualifications'].isin(qualifications)]

    if 'Work_Type' in df.columns and work_type:
        df = df[df['Work_Type'].isin(work_type)]

    if job_title_contains and 'Job_Title' in df.columns:
        df = df[df['Job_Title'].str.contains(job_title_contains, case=False, na=False)]

    if role_contains and 'Role' in df.columns:
        df = df[df['Role'].str.contains(role_contains, case=False, na=False)]

    if location_contains and 'location' in df.columns:
        df = df[df['location'].str.contains(location_contains, case=False, na=False)]

    st.markdown(f"<h2>👥 Filtered Candidates ({len(df)} found)</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Candidates", len(df))
    with col2:
        avg_exp = df['Experience_Value'].mean() if len(df) > 0 else 0
        st.metric("Average Experience", f"{avg_exp:.1f} years")

    st.markdown("---")
    st.markdown("<h2>🏆 Top Candidates</h2>", unsafe_allow_html=True)

    if len(df) > 0:
        max_candidates = min(20, len(df))
        top_n = st.slider(
            "Number of top candidates to show",
            min_value=1,
            max_value=max_candidates,
            value=min(5, max_candidates),
            key="top_n_slider"
        )

        for i, (_, row) in enumerate(df.head(top_n).iterrows()):
            st.markdown(f"""
            <div class="candidate-card">
                <h3>#{i+1} {row.get('Contact Person', 'N/A')}</h3>
                <p><strong>📌 Role:</strong> {row.get('Role', 'N/A')}</p>
                <p><strong>📅 Experience:</strong> {row.get('Experience', 'N/A')}</p>
                <p><strong>📍 Location:</strong> {row.get('location', 'N/A')}</p>
                <p><strong>🎓 Qualifications:</strong> {row.get('Qualifications', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No candidates match your filters")

    st.markdown("---")
    st.markdown("<h2>📋 Complete Results</h2>", unsafe_allow_html=True)
    display_cols = [col for col in ['Contact Person', 'Role', 'Job_Title', 'Experience', 'location', 'Qualifications', 'Work_Type'] if col in df.columns]
    if display_cols:
        st.dataframe(df[display_cols], height=600, use_container_width=True)
    else:
        st.warning("No displayable columns found in the data")

    st.markdown("---")
    st.markdown("<h2>📤 Export Results</h2>", unsafe_allow_html=True)
    export_format = st.radio("Export format", options=["CSV", "Excel"], horizontal=True)

    if st.button("Generate Export File"):
        if export_format == "CSV":
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name="filtered_candidates.csv", mime="text/csv")
        else:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                "Download Excel",
                data=buffer.getvalue(),
                file_name="filtered_candidates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; margin-top: 2rem;">
    <p>Candidate Filter System • Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)

if __name__ == '__main__':
    pass
