import streamlit as st
import pandas as pd
import numpy as np
import datetime
import casbin

# ==========================================
# 1. INITIALIZE CASBIN GOVERNANCE ENGINE
# ==========================================
try:
    casbin_engine = casbin.Enforcer("model.conf", "policy.csv")
except Exception as error:
    st.error("⚠️ Casbin Engine Error: Make sure model.conf and policy.csv are in your folder!")
    st.stop()

# ==========================================
# 2. SYSTEM CONFIGURATION & MEMORY
# ==========================================
st.set_page_config(page_title="ADSP - Final Thesis Artifact", layout="wide", page_icon="🛡️")

if 'db_consent' not in st.session_state:
    st.session_state['db_consent'] = {
        'share_technical': True,    
        'share_medical': True,      
        'share_commercial': False,  
        'quiet_hours_start': 20,    
        'quiet_hours_end': 8,       
        'is_youth': False           
    }

if 'audit_log' not in st.session_state:
    st.session_state['audit_log'] = []

def log_action(user, action, status, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['audit_log'].append({
        "Time": timestamp, "User": user, "Action": action, "Status": status, "Details": details
    })

def generate_mock_data(is_youth=False):
    return pd.DataFrame({
        'Time': [f"{i}:00" for i in range(10, 21)],
        'Heart Rate': np.random.randint(100 if is_youth else 60, 160 if is_youth else 180, 11),
        'Speed': np.random.randint(5, 35, 11),       
        'Stress Level': np.random.randint(2, 9, 11)  
    })

# ==========================================
# 3. SMART SIDEBAR: LOGIN & ROSTER
# ==========================================
with st.sidebar:
    st.header("🔐 ADSP Secure Login")
    role_display = st.selectbox("Select Your Role", ["Professional Athlete", "Youth Athlete", "Head Coach", "Commercial Partner", "Compliance Officer"])
    
    if role_display == "Head Coach": casbin_role = "coach"
    elif role_display == "Commercial Partner": casbin_role = "sponsor"
    else: casbin_role = "user"
    
    st.markdown("---")
    
    if "Athlete" in role_display:
        st.session_state['db_consent']['is_youth'] = True if "Youth" in role_display else False
        
        # ⚡ SECURITY FIX 1: Force Commercial Consent to False for Youth
        if st.session_state['db_consent']['is_youth']:
            st.session_state['db_consent']['share_commercial'] = False
            
        st.subheader("👤 My Profile Status")
        st.write("Logged in as:", role_display)
        simulated_stress = st.slider("My Live Stress Level", 1, 10, 3)
        target_athlete = "Myself"
        player_id = "My Profile"
    else:
        st.subheader("📋 Anonymized Athlete Roster")
        target_athlete = st.selectbox("Select Profile to View:", [
            "Athlete Profile A (Adult Professional)",
            "Athlete Profile B (Youth Academy - Under 18)",
            "Athlete Profile C (Adult Professional)"
        ])
        
        st.session_state['db_consent']['is_youth'] = True if "Youth" in target_athlete else False
        
        # ⚡ SECURITY FIX 2: Force Commercial Consent to False for Youth
        if st.session_state['db_consent']['is_youth']:
            st.session_state['db_consent']['share_commercial'] = False
            
        player_id = target_athlete.split(' (')[0] 
        simulated_stress = st.slider(f"{player_id} Live Stress Level", 1, 10, 3)

    st.markdown("---")
    st.subheader("🌍 Environment Context")
    simulated_hour = st.slider("Time of Day (24h)", 0, 23, 14)
    simulated_location = st.radio("Location", ["Training Ground", "Home", "School/Public"])
    

    if st.session_state['db_consent']['is_youth']:
        st.session_state['db_consent']['quiet_hours_start'] = 20
        
    start = st.session_state['db_consent']['quiet_hours_start']
    end = st.session_state['db_consent']['quiet_hours_end']
    is_quiet_hours = (simulated_hour >= start or simulated_hour < end)
# ==========================================
# 4. MAIN DASHBOARD HEADER
# ==========================================
st.title("🛡️ Context-Aware Ethical Framework (CAEF)")
if "Athlete" in role_display:
    st.markdown(f"**User:** {role_display} | **Context:** {simulated_hour}:00 at {simulated_location}")
else:
    st.markdown(f"**User:** {role_display} | **Viewing:** {player_id} | **Context:** {simulated_hour}:00 at {simulated_location}")
st.divider()

# ==========================================
# 5. MODULES (ATHLETE, COACH, PARTNER)
# ==========================================

# --- MODULE A: ATHLETE ---
if "Athlete" in role_display:
    is_youth = st.session_state['db_consent']['is_youth']
    if is_youth: st.warning("⚠️ YOUTH ACCOUNT: Protective Governance Active.")

    tab1, tab2 = st.tabs(["🎛️ Consent", "📊 My Full Data"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 1. Consent Settings")
            st.session_state['db_consent']['share_technical'] = st.toggle("Share Technical Data (Speed)", value=st.session_state['db_consent']['share_technical'])
            st.session_state['db_consent']['share_medical'] = st.toggle("Share Medical Data (Heart Rate)", value=st.session_state['db_consent']['share_medical'])
            
            if is_youth:
                # ⚡ SECURITY FIX 3: Lock UI and backend state simultaneously
                st.session_state['db_consent']['share_commercial'] = False
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
elif role_display == "Head Coach":
    st.subheader("⚽ Decision Support Dashboard")
    
    if st.session_state['db_consent']['is_youth']:
        st.info("🛡️ **YOUTH ATHLETE PROTOCOL ACTIVE:** Enhanced privacy safeguards are in place for this minor. Please adjust coaching expectations accordingly.")
    
    can_read_tech = casbin_engine.enforce(
        casbin_role, "technical_data", "read", 
        str(st.session_state['db_consent']['share_technical']), 
        str(st.session_state['db_consent']['is_youth']), 
        str(is_quiet_hours), simulated_location, simulated_stress
    )
    can_read_med = casbin_engine.enforce(
        casbin_role, "medical_data", "read", 
        str(st.session_state['db_consent']['share_medical']), 
        str(st.session_state['db_consent']['is_youth']), 
        str(is_quiet_hours), simulated_location, simulated_stress
    )

    if can_read_tech or can_read_med:
        st.success(f"✅ Access Granted to {player_id}")
        df = generate_mock_data(st.session_state['db_consent']['is_youth'])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if can_read_tech:
                st.markdown("#### Technical (Speed)")
                st.line_chart(df.set_index('Time')['Speed'])
            if can_read_med:
                st.markdown("#### Medical (Heart Rate)")
                st.line_chart(df.set_index('Time')['Heart Rate'], color="#FF0000")
        
        with col2:
            st.markdown("#### 🧠 AI Insight")
            if can_read_tech:
                max_speed = df['Speed'].max()
                st.metric("Max Speed", f"{max_speed} km/h")
            if can_read_med:
                avg_hr = df['Heart Rate'].mean()
                st.metric("Avg HR", f"{int(avg_hr)} bpm")
                if simulated_stress > 7:
                    st.error("⚠️ HIGH STRESS FLAG")
                    st.caption("Governance Protocol: Rest Required")
                else:
                    st.success("🟢 Mental State OK")
                    
        log_action("Head Coach", f"Viewed {player_id}", "GRANTED", "Passed Casbin Rules")
    else:
        st.error(f"⛔ ACCESS TO {player_id.upper()} DENIED BY CASBIN")
        if not st.session_state['db_consent']['share_medical'] and not st.session_state['db_consent']['share_technical']:
            st.warning("Reason: [CAEF-R4] Athlete Revoked All Consent.")
        elif simulated_location == "Home":
            st.warning("Reason: [CAEF-R3] Geo-Fenced Privacy Active.")
        elif is_quiet_hours:
            st.warning("Reason: [CAEF-R1/R2] Quiet Hours / Youth Curfew Active.")
        log_action("Head Coach", f"Viewed {player_id}", "DENIED", "Blocked by Casbin")

# --- MODULE C: PARTNER ---
elif role_display == "Commercial Partner":
    st.subheader("💰 Commercial Partner Portal")
    
    can_read_comm = casbin_engine.enforce(
        casbin_role, "commercial_data", "read", 
        str(st.session_state['db_consent']['share_commercial']), 
        str(st.session_state['db_consent']['is_youth']), 
        str(is_quiet_hours), simulated_location, simulated_stress
    )

    if can_read_comm:
        st.success(f"✅ Commercial License Active for {player_id}")
        df = generate_mock_data(st.session_state['db_consent']['is_youth'])
        current_speed = df['Speed'].iloc[-1]
        
        st.metric("Live Sprint Speed", f"{current_speed} km/h")
        st.caption("🔒 Medical data (Heart Rate and Stress) is strictly blocked by Casbin.")
        log_action("Partner", f"Viewed {player_id}", "GRANTED", "Passed Casbin Rules")
    else:
        st.error(f"🚫 ACCESS TO {player_id.upper()} DENIED BY CASBIN")
        if st.session_state['db_consent']['is_youth']:
            st.warning("Reason: Commercial access strictly prohibited for Youth Athletes.")
        elif simulated_stress >= 8:
            st.warning("Reason: [CAEF-R5] Psychological Safety Override. Athlete is highly stressed.")
        elif not st.session_state['db_consent']['share_commercial']:
            st.warning("Reason: Athlete opted out.")
        log_action("Partner", f"Viewed {player_id}", "DENIED", "Blocked by Casbin")

# --- MODULE D: AUDIT ---
elif role_display == "Compliance Officer":
    st.subheader("📜 System Audit Log")
    if st.session_state['audit_log']:
        st.dataframe(pd.DataFrame(st.session_state['audit_log'][::-1]), use_container_width=True)
    else:
        st.info("No activity yet.")