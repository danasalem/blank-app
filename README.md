import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# ==========================================
# 1. SYSTEM CONFIGURATION & CAEF LAYER
# ==========================================
st.set_page_config(page_title="ADSP - Context-Aware Governance", layout="wide", page_icon="🛡️")

# --- CAEF ENFORCEMENT LAYER: INITIALIZATION ---
# Context -> Consent -> Governance Decision
if 'db_consent' not in st.session_state:
    st.session_state['db_consent'] = {
        'share_technical': True,    
        'share_medical': True,      
        'share_commercial': False,  
        'quiet_hours_start': 20,    # 8 PM
        'quiet_hours_end': 8,       # 8 AM
        'is_youth': False           # Default is Pro
    }

if 'audit_log' not in st.session_state:
    st.session_state['audit_log'] = []

# ==========================================
# 2. LOGGING & SIMULATION ENGINE
# ==========================================

def log_action(user, action, details):
    """Logs user actions to the Immutable Ledger (Symmetry: Athletes are logged too)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Time": timestamp,
        "User": user,
        "Action": action,
        "Status": "LOGGED",
        "Details": details
    }
    st.session_state['audit_log'].append(entry)

def generate_mock_data(is_youth=False):
    """Simulates sensor data. Youth data is anonymized/limited in resolution."""
    # CAEF Principle: Data Minimization for Youth
    hr_range = (100, 160) if is_youth else (60, 180)
    return pd.DataFrame({
        'Time': [f"{i}:00" for i in range(10, 21)],
        'Heart Rate (bpm)': np.random.randint(hr_range[0], hr_range[1], 11),
        'Speed (km/h)': np.random.randint(5, 25, 11),
        'Stress Level': np.random.randint(1, 8, 11)
    })

# ---------------------------------------------------------
# CAEF Core Enforcement Function:
# Applies vulnerability, time, and role-based ethical constraints
# ---------------------------------------------------------
def check_context_rules(current_hour, user_role):
    """
    Returns (True, Message) if access is allowed, (False, Reason) if blocked.
    """
    start = st.session_state['db_consent']['quiet_hours_start']
    end = st.session_state['db_consent']['quiet_hours_end']
    
    # 1. YOUTH PROTECTION RULE (Vulnerability Check)
    if "Youth" in user_role:
        # Youth have stricter disconnect rules (e.g., forced stop at 8 PM)
        if current_hour >= 20 or current_hour < 7:
             return False, "🛡️ YOUTH PROTECTION ACTIVE: Mandatory Sleep Hours"

    # 2. GENERAL RIGHT TO DISCONNECT (Context Check)
    if current_hour >= start or current_hour < end:
        return False, "😴 RIGHT TO DISCONNECT ACTIVE (Quiet Hours)"
        
    return True, "✅ Active Training Context"

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.header("🔐 ADSP Secure Login")
    
    # GENERIC ROLES (No Names)
    role = st.selectbox("Select Role", [
        "Professional Athlete", 
        "Youth Athlete", 
        "Head Coach", 
        "Commercial Partner", 
        "Compliance Officer"
    ])
    
    # Update Youth Flag in Session State based on selection
    st.session_state['db_consent']['is_youth'] = True if "Youth" in role else False

    st.markdown("---")
    st.subheader("🌍 Context Simulator")
    st.info("Simulate environment to test CAEF enforcement.")
    simulated_hour = st.slider("Time of Day (24h)", 0, 23, 14)
    simulated_location = st.radio("Location", ["Training Ground", "Home", "School/Public"])

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("🛡️ Context-Aware Ethical Framework (CAEF) Platform")
st.markdown(f"**User:** {role} | **Context:** {simulated_hour}:00 at {simulated_location}")
st.divider()

# ------------------------------------------
# MODULE A: ATHLETE PORTAL (Pro vs Youth)
# ------------------------------------------
if "Athlete" in role:
    is_youth = "Youth" in role
    st.subheader(f"👤 {role} Command Center")
    
    if is_youth:
        st.warning("⚠️ YOUTH ACCOUNT DETECTED: Protective Governance Active. Some settings are locked for your safety.")

    tab1, tab2 = st.tabs(["🎛️ Consent Manager", "📊 My Data"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 1. Dynamic Consent Settings")
            
            # CALLBACKS for Logging
            def log_tech_change():
                log_action(role, "Update Consent", f"Technical Data: {st.session_state['db_consent']['share_technical']}")
            
            st.session_state['db_consent']['share_technical'] = st.toggle(
                "Share Technical Data (Speed/Tactics)", 
                value=st.session_state['db_consent']['share_technical'],
                on_change=log_tech_change
            )

            # YOUTH RESTRICTION: Commercial Data
            if is_youth:
                st.toggle("Share Commercial Data (Sponsorships/Ads)", value=False, disabled=True, 
                          help="LOCKED: CAEF prohibits commercialization of youth data.")
                st.caption("🔒 Commercial sharing disabled by Youth Protection Protocol.")
            else:
                def log_comm_change():
                    log_action(role, "Update Consent", f"Commercial Data: {st.session_state['db_consent']['share_commercial']}")
                
                # RENAMED "Betting" to "Sponsorships/Ads"
                st.session_state['db_consent']['share_commercial'] = st.toggle(
                    "Share Commercial Data (Sponsorships/Ads)", 
                    value=st.session_state['db_consent']['share_commercial'],
                    on_change=log_comm_change
                )

        with col2:
            st.markdown("### 2. Context Awareness")
            
            if is_youth:
                st.slider("Quiet Hours Start (PM)", 17, 23, 20, disabled=True, 
                          help="LOCKED: Youth athletes require fixed sleep windows.")
                st.caption("🔒 Mandatory 8:00 PM cutoff for Youth.")
            else:
                def log_hours_change():
                    log_action(role, "Update Context", f"Quiet Hours changed to {st.session_state['db_consent']['quiet_hours_start']} PM")
                
                st.session_state['db_consent']['quiet_hours_start'] = st.slider(
                    "Quiet Hours Start (PM)", 17, 23, 20, 
                    on_change=log_hours_change
                )

    with tab2:
        df = generate_mock_data(is_youth)
        st.dataframe(df)

# ------------------------------------------
# MODULE B: COACH DASHBOARD
# ------------------------------------------
elif role == "Head Coach":
    st.subheader("⚽ Decision Support Dashboard")
    
    # 1. CAEF CONTEXT CHECK
    is_active_hours, context_msg = check_context_rules(simulated_hour, "Coach")
    target_is_youth = st.session_state['db_consent']['is_youth'] 

    # 1a. YOUTH PROTECTION OVERRIDE
    if target_is_youth and (simulated_hour >= 20 or simulated_hour < 7):
        st.error(f"🛡️ ACCESS DENIED: {context_msg}")
        log_action("Head Coach", "View Data", f"DENIED: {context_msg}")
        
    # 1b. GENERAL CONTEXT CHECK
    elif not is_active_hours:
        st.error(f"⛔ ACCESS DENIED: {context_msg}")
        log_action("Head Coach", "View Data", f"DENIED: {context_msg}")
    
    elif simulated_location == "Home":
        st.error("⛔ ACCESS DENIED: Athlete is at Home (Geo-Fenced Privacy)")
        log_action("Head Coach", "View Data", "DENIED: Geo-Location Rule")
        
    else:
        # 2. CONSENT CHECK
        if st.session_state['db_consent']['share_technical']:
            st.success("✅ Access Granted: Viewing Technical Data")
            df = generate_mock_data(target_is_youth)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                fig = px.line(df, x='Time', y='Speed (km/h)', title="Athlete Performance Telemetry")
                st.plotly_chart(fig)
            with col2:
                # RENAMED "AI" to "Decision Support"
                st.markdown("### 🧠 Decision Support Insight")
                st.caption("(Rule-Based Simulation)") 
                
                if df['Speed (km/h)'].max() > 20:
                    st.warning("⚠️ High Load Detected")
                    with st.expander("Explain Logic (Glass Box)"):
                        st.write("**Rule Triggered:**")
                        st.write("- Speed > 20km/h sustained")
                        st.write("- Context: Late Training Session")
                else:
                    st.success("🟢 Load Optimal")
            
            log_action("Head Coach", "View Data", "GRANTED")
        else:
            st.warning("🔒 DATA HIDDEN: Athlete has revoked Technical Data consent.")
            log_action("Head Coach", "View Data", "DENIED: Consent Revoked")

# ------------------------------------------
# MODULE C: COMMERCIAL PARTNER PORTAL
# ------------------------------------------
elif "Partner" in role:
    st.subheader("💰 Commercial Partner Portal")
    
    target_is_youth = st.session_state['db_consent']['is_youth']

    if target_is_youth:
        st.error("🛑 ACCESS BLOCKED: CAEF prohibits commercial access to Youth Athlete data.")
        st.image("https://placehold.co/600x400?text=YOUTH+PROTECTION+ACTIVE", caption="Data Redacted")
        log_action("Commercial Partner", "View Biometrics", "DENIED: Youth Protection Protocol")
    
    elif st.session_state['db_consent']['share_commercial']:
        st.success("✅ Commercial License Active")
        st.metric("Live Heart Rate", "142 bpm")
        log_action("Commercial Partner", "View Biometrics", "GRANTED")
    else:
        st.error("🚫 ACCESS DENIED: Data Sovereignty Protocol Active")
        log_action("Commercial Partner", "View Biometrics", "DENIED: Consent Revoked by Athlete")

# ------------------------------------------
# MODULE D: AUDIT LOG
# ------------------------------------------
elif role == "Compliance Officer":
    st.subheader("📜 Immutable Audit Log (Symmetry)")
    st.markdown("Tracks **all** stakeholder actions: Athletes, Coaches, and Partners.")
    
    if len(st.session_state['audit_log']) > 0:
        audit_df = pd.DataFrame(st.session_state['audit_log'])
        st.dataframe(audit_df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No activity recorded yet.")
