import streamlit as st
from db import Session, Space, Member

session = Session()

st.title("➕ Create Space")

# ---------------- SESSION STATE ----------------
if "members_input" not in st.session_state:
    st.session_state.members_input = [""]

space_name = st.text_input("Space Name")

# ---------------- MEMBERS ----------------
st.subheader("Members")

new_members = []

for i, m in enumerate(st.session_state.members_input):
    col1, col2 = st.columns([4, 1])

    with col1:
        name = st.text_input(f"Member {i+1}", value=m, key=f"m_{i}")
        new_members.append(name)

    with col2:
        if st.button("❌", key=f"del_{i}"):
            st.session_state.members_input.pop(i)
            st.rerun()

st.session_state.members_input = new_members

if st.button("➕ Add Member"):
    st.session_state.members_input.append("")
    st.rerun()

# ---------------- CREATE SPACE ----------------
if st.button("Create Space"):
    clean = [m.strip() for m in new_members if m.strip()]

    if not space_name:
        st.error("Enter space name")

    elif len(clean) < 2:
        st.error("At least 2 members required")

    elif len(set(clean)) != len(clean):
        st.error("Duplicate members not allowed")

    else:
        space = Space(name=space_name)
        session.add(space)
        session.commit()

        for m in clean:
            session.add(Member(name=m, space_id=space.id))

        session.commit()

        st.session_state.members_input = [""]
        st.success("✅ Space created!")