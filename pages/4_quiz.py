import streamlit as st
import pandas as pd
import random
from utils import save_user_data

st.set_page_config(page_title="תרגול מילים", page_icon="📝")

# --- 1. הגנת גישה וטעינת נתונים ---
if not st.session_state.get('logged_in'):
    st.warning("אנא התחבר דרך העמוד הראשי.")
    st.stop()

user_data = st.session_state.user_data
DONT_KNOW_STR = "🤷 אני לא יודע/ת"


@st.cache_data
def load_lexicon_df():
    """טעינת מאגר המילים הכללי לצורך הסחות דעת ותרגומים"""
    return pd.read_csv("data/psychometry_words.csv")


@st.cache_data
def get_translation_pool():
    df = load_lexicon_df()
    return df['Translation'].dropna().unique().tolist()


# --- 2. לוגיקת יצירת המבחן (80/20) ---
def generate_quiz(num_questions=10):
    learning_words = list(user_data.get("learning", {}).keys())
    learned_words = user_data.get("learned", [])

    total_available = len(learning_words) + len(learned_words)
    if total_available < 4:
        st.warning("אין לך מספיק מילים במאגר למבחן. הוסף לפחות 4 מילים בסינון המילים.")
        return False

    actual_num_questions = min(num_questions, total_available)
    target_learning = int(actual_num_questions * 0.8)
    target_learned = actual_num_questions - target_learning

    quiz_learning = random.sample(learning_words, min(target_learning, len(learning_words)))
    quiz_learned = random.sample(learned_words, min(target_learned, len(learned_words)))

    # השלמת שאלות אם אין מספיק מסוג אחד
    shortfall = actual_num_questions - (len(quiz_learning) + len(quiz_learned))
    if shortfall > 0:
        remaining_pool = list(set(learning_words + learned_words) - set(quiz_learning + quiz_learned))
        quiz_extra = random.sample(remaining_pool, min(shortfall, len(remaining_pool)))
        quiz_learning += quiz_extra

    quiz_pool = quiz_learning + quiz_learned
    random.shuffle(quiz_pool)

    all_translations_pool = get_translation_pool()
    df_lexicon = load_lexicon_df()
    questions = []

    for word in quiz_pool:
        if word in user_data.get("learning", {}):
            correct_translation = user_data["learning"][word]["translation"]
        else:
            match = df_lexicon[df_lexicon['Word'].astype(str).str.lower() == word.lower()]
            correct_translation = match['Translation'].values[0] if not match.empty else "N/A"

        distractors = random.sample([t for t in all_translations_pool if t != correct_translation], 3)
        options = distractors + [correct_translation]
        random.shuffle(options)
        options.append(DONT_KNOW_STR)

        questions.append({
            "word": word,
            "correct": correct_translation,
            "options": options
        })

    st.session_state.quiz_questions = questions
    st.session_state.quiz_active = True
    st.session_state.current_q_index = 0
    st.session_state.score = 0
    st.session_state.answered_current = False
    return True


# --- 3. ממשק המשתמש של המבחן ---
st.title("תרגול מילים ⏱️")

if 'quiz_active' not in st.session_state or not st.session_state.quiz_active:
    st.write("המקבץ מורכב ברובו ממילים שאתה לומד כרגע (80%) ומילים שסימנת כנלמדו (20%).")
    num_q = st.slider("כמה שאלות?", 5, 20, 10, 1)

    if st.button("🚀 התחל תרגול!", use_container_width=True):
        if generate_quiz(num_q):
            st.rerun()

    # כפתור חזור לדשבורד במסך הפתיחה
    if st.button("🏠 חזור לדשבורד", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")
else:
    q_index = st.session_state.current_q_index
    questions = st.session_state.quiz_questions

    # מסך סיום מבחן (מוצג בסוף המכסה או בלחיצה על כפתור סיום)
    if q_index >= len(questions):
        st.balloons()
        st.success(f"סיימת! הציון שלך: {st.session_state.score} מתוך {len(questions)}")
        if st.button("חזור לדשבורד"):
            st.session_state.quiz_active = False
            st.switch_page("pages/1_dashboard.py")
        st.stop()

    current_q = questions[q_index]
    st.progress(q_index / len(questions), text=f"שאלה {q_index + 1} מתוך {len(questions)}")

    st.markdown(f"### איך מתרגמים את המילה:")
    st.info(f"## {current_q['word'].capitalize()}")

    selected_option = st.radio("בחר תשובה:", current_q['options'], index=None, key=f"radio_{q_index}")

    st.write("---")

    # ניהול כפתורי הפעולה
    if not st.session_state.answered_current:
        if st.button("בדוק תשובה ✔️", use_container_width=True):
            if selected_option:
                st.session_state.answered_current = True
                is_correct = (selected_option == current_q['correct'])
                st.session_state.last_was_correct = is_correct

                if is_correct:
                    st.session_state.score += 1
                    if current_q['word'] in user_data.get("learning", {}):
                        user_data["learning"][current_q['word']]["score"] += 1
                        if user_data["learning"][current_q['word']]["score"] >= 6:
                            user_data["learned"].append(current_q['word'])
                            del user_data["learning"][current_q['word']]
                            st.toast(f"המילה {current_q['word']} הועברה לידועות! ⭐")
                else:
                    if selected_option != DONT_KNOW_STR and current_q['word'] in user_data.get("learning", {}):
                        user_data["learning"][current_q['word']]["score"] = max(0, user_data["learning"][
                            current_q['word']]["score"] - 1)

                save_user_data(user_data)
                st.rerun()
            else:
                st.warning("בחר תשובה קודם.")
    else:
        if st.session_state.last_was_correct:
            st.success("נכון מאוד! 🎉")
        else:
            st.error(f"לא נכון. התשובה היא: {current_q['correct']}")

        if st.button("לשאלה הבאה ➡️", use_container_width=True):
            st.session_state.answered_current = False
            st.session_state.current_q_index += 1
            st.rerun()

    # כפתורי עזר בתחתית המבחן הפעיל
    col_end, col_dash = st.columns(2)
    with col_end:
        if st.button("🏁 סיום מקבץ", use_container_width=True):
            # הקפצה למסך התוצאות על ידי הגדלת האינדקס
            st.session_state.current_q_index = len(questions)
            st.rerun()
    with col_dash:
        if st.button("🏠 חזור לדשבורד", use_container_width=True):
            st.session_state.quiz_active = False
            st.switch_page("pages/1_dashboard.py")