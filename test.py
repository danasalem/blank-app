import casbin


e = casbin.Enforcer("model.conf", "policy.csv")

def check_access(role, data, act, consent, is_youth, is_quiet_hours, location, stress):
    print(f"\n---  Request: {role.upper()} wants {data.upper()} ---")
    
  
    allowed = e.enforce(role, data, act, str(consent), str(is_youth), str(is_quiet_hours), location, stress)
    

    if allowed:
        print("CASBIN DECISION: Access Granted")
    else:
        print(" CASBIN DECISION: Access Denied")
        print("   ↳  CAEF AUDIT TRAIL (Why it was blocked):")
        
    
        if not consent:
            print("      Reason: [CAEF-R4] The athlete has dynamically revoked consent for this data stream.")
        elif role == "coach" and location == "Home":
            print("      Reason: [CAEF-R3] Geo-Fencing Triggered. Athlete is at Home; workplace monitoring suspended.")
        elif is_quiet_hours:
            print("      Reason: [CAEF-R2] Right to Disconnect. Request occurred during mandatory rest hours.")
        elif role == "sponsor" and stress >= 8:
            print("      Reason: [CAEF-R5] Psychological Safety Override. Commercial access blocked due to high athlete stress (Level 8+).")
        else:
            print("      Reason: [CAEF-R0] Baseline Policy Block. This role is not authorized to view this data type in policy.csv.")

# ==========================================
# RUNNING THE AUDIT TESTS
# ==========================================
print("STARTING CAEF AUDIT AND COMPLIANCE SIMULATION...")

# Test 1: Perfect conditions for Coach
check_access("coach", "medical_data", "read", consent=True, is_youth=False, is_quiet_hours=False, location="Training Ground", stress=3)

# Test 2: Athlete turns Consent OFF
check_access("coach", "medical_data", "read", consent=False, is_youth=False, is_quiet_hours=False, location="Training Ground", stress=3)

# Test 3: Athlete goes Home (Geo-Fencing Rule triggers!)
check_access("coach", "medical_data", "read", consent=True, is_youth=False, is_quiet_hours=False, location="Home", stress=3)

# Test 4: Sponsor tries to get commercial data, but athlete is highly Stressed (Level 9)
check_access("sponsor", "commercial_data", "read", consent=True, is_youth=False, is_quiet_hours=False, location="Training Ground", stress=9)

# Test 5: Sponsor tries to get medical data (Should be blocked by baseline policy)
check_access("sponsor", "medical_data", "read", consent=True, is_youth=False, is_quiet_hours=False, location="Training Ground", stress=3)