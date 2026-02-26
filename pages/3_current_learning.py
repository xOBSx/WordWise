import streamlit as st
import urllib.parse
from utils import save_user_data  # ייבוא פונקציית השמירה לענן

st.set_page_config(page_title="המילים שלי", page_icon="📚")

# --- 1. הגנת גישה ---
if not st.session_state.get('logged_in'):
    st.warning("אנא התחבר דרך העמוד הראשי.")
    st.stop()

user_data = st.session_state.user_data
learning_dict = user_data.get("learning", {})

st.title("המילים שאני לומד כרגע 🧠")

if not learning_dict:
    st.info("רשימת הלמידה שלך ריקה כרגע! סנן מילים חדשות כדי להתחיל ללמוד.")
    if st.button("🔍 למסך סינון המילים"):
        st.switch_page("pages/2_filter_words.py")
    st.stop()

st.write(
    f"היי {user_data['username'].capitalize()}, גלול למטה כדי לעבור על המילים שלך. השתמש בכפתור התמונה לרמז ויזואלי!")
st.write("---")

# --- 2. תצוגת רשימת המילים ---
# הפיכת המפתחות לרשימה כדי שנוכל לשנות את הדיקשנרי בזמן ריצה (במקרה של "למדתי")
word_keys = list(learning_dict.keys())

for word_key in word_keys:
    word_info = learning_dict[word_key]
    # וידוא שיש לנו את המילה המקורית להצגה
    original_word = word_info.get('original', word_key)

    # -- סידור הכותרת והכפתור בשורה אחת --
    col_text, col_img_btn = st.columns([0.8, 0.2])

    with col_text:
        st.subheader(f"🔹 {original_word.capitalize()}")

    with col_img_btn:
        # יצירת קישור לחיפוש תמונות בגוגל
        google_query = urllib.parse.quote(original_word)
        search_url = f"https://www.google.com/search?q={google_query}&tbm=isch"
        st.link_button("🖼️ תמונה", search_url, help="חפש תמונה בגוגל כרמז")

    # ניהול מפתח ייחודי לחשיפה (Session State)
    reveal_state_key = f"reveal_{word_key}"
    if reveal_state_key not in st.session_state:
        st.session_state[reveal_state_key] = False

    # אזור החשיפה והתרגול
    if not st.session_state[reveal_state_key]:
        if st.button("חשוף תרגום 👁️", key=f"btn_reveal_{word_key}", use_container_width=True):
            st.session_state[reveal_state_key] = True
            st.rerun()

    else:
        # אזור התוכן הגלוי
        st.info(f"**תרגום:** {word_info['translation']} | **רמה:** {word_info.get('level', '?')}")

        current_assoc = word_info.get("association", "")
        new_assoc = st.text_area(
            "אסוציאציה אישית:",
            value=current_assoc,
            placeholder="למשל: נשמע כמו המילה בעברית...",
            key=f"text_{word_key}"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 שמור אסוציאציה", key=f"save_{word_key}", use_container_width=True):
                user_data["learning"][word_key]["association"] = new_assoc
                save_user_data(user_data)  # שמירה לענן Supabase
                st.toast("האסוציאציה נשמרה בענן! ☁️")

        with col2:
            if st.button("✅ למדתי!", key=f"learned_{word_key}", use_container_width=True):
                # העברה מרשימת למידה לרשימת ידועים
                if word_key not in user_data["learned"]:
                    user_data["learned"].append(word_key)
                if word_key in user_data["learning"]:
                    del user_data["learning"][word_key]

                save_user_data(user_data)  # עדכון ה-Supabase
                st.session_state[reveal_state_key] = False
                st.rerun()

        if st.button("הסתר תרגום 🙈", key=f"hide_{word_key}", use_container_width=True):
            st.session_state[reveal_state_key] = False
            st.rerun()

    st.write("---")

if st.button("חזור לדשבורד 🏠", use_container_width=True):
    st.switch_page("pages/1_dashboard.py")