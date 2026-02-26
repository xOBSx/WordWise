import streamlit as st
from utils import load_user_data

# שינוי השם בחלונית הדפדפן ל-WordWise כדי להימנע מבעיות זכויות יוצרים
st.set_page_config(page_title="WordWise - התחברות", page_icon="🎓")


def main():
    # --- 1. אתחול משתני זיכרון (Session State) ---
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'user_data' not in st.session_state:
        st.session_state.user_data = None

    # --- 2. ממשק המשתמש ---

    # אם המשתמש לא מחובר, נציג דף כניסה נקי
    if not st.session_state.logged_in:
        st.title("ברוכים הבאים ל-WordWise 🧠")
        st.write("הכנס שם משתמש כדי להתחבר (הנתונים נשמרים בענן של Supabase):")

        with st.form("login_form"):
            username_input = st.text_input("שם משתמש (ללא רווחים):")
            submitted = st.form_submit_button("היכנס")

            if submitted:
                clean_username = username_input.strip().lower()
                if clean_username:
                    with st.spinner("מתחבר למסד הנתונים..."):
                        data = load_user_data(clean_username)
                        if data:
                            st.session_state.user_data = data
                            st.session_state.logged_in = True
                            st.switch_page("pages/1_dashboard.py")
                else:
                    st.error("אנא הכנס שם משתמש חוקי.")

    # אם המשתמש מחובר, נציג לו את הברכה והדשבורד
    else:
        # כאן בטוח להשתמש ב-user_data כי אנחנו אחרי בדיקת ה-logged_in
        username = st.session_state.user_data['username'].capitalize()
        st.title(f"Hey {username}, Welcome back! 🚀")

        st.success(f"אתה מחובר כ- {username}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("עבור לדשבורד 📊", use_container_width=True):
                st.switch_page("pages/1_dashboard.py")

        with col2:
            if st.button("התנתק 🚪", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_data = None
                st.rerun()


if __name__ == "__main__":
    main()