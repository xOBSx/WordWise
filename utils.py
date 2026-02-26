import streamlit as st
from supabase import create_client, Client

# חיבור למסד הנתונים בעזרת המפתחות מה-Secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


def load_user_data(username):
    """טוענת נתוני משתמש מ-Supabase או יוצרת חדש"""
    try:
        response = supabase.table("users").select("data").eq("username", username).execute()

        if response.data:
            return response.data[0]['data']

        # יצירת מבנה בסיסי למשתמש חדש אם לא נמצא בבסיס הנתונים
        new_user = {
            "username": username,
            "learned": [],
            "learning": {},
            "restatements_solved": [],
            "sentence_completions_solved": []
        }
        save_user_data(new_user)
        return new_user
    except Exception as e:
        st.error(f"שגיאה בחיבור למסד הנתונים: {e}")
        return None


def save_user_data(user_data):
    """שומרת/מעדכנת את נתוני המשתמש ב-Supabase"""
    try:
        username = user_data["username"]
        # שימוש ב-upsert: מעדכן שורה קיימת או מוסיף חדשה לפי ה-username
        supabase.table("users").upsert({
            "username": username,
            "data": user_data
        }, on_conflict="username").execute()
    except Exception as e:
        st.error(f"שגיאה בשמירת הנתונים: {e}")