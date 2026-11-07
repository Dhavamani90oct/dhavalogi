import streamlit as st
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

# Initialize database in session state if it doesn't exist
if "books" not in st.session_state:
    st.session_state.books = [
        {"Book ID": "B001", "Title": "The Great Gatsby", "Author": "F. Scott Fitzgerald", "Total Copies": 5, "Available Copies": 5},
        {"Book ID": "B002", "Title": "To Kill a Mockingbird", "Author": "Harper Lee", "Total Copies": 3, "Available Copies": 2},
        {"Book ID": "B003", "Title": "1984", "Author": "George Orwell", "Total Copies": 4, "Available Copies": 4},
    ]

if "records" not in st.session_state:
    st.session_state.records = [
        {"Student Name": "John Doe", "Student ID": "S101", "Book ID": "B002", "Book Title": "To Kill a Mockingbird", "Issue Date": "2026-11-01", "Status": "Issued"}
    ]

# Application Header
st.title("📚 Library Management System")
st.markdown("---")

# Sidebar navigation
menu = ["Dashboard & View Books", "Add New Book", "Search Books", "Issue Book", "Return Book", "Borrowing Records"]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# Helper function to get book by ID
def get_book(book_id):
    for book in st.session_state.books:
        if book["Book ID"] == book_id:
            return book
    return None

# --- MODULE 1: DASHBOARD & VIEW BOOKS ---
if choice == "Dashboard & View Books":
    st.header("📋 Library Inventory Dashboard")
    
    # Metrics
    total_books_types = len(st.session_state.books)
    total_physical_books = sum(book["Total Copies"] for book in st.session_state.books)
    total_issued = sum(1 for r in st.session_state.records if r["Status"] == "Issued")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Unique Titles", total_books_types)
    col2.metric("Total Physical Copies", total_physical_books)
    col3.metric("Currently Issued", total_issued)
    
    st.subheader("Current Book Catalog")
    if st.session_state.books:
        df_books = pd.DataFrame(st.session_state.books)
        st.dataframe(df_books, use_container_width=True, hide_index=True)
    else:
        st.info("The library catalog is currently empty.")

# --- MODULE 2: ADD NEW BOOK ---
elif choice == "Add New Book":
    st.header("➕ Add a New Book to Catalog")
    
    with st.form("add_book_form", clear_on_submit=True):
        book_id = st.text_input("Book ID (Unique)", placeholder="e.g., B004").strip()
        title = st.text_input("Book Title", placeholder="e.g., Moby Dick").strip()
        author = st.text_input("Author Name", placeholder="e.g., Herman Melville").strip()
        copies = st.number_input("Total Copies", min_value=1, value=1, step=1)
        
        submit_btn = st.form_submit_button("Add Book")
        
        if submit_btn:
            if not book_id or not title or not author:
                st.error("⚠️ All fields are mandatory!")
            elif get_book(book_id):
                st.error(f"⚠️ A book with ID '{book_id}' already exists!")
            else:
                new_book = {
                    "Book ID": book_id,
                    "Title": title,
                    "Author": author,
                    "Total Copies": copies,
                    "Available Copies": copies
                }
                st.session_state.books.append(new_book)
                st.success(f"🎉 Success: '{title}' has been added to the library!")

# --- MODULE 3: SEARCH BOOKS ---
elif choice == "Search Books":
    st.header("🔍 Search Book Inventory")
    
    search_query = st.text_input("Enter Book Title, Author, or Book ID to search:").strip().lower()
    
    if search_query:
        results = [
            b for b in st.session_state.books 
            if search_query in b["Book ID"].lower() or 
               search_query in b["Title"].lower() or 
               search_query in b["Author"].lower()
        ]
        
        if results:
            st.write(f"Found {len(results)} match(es):")
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        else:
            st.warning("No matches found for your query.")
    else:
        st.info("Type a query above to filter the system data.")

# --- MODULE 4: ISSUE BOOK ---
elif choice == "Issue Book":
    st.header("📤 Issue a Book to a Student")
    
    # Dynamic selection of available books
    available_books = [b for b in st.session_state.books if b["Available Copies"] > 0]
    
    if not available_books:
        st.warning("⚠️ No books are currently available for issuing.")
    else:
        book_options = {f"{b['Book ID']} - {b['Title']} ({b['Available Copies']} left)": b['Book ID'] for b in available_books}
        selected_book_str = st.selectbox("Select Book to Issue", list(book_options.keys()))
        selected_book_id = book_options[selected_book_str]
        
        with st.form("issue_form", clear_on_submit=True):
            student_name = st.text_input("Student Name").strip()
            student_id = st.text_input("Student ID").strip()
            issue_date = st.date_input("Issue Date", value=datetime.today())
            
            issue_btn = st.form_submit_button("Confirm Issue")
            
            if issue_btn:
                if not student_name or not student_id:
                    st.error("⚠️ Student details cannot be empty!")
                else:
                    # Update Book inventory count
                    target_book = get_book(selected_book_id)
                    target_book["Available Copies"] -= 1
                    
                    # Create Log Entry
                    new_record = {
                        "Student Name": student_name,
                        "Student ID": student_id,
                        "Book ID": selected_book_id,
                        "Book Title": target_book["Title"],
                        "Issue Date": str(issue_date),
                        "Status": "Issued"
                    }
                    st.session_state.records.append(new_record)
                    st.success(f"✅ Success: '{target_book['Title']}' issued successfully to {student_name} ({student_id})!")

# --- MODULE 5: RETURN BOOK ---
elif choice == "Return Book":
    st.header("📥 Process a Book Return")
    
    # Filter only records that are currently 'Issued'
    active_records = [r for r in st.session_state.records if r["Status"] == "Issued"]
    
    if not active_records:
        st.info("No books are currently issued out to students.")
    else:
        record_options = {
            f"{r['Student Name']} ({r['Student ID']}) - {r['Book Title']} [ID: {r['Book ID']}]": idx 
            for idx, r in enumerate(st.session_state.records) if r["Status"] == "Issued"
        }
        
        selected_record_str = st.selectbox("Select the active transaction to return:", list(record_options.keys()))
        target_record_idx = record_options[selected_record_str]
        
        if st.button("Confirm Book Return"):
            # Update Record Status
            st.session_state.records[target_record_idx]["Status"] = "Returned"
            
            # Increment the available copy count back in inventory
            returned_book_id = st.session_state.records[target_record_idx]["Book ID"]
            target_book = get_book(returned_book_id)
            if target_book:
                target_book["Available Copies"] += 1
                
            st.success(f"🎉 Success: '{st.session_state.records[target_record_idx]['Book Title']}' has been checked back in successfully!")

# --- MODULE 6: BORROWING RECORDS ---
elif choice == "Borrowing Records":
    st.header("📊 Complete Transaction Log")
    
    if st.session_state.records:
        df_records = pd.DataFrame(st.session_state.records)
        
        # Add a filter status filter toggle
        filter_status = st.radio("Filter records by:", ["All Logs", "Only Currently Issued", "Only Returned"], horizontal=True)
        
        if filter_status == "Only Currently Issued":
            df_records = df_records[df_records["Status"] == "Issued"]
        elif filter_status == "Only Returned":
            df_records = df_records[df_records["Status"] == "Returned"]
            
        st.dataframe(df_records, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions or operations have been recorded yet.")
