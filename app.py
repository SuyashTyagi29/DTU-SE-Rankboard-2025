import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"

# ================== Load Data ==================
df = pd.read_csv("final_results_updated.csv")
df['roll_no'] = df['roll_no'].str.upper().str.strip()
df['name'] = df['name'].str.title()

# ================== Page Config ==================
st.set_page_config(page_title="SE Rank & Analysis", layout="wide")

# ================== Sidebar Toggle ==================
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = True
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

if st.button("📂 Toggle Sidebar"):
    st.session_state.show_sidebar = not st.session_state.show_sidebar

if st.session_state.show_sidebar:
    with st.sidebar:
        st.markdown("### 🔍 Quick Search")
        sidebar_input = st.text_input("Enter Roll Number or Name", "").strip().upper()
else:
    sidebar_input = ""

# ================== Main Title ==================
st.markdown("<h1 style='text-align: center;'>🎓 SE Department Rank & Analysis</h1>", unsafe_allow_html=True)
st.write("---")

# ================== Home Button ==================
if st.button("🏠 Home"):
    st.rerun()

# ================== Main Search Form ==================
with st.form(key="search_form", clear_on_submit=False):
    roll_or_name = st.text_input("Enter Roll Number or Name", "").strip().upper()
    submitted = st.form_submit_button("🔍 Search Student", use_container_width=True)

# Pick input source: main form or sidebar
search_query = roll_or_name or sidebar_input

# ================== Compare Mode Button ==================
# ================== Compare Mode Button ==================
col_compare, col_clear = st.columns([1, 1])
with col_compare:
    if st.button("👥 Compare with Friend"):
        st.session_state.compare_mode = not st.session_state.compare_mode

with col_clear:
    if st.button("❌ Clear Friend"):
        st.session_state.compare_mode = False
        friend_query = ""

friend_query = ""
if st.session_state.compare_mode:
    with st.form(key="friend_search_form", clear_on_submit=False):
        friend_query = st.text_input("Enter Friend's Roll Number or Name", "").strip().upper()
        friend_submitted = st.form_submit_button("🔍 Search Friend", use_container_width=True)
 
# ================== Helper Function ==================
def get_student_data(query):
    # Allow search by roll number or partial name
    student = df[(df['roll_no'] == query) | (df['name'].str.upper().str.contains(query))]
    if student.empty:
        return None
    return student.iloc[0]

# ================== Display Function ==================
def display_student(student_data, title_suffix=""):
    name = student_data['name']
    roll_no = student_data['roll_no']
    cgpa = student_data['cgpa']
    credits = student_data['total_credits']

    df_sorted = df.sort_values(by="cgpa", ascending=False).reset_index(drop=True)
    df_sorted['rank'] = df_sorted['cgpa'].rank(method='min', ascending=False)
    dept_df = df[df['roll_no'].str.contains("/SE/")]
    dept_df['dept_rank'] = dept_df['cgpa'].rank(method='min', ascending=False)

    overall_rank = int(df_sorted[df_sorted['roll_no'] == roll_no]['rank'])
    dept_rank = int(dept_df[dept_df['roll_no'] == roll_no]['dept_rank'])
    behind = 194 - dept_rank
    percentile = float(round((behind/194) * 100, 3))
    
    st.markdown(f"### 🧑‍🎓 {name} ({roll_no}) {title_suffix}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CGPA", f"{cgpa:.2f}")
    col2.metric("Total Credits", credits)
    col3.metric("Percentile",percentile)
    col4.metric("Department Rank", dept_rank)

    sem_cols = [c for c in df.columns if c.startswith("sem") and c.endswith("_sgpa")]
    st.subheader("📘 Semester-wise SGPA")
    cols = st.columns(len(sem_cols))
    for idx, sem in enumerate(sem_cols):
        cols[idx].metric(f"Sem {idx+1}", student_data[sem])

    sgpa_values = [student_data[c] for c in sem_cols]
    sem_numbers = list(range(1, len(sem_cols)+1))
    sgpa_df = pd.DataFrame({"Semester": sem_numbers, "SGPA": sgpa_values})
    fig = px.line(sgpa_df, x="Semester", y="SGPA", markers=True, title=f"{name}'s SGPA Progression")
    fig.update_traces(line_color="orange", marker=dict(size=8, color="red"))
    st.plotly_chart(fig, use_container_width=True)

