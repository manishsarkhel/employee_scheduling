import streamlit as st
import pandas as pd

# --- Configuration & Data ---
# Staffing requirements from the Case Study [Source: 61]
REQUIREMENTS = {
    "Monday": 6,
    "Tuesday": 4,
    "Wednesday": 8,
    "Thursday": 9,
    "Friday": 10,
    "Saturday": 3,
    "Sunday": 2
}

DAYS = list(REQUIREMENTS.keys())

# Define valid shift patterns based on "Consecutive Days Off" rule [Source: 59]
# Format: "Label": [Days Off]
SHIFT_PATTERNS = {
    "Sat-Sun Off (Work Mon-Fri)": ["Saturday", "Sunday"],
    "Sun-Mon Off (Work Tue-Sat)": ["Sunday", "Monday"],
    "Mon-Tue Off (Work Wed-Sun)": ["Monday", "Tuesday"],
    "Tue-Wed Off (Work Thu-Mon)": ["Tuesday", "Wednesday"],
    "Wed-Thu Off (Work Fri-Tue)": ["Wednesday", "Thursday"],
    "Thu-Fri Off (Work Sat-Wed)": ["Thursday", "Friday"],
    "Fri-Sat Off (Work Sun-Thu)": ["Friday", "Saturday"]
}

def init_state():
    """Initialize session state for employees."""
    if 'schedule' not in st.session_state:
        # Start with 0 employees
        st.session_state.schedule = []

def calculate_coverage(schedule):
    """Calculate how many staff are working on each day."""
    current_coverage = {day: 0 for day in DAYS}
    
    for shift_type in schedule:
        days_off = SHIFT_PATTERNS[shift_type]
        # Employee works on days that are NOT their days off
        working_days = [day for day in DAYS if day not in days_off]
        
        for day in working_days:
            current_coverage[day] += 1
            
    return current_coverage

def main():
    st.set_page_config(page_title="Project Roster: Scheduling Challenge", layout="wide")
    init_state()

    # --- Header ---
    st.title("🧩 Project Roster: The Scheduling Challenge")
    st.markdown("""
    **Objective:** Build a workforce schedule that meets daily requirements while minimizing excess labor costs (slack).
    
    **Constraints:**
    1. The facility operates 7 days a week.
    2. [cite_start]Every employee must have **2 consecutive days off**[cite: 62].
    3. You must meet or exceed the required staffing level for every single day.
    """)

    # --- Sidebar: Manage Workforce ---
    with st.sidebar:
        st.header("Manage Workforce")
        
        # Add new employee
        st.subheader("Add Employee")
        selected_shift = st.selectbox(
            "Select Shift Pattern (Days Off):", 
            options=list(SHIFT_PATTERNS.keys())
        )
        
        if st.button("Hire Employee"):
            st.session_state.schedule.append(selected_shift)
            st.success(f"Added Employee #{len(st.session_state.schedule)}")
        
        st.markdown("---")
        
        # Remove employee
        st.subheader("Remove Employee")
        if len(st.session_state.schedule) > 0:
            if st.button("Fire Last Employee"):
                st.session_state.schedule.pop()
        else:
            st.info("No employees to remove.")
            
        st.markdown("---")
        if st.button("Reset Simulation"):
            st.session_state.schedule = []
            st.rerun()

    # --- Main Dashboard ---
    
    # 1. Calculate Metrics
    coverage = calculate_coverage(st.session_state.schedule)
    total_employees = len(st.session_state.schedule)
    
    # Create DataFrame for display
    data = []
    total_slack = 0
    all_met = True
    
    for day in DAYS:
        req = REQUIREMENTS[day]
        actual = coverage[day]
        diff = actual - req
        status = "✅ OK"
        
        if diff < 0:
            status = "🚨 Understaffed"
            all_met = False
        elif diff > 0:
            status = f"⚠️ +{diff} Slack"
            total_slack += diff
        else:
            status = "✨ Perfect"
            
        data.append({
            "Day": day,
            "Required": req,
            "Actual": actual,
            "Status": status
        })
        
    df = pd.DataFrame(data)

    # 2. Display Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Employees", total_employees)
    with col2:
        st.metric("Total Slack (Excess Shifts)", total_slack, 
                  help="Minimize this number while keeping all days green.")
    with col3:
        if all_met:
            st.success("Target Met! All shifts covered.")
        else:
            st.error("Requirements not met.")

    # 3. Visualizations
    st.subheader("Current Coverage vs. Requirements")
    
    # Custom CSS for table to highlight rows
    st.dataframe(
        df.style.apply(lambda x: ['background-color: #ffcccc' if v == "🚨 Understaffed" 
                                  else ('background-color: #ccffcc' if "Perfect" in v 
                                  else '') for v in x], axis=1),
        use_container_width=True,
        height=280
    )

    # Simple Bar Chart
    st.subheader("Visual Analysis")
    chart_data = pd.DataFrame({
        'Day': DAYS,
        'Required': [REQUIREMENTS[d] for d in DAYS],
        'Actual': [coverage[d] for d in DAYS]
    })
    
    # Using Streamlit's native bar chart (Stacked to show gap)
    st.bar_chart(
        chart_data.set_index('Day'),
        color=["#FF4B4B", "#0068C9"] # Red for Req, Blue for Actual (Rough approximation)
    )
    st.caption("Note: Ensure the 'Actual' bars meet or exceed the 'Required' levels.")

    # --- Employee Roster List ---
    with st.expander("View Current Roster Details"):
        if total_employees == 0:
            st.write("No employees hired yet.")
        else:
            roster_data = []
            for i, shift in enumerate(st.session_state.schedule):
                roster_data.append({"ID": i+1, "Shift Pattern": shift})
            st.table(roster_data)

if __name__ == "__main__":
    main()
