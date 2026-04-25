import streamlit as st
from db import Session, Space, Member, Expense, ExpenseSplit
from datetime import datetime
import pandas as pd

session = Session()

st.set_page_config(layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.block-container { padding-top: 2rem; }

.card {
    padding: 1.2rem;
    border-radius: 12px;
    background-color: #1e1e1e;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    margin-bottom: 1rem;
}

.section-title {
    font-size: 18px;
    font-weight: 600;
}

.small-text {
    color: gray;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Manage Space")

# ---------------- SETTLE UP ----------------
def settle_up(balances):
    debtors, creditors = [], []

    for p, amt in balances.items():
        if amt > 0:
            debtors.append([p, amt])
        elif amt < 0:
            creditors.append([p, -amt])

    i, j = 0, 0
    txns = []

    while i < len(debtors) and j < len(creditors):
        d, da = debtors[i]
        c, ca = creditors[j]

        pay = min(da, ca)
        txns.append(f"{d} pays ₹{round(pay,2)} to {c}")

        debtors[i][1] -= pay
        creditors[j][1] -= pay

        if debtors[i][1] == 0: i += 1
        if creditors[j][1] == 0: j += 1

    return txns

# ---------------- SELECT SPACE ----------------
spaces = session.query(Space).all()

if not spaces:
    st.warning("No spaces available.")
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

# ---------------- DELETE SPACE ----------------
st.sidebar.subheader("⚠️ Danger Zone")

if st.sidebar.button("🗑️ Delete Space"):
    for e in expenses:
        session.query(ExpenseSplit).filter_by(expense_id=e.id).delete()

    session.query(Member).filter_by(space_id=space.id).delete()
    session.query(Expense).filter_by(space_id=space.id).delete()
    session.delete(space)

    session.commit()
    st.rerun()

# ---------------- ADD EXPENSE ----------------
st.markdown("## ➕ Add Expense")

col1, col2 = st.columns(2)

with col1:
    title = st.text_input("Title")
    amount = st.number_input("Amount", min_value=0.0)

with col2:
    date = st.date_input("Date", datetime.today())
    split_type = st.selectbox("Split Type", ["Equal", "Custom", "Selected Members (Equal)"])

custom_split = {}
selected_members = member_names

if split_type == "Selected Members (Equal)":
    selected_members = st.multiselect("Select members", member_names, default=member_names)

elif split_type == "Custom":
    total = 0
    for m in member_names:
        val = st.number_input(f"{m}", min_value=0.0, key=f"s_{m}")
        custom_split[m] = val
        total += val

    if total != amount:
        st.warning("Split must equal total")

# SAVE
if st.button("Add Expense"):
    if not title:
        st.error("Enter title")

    elif amount <= 0:
        st.error("Invalid amount")

    elif split_type == "Selected Members (Equal)" and len(selected_members) == 0:
        st.error("Select at least one member")

    else:
        exp = Expense(title=title, amount=amount, space_id=space.id, date=date)
        session.add(exp)
        session.commit()

        if split_type == "Custom":
            for m, val in custom_split.items():
                session.add(ExpenseSplit(expense_id=exp.id, member_name=m, amount=val))

        elif split_type == "Selected Members (Equal)":
            equal = amount / len(selected_members)
            for m in member_names:
                val = equal if m in selected_members else 0
                session.add(ExpenseSplit(expense_id=exp.id, member_name=m, amount=val))

        else:
            equal = amount / len(member_names)
            for m in member_names:
                session.add(ExpenseSplit(expense_id=exp.id, member_name=m, amount=equal))

        session.commit()
        st.success("✅ Expense added!")
        st.rerun()

# ---------------- EXPENSE TABLE ----------------
st.markdown("## 📋 Expense History")

if expenses:
    data = [{
        "ID": e.id,
        "Title": e.title,
        "Amount": e.amount,
        "Date": e.date
    } for e in expenses]

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, height=300)

# ---------------- MEMBER BREAKDOWN ----------------
st.markdown("## 💵 Member Breakdown")

cols = st.columns(len(member_names))

for i, m in enumerate(member_names):
    with cols[i]:
        total = 0
        details = []

        for e in expenses:
            splits = session.query(ExpenseSplit).filter_by(expense_id=e.id).all()

            for s in splits:
                if s.member_name == m and s.amount > 0:
                    details.append(f"{e.title} → ₹{round(s.amount,2)}")
                    total += s.amount

        st.markdown(f"""
        <div class="card">
            <div class="section-title">{m}</div>
            <div class="small-text">
                {"<br>".join(details) if details else "No expenses"}
            </div>
            <hr>
            <b>Total: ₹{round(total,2)}</b>
        </div>
        """, unsafe_allow_html=True)

# ---------------- SETTLE UP ----------------
st.markdown("## 🤝 Settle Up")

balances = {m: 0 for m in member_names}

for e in expenses:
    splits = session.query(ExpenseSplit).filter_by(expense_id=e.id).all()
    for s in splits:
        balances[s.member_name] += s.amount

txns = settle_up(balances)

if txns:
    for t in txns:
        st.markdown(f'<div class="card">💸 {t}</div>', unsafe_allow_html=True)
else:
    st.success("All settled 🎉")

# ---------------- MEMBER SPECIFIC REPORT ----------------
st.markdown("## 👤 Personal Report")

selected_person = st.selectbox("Select Member", member_names, key="report_user")

if selected_person:

    personal_summary = f"*📊 Personal Expense Report - {selected_person} ({space.name})*\n\n"

    total = 0

    personal_summary += "📋 Your Expenses:\n"

    for e in expenses:
        splits = session.query(ExpenseSplit).filter_by(expense_id=e.id).all()

        for s in splits:
            if s.member_name == selected_person and s.amount > 0:
                personal_summary += f"- {e.title}: ₹{round(s.amount,2)}\n"
                total += s.amount

    personal_summary += f"\n💵 Total: ₹{round(total,2)}\n"
    # ---------------- UI ----------------
    st.text_area("Copy Personal Report", personal_summary, height=250)

    st.download_button(
        label="📥 Download Personal Report",
        data=personal_summary,
        file_name=f"{selected_person}_report.txt",
        mime="text/plain"
    )

# ---------------- CHART ----------------
st.markdown("## 📊 Expense Chart")

if expenses:
    df_chart = pd.DataFrame(data)
    st.bar_chart(df_chart.set_index("Date")["Amount"])