# ================== Animated Leaderboard ==================
def display_leaderboard(main_roll, friend_roll=""):
    import plotly.graph_objects as go

    # prepare department df with global ranks
    dept_df = df[df['roll_no'].str.contains("/SE/")].copy()
    dept_df['rank'] = dept_df['cgpa'].rank(method='min', ascending=False).astype(int)

    TOP_N = 10
    highlighted_rolls = {main_roll}
    if friend_roll:
        highlighted_rolls.add(friend_roll)

    # 1) Always include top N naturally
    selected_students = dept_df[dept_df['rank'] <= TOP_N].copy()

    # 2) Add main/friend only if they are outside top N (avoid duplicates)
    extras = dept_df[
        (dept_df['roll_no'].isin(highlighted_rolls)) &
        (~dept_df['roll_no'].isin(selected_students['roll_no']))
    ].copy()

    selected_students = pd.concat([selected_students, extras], ignore_index=True)

    # 3) Sort by global rank so rows are in true leaderboard order
    selected_students = selected_students.sort_values(by='rank', ascending=True).reset_index(drop=True)

    # 4) Assign colors (medals for top 3 override other highlights)
    def assign_color(row):
        if row['rank'] == 1:
            return "#B59A07"   # Gold
        elif row['rank'] == 2:
            return "#C0C0C0"   # Silver
        elif row['rank'] == 3:
            return "#CD7F32"   # Bronze
        elif row['roll_no'] == main_roll:
            return "#FF4B4B"   # Current student
        elif friend_roll and row['roll_no'] == friend_roll:
            return "#00B050"   # Friend
        else:
            return "#3B82F6"   # Others

    selected_students['bar_color'] = selected_students.apply(assign_color, axis=1)

    # 5) Plot with graph_objects so color order strictly follows rows
    names = selected_students['name'].astype(str)
    cgpas = selected_students['cgpa'].astype(float)
    colors = selected_students['bar_color'].tolist()

    fig_bar = go.Figure(go.Bar(
        x=cgpas,
        y=names,
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.6)', width=1)),
        text=[f"{v:.3f}" for v in cgpas],
        textposition='outside',
        hovertemplate="%{y}<br>CGPA: %{x}<extra></extra>"
    ))

    # 6) Layout (dark theme friendly) and ensure rank1 at top
    fig_bar.update_layout(
        title=f"🏆 Top {TOP_N} Students in SE (Highlighted View)",
        xaxis_title="CGPA",
        yaxis_title="Name",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=200, r=20, t=60, b=40)  # increase left margin for long names
    )
    # Show the first row at the top (rank 1 at top)
    fig_bar.update_yaxes(autorange='reversed', showgrid=False)

    st.plotly_chart(fig_bar, use_container_width=True)


def display_friend_comparison(student_data, friend_data):
    sem_cols = [c for c in df.columns if c.startswith("sem") and c.endswith("_sgpa")]
    student_sgpa = [student_data[c] for c in sem_cols]
    friend_sgpa = [friend_data[c] for c in sem_cols]
    semesters = [f"Sem {i+1}" for i in range(len(sem_cols))]

    comp_df = pd.DataFrame({
        "Semester": semesters,
        student_data['name']: student_sgpa,
        friend_data['name']: friend_sgpa
    })

    comp_df_melt = comp_df.melt(id_vars="Semester", var_name="Student", value_name="SGPA")

    fig = px.bar(
        comp_df_melt,
        x="Semester",
        y="SGPA",
        color="Student",
        barmode="group",
        title="📊 Semester-wise SGPA Comparison"
    )
    fig.update_layout(
        yaxis=dict(showgrid=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    #fig.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)


# ================== Main Display ==================
if search_query:
    student_data = get_student_data(search_query)
    if student_data is not None:
        display_student(student_data)

        if st.session_state.compare_mode and friend_query:
            friend_data = get_student_data(friend_query)
            if friend_data is not None:
                display_student(friend_data, title_suffix=" - Friend")
                display_friend_comparison(student_data, friend_data)
            else:
                st.error("Friend's roll number or name not found!")

        display_leaderboard(student_data['roll_no'], friend_data['roll_no'] if st.session_state.compare_mode and friend_query else "")
    else:
        st.error("⚠️ Student not found!")
else:
    st.info("Please enter a roll number or name to view details.")

# ================== Footer with LinkedIn & Suggestion ==================
st.write("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        "💡 **Have suggestions?** [Click here to email me](mailto:your_email@example.com?subject=SE%20Rank%20App%20Feedback) 📧"
    )
with col2:
    st.markdown(
        "[🌐 My LinkedIn](https://www.linkedin.com/in/suyash-tyagi-99a990228/)"
    )
