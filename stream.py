import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LibraX | Library Management",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* ---------- Main Background ---------- */

    .stApp {
        background: #0f172a;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }


    /* ---------- Headings ---------- */

    h1 {
        font-size: 2.4rem !important;
        font-weight: 700 !important;
    }

    h2 {
        font-weight: 650 !important;
    }

    h3 {
        font-weight: 600 !important;
    }


    /* ---------- Metric Cards ---------- */

    div[data-testid="metric-container"] {
        background: #172033;
        border: 1px solid #26344a;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.18);
    }


    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        border: none;
        font-weight: 600;
        min-height: 42px;
        transition: 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
    }


    /* ---------- Cards ---------- */

    .custom-card {
        background: #172033;
        border: 1px solid #26344a;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }


    .book-card {
        background: linear-gradient(
            135deg,
            #172033,
            #1d2940
        );
        border: 1px solid #334155;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 14px;
    }


    .book-title {
        font-size: 20px;
        font-weight: 700;
    }


    .book-author {
        color: #94a3b8;
        margin-top: 5px;
    }


    .book-id {
        color: #64748b;
        font-size: 13px;
    }


    /* ---------- Status ---------- */

    .available {
        color: #34d399;
        font-weight: 700;
    }

    .unavailable {
        color: #fb7185;
        font-weight: 700;
    }


    /* ---------- Hero ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #312e81,
            #4f46e5,
            #7c3aed
        );
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 15px 40px rgba(79,70,229,0.25);
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        color: white;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #e0e7ff;
        margin-top: 8px;
    }


    /* ---------- Sidebar Logo ---------- */

    .logo {
        font-size: 27px;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 5px;
    }

    .logo-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-bottom: 25px;
    }


    /* ---------- Divider ---------- */

    hr {
        border-color: #263244 !important;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

DATABASE = Path("library.json")


def generate_id(prefix="B"):

    random_id = "".join(
        random.choice(
            string.ascii_uppercase + string.digits
        )
        for _ in range(5)
    )

    return f"{prefix}-{random_id}"


def save_data(data):

    DATABASE.write_text(
        json.dumps(
            data,
            indent=4,
            default=str
        ),
        encoding="utf-8"
    )


def load_data():

    default_data = {
        "books": [],
        "members": []
    }

    if not DATABASE.exists():

        save_data(default_data)

        return default_data

    try:

        content = DATABASE.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return default_data

        data = json.loads(content)

    except Exception:

        return default_data


    # Fix old data if needed

    for member in data.get("members", []):

        if "borowed" in member and "borrowed" not in member:

            member["borrowed"] = member.pop("borowed")

        if "borrowed" not in member:

            member["borrowed"] = []


    return data


def current_time():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


data = load_data()


# ============================================================
# CALCULATIONS
# ============================================================

total_titles = len(data["books"])

total_copies = sum(
    book.get("total_copies", 0)
    for book in data["books"]
)

available_copies = sum(
    book.get("available_copies", 0)
    for book in data["books"]
)

borrowed_copies = (
    total_copies - available_copies
)

total_members = len(data["members"])

active_borrowers = sum(
    1
    for member in data["members"]
    if member.get("borrowed")
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="logo">📚 LibraX</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="logo-subtitle">'
        'Smart Library Management'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "📚 Books",
            "👥 Members",
            "🔄 Transactions"
        ],
        label_visibility="visible"
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div class="custom-card">
        <b>Library Status</b><br><br>
        📚 {total_titles} Book Titles<br>
        📦 {available_copies} Available<br>
        👥 {total_members} Members<br>
        🔄 {borrowed_copies} Borrowed
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("LibraX • Library Management System")


# ============================================================
# DASHBOARD
# ============================================================

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    # ---------- Hero Section ----------

   # ---------- Hero Section ----------

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                Welcome to LibraX 📚
            </div>
        </div>
        """,
        unsafe_allow_html=True
)


    # ---------- Statistics ----------

    st.markdown("### 📊 Library Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "📚 Book Titles",
            total_titles
        )

    with c2:
        st.metric(
            "📦 Total Copies",
            total_copies
        )

    with c3:
        st.metric(
            "🟢 Available Copies",
            available_copies
        )

    with c4:
        st.metric(
            "👥 Registered Members",
            total_members
        )


    st.markdown("---")


    # ---------- Library Status ----------

    st.markdown("### 📈 Library Status")

    col1, col2 = st.columns(2)


    # Available books

    with col1:

        if total_copies > 0:

            availability_percentage = (
                available_copies / total_copies
            ) * 100

        else:

            availability_percentage = 0


        st.markdown(
            """
            <div class="custom-card">
            <h3>📚 Book Availability</h3>
            """,
            unsafe_allow_html=True
        )


        st.progress(
            availability_percentage / 100
        )


        st.write(
            f"**{available_copies}** of "
            f"**{total_copies}** copies are currently available."
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # Borrowed books

    with col2:

        st.markdown(
            """
            <div class="custom-card">
            <h3>🔄 Borrowing Status</h3>
            """,
            unsafe_allow_html=True
        )


        st.write(
            f"📕 **{borrowed_copies}** "
            f"copies currently borrowed"
        )

        st.write(
            f"👤 **{active_borrowers}** "
            f"active borrowers"
        )

        st.write(
            f"👥 **{total_members}** "
            f"registered members"
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    st.markdown("---")


    # ---------- Empty / Initial State ----------

    if total_titles == 0 and total_members == 0:

        st.info(
            "📚 Your library is ready to use. "
            "Start by adding books and registering members."
        )

    else:

        st.success(
            "✅ Library system is running normally."
        )

# ============================================================
# BOOKS
# ============================================================

elif page == "📚 Books":

    st.title("📚 Book Management")

    add_tab, browse_tab = st.tabs(
        [
            "➕ Add Book",
            "🔎 Browse Books"
        ]
    )


    # --------------------------------------------------------
    # ADD BOOK
    # --------------------------------------------------------

    with add_tab:

        st.subheader(
            "Add a new book to the library"
        )

        with st.form("add_book_form"):

            c1, c2 = st.columns(2)

            with c1:

                title = st.text_input(
                    "Book Title",
                    placeholder="e.g. Python Crash Course"
                )

            with c2:

                author = st.text_input(
                    "Author",
                    placeholder="e.g. Eric Matthes"
                )


            copies = st.number_input(
                "Number of Copies",
                min_value=1,
                value=1,
                step=1
            )


            submitted = st.form_submit_button(
                "➕ Add Book",
                use_container_width=True
            )


        if submitted:

            if not title.strip():

                st.error(
                    "Please enter a book title."
                )

            elif not author.strip():

                st.error(
                    "Please enter the author name."
                )

            else:

                book = {

                    "id": generate_id("B"),

                    "title": title.strip(),

                    "author": author.strip(),

                    "total_copies": int(copies),

                    "available_copies": int(copies),

                    "added_on": current_time()
                }


                data["books"].append(book)

                save_data(data)

                st.success(
                    f"📚 '{title}' has been added successfully!"
                )

                st.rerun()


    # --------------------------------------------------------
    # BROWSE BOOKS
    # --------------------------------------------------------

    with browse_tab:

        st.subheader("Library Collection")

        if not data["books"]:

            st.info(
                "Your library is empty. Add your first book."
            )

        else:

            search = st.text_input(
                "🔎 Search books",
                placeholder="Search by title or author..."
            )


            availability = st.selectbox(
                "Filter",
                [
                    "All Books",
                    "Available",
                    "Unavailable"
                ]
            )


            books = data["books"]


            if search:

                search_lower = search.lower()

                books = [

                    book for book in books

                    if search_lower
                    in book["title"].lower()

                    or search_lower
                    in book["author"].lower()
                ]


            if availability == "Available":

                books = [
                    book for book in books
                    if book.get(
                        "available_copies", 0
                    ) > 0
                ]

            elif availability == "Unavailable":

                books = [
                    book for book in books
                    if book.get(
                        "available_copies", 0
                    ) == 0
                ]


            st.caption(
                f"Showing {len(books)} book(s)"
            )


            for book in books:

                available = book.get(
                    "available_copies", 0
                )

                total = book.get(
                    "total_copies", 0
                )


                if available > 0:

                    status_text = (
                        f"🟢 {available} available"
                    )

                else:

                    status_text = (
                        "🔴 Currently unavailable"
                    )


                st.markdown(
                    f"""
                    <div class="book-card">

                    <div class="book-title">
                    📖 {book['title']}
                    </div>

                    <div class="book-author">
                    Author: {book['author']}
                    </div>

                    <br>

                    <div class="book-id">
                    Book ID: {book['id']}
                    <br>
                    Copies: {available}/{total}
                    <br><br>
                    {status_text}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# MEMBERS
# ============================================================

elif page == "👥 Members":

    st.title("👥 Member Management")

    add_tab, members_tab = st.tabs(
        [
            "➕ Register Member",
            "👥 Member Directory"
        ]
    )


    # --------------------------------------------------------
    # ADD MEMBER
    # --------------------------------------------------------

    with add_tab:

        st.subheader(
            "Register a new library member"
        )

        with st.form("member_form"):

            name = st.text_input(
                "Full Name",
                placeholder="Enter member name"
            )

            email = st.text_input(
                "Email Address",
                placeholder="example@email.com"
            )


            submitted = st.form_submit_button(
                "👤 Register Member",
                use_container_width=True
            )


        if submitted:

            if not name.strip():

                st.error(
                    "Please enter member name."
                )

            elif not email.strip():

                st.error(
                    "Please enter email address."
                )

            elif "@" not in email:

                st.error(
                    "Please enter a valid email."
                )

            else:

                duplicate = any(

                    m["email"].lower()
                    == email.strip().lower()

                    for m in data["members"]
                )


                if duplicate:

                    st.error(
                        "A member with this email already exists."
                    )

                else:

                    member = {

                        "id": generate_id("M"),

                        "name": name.strip(),

                        "email": email.strip(),

                        "borrowed": []
                    }


                    data["members"].append(
                        member
                    )

                    save_data(data)

                    st.success(
                        f"👤 {name} registered successfully!"
                    )

                    st.rerun()


    # --------------------------------------------------------
    # MEMBER DIRECTORY
    # --------------------------------------------------------

    with members_tab:

        st.subheader("Member Directory")


        if not data["members"]:

            st.info(
                "No members registered yet."
            )

        else:

            search = st.text_input(
                "🔎 Search members",
                placeholder="Search by name or email..."
            )


            members = data["members"]


            if search:

                search_lower = search.lower()

                members = [

                    m for m in members

                    if search_lower
                    in m["name"].lower()

                    or search_lower
                    in m["email"].lower()
                ]


            for member in members:

                borrowed = member.get(
                    "borrowed", []
                )


                st.markdown(
                    f"""
                    <div class="custom-card">

                    <h3>
                    👤 {member['name']}
                    </h3>

                    📧 {member['email']}
                    <br>
                    🆔 {member['id']}
                    <br><br>

                    📕 Currently Borrowed:
                    <b>{len(borrowed)}</b>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                if borrowed:

                    with st.expander(
                        "View borrowed books"
                    ):

                        for book in borrowed:

                            st.write(
                                f"📖 **{book['title']}**"
                            )

                            st.caption(
                                f"Borrowed on: "
                                f"{book.get('borrow_on', '')}"
                            )


# ============================================================
# TRANSACTIONS
# ============================================================

elif page == "🔄 Transactions":

    st.title("🔄 Library Transactions")

    borrow_tab, return_tab = st.tabs(
        [
            "📕 Borrow Book",
            "📗 Return Book"
        ]
    )


    # ========================================================
    # BORROW
    # ========================================================

    with borrow_tab:

        st.subheader(
            "Issue a book to a member"
        )


        if not data["members"]:

            st.warning(
                "Please register a member first."
            )

        elif not data["books"]:

            st.warning(
                "Please add books first."
            )

        else:

            members = {

                f"{m['name']} — {m['id']}":
                m["id"]

                for m in data["members"]
            }


            available_books = [

                b for b in data["books"]

                if b.get(
                    "available_copies", 0
                ) > 0
            ]


            if not available_books:

                st.error(
                    "No books are currently available."
                )

            else:

                member_option = st.selectbox(
                    "👤 Select Member",
                    list(members.keys())
                )


                books = {

                    f"{b['title']} — "
                    f"{b['author']} "
                    f"({b['available_copies']} available)":
                    b["id"]

                    for b in available_books
                }


                book_option = st.selectbox(
                    "📖 Select Book",
                    list(books.keys())
                )


                if st.button(
                    "📕 Issue Book",
                    type="primary",
                    use_container_width=True
                ):

                    member_id = members[
                        member_option
                    ]

                    book_id = books[
                        book_option
                    ]


                    member = next(

                        m for m in data["members"]

                        if m["id"] == member_id
                    )


                    book = next(

                        b for b in data["books"]

                        if b["id"] == book_id
                    )


                    already_borrowed = any(

                        item["book_id"] == book_id

                        for item in member.get(
                            "borrowed", []
                        )
                    )


                    if already_borrowed:

                        st.error(
                            "This member already has this book."
                        )

                    else:

                        borrow_entry = {

                            "book_id":
                                book["id"],

                            "title":
                                book["title"],

                            "borrow_on":
                                current_time()
                        }


                        member.setdefault(
                            "borrowed", []
                        ).append(
                            borrow_entry
                        )


                        book["available_copies"] -= 1


                        save_data(data)


                        st.success(
                            f"📕 {book['title']} "
                            f"issued to {member['name']}!"
                        )


                        st.rerun()


    # ========================================================
    # RETURN
    # ========================================================

    with return_tab:

        st.subheader(
            "Return a borrowed book"
        )


        borrowers = [

            m for m in data["members"]

            if m.get("borrowed")
        ]


        if not borrowers:

            st.success(
                "🎉 No books are currently borrowed."
            )

        else:

            member_options = {

                f"{m['name']} — {m['id']}":
                m["id"]

                for m in borrowers
            }


            selected_member = st.selectbox(
                "👤 Select Member",
                list(member_options.keys()),
                key="return_member"
            )


            member_id = member_options[
                selected_member
            ]


            member = next(

                m for m in data["members"]

                if m["id"] == member_id
            )


            borrowed = member.get(
                "borrowed", []
            )


            book_options = {

                f"{b['title']} "
                f"({b['book_id']})":
                b["book_id"]

                for b in borrowed
            }


            selected_book = st.selectbox(
                "📖 Select Book",
                list(book_options.keys())
            )


            if st.button(
                "📗 Return Book",
                type="primary",
                use_container_width=True
            ):

                book_id = book_options[
                    selected_book
                ]


                selected = next(

                    item
                    for item in borrowed

                    if item["book_id"]
                    == book_id
                )


                member["borrowed"].remove(
                    selected
                )


                for book in data["books"]:

                    if book["id"] == book_id:

                        book["available_copies"] += 1

                        break


                save_data(data)


                st.success(
                    f"📗 {selected['title']} "
                    f"returned successfully!"
                )


                st.rerun()