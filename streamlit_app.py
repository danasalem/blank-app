import streamlit as st
import pandas as pd
import numpy as np
import datetime

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(page_title="ADSP - Final Thesis Artifact", layout="wide", page_icon="🛡️")

# --- CAEF MEMORY ---
if 'db_consent' not in st.session_state:
    st.session_state['db_consent'] = {
        'share_technical': True,    # Speed & Distance
        'share_medical': True,      # Heart Rate & Stress
        'share_commercial': False,  # Biometrics for Ads
        'quiet_hours_start': 20,    
        'quiet_hours_end': 8,       
        'is_youth': False           
    }

if 'audit_log' not in st.session_state:
    st.session_state['audit_log'] = []

# ==========================================
# 2. LOGGING & DATA ENGINE
# ==========================================
def log_action(user, action, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['audit_log'].append({
        "Time": timestamp, "User": user, "Action": action, "Status": "LOGGED", "Details": details
    })

def generate_mock_data(is_youth=False):
    # NOW INCLUDES ALL 3 METRICS
    return pd.DataFrame({
        'Time': [f"{i}:00" for i in range(10, 21)],
        'Heart Rate': np.random.randint(100 if is_youth else 60, 160 if is_youth else 180, 11),
        'Speed': np.random.randint(5, 35, 11),       
        'Stress Level': np.random.randint(2, 9, 11)  
    })

def check_context_rules(current_hour, user_role):
    start = st.session_state['db_consent']['quiet_hours_start']
    end = st.session_state['db_consent']['quiet_hours_end']
    
    if "Youth" in user_role and (current_hour >= 20 or current_hour < 7):
         return False, "🛡️ YOUTH PROTECTION ACTIVE: Mandatory Sleep Hours"

    if current_hour >= start or current_hour < end:
        return False, "😴 RIGHT TO DISCONNECT ACTIVE (Quiet Hours)"
        
    return True, "✅ Active Training Context"

# ==========================================
# 3. INTERFACE
# ==========================================
with st.sidebar:
    st.header("🔐 ADSP Secure Login")
    role = st.selectbox("Select Role", ["Professional Athlete", "Youth Athlete", "Head Coach", "Commercial Partner", "Compliance Officer"])
    st.session_state['db_consent']['is_youth'] = True if "Youth" in role else False
    
    st.markdown("---")
    st.subheader("🌍 Context Simulator")
    simulated_hour = st.slider("Time of Day (24h)", 0, 23, 14)
    simulated_location = st.radio("Location", ["Training Ground", "Home", "School/Public"])

st.title("🛡️ Context-Aware Ethical Framework (CAEF)")
st.markdown(f"**User:** {role} | **Context:** {simulated_hour}:00 at {simulated_location}")
st.divider()

# --- MODULE A: ATHLETE ---
if "Athlete" in role:
    is_youth = "Youth" in role
    if is_youth: st.warning("⚠️ YOUTH ACCOUNT: Protective Governance Active.")

    tab1, tab2 = st.tabs(["🎛️ Consent", "📊 My Full Data"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 1. Consent Settings")
            st.session_state['db_consent']['share_technical'] = st.toggle("Share Technical Data (Speed)", value=st.session_state['db_consent']['share_technical'])
            st.session_state['db_consent']['share_medical'] = st.toggle("Share Medical Data (Heart Rate)", value=st.session_state['db_consent']['share_medical'])
            
            if is_youth:
                st.toggle("Share Commercial Data", value=False, disabled=True, help="LOCKED by CAEF")
            else:
                st.session_state['db_consent']['share_commercial'] = st.toggle("Share Commercial Data", value=st.session_state['db_consent']['share_commercial'])
        
        with col2:
            st.markdown("### 2. Context Settings")
            if is_youth:
                st.slider("Quiet Hours Start", 17, 23, 20, disabled=True)
            else:
                st.session_state['db_consent']['quiet_hours_start'] = st.slider("Quiet Hours Start", 17, 23, 20)

    with tab2:
        df = generate_mock_data(is_youth)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.write("**Performance (Speed)**")
            st.line_chart(df.set_index('Time')['Speed'])
        with col_b:
            st.write("**Health (Heart Rate)**")
            st.line_chart(df.set_index('Time')['Heart Rate'], color="#FF0000")
        with col_c:
            st.write("**Psychological Safety (Stress)**")
            st.bar_chart(df.set_index('Time')['Stress Level'], color="#FFA500")

# --- MODULE B: COACH ---
elif role == "Head Coach":
    st.subheader("⚽ Decision Support Dashboard")
    is_active, msg = check_context_rules(simulated_hour, "Coach")
    
    if not is_active:
        st.error(f"⛔ ACCESS DENIED: {msg}")
        log_action("Head Coach", "View Data", f"DENIED: {msg}")
    elif simulated_location == "Home":
        st.error("⛔ ACCESS DENIED: Geo-Fenced Privacy")
        log_action("Head Coach", "View Data", "DENIED: Geo-Location")
    else:
        # Check CONSENT for separate streams
        has_tech = st.session_state['db_consent']['share_technical']
        has_med = st.session_state['db_consent']['share_medical']
        
        if not has_tech and not has_med:
             st.warning("🔒 ALL DATA HIDDEN: Full Consent Revoked")
             log_action("Head Coach", "View Data", "DENIED: All Consent Revoked")
        else:
            st.success("✅ Access Granted (Based on Permissions)")
            df = generate_mock_data(st.session_state['db_consent']['is_youth'])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if has_tech:
                    st.markdown("#### Technical (Speed)")
                    st.line_chart(df.set_index('Time')['Speed'])
                if has_med:
                    st.markdown("#### Medical (Heart Rate)")
                    st.line_chart(df.set_index('Time')['Heart Rate'], color="#FF0000")
            
            with col2:
                st.markdown("#### 🧠 AI Insight")
                
                # Rule 1: Speed (Technical)
                if has_tech:
                    max_speed = df['Speed'].max()
                    st.metric("Max Speed", f"{max_speed} km/h")
                
                # Rule 2: Stress/HR (Medical)
                if has_med:
                    avg_hr = df['Heart Rate'].mean()
                    st.metric("Avg HR", f"{int(avg_hr)} bpm")
                    
                    # BURNOUT CHECK
                    current_stress = df['Stress Level'].iloc[-1]
                    if current_stress > 7:
                        st.error("⚠️ HIGH STRESS FLAG")
                        st.caption("Governance Protocol: Rest Required")
                    else:
                        st.success("🟢 Mental State OK")
                elif not has_med:
                    st.info("Medical Insights Hidden (Privacy)")

            log_action("Head Coach", "View Data", "GRANTED")

# --- MODULE C: PARTNER ---
elif "Partner" in role:
    st.subheader("💰 Commercial Partner Portal")
    if st.session_state['db_consent']['is_youth']:
        st.error("🛑 ACCESS BLOCKED: Youth Protection Protocol")
    elif st.session_state['db_consent']['share_commercial']:
        st.success("✅ Commercial License Active")
        st.metric("Live Heart Rate", "142 bpm")
        st.caption("Speed/Stress data is not included in commercial license.")
    else:
        st.error("🚫 ACCESS DENIED: Athlete Opted Out")

# --- MODULE D: AUDIT ---
elif role == "Compliance Officer":
    st.subheader("📜 Audit Log")
    if st.session_state['audit_log']:
        st.dataframe(pd.DataFrame(st.session_state['audit_log']), use_container_width=True)
    else:
        st.info("No activity yet.")