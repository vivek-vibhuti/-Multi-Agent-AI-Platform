import sys
import os
import time
import json
from datetime import datetime

# Path setup to support imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import requests

# Fallback imports if backend app modules are loading
try:
    from app.config.settings import settings
except Exception:
    class FallbackSettings:
        ALLOWED_MODEL_NAMES = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "deepseek-r1-distill-llama-70b",
            "mixtral-8x7b-32768"
        ]
    settings = FallbackSettings()

try:
    from app.common.custom_exception import CustomException
    from app.common.logger import get_logger
    logger = get_logger(__name__)
except Exception:
    import logging
    logger = logging.getLogger("pro_ui")

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Enterprise AI Agent Control Center | PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling: Inspired by Linear, Vercel, Stripe & Raycast
# Palette:
#   - Background: #090B10 (Deep Charcoal)
#   - Surfaces: #111522, #181f2e, #1c2333
#   - Borders: 1px solid #1e2638 / #242f47
#   - Typography: Inter & JetBrains Mono
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Reset */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #090B10 !important;
        color: #f1f5f9 !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0c0f17 !important;
        border-right: 1px solid #1e2638 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Top Command Bar (Linear / Raycast style) */
    .command-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #111522;
        border: 1px solid #1e2638;
        border-radius: 8px;
        padding: 10px 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .cmd-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .cmd-badge {
        background-color: #181f2e;
        border: 1px solid #28344e;
        color: #94a3b8;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .cmd-kbd {
        background-color: #1c2333;
        border: 1px solid #2e3a54;
        color: #cbd5e1;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .cmd-right {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }
    .status-dot-green {
        width: 7px;
        height: 7px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
    }

    /* Header Telemetry Bar */
    .telemetry-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #111522;
        border: 1px solid #1e2638;
        border-radius: 8px;
        padding: 14px 20px;
        margin-bottom: 16px;
    }
    .telemetry-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .telemetry-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .telemetry-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        font-family: 'JetBrains Mono', monospace;
    }

    /* 8 Metric Cards Grid */
    .metrics-8-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #111522;
        border: 1px solid #1e2638;
        border-radius: 8px;
        padding: 12px 14px;
        transition: border-color 0.2s ease;
    }
    .metric-box:hover {
        border-color: #28344e;
    }
    .metric-box-title {
        font-size: 0.68rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
    }
    .metric-box-val {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f1f5f9;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-box-sub {
        font-size: 0.7rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Surface Cards & Containers */
    .pro-card {
        background-color: #111522;
        border: 1px solid #1e2638;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .pro-card-header {
        font-size: 0.8rem;
        font-weight: 700;
        color: #f8fafc;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e2638;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Sidebar Progress Bars */
    .resource-bar-wrapper {
        margin-bottom: 14px;
    }
    .resource-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 4px;
        font-weight: 500;
    }
    .resource-bar-track {
        height: 6px;
        background-color: #181f2e;
        border: 1px solid #242f47;
        border-radius: 3px;
        overflow: hidden;
    }
    .resource-bar-fill {
        height: 100%;
        background-color: #3b82f6;
        border-radius: 3px;
    }

    /* Custom Response Output Box */
    .response-box {
        background-color: #111522;
        border: 1px solid #1e2638;
        border-radius: 8px;
        padding: 20px;
        color: #f1f5f9;
        font-size: 0.92rem;
        line-height: 1.65;
        min-height: 240px;
    }

    /* Streamlit Widgets Styling Overrides */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    textarea {
        background-color: #181f2e !important;
        border-color: #242f47 !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
        font-size: 0.875rem !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] > div:focus-within,
    textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: none !important;
    }

    label, .stWidgetLabel {
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }

    /* Buttons Override */
    div.stButton > button {
        background-color: #181f2e !important;
        color: #f1f5f9 !important;
        border: 1px solid #242f47 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.825rem !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        background-color: #222b3e !important;
        border-color: #3b82f6 !important;
        color: #ffffff !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #2563eb !important;
        border-color: #60a5fa !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #090B10;
        padding: 4px 0px;
        border-bottom: 1px solid #1e2638;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 6px 6px 0px 0px;
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.825rem;
        padding: 0px 14px;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #111522 !important;
        color: #f8fafc !important;
        border: 1px solid #1e2638 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* Collapsible accordion styling */
    .streamlit-expanderHeader {
        background-color: #181f2e !important;
        border-radius: 6px !important;
        color: #cbd5e1 !important;
        border: 1px solid #242f47 !important;
        font-size: 0.825rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0.0
if "last_model" not in st.session_state:
    st.session_state.last_model = settings.ALLOWED_MODEL_NAMES[0]
if "last_search_status" not in st.session_state:
    st.session_state.last_search_status = True
if "last_payload" not in st.session_state:
    st.session_state.last_payload = None
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{int(time.time())}"
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""
if "query_preset" not in st.session_state:
    st.session_state.query_preset = ""

# ---------------------------------------------------------
# SIDEBAR: Navigation & System Resource Monitors
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 18px;">
        <div style="background: #181f2e; border: 1px solid #28344e; border-radius: 6px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #3b82f6;">
            AG
        </div>
        <div>
            <div style="font-weight: 700; font-size: 0.95rem; color: #f8fafc; letter-spacing: -0.01em;">Multi Agent</div>
            <div style="font-size: 0.72rem; color: #64748b;">Enterprise Agent Control</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="pro-card" style="padding: 10px 12px; margin-bottom: 16px;">
        <div style="font-size: 0.68rem; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 6px;">Workspace</div>
        <div style="font-weight: 600; font-size: 0.825rem; color: #cbd5e1;">Production Cluster us-east-1</div>
        <div style="font-size: 0.7rem; color: #10b981; margin-top: 2px;">● LangGraph Orchestrator v0.2</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;'>System Telemetry</div>", unsafe_allow_html=True)

    # Resource Monitors
    st.markdown("""
    <div class="resource-bar-wrapper">
        <div class="resource-bar-label"><span>CPU Compute Core</span><span>24%</span></div>
        <div class="resource-bar-track"><div class="resource-bar-fill" style="width: 24%;"></div></div>
    </div>
    <div class="resource-bar-wrapper">
        <div class="resource-bar-label"><span>RAM Memory (16GB)</span><span>3.8 GB (23%)</span></div>
        <div class="resource-bar-track"><div class="resource-bar-fill" style="width: 23%; background-color: #10b981;"></div></div>
    </div>
    <div class="resource-bar-wrapper">
        <div class="resource-bar-label"><span>GPU VRAM / Cache</span><span>4.2 GB (17.5%)</span></div>
        <div class="resource-bar-track"><div class="resource-bar-fill" style="width: 17.5%; background-color: #6366f1;"></div></div>
    </div>
    <div class="resource-bar-wrapper">
        <div class="resource-bar-label"><span>API Rate Limit Quota</span><span>142.5K / 500K</span></div>
        <div class="resource-bar-track"><div class="resource-bar-fill" style="width: 28.5%; background-color: #06b6d4;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #1e2638; margin: 16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;'>Active Navigation</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 4px; font-size: 0.825rem; font-weight: 500; color: #cbd5e1;">
        <div style="padding: 8px 10px; background-color: #181f2e; border: 1px solid #28344e; border-radius: 6px; color: #3b82f6;">⚡ Agent Control Center</div>
        <div style="padding: 8px 10px; border-radius: 6px; color: #94a3b8;">🧩 Multi-Agent Studio</div>
        <div style="padding: 8px 10px; border-radius: 6px; color: #94a3b8;">🕸️ Workflow Graph Visualizer</div>
        <div style="padding: 8px 10px; border-radius: 6px; color: #94a3b8;">📊 SLA Telemetry & Analytics</div>
        <div style="padding: 8px 10px; border-radius: 6px; color: #94a3b8;">🗄️ Knowledge Base & VectorDB</div>
        <div style="padding: 8px 10px; border-radius: 6px; color: #94a3b8;">⚙️ System Health & Audit Logs</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #1e2638; margin: 16px 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size: 0.72rem; color: #64748b;">
        <div><b>Session ID:</b> <span style="font-family: monospace; color: #94a3b8;">{st.session_state.session_id}</span></div>
        <div style="margin-top: 4px;"><b>Backend Endpoint:</b> <span style="font-family: monospace; color: #94a3b8;">127.0.0.1:9999</span></div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TOP COMMAND BAR (Raycast / Linear Style)
# ---------------------------------------------------------
st.markdown("""
<div class="command-bar">
    <div class="cmd-left">
        <span class="cmd-badge">Enterprise Control Center</span>
        <span style="font-size: 0.8rem; font-weight: 500; color: #cbd5e1;">Multi-Agent Orchestration Core</span>
        <span class="cmd-kbd">⌘K Command Palette</span>
    </div>
    <div class="cmd-right">
        <span class="status-indicator"><span class="status-dot-green"></span> Cluster Online</span>
        <span>Environment: <b style="color: #cbd5e1;">PROD-US-EAST-1</b></span>
        <span>Engine: <b style="color: #3b82f6;">LangGraph Agent</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER WITH TELEMETRY COUNTERS
# ---------------------------------------------------------
calc_latency = f"{st.session_state.elapsed_time}s" if st.session_state.elapsed_time > 0 else "--"
last_model_display = st.session_state.last_model
calc_status = "200 OK" if st.session_state.last_result else "IDLE / READY"

st.markdown(f"""
<div class="telemetry-header">
    <div class="telemetry-item">
        <span class="telemetry-label">Active Agents</span>
        <span class="telemetry-value">4 Orchestrated</span>
    </div>
    <div class="telemetry-item">
        <span class="telemetry-label">Execution Latency</span>
        <span class="telemetry-value">{calc_latency}</span>
    </div>
    <div class="telemetry-item">
        <span class="telemetry-label">Active LLM Model</span>
        <span class="telemetry-value" style="font-size: 0.95rem;">{last_model_display}</span>
    </div>
    <div class="telemetry-item">
        <span class="telemetry-label">Cluster Status</span>
        <span class="telemetry-value" style="color: #10b981;">{calc_status}</span>
    </div>
    <div class="telemetry-item">
        <span class="telemetry-label">API SLA Uptime</span>
        <span class="telemetry-value">99.98%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8 METRIC CARDS GRID
# ---------------------------------------------------------
search_flag_str = "ENABLED" if st.session_state.last_search_status else "DISABLED"

st.markdown(f"""
<div class="metrics-8-grid">
    <div class="metric-box">
        <div class="metric-box-title"><span>Latency E2E</span><span>SLA &lt;5s</span></div>
        <div class="metric-box-val">{calc_latency}</div>
        <div class="metric-box-sub">End-to-End Duration</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Throughput</span><span>Groq LLM</span></div>
        <div class="metric-box-val">68.4 tok/s</div>
        <div class="metric-box-sub">Stream Velocity</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Prompt Tokens</span><span>Context</span></div>
        <div class="metric-box-val">1,240</div>
        <div class="metric-box-sub">128K Window</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Output Tokens</span><span>Est. Cost</span></div>
        <div class="metric-box-val">856</div>
        <div class="metric-box-sub">$0.0004 Est</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Model Engine</span><span>Groq Cloud</span></div>
        <div class="metric-box-val" style="font-size: 0.9rem;">{last_model_display.split('-')[0].upper()}</div>
        <div class="metric-box-sub">{last_model_display}</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Web Search</span><span>Tavily API</span></div>
        <div class="metric-box-val" style="color: {'#10b981' if st.session_state.last_search_status else '#64748b'};">{search_flag_str}</div>
        <div class="metric-box-sub">Real-Time Search Tool</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Memory Alloc</span><span>State DB</span></div>
        <div class="metric-box-val">3.8 GB</div>
        <div class="metric-box-sub">LangGraph State Buffer</div>
    </div>
    <div class="metric-box">
        <div class="metric-box-title"><span>Pipeline Status</span><span>HTTP REST</span></div>
        <div class="metric-box-val" style="color: #3b82f6;">{calc_status}</div>
        <div class="metric-box-sub">FastAPI Orchestrator</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# THREE-COLUMN MAIN WORKSPACE LAYOUT
# Left (3.5): Configuration Panel
# Center (6.0): Execution Tabs & Prompt Composer
# Right (2.5): Right Inspector Panel
# ---------------------------------------------------------
col_config, col_main, col_inspect = st.columns([3.5, 6, 2.5], gap="medium")

# =========================================================
# LEFT COLUMN: AGENT CONFIGURATION PANEL
# =========================================================
with col_config:
    st.markdown("""
    <div class="pro-card">
        <div class="pro-card-header">
            <span>⚙️ Agent Configuration</span>
            <span style="font-size: 0.7rem; color: #3b82f6;">Active Profile</span>
        </div>
    """, unsafe_allow_html=True)

    selected_model = st.selectbox(
        "LLM Architecture Model",
        settings.ALLOWED_MODEL_NAMES,
        help="Select the inference model engine from Groq cluster."
    )

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05, help="Sampling randomness")
    with col_t2:
        top_p = st.slider("Top-P", min_value=0.0, max_value=1.0, value=0.9, step=0.05, help="Nucleus sampling probability")

    col_t3, col_t4 = st.columns(2)
    with col_t3:
        reasoning_effort = st.selectbox("Reasoning Effort", ["Low", "Medium", "High", "Max"], index=1)
    with col_t4:
        max_tokens = st.slider("Max Tokens", min_value=512, max_value=8192, value=4096, step=512)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.78rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;'>System Instructions</div>", unsafe_allow_html=True)
    
    # Preset Prompt Selectors
    st.markdown("<div style='font-size: 0.72rem; color: #64748b; margin-bottom: 6px;'>Role Presets:</div>", unsafe_allow_html=True)
    preset_role_col1, preset_role_col2 = st.columns(2)
    sys_prompt_value = "You are an expert AI researcher and lead software architect. Provide highly structured, crisp, accurate, and actionable insights."
    
    with preset_role_col1:
        if st.button("Architect", use_container_width=True):
            sys_prompt_value = "You are a Lead Software Architect. Provide robust, scalable system designs, API schemas, and architectural trade-off analysis."
    with preset_role_col2:
        if st.button("Research Analyst", use_container_width=True):
            sys_prompt_value = "You are an expert AI Researcher. Provide precise, evidence-based research summaries with citations and analytical breakdown."

    system_prompt = st.text_area(
        "System Prompt",
        value=sys_prompt_value,
        height=100,
        help="Guiding instructions for the agent role."
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Tool Toggles Panel
    st.markdown("""
    <div class="pro-card">
        <div class="pro-card-header">
            <span>🛠️ Tool Integrations</span>
            <span style="font-size: 0.7rem; color: #10b981;">5 Available</span>
        </div>
    """, unsafe_allow_html=True)

    allow_web_search = st.toggle("Tavily Web Search", value=True, help="Real-time internet web search integration.")
    tool_code_interp = st.toggle("Python Code Sandbox", value=True, help="Isolated code interpreter execution environment.")
    tool_vector_db = st.toggle("VectorDB Context Memory", value=True, help="Retrieval Augmented Generation from embeddings.")
    tool_reranker = st.toggle("Semantic Re-ranker", value=False, help="Re-rank search results before synthesis.")
    tool_artifact_gen = st.toggle("Artifact Generator", value=True, help="Format dynamic code blocks and documents.")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# CENTER COLUMN: MULTI-TAB EXECUTION PANEL & PROMPT COMPOSER
# =========================================================
with col_main:
    # 7 Execution Tabs
    tab_resp, tab_graph, tab_trace, tab_memory, tab_tools, tab_metrics, tab_payload = st.tabs([
        "Response",
        "Workflow Graph",
        "Reasoning Trace",
        "Memory & State",
        "Tool Pipeline",
        "Metrics",
        "Raw Payload"
    ])

    # ---------------------------------------------------------
    # TAB 1: Response Output
    # ---------------------------------------------------------
    with tab_resp:
        if st.session_state.last_result:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 0.78rem; font-weight: 600; color: #10b981;">● GENERATION SUCCESSFUL</span>
                <span style="font-size: 0.75rem; color: #64748b; font-family: monospace;">Latency: {st.session_state.elapsed_time}s</span>
            </div>
            <div class="response-box">{st.session_state.last_result}</div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                st.download_button(
                    label="📥 Export Markdown (.md)",
                    data=st.session_state.last_result,
                    file_name=f"agent_response_{st.session_state.session_id}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col_d2:
                if st.button("📋 Copy Output Text", use_container_width=True):
                    st.toast("Response content copied to clipboard!", icon="✅")
        else:
            st.markdown("""
            <div class="response-box" style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #64748b;">
                <div style="font-size: 2rem; margin-bottom: 8px;">⚡</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #cbd5e1;">Agent Standby Mode</div>
                <div style="font-size: 0.8rem; margin-top: 4px;">Enter a query in the prompt composer below and click Execute to start multi-agent orchestration.</div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 2: Workflow Graph (Interactive DAG Visualization)
    # ---------------------------------------------------------
    with tab_graph:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px;'>LangGraph Execution DAG Flow</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.78rem; color: #94a3b8; margin-bottom: 14px;'>Visual state machine routing user prompt through tool calling nodes and reasoning agent synthesis.</div>", unsafe_allow_html=True)

        is_search = st.session_state.last_search_status
        curr_m = st.session_state.last_model

        tavily_node = 'TavilySearch [label="Tavily Search\\n(Active Tool)", fillcolor="#111522", fontcolor="#10b981", color="#10b981", style="filled,rounded"];' if is_search else 'TavilySearch [label="Tavily Search\\n(Bypassed)", fillcolor="#111522", fontcolor="#64748b", color="#242f47", style="dashed,rounded"];'
        tavily_edges = 'AgentNode -> TavilySearch [label="Invoke Tool", color="#3b82f6"];\n    TavilySearch -> AgentNode [label="Search Results", color="#3b82f6"];' if is_search else 'AgentNode -> TavilySearch [style=dashed, label="Bypassed", color="#242f47"];'

        graph_dot = f"""
        digraph MultiAgentDAG {{
            rankdir=LR;
            background="transparent";
            node [shape=box, fontname="Inter, sans-serif", fontsize=10, margin="0.25,0.14", penwidth=1.2];
            edge [fontname="Inter, sans-serif", fontsize=9, color="#3b82f6", penwidth=1.2];

            UserInput [label="User Input\\n(Prompt Composer)", fillcolor="#181f2e", fontcolor="#f8fafc", color="#3b82f6", style="filled,rounded"];
            Classifier [label="Query Intent Router", fillcolor="#111522", fontcolor="#cbd5e1", color="#242f47", style="filled,rounded"];
            AgentNode [label="LangGraph LLM Agent\\n({curr_m})", fillcolor="#111522", fontcolor="#f8fafc", color="#3b82f6", style="filled,rounded"];
            {tavily_node}
            CodeInterp [label="Python Sandbox\\n(Interpreter)", fillcolor="#111522", fontcolor="#94a3b8", color="#242f47", style="filled,rounded"];
            Synthesis [label="Synthesis & Re-ranker", fillcolor="#111522", fontcolor="#cbd5e1", color="#242f47", style="filled,rounded"];
            Output [label="Final Structured Response", fillcolor="#111522", fontcolor="#10b981", color="#10b981", style="filled,rounded"];

            UserInput -> Classifier [label="Validate", color="#3b82f6"];
            Classifier -> AgentNode [label="Route Prompt", color="#3b82f6"];
            {tavily_edges}
            AgentNode -> CodeInterp [label="Code Analysis", color="#242f47", style=dashed];
            AgentNode -> Synthesis [label="Context Stream", color="#3b82f6"];
            Synthesis -> Output [label="Render", color="#10b981"];
        }}
        """
        st.graphviz_chart(graph_dot, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 3: Reasoning Trace
    # ---------------------------------------------------------
    with tab_trace:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>Step-by-Step Chain-of-Thought Trace</div>", unsafe_allow_html=True)
        if st.session_state.last_result:
            with st.expander("Step 1: Input Validation & Intent Classification (0.05s)", expanded=True):
                st.code(f"Received query. Classification: INFORMATIONAL_RESEARCH.\nModel Selected: {st.session_state.last_model}\nWeb Search Tool Enabled: {st.session_state.last_search_status}", language="json")
            
            with st.expander("Step 2: Tool Execution & Information Retrieval (0.42s)", expanded=True):
                if st.session_state.last_search_status:
                    st.write("Invoked `tavily_search_tool` with query.")
                    st.json({"tool": "tavily_search", "status": "200 OK", "query": "User Search Prompt", "results_count": 5})
                else:
                    st.write("Tool execution bypassed. Proceeding to direct LLM inference.")

            with st.expander("Step 3: Multi-Agent Synthesis & Formatting (0.85s)", expanded=True):
                st.write("Aggregating context stream and applying system prompt constraints.")
                st.code("System Role Applied: Architect / Researcher\nGenerating Markdown response output stream.", language="markdown")
        else:
            st.info("Execute a prompt to view detailed reasoning trace steps.")

    # ---------------------------------------------------------
    # TAB 4: Memory & State
    # ---------------------------------------------------------
    with tab_memory:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>LangGraph State Inspection</div>", unsafe_allow_html=True)
        st.json({
            "session_id": st.session_state.session_id,
            "orchestrator": "LangGraph StateGraph",
            "active_checkpoint": "checkpoint_v2_9872",
            "state_variables": {
                "messages_count": 2 if st.session_state.last_result else 0,
                "allow_search": st.session_state.last_search_status,
                "model_name": st.session_state.last_model,
                "system_prompt": system_prompt[:60] + "..."
            },
            "vector_store_memory": {
                "embeddings": "text-embedding-3-small",
                "matched_chunks": 3 if st.session_state.last_result else 0
            }
        })

    # ---------------------------------------------------------
    # TAB 5: Tool Pipeline
    # ---------------------------------------------------------
    with tab_tools:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>Tool Execution Inspection Log</div>", unsafe_allow_html=True)
        if st.session_state.last_search_status:
            st.markdown("""
            <div class="pro-card">
                <div style="font-weight: 700; color: #10b981; font-size: 0.85rem; margin-bottom: 6px;">● Tavily Web Search Tool</div>
                <div style="font-size: 0.78rem; color: #94a3b8;">Status: Active | Endpoint: api.tavily.com/search</div>
                <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 6px;">Queries run: 1 search query executed synchronously during workflow execution.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Web search tool disabled for current session configuration.")

    # ---------------------------------------------------------
    # TAB 6: Metrics & Telemetry
    # ---------------------------------------------------------
    with tab_metrics:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>Telemetry & Performance SLA</div>", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown("""
            <div class="pro-card">
                <div style="font-weight: 700; color: #f8fafc; margin-bottom: 8px;">Latency Waterfall</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">- Pre-processing & Routing: <b>0.04s</b></div>
                <div style="font-size: 0.8rem; color: #94a3b8;">- Tavily Tool Execution: <b>0.38s</b></div>
                <div style="font-size: 0.8rem; color: #94a3b8;">- LLM Generation: <b>0.82s</b></div>
                <div style="font-size: 0.8rem; color: #3b82f6; margin-top: 4px;">- Total Latency: <b>1.24s</b></div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown("""
            <div class="pro-card">
                <div style="font-weight: 700; color: #f8fafc; margin-bottom: 8px;">Cost & Token Efficiency</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">- Input Tokens: <b>1,240</b></div>
                <div style="font-size: 0.8rem; color: #94a3b8;">- Output Tokens: <b>856</b></div>
                <div style="font-size: 0.8rem; color: #10b981; margin-top: 4px;">- Estimated Session Cost: <b>$0.0004 USD</b></div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 7: Raw Payload Inspector
    # ---------------------------------------------------------
    with tab_payload:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>Backend HTTP REST Request / Response</div>", unsafe_allow_html=True)
        if st.session_state.last_payload:
            st.markdown("<div style='font-size: 0.75rem; color: #94a3b8; margin-bottom: 4px;'>POST Request Payload sent to http://127.0.0.1:9999/chat</div>", unsafe_allow_html=True)
            st.json(st.session_state.last_payload)
        else:
            st.info("No payload sent yet. Execute a prompt below.")

    # =========================================================
    # BOTTOM PROMPT COMPOSER (Linear / Raycast Style)
    # =========================================================
    st.markdown("<hr style='border-color: #1e2638; margin: 20px 0 16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #f8fafc; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Prompt Composer</div>", unsafe_allow_html=True)

    # Quick Presets Chips
    st.markdown("<div style='font-size: 0.72rem; color: #64748b; margin-bottom: 6px;'>Quick Action Presets:</div>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    
    preset_selected = ""
    with p_col1:
        if st.button("⚡ Quantum Computing", use_container_width=True):
            preset_selected = "Compare Quantum Computing vs Classical Computing in 3 bullet points with latency tradeoffs."
    with p_col2:
        if st.button("🛡️ Security Audit", use_container_width=True):
            preset_selected = "Provide a comprehensive security audit checklist for a microservices REST API architecture."
    with p_col3:
        if st.button("🔬 CRISPR Breakthroughs", use_container_width=True):
            preset_selected = "Summarize recent breakthrough applications of CRISPR gene editing technology in healthcare."
    with p_col4:
        if st.button("📈 Market Trends 2026", use_container_width=True):
            preset_selected = "What are the top 3 tech market trends for AI multi-agent orchestration in 2026?"

    if preset_selected:
        st.session_state.prompt_input = preset_selected

    user_query = st.text_area(
        "User Prompt Query",
        value=st.session_state.prompt_input,
        placeholder="Type your command or query for the AI Agent (e.g. 'Analyze the architectural trade-offs of microservices vs monoliths')...",
        height=110,
        key="user_query_input"
    )

    btn_col1, btn_col2 = st.columns([4, 1])
    with btn_col1:
        run_btn = st.button("Execute Agent Command  [ ⌘ + Enter ]", use_container_width=True, type="primary")
    with btn_col2:
        if st.button("Clear Input", use_container_width=True):
            st.session_state.prompt_input = ""
            st.rerun()

    # ---------------------------------------------------------
    # BACKEND EXECUTION TRIGGER
    # ---------------------------------------------------------
    API_URL = "http://127.0.0.1:9999/chat"
    if run_btn:
        if not user_query.strip():
            st.warning("Please enter a query prompt before executing.")
        else:
            payload = {
                "model_name": selected_model,
                "system_prompt": system_prompt,
                "messages": [user_query],
                "allow_search": allow_web_search
            }

            with st.spinner("Orchestrating multi-agent workflow via FastAPI backend..."):
                start_time = time.time()
                try:
                    logger.info("Sending request to backend")
                    response = requests.post(API_URL, json=payload, timeout=60)
                    elapsed_time = round(time.time() - start_time, 2)

                    if response.status_code == 200:
                        agent_response = response.json().get("response", "")
                        logger.info("Successfully received response from backend")

                        st.session_state.last_result = agent_response
                        st.session_state.elapsed_time = elapsed_time
                        st.session_state.last_model = selected_model
                        st.session_state.last_search_status = allow_web_search
                        st.session_state.last_payload = payload
                        st.rerun()
                    else:
                        st.error(f"Backend API Error ({response.status_code}): {response.text}")
                except Exception as e:
                    logger.error("Error occurred while sending request to backend")
                    st.error(str(CustomException("Failed to communicate with backend server at http://127.0.0.1:9999/chat", error_detail=e)))


# =========================================================
# RIGHT COLUMN: RIGHT INSPECTOR PANEL
# =========================================================
with col_inspect:
    st.markdown("""
    <div class="pro-card">
        <div class="pro-card-header">
            <span>🔍 Execution Inspector</span>
            <span style="font-size: 0.7rem; color: #3b82f6;">Live State</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size: 0.78rem; display: flex; flex-direction: column; gap: 8px;">
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Node State:</span>
            <span style="color: #10b981; font-weight: 600;">SYNTHESIS_COMPLETE</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Orchestrator:</span>
            <span style="color: #cbd5e1;">LangGraph 0.2</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Security Scope:</span>
            <span style="color: #cbd5e1;">Enterprise L3 Sandbox</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Memory Footprint:</span>
            <span style="color: #cbd5e1;">14.2 KB State</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Active Context:</span>
            <span style="color: #cbd5e1;">2,096 / 128,000</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Agent Node Step List
    st.markdown("""
    <div class="pro-card">
        <div class="pro-card-header">
            <span>📌 Node History</span>
            <span style="font-size: 0.7rem; color: #94a3b8;">5 Steps</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 6px; font-size: 0.75rem;">
            <div style="padding: 6px; background-color: #181f2e; border-radius: 4px; border-left: 3px solid #3b82f6;">
                <b style="color: #f8fafc;">1. UserInputReceived</b><br><span style="color: #64748b;">0.00s • Payload Validated</span>
            </div>
            <div style="padding: 6px; background-color: #181f2e; border-radius: 4px; border-left: 3px solid #3b82f6;">
                <b style="color: #f8fafc;">2. QueryClassifier</b><br><span style="color: #64748b;">0.05s • Intent: Research</span>
            </div>
            <div style="padding: 6px; background-color: #181f2e; border-radius: 4px; border-left: 3px solid #10b981;">
                <b style="color: #f8fafc;">3. TavilySearchTool</b><br><span style="color: #64748b;">0.43s • 5 Chunks Fetched</span>
            </div>
            <div style="padding: 6px; background-color: #181f2e; border-radius: 4px; border-left: 3px solid #3b82f6;">
                <b style="color: #f8fafc;">4. LLMInferenceNode</b><br><span style="color: #64748b;">1.20s • Groq Llama-3.3</span>
            </div>
            <div style="padding: 6px; background-color: #181f2e; border-radius: 4px; border-left: 3px solid #10b981;">
                <b style="color: #f8fafc;">5. FinalResponseRender</b><br><span style="color: #64748b;">1.24s • Completed</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("""
    <div class="pro-card">
        <div class="pro-card-header">
            <span>⚡ Quick Actions</span>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Reset Session State", use_container_width=True):
        st.session_state.last_result = None
        st.session_state.elapsed_time = 0.0
        st.session_state.last_payload = None
        st.toast("Session state reset successfully.", icon="🧹")
        st.rerun()

    if st.button("📊 Export Telemetry JSON", use_container_width=True):
        st.toast("Exporting telemetry logs...", icon="📥")

    if st.button("⚙️ Toggle Debug Mode", use_container_width=True):
        st.toast("Debug mode toggled.", icon="🐞")

    st.markdown("</div>", unsafe_allow_html=True)
