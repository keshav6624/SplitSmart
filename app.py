import streamlit as st
from db import init_db

st.set_page_config(page_title="Splitwise Pro", layout="wide")

init_db()

st.title("💸 Splitwise Pro")
st.write("Use sidebar to navigate")