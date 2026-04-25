import streamlit as st
from db import Session, Space, Member, Expense

session = Session()

st.set_page_config(layout="wide")

st.title("📊 Dashboard")

spaces = session.query(Space).all()

if not spaces:
    st.warning("No spaces yet")
    st.stop()

selected = st.selectbox("Select Space", [s.name for s in spaces])
space = session.query(Space).filter_by(name=selected).first()

members = session.query(Member).filter_by(space_id=space.id).all()
expenses = session.query(Expense).filter_by(space_id=space.id).all()

member_names = [m.name for m in members]

# ---------------- OVERVIEW ----------------
st.markdown("## 📊 Overview")

total_expense = sum(e.amount for e in expenses)

col1, col2 = st.columns(2)

col1.metric("Total Expenses", f"₹{round(total_expense,2)}")
col2.metric("Members", len(member_names))

# ---------------- MEMBERS ----------------
st.markdown("## 👥 Members")

cols = st.columns(len(member_names))

for i, m in enumerate(member_names):
    cols[i].markdown(f"""
    <div style='padding:10px; background:#1e1e1e; border-radius:10px; text-align:center'>
        {m}
    </div>
    """, unsafe_allow_html=True)

# ---------------- EXPENSES ----------------
st.markdown("## 📋 Expenses")

if expenses:
    data = [{
        "Title": e.title,
        "Amount": e.amount,
        "Date": e.date
    } for e in expenses]

    st.dataframe(data, use_container_width=True)

else:
    st.info("No expenses yet")