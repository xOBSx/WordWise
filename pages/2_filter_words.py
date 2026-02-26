import streamlit as st
import pandas as pd
import random
from utils import save_user_data

st.set_page_config(page_title="סינון מילים", page_icon="🔍")

# הגנה על העמוד
if not st.session_state.get('logged_in'):
    st.warning("אנא התחבר דרך עמוד הבית.")
    st.stop()

user_data = st.session_state.user_data


@st.cache_data
def load_lexicon():
    # טעינת קובץ המילים מהתיקייה המקומית
    df = pd.read_csv("data/psychometry_words.csv")
    return df


df_full = load_lexicon()

st.title("סינון מילים חדשות 🔍")

# --- 1. בחירת רמה (Level) ---
available_levels = sorted(df_full['Level'].unique().tolist())
selected_level = st.selectbox("בחר רמת קושי לתרגול:", available_levels)

# הגדרת המילים שכבר ראינו (כדי לסנן אותן מהתור החדש)
seen_words = set(user_data.get("learned", [])) | set(user_data.get("learning", {}).keys())

# --- 2. לוגיקת ניהול תור המילים (תיקון ה-IndexError) ---
# אנחנו יוצרים תור של מילים (Strings) ולא אינדקסים מספריים
if 'filter_queue' not in st.session_state or st.session_state.get('last_level') != selected_level:
    # סינון ראשוני של מילים לרמה שנבחרה שטרם נראו
    level_df = df_full[df_full['Level'] == selected_level]
    remaining_words_df = level_df[~level_df['Word'].astype(str).str.lower().isin(seen_words)]

    # יצירת רשימת המילים וערבובה
    queue = remaining_words_df['Word'].tolist()
    random.shuffle(queue)

    st.session_state.filter_queue = queue
    st.session_state.current_filter_index = 0
    st.session_state.last_level = selected_level

# בדיקה אם התור ריק או שסיימנו אותו
if not st.session_state.filter_queue or st.session_state.current_filter_index >= len(st.session_state.filter_queue):
    st.balloons()
    st.success(f"כל הכבוד! סיימת את כל המילים ברמה {selected_level}! 🎉")
    if st.button("חזור לדשבורד 🏠", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")
    st.stop()

# שליפת המילה הנוכחית מתוך התור המעורבב
current_word = st.session_state.filter_queue[st.session_state.current_filter_index]

# שליפת נתוני המילה (תרגום) מתוך ה-DF המלא לפי המילה עצמה (בטוח לגמרי)
word_row = df_full[df_full['Word'] == current_word].iloc[0]
word = str(word_row['Word']).strip()
translation = str(word_row['Translation']).strip()

st.markdown(f"### המילה:")
st.info(f"## {word}")

with st.expander("לחץ כאן לצפייה בתרגום"):
    st.write(f"**תרגום:** {translation}")

# --- 3. מלל רמה וספירה מתחת לתרגום ---
remaining_count = len(st.session_state.filter_queue) - st.session_state.current_filter_index
st.write(f"רמה: {selected_level} | מילים שנותרו בתור הנוכחי: {remaining_count}")

st.write("---")
col1, col2, col3 = st.columns(3)


def next_word():
    """קידום האינדקס בתור ומעבר למילה הבאה"""
    st.session_state.current_filter_index += 1
    st.rerun()


with col1:
    if st.button("✅ יודע", use_container_width=True):
        if word.lower() not in user_data["learned"]:
            user_data["learned"].append(word.lower())
            save_user_data(user_data)  # שמירה לענן Supabase
        next_word()

with col2:
    if st.button("📖 רוצה ללמוד", use_container_width=True):
        user_data["learning"][word.lower()] = {"translation": translation, "score": 0}
        save_user_data(user_data)  # שמירה לענן Supabase
        next_word()

with col3:
    if st.button("⏭️ דלג", use_container_width=True):
        next_word()

if st.button("חזור לדשבורד 🏠", use_container_width=True):
    st.switch_page("pages/1_dashboard.py")