import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="LibraX | Smart Library Management",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
<style>
.stApp { background: #0b1120; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1450px; }
section[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #263244; }
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

h1 { font-size: 2.35rem !important; font-weight: 800 !important; }
h2 { font-weight: 750 !important; }
h3 { font-weight: 650 !important; }

.logo { font-size: 28px; font-weight: 850; color: white; text-align: center; margin-bottom: 4px; }
.logo-subtitle { text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 22px; }

.hero {
    background: linear-gradient(135deg, #312e81 0%, #4f46e5 55%, #7c3aed 100%);
    padding: 30px 32px;
    border-radius: 22px;
    margin-bottom: 24px;
    box-shadow: 0 18px 50px rgba(79,70,229,.22);
}
.hero-title { font-size: 34px; font-weight: 850; color: white; }
.hero-subtitle { font-size: 16px; color: #e0e7ff; margin-top: 7px; max-width: 760px; }
.hero-badge { display:inline-block; margin-top:16px; padding:7px 12px; border-radius:999px; background:rgba(255,255,255,.13); color:#eef2ff; font-size:13px; }

.metric-card {
    background: linear-gradient(145deg, #172033, #111827);
    border: 1px solid #26344a;
    border-radius: 17px;
    padding: 19px;
    min-height: 115px;
    box-shadow: 0 8px 28px rgba(0,0,0,.14);
}
.metric-label { color:#94a3b8; font-size:13px; font-weight:600; }
.metric-value { color:#f8fafc; font-size:28px; font-weight:800; margin-top:5px; }
.metric-note { color:#64748b; font-size:12px; margin-top:4px; }

.custom-card, .book-card {
    background: #111b2e;
    border: 1px solid #26344a;
    border-radius: 17px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 8px 26px rgba(0,0,0,.13);
}
.book-card { background: linear-gradient(145deg, #172033, #111827); }
.book-title { font-size:20px; font-weight:750; color:#f8fafc; }
.book-author { color:#94a3b8; margin-top:5px; }
.book-id { color:#64748b; font-size:12px; }
.available { color:#34d399; font-weight:700; }
.unavailable { color:#fb7185; font-weight:700; }
.alert-card { border-left: 4px solid #f59e0b; background:#241c0d; }
.success-card { border-left: 4px solid #10b981; background:#0b211b; }
.insight-card { border-left: 4px solid #818cf8; background:linear-gradient(135deg,#141d38,#111827); }
.activity-row { padding:10px 0; border-bottom:1px solid #263244; }
.activity-row:last-child { border-bottom:none; }
.small-muted { color:#64748b; font-size:12px; }

.stButton > button { border-radius:10px; min-height:42px; font-weight:650; transition:.18s; }
.stButton > button:hover { transform:translateY(-2px); }

div[data-testid="stMetric"] { background:#172033; border:1px solid #26344a; border-radius:16px; padding:16px; }
hr { border-color:#263244 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATABASE
# ============================================================
DATABASE = Path("library.json")
LOAN_DAYS = 7


def generate_id(prefix="B"):
    random_id = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return f"{prefix}-{random_id}"


def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            return None


def save_data(data):
    DATABASE.write_text(json.dumps(data, indent=4, default=str), encoding="utf-8")


def load_data():
    default_data = {"books": [], "members": [], "transactions": []}

    if not DATABASE.exists():
        save_data(default_data)
        return default_data

    try:
        content = DATABASE.read_text(encoding="utf-8").strip()
        if not content:
            return default_data
        data = json.loads(content)
    except Exception:
        return default_data

    data.setdefault("books", [])
    data.setdefault("members", [])
    data.setdefault("transactions", [])

    # Compatibility with older versions of the project.
    for member in data["members"]:
        if "borowed" in member and "borrowed" not in member:
            member["borrowed"] = member.pop("borowed")
        member.setdefault("borrowed", [])

        # Add due dates to old borrowed records if missing.
        for item in member["borrowed"]:
            if "borrow_on" not in item:
                item["borrow_on"] = current_time()
            if "due_date" not in item:
                dt = parse_dt(item["borrow_on"]) or datetime.now()
                item["due_date"] = (dt + timedelta(days=LOAN_DAYS)).strftime("%Y-%m-%d %H:%M:%S")

    return data


def add_transaction(data, action, member, book, details=""):
    data.setdefault("transactions", []).append(
        {
            "id": generate_id("T"),
            "action": action,
            "member_id": member.get("id", ""),
            "member_name": member.get("name", ""),
            "book_id": book.get("id", book.get("book_id", "")),
            "book_title": book.get("title", ""),
            "timestamp": current_time(),
            "details": details,
        }
    )


def overdue_items(data):
    now = datetime.now()
    results = []
    for member in data["members"]:
        for item in member.get("borrowed", []):
            due = parse_dt(item.get("due_date"))
            if due and due < now:
                results.append(
                    {
                        "member": member,
                        "item": item,
                        "days": max(1, (now.date() - due.date()).days),
                    }
                )
    return results


# ============================================================
# LOAD DATA + CALCULATIONS
# ============================================================
data = load_data()

total_titles = len(data["books"])
total_copies = sum(int(b.get("total_copies", 0)) for b in data["books"])
available_copies = sum(int(b.get("available_copies", 0)) for b in data["books"])
borrowed_copies = max(0, total_copies - available_copies)
total_members = len(data["members"])
active_borrowers = sum(1 for m in data["members"] if m.get("borrowed"))
overdues = overdue_items(data)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="logo">📚 LibraX</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-subtitle">Smart Library Management</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "MAIN MENU",
        ["🏠 Dashboard", "📚 Books", "👥 Members", "🔄 Transactions"],
    )

    st.markdown("---")
    st.markdown(
        f"""
        <div class="custom-card">
            <b>Library Status</b><br><br>
            📚 {total_titles} Book Titles<br>
            📦 {available_copies} Available<br>
            👥 {total_members} Members<br>
            🔄 {borrowed_copies} Borrowed<br>
            ⚠️ {len(overdues)} Overdue
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("LibraX • Smart Library Management")

# ============================================================
# DASHBOARD
# ============================================================
if page == "🏠 Dashboard":
    availability_pct = (available_copies / total_copies * 100) if total_copies else 0
    utilization_pct = (borrowed_copies / total_copies * 100) if total_copies else 0

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Welcome to LibraX 📚</div>
            <div class="hero-subtitle">A smarter way to manage books, members and library activity — all from one place.</div>
            <div class="hero-badge">✨ Smart Library Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 Library Overview")
    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (c1, "📚 Book Titles", total_titles, "Unique titles in collection"),
        (c2, "📦 Total Copies", total_copies, "Physical copies"),
        (c3, "🔄 Borrowed", borrowed_copies, f"{utilization_pct:.1f}% utilization"),
        (c4, "👥 Members", total_members, f"{active_borrowers} active borrowers"),
    ]
    for col, label, value, note in metrics:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Alerts + availability
    left, right = st.columns([1.05, 1])

    with left:
        st.markdown("### ⚠️ Attention Needed")
        if overdues:
            for item in overdues[:5]:
                st.markdown(
                    f"""
                    <div class="custom-card alert-card">
                        <b>📕 {item['item']['title']}</b><br>
                        👤 {item['member']['name']}<br>
                        <span class="small-muted">Overdue by {item['days']} day(s) • Due {item['item'].get('due_date','')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if len(overdues) > 5:
                st.caption(f"+ {len(overdues) - 5} more overdue book(s)")
        elif total_titles:
            st.markdown(
                '<div class="custom-card success-card"><b>🎉 Everything is on track</b><br>No overdue books are currently detected.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Add books and members to start tracking library activity.")

    with right:
        st.markdown("### 📈 Library Utilization")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.write(f"**Available:** {available_copies} / {total_copies} copies")
        st.progress(min(availability_pct / 100, 1.0))
        st.caption(f"{availability_pct:.1f}% of copies are currently available")
        st.write(f"**Borrowed:** {borrowed_copies} / {total_copies} copies")
        st.progress(min(utilization_pct / 100, 1.0))
        st.caption(f"{utilization_pct:.1f}% of the collection is currently in use")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    chart_col, activity_col = st.columns([1.15, 1])

    with chart_col:
        st.markdown("### 📊 Collection Status")
        if total_copies:
            st.bar_chart(
                {"Copies": {"Available": available_copies, "Borrowed": borrowed_copies}},
                height=260,
            )
        else:
            st.info("No collection data available yet.")

    with activity_col:
        st.markdown("### 🕐 Recent Activity")
        transactions = list(reversed(data.get("transactions", [])))
        if transactions:
            for tx in transactions[:7]:
                icon = "📕" if tx.get("action") == "Borrow" else "📗" if tx.get("action") == "Return" else "👤"
                st.markdown(
                    f"""
                    <div class="activity-row">
                        {icon} <b>{tx.get('action','Activity')}</b> — {tx.get('book_title','') or tx.get('member_name','')}<br>
                        <span class="small-muted">{tx.get('member_name','')} • {tx.get('timestamp','')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No transactions recorded yet.")

    st.markdown("---")
    insight_col, popular_col = st.columns([1, 1])

    with insight_col:
        st.markdown("### 🤖 Smart Library Insights")
        if total_copies == 0:
            st.markdown(
                '<div class="custom-card insight-card">💡 Add your first book to start generating library insights.</div>',
                unsafe_allow_html=True,
            )
        else:
            insight_lines = []
            if utilization_pct >= 70:
                insight_lines.append("🔥 A large share of your collection is currently in use.")
            elif utilization_pct <= 20:
                insight_lines.append("💡 Most copies are available — consider promoting the collection.")
            else:
                insight_lines.append("📚 The collection has a balanced availability level.")
            if overdues:
                insight_lines.append(f"⚠️ {len(overdues)} overdue borrowing record(s) need attention.")
            if total_members:
                insight_lines.append(f"👥 {active_borrowers} member(s) currently have books issued.")
            insight_lines.append(f"📦 {available_copies} physical copy/copies are ready to borrow.")
            st.markdown('<div class="custom-card insight-card">' + "<br><br>".join(insight_lines) + "</div>", unsafe_allow_html=True)

    with popular_col:
        st.markdown("### 🔥 Popular Books")
        borrow_counts = Counter(tx.get("book_title") for tx in data.get("transactions", []) if tx.get("action") == "Borrow")
        popular = [(title, count) for title, count in borrow_counts.most_common(5) if title]
        if popular:
            for rank, (title, count) in enumerate(popular, 1):
                st.markdown(
                    f'<div class="activity-row"><b>#{rank} {title}</b><br><span class="small-muted">{count} borrow(s) recorded</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Borrow a book to begin building popularity insights.")

# ============================================================
# BOOKS
# ============================================================
elif page == "📚 Books":
    st.title("📚 Book Management")
    add_tab, browse_tab = st.tabs(["➕ Add Book", "🔎 Browse Books"])

    with add_tab:
        st.subheader("Add a new book to the library")
        with st.form("add_book_form"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Book Title", placeholder="e.g. Python Crash Course")
            with c2:
                author = st.text_input("Author", placeholder="e.g. Eric Matthes")
            copies = st.number_input("Number of Copies", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("➕ Add Book", use_container_width=True, type="primary")

        if submitted:
            if not title.strip():
                st.error("Please enter a book title.")
            elif not author.strip():
                st.error("Please enter the author name.")
            else:
                book = {
                    "id": generate_id("B"),
                    "title": title.strip(),
                    "author": author.strip(),
                    "total_copies": int(copies),
                    "available_copies": int(copies),
                    "added_on": current_time(),
                }
                data["books"].append(book)
                save_data(data)
                st.success(f"📚 '{title}' has been added successfully!")
                st.rerun()

    with browse_tab:
        st.subheader("Library Collection")
        if not data["books"]:
            st.info("Your library is empty. Add your first book.")
        else:
            c1, c2 = st.columns([2, 1])
            with c1:
                search = st.text_input("🔎 Search books", placeholder="Search by title or author...")
            with c2:
                availability = st.selectbox("Filter", ["All Books", "Available", "Unavailable"])

            books = data["books"]
            if search:
                s = search.lower()
                books = [b for b in books if s in b["title"].lower() or s in b["author"].lower()]
            if availability == "Available":
                books = [b for b in books if b.get("available_copies", 0) > 0]
            elif availability == "Unavailable":
                books = [b for b in books if b.get("available_copies", 0) == 0]

            st.caption(f"Showing {len(books)} book(s)")
            for book in books:
                available = book.get("available_copies", 0)
                total = book.get("total_copies", 0)
                status = f'<span class="available">🟢 {available} available</span>' if available else '<span class="unavailable">🔴 Currently unavailable</span>'
                st.markdown(
                    f"""
                    <div class="book-card">
                        <div class="book-title">📖 {book['title']}</div>
                        <div class="book-author">Author: {book['author']}</div><br>
                        <div class="book-id">Book ID: {book['id']}<br>Copies: {available}/{total}<br><br>{status}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ============================================================
# MEMBERS
# ============================================================
elif page == "👥 Members":
    st.title("👥 Member Management")
    add_tab, members_tab = st.tabs(["➕ Register Member", "👥 Member Directory"])

    with add_tab:
        st.subheader("Register a new library member")
        with st.form("member_form"):
            name = st.text_input("Full Name", placeholder="Enter member name")
            email = st.text_input("Email Address", placeholder="example@email.com")
            submitted = st.form_submit_button("👤 Register Member", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("Please enter member name.")
            elif not email.strip():
                st.error("Please enter email address.")
            elif "@" not in email:
                st.error("Please enter a valid email.")
            elif any(m["email"].lower() == email.strip().lower() for m in data["members"]):
                st.error("A member with this email already exists.")
            else:
                member = {"id": generate_id("M"), "name": name.strip(), "email": email.strip(), "borrowed": []}
                data["members"].append(member)
                save_data(data)
                st.success(f"👤 {name} registered successfully!")
                st.rerun()

    with members_tab:
        st.subheader("Member Directory")
        if not data["members"]:
            st.info("No members registered yet.")
        else:
            search = st.text_input("🔎 Search members", placeholder="Search by name or email...")
            members = data["members"]
            if search:
                s = search.lower()
                members = [m for m in members if s in m["name"].lower() or s in m["email"].lower()]

            for member in members:
                borrowed = member.get("borrowed", [])
                member_overdue = sum(1 for x in borrowed if (parse_dt(x.get("due_date")) or datetime.now()) < datetime.now())
                st.markdown(
                    f"""
                    <div class="custom-card">
                        <h3>👤 {member['name']}</h3>
                        📧 {member['email']}<br>
                        🆔 {member['id']}<br><br>
                        📕 Currently Borrowed: <b>{len(borrowed)}</b>
                        &nbsp;&nbsp; ⚠️ Overdue: <b>{member_overdue}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if borrowed:
                    with st.expander("View borrowed books"):
                        for item in borrowed:
                            due = item.get("due_date", "Not set")
                            overdue_label = " ⚠️ OVERDUE" if parse_dt(due) and parse_dt(due) < datetime.now() else ""
                            st.write(f"📖 **{item['title']}**{overdue_label}")
                            st.caption(f"Borrowed: {item.get('borrow_on','')} • Due: {due}")

# ============================================================
# TRANSACTIONS
# ============================================================
elif page == "🔄 Transactions":
    st.title("🔄 Library Transactions")
    borrow_tab, return_tab, history_tab = st.tabs(["📕 Borrow Book", "📗 Return Book", "📜 Transaction History"])

    with borrow_tab:
        st.subheader("Issue a book to a member")
        if not data["members"]:
            st.warning("Please register a member first.")
        elif not data["books"]:
            st.warning("Please add books first.")
        else:
            member_options = {f"{m['name']} — {m['id']}": m["id"] for m in data["members"]}
            available_books = [b for b in data["books"] if b.get("available_copies", 0) > 0]
            if not available_books:
                st.error("No books are currently available.")
            else:
                member_option = st.selectbox("👤 Select Member", list(member_options.keys()))
                book_options = {f"{b['title']} — {b['author']} ({b['available_copies']} available)": b["id"] for b in available_books}
                book_option = st.selectbox("📖 Select Book", list(book_options.keys()))
                loan_days = st.number_input("Loan Period (days)", min_value=1, max_value=60, value=LOAN_DAYS)

                if st.button("📕 Issue Book", type="primary", use_container_width=True):
                    member = next(m for m in data["members"] if m["id"] == member_options[member_option])
                    book = next(b for b in data["books"] if b["id"] == book_options[book_option])
                    already_borrowed = any(x["book_id"] == book["id"] for x in member.get("borrowed", []))

                    if already_borrowed:
                        st.error("This member already has this book.")
                    else:
                        borrowed_at = datetime.now()
                        due_date = borrowed_at + timedelta(days=int(loan_days))
                        borrow_entry = {
                            "book_id": book["id"],
                            "title": book["title"],
                            "borrow_on": borrowed_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "due_date": due_date.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        member.setdefault("borrowed", []).append(borrow_entry)
                        book["available_copies"] -= 1
                        add_transaction(data, "Borrow", member, book, f"Due on {due_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        save_data(data)
                        st.success(f"📕 {book['title']} issued to {member['name']}! Due: {due_date.strftime('%d %b %Y')}")
                        st.rerun()

    with return_tab:
        st.subheader("Return a borrowed book")
        borrowers = [m for m in data["members"] if m.get("borrowed")]
        if not borrowers:
            st.success("🎉 No books are currently borrowed.")
        else:
            member_options = {f"{m['name']} — {m['id']}": m["id"] for m in borrowers}
            selected_member = st.selectbox("👤 Select Member", list(member_options.keys()), key="return_member")
            member = next(m for m in data["members"] if m["id"] == member_options[selected_member])
            borrowed = member.get("borrowed", [])
            book_options = {f"{b['title']} ({b['book_id']})": b["book_id"] for b in borrowed}
            selected_book = st.selectbox("📖 Select Book", list(book_options.keys()))

            if st.button("📗 Return Book", type="primary", use_container_width=True):
                book_id = book_options[selected_book]
                selected = next(item for item in borrowed if item["book_id"] == book_id)
                member["borrowed"].remove(selected)
                book = next((b for b in data["books"] if b["id"] == book_id), None)
                if book:
                    book["available_copies"] += 1
                    add_transaction(data, "Return", member, book, f"Borrowed on {selected.get('borrow_on','')} and due on {selected.get('due_date','')}" )
                save_data(data)
                st.success(f"📗 {selected['title']} returned successfully!")
                st.rerun()

    with history_tab:
        st.subheader("📜 Transaction History")
        transactions = list(reversed(data.get("transactions", [])))
        if not transactions:
            st.info("No transaction history is available yet. Borrow or return a book to create activity records.")
        else:
            for tx in transactions:
                icon = "📕" if tx.get("action") == "Borrow" else "📗" if tx.get("action") == "Return" else "👤"
                st.markdown(
                    f"""
                    <div class="custom-card">
                        <b>{icon} {tx.get('action','Activity')}</b> — {tx.get('book_title','')}<br>
                        👤 {tx.get('member_name','')}<br>
                        🕐 {tx.get('timestamp','')}<br>
                        <span class="small-muted">{tx.get('details','')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
