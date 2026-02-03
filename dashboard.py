import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from models.analysis_result import AnalysisResult
import time

st.set_page_config(
    page_title="🔍 Advanced Plagiarism Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; color: #1f77b4; }
.metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔍 Internet Research Plagiarism Detector</h1>', unsafe_allow_html=True)
st.markdown("**M.Tech Final Year Project** | *Single PDF → Automatic Research Search → AI Analysis*")

# Sidebar
st.sidebar.header("⚙️ Configuration")
api_url = st.sidebar.text_input("API URL", value="http://localhost:8000")
max_papers = st.sidebar.slider("Max Internet Papers", 3, 10, 5)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📤 Upload Your Research Paper")
    uploaded_file = st.file_uploader(
        "Choose PDF file", 
        type="pdf",
        help="Upload your research paper for automatic plagiarism analysis against internet research"
    )

with col2:
    st.info("**How it works:**\n1. Upload PDF\n2. AI searches Arxiv/Google Scholar\n3. Semantic analysis\n4. Instant report")

if uploaded_file is not None and st.button("🚀 Run Plagiarism Analysis", type="primary"):
    with st.spinner(f"🤖 Multi-agent analysis running... ({max_papers} papers)"):
        
        # Progress simulation
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(6):
            steps = ["📖 Parsing PDF", "🔍 Searching Arxiv", "🧠 Extracting Concepts", 
                    "⚡ Semantic Matching", "📊 Risk Scoring", "✨ Generating Report"]
            status_text.text(f"Step {i+1}/6: {steps[i]}")
            progress_bar.progress((i + 1) / 6)
            time.sleep(0.5)
        
        status_text.text("✅ Analysis Complete!")
        
        # API call
        try:
            files = {'research_paper': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            response = requests.post(f"{api_url}/api/v1/detect-plagiarism", files=files, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                
                # Key Metrics Row
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("🎯 Novelty Score", f"{result['novelty_score']:.1f}%")
                with col_b:
                    st.metric("⚠️ Risk Level", result['overall_plagiarism_risk'])
                with col_c:
                    st.metric("📚 Papers Analyzed", result['total_internet_papers_analyzed'])
                with col_d:
                    st.metric("🔥 High-Risk Matches", result['explainability']['total_matches'])
                
                # Risk Visualization
                st.subheader("📊 Similarity Heatmap")
                df = pd.DataFrame(result['top_similar_papers'][:10])
                if not df.empty:
                    fig = px.bar(
                        df, 
                        x="paper_title", 
                        y="overlap_pct",
                        color="overlap_pct",
                        color_continuous_scale="RdYlGn_r",
                        title="Top Similar Research Papers",
                        hover_data=["paper_url", "source"]
                    )
                    fig.update_layout(xaxis_tickangle=45, height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed Matches
                st.subheader("🔍 Top Matches & Recommendations")
                for i, match in enumerate(result['top_similar_papers'][:5], 1):
                    with st.expander(f"#{i} {match['paper_title']} ({match['overlap_pct']:.1f}%)"):
                        st.markdown(f"**Source**: {match['source']} | **Link**: [{match['paper_url'][:50]}...]({match['paper_url']})")
                        st.write("**Matching Concepts:**")
                        for concept_match in match['matching_concepts'][:5]:
                            st.write(f"• {concept_match.get('a', 'Unknown')} ↔ {concept_match.get('b', 'Unknown')}")
                
                # Recommendations
                if result['recommendations']:
                    st.subheader("💡 Actionable Recommendations")
                    for rec in result['recommendations']:
                        st.info(rec)
                
                # Download Report
                report_json = json.dumps(result, indent=2, default=str)
                st.download_button(
                    "📥 Download Full Report (JSON)",
                    report_json,
                    f"plagiarism_report_{int(time.time())}.json",
                    "application/json"
                )
                
            else:
                st.error(f"❌ API Error: {response.status_code}\n{response.text}")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Analysis timeout. Try smaller paper or check API.")
        except Exception as e:
            st.error(f"💥 Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
**M.Tech Final Year Project** | *LangChain + LangGraph + FastAPI + Streamlit*  
🔗 [GitHub](https://github.com/) | 📄 [Research Paper](docs/paper.pdf)
""")

# Add at bottom of dashboard.py
def start_dashboard():
    """uv script entry point"""
    import streamlit as st
    st.cli()
    
if __name__ == "__main__":
    start_dashboard()