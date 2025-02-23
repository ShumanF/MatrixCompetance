import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import json
import os

# Configure page
st.set_page_config(page_title="Competence Matrix", layout="wide")
st.title("Team Competence Overview")

# File to store skill definitions
SKILL_INFO_FILE = "skill_info.json"

# Load skill definitions from file
def load_skill_info():
    if os.path.exists(SKILL_INFO_FILE):
        with open(SKILL_INFO_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}  # Return an empty dictionary if the file is empty or invalid
    return {}

# Save skill definitions to file
def save_skill_info(skill_info):
    with open(SKILL_INFO_FILE, "w") as f:
        json.dump(skill_info, f)

# Initialize default skills and info
if 'skills' not in st.session_state:
    st.session_state.skills = ["Java", "Git", "Gerrit", "CloudRan", "Helm", "Kubernetes", "MJE Wow", "JCAT"]
if 'skill_info' not in st.session_state:
    st.session_state.skill_info = load_skill_info()

# Create tabs
tab1, tab2 = st.tabs(["Competence Matrix", "Skill Definitions"])

with tab1:
    # Skill management section
    st.sidebar.header("Manage Skills")
    new_skill = st.sidebar.text_input("Add new skill")
    if st.sidebar.button("Add Skill") and new_skill and new_skill not in st.session_state.skills:
        st.session_state.skills.append(new_skill)
        st.session_state.skill_info[new_skill] = ""  # Initialize info for new skill
        if 'df' in st.session_state:
            st.session_state.df[new_skill] = 3  # Default value for new skill

    # Show skills that can be removed
    skills_to_remove = st.sidebar.multiselect("Select skills to remove", st.session_state.skills)
    if st.sidebar.button("Remove Selected Skills") and skills_to_remove:
        for skill in skills_to_remove:
            st.session_state.skills.remove(skill)
            del st.session_state.skill_info[skill]  # Remove info for deleted skill
            if 'df' in st.session_state:
                st.session_state.df = st.session_state.df.drop(columns=[skill])

    # Create empty DataFrame if no entries exist
    if 'df' not in st.session_state:
        # Generate random names
        random_names = [
            "Emma Thompson", "James Wilson", "Sarah Chen", 
            "Michael Rodriguez", "Lisa Anderson", "David Kim",
            "Rachel Martinez"
        ]
        
        # Create random data
        random_data = {"Name": random_names}
        for skill in st.session_state.skills:
            random_data[skill] = [random.randint(1, 5) for _ in range(len(random_names))]
        st.session_state.df = pd.DataFrame(random_data)

    # Display editable matrix with data editor
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        height=400,
        num_rows="dynamic",
        column_config={
            "Name": st.column_config.TextColumn(
                "Name",
                help="Enter team member name",
                required=True
            ),
            **{skill: st.column_config.NumberColumn(
                skill,
                help=f"Rate {skill} competency (1-5). {st.session_state.skill_info.get(skill, '')}",
                min_value=1,
                max_value=5,
                step=1,
                required=True
            ) for skill in st.session_state.skills}
        },
        hide_index=True
    )

    # Store the edited dataframe back in session state
    st.session_state.df = edited_df

    # Calculate averages for each skill
    skill_averages = edited_df[st.session_state.skills].mean()

    # Create radar chart
    fig = go.Figure()

    # Add team average trace
    fig.add_trace(go.Scatterpolar(
        r=skill_averages,
        theta=st.session_state.skills,
        name='Team Average',
        line_width=3,
        line_color='red',
        fill='toself'
    ))

    # Update layout with flatter structure
    fig.update_layout(
        title='Team Skill Overview',
        polar_radialaxis_visible=True,
        polar_radialaxis_range=[0, 5],
        polar_radialaxis_ticktext=['0', '1', '2', '3', '4', '5'],
        polar_radialaxis_tickvals=[0, 1, 2, 3, 4, 5],
        polar_radialaxis_gridcolor='lightgrey',
        polar_angularaxis_gridcolor='lightgrey',
        polar_bgcolor='white',
        showlegend=False,
        height=800,
        width=1000
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Add download button
    csv = edited_df.to_csv().encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="competence_matrix.csv",
        mime="text/csv"
    )

with tab2:
    st.header("Skill Definitions")
    for skill in st.session_state.skills:
        with st.expander(f"Definition for {skill}"):
            st.session_state.skill_info[skill] = st.text_area("", st.session_state.skill_info.get(skill, ""), key=f"def_{skill}")
    
    # Save skill definitions when the user updates them
    if st.button("Save Definitions"):
        save_skill_info(st.session_state.skill_info)
        st.success("Skill definitions saved!")
