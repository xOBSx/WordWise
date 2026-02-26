import streamlit as st

st.set_page_config(page_title="דשבורד התקדמות", page_icon="📊")

# הגנה על העמוד - רק למחוברים
if not st.session_state.get('logged_in'):
    st.warning("אנא התחבר דרך העמוד הראשי.")
    st.stop()

user_data = st.session_state.user_data
username = user_data["username"]

st.title(f"היי {username.capitalize()}! 👋")

# הצגת נתונים מהענן (Supabase)
col1, col2, col3 = st.columns(3)
col1.metric("מילים שלמדתי", len(user_data.get("learned", [])))
col2.metric("מילים בלמידה", len(user_data.get("learning", {})))
col3.metric("שאלות שפתרתי",
            len(user_data.get("restatements_solved", [])) + len(user_data.get("sentence_completions_solved", [])))

st.write("---")
st.subheader("מה תרצה לעשות?")

# כפתורים לניווט בין חלקי האפליקציה
col_a, col_b = st.columns(2)

with col_a:
    if st.button("🔍 סינון מילים חדשות", use_container_width=True):
        st.switch_page("pages/2_filter_words.py")

    if st.button("📚 המילים שלי (למידה)", use_container_width=True):  # הכפתור שהיה חסר
        st.switch_page("pages/3_current_learning.py")

with col_b:
    if st.button("🎯 מבחן מילים (Quiz)", use_container_width=True):
        st.switch_page("pages/4_quiz.py")

    if st.button("🧩 תרגול ניסוח מחדש", use_container_width=True):
        st.switch_page("pages/5_restatements.py")

if st.button("✏️ השלמת משפטים", use_container_width=True):
    st.switch_page("pages/6_sentence_completions.py")

st.write("---")
if st.button("התנתק"):
    st.session_state.logged_in = False
    st.switch_page("app.py")