import streamlit as st
import pandas as pd
import json
import os
import random
from utils import save_user_data  # ייבוא פונקציית השמירה לענן

st.set_page_config(page_title="תרגול ניסוח מחדש", page_icon="🧩")

# --- 1. הגנת גישה וטעינת נתונים ---
if not st.session_state.get('logged_in'):
    st.warning("אנא התחבר דרך העמוד הראשי.")
    st.stop()

user_data = st.session_state.user_data
DATA_FILE = "data/restatements.json"

if "restatements_solved" not in user_data:
    user_data["restatements_solved"] = []


@st.cache_data
def load_restatements_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


all_questions = load_restatements_data()

if not all_questions:
    st.error("קובץ השאלות (data/restatements.json) חסר או ריק.")
    st.stop()

# --- 2. ממשק עליון (איפוס והתקדמות) ---
st.title("תרגול ניסוח מחדש (Restatements) 🧩")

with st.expander("⚙️ הגדרות ואיפוס"):
    st.write("כאן תוכל למחוק את היסטוריית התרגול שלך ולהתחיל מאפס.")
    if st.button("איפוס היסטוריית פתרונות", type="primary"):
        user_data["restatements_solved"] = []
        save_user_data(user_data)
        st.session_state.rs_batch_active = False
        st.success("ההיסטוריה אופסה בהצלחה!")
        st.rerun()

solved_ids = set(user_data["restatements_solved"])
all_ids = {q['id'] for q in all_questions if 'id' in q}
remaining_ids = list(all_ids - solved_ids)

total_q = len(all_ids)
solved_count = len(solved_ids)
st.progress(solved_count / total_q if total_q > 0 else 0, text=f"פתרת {solved_count} מתוך {total_q} שאלות")

if not remaining_ids:
    st.balloons()
    st.success("🏆 מדהים! סיימת את כל השאלות במאגר!")
    if st.button("חזור לדשבורד 🏠"):
        st.switch_page("pages/1_dashboard.py")
    st.stop()

# --- 3. ניהול מצב המקבץ ---
if 'rs_batch_active' not in st.session_state:
    st.session_state.rs_batch_active = False

if not st.session_state.rs_batch_active:
    st.write("---")
    st.write("התרגול מתבצע במקבצים של 4 שאלות. התקדמותך נשמרת בענן בסיום כל מקבץ.")
    if st.button("התחל מקבץ חדש 🚀", use_container_width=True):
        batch_size = min(4, len(remaining_ids))
        batch_ids = random.sample(remaining_ids, batch_size)
        st.session_state.rs_current_batch = [q for q in all_questions if q['id'] in batch_ids]
        st.session_state.rs_batch_active = True
        st.session_state.rs_batch_submitted = False

        for q in st.session_state.rs_current_batch:
            key = f"rs_q_{q['id']}"
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # כפתור חזור לדשבורד כשאין מקבץ פעיל
    if st.button("🏠 חזור לדשבורד", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

# --- 4. תצוגת המקבץ הנוכחי ---
else:
    batch = st.session_state.rs_current_batch
    is_submitted = st.session_state.rs_batch_submitted

    for i, q in enumerate(batch):
        st.subheader(f"שאלה {i + 1}")
        st.info(f"**{q['original']}**")

        selected_ans = st.radio(
            "בחר את הניסוח המדויק ביותר:",
            q['options'],
            key=f"rs_q_{q['id']}",
            disabled=is_submitted,
            index=None
        )

        if is_submitted:
            correct_ans = q['options'][q['correct_index']]
            if selected_ans == correct_ans:
                st.success("✅ נכון!")
            else:
                st.error(f"❌ טעות. התשובה: **{correct_ans}**")
            st.markdown(f"💡 **הסבר:** {q['explanation']}")
        st.write("---")

    # --- 5. כפתורי שליטה ---
    if not is_submitted:
        if st.button("סיום מקבץ ובדיקת תשובות ✔️", type="primary", use_container_width=True):
            st.session_state.rs_batch_submitted = True
            for q in batch:
                selected = st.session_state.get(f"rs_q_{q['id']}")
                correct_ans = q['options'][q['correct_index']]
                if selected == correct_ans and q['id'] not in user_data["restatements_solved"]:
                    user_data["restatements_solved"].append(q['id'])
            save_user_data(user_data)
            st.rerun()
    else:
        if st.button("למקבץ הבא ➡️", use_container_width=True):
            st.session_state.rs_batch_active = False
            st.rerun()

    # כפתורי עזר בתחתית המקבץ הפעיל (בדומה ל-Quiz)
    col_end, col_dash = st.columns(2)
    with col_end:
        if st.button("🏁 בטל מקבץ נוכחי", use_container_width=True, help="סגור את המקבץ בלי לשמור התקדמות"):
            st.session_state.rs_batch_active = False
            st.rerun()
    with col_dash:
        if st.button("🏠 חזור לדשבורד", use_container_width=True):
            st.session_state.rs_batch_active = False
            st.switch_page("pages/1_dashboard.py")