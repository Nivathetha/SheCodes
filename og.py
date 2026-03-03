import streamlit as st
import hashlib
import requests
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# -------------------------------------------------
# OLLAMA AI FUNCTION (phi3)
# -------------------------------------------------
def ask_ai(prompt):
    try:
        url = "http://127.0.0.1:11434/api/generate"

        payload = {
            "model": "gemma:2b",
            "prompt": f"""
You are a legal compliance advisor for Indian women entrepreneurs.
Based on the business description, list required registrations such as:
GST, FSSAI, MSME (Udyam), Shop Act, Trade License.
Explain simply.

Business description:
{prompt}
""",
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No AI response.")
        else:
            return f"AI Error: {response.text}"

    except Exception as e:
        return f"Connection Error: {str(e)}"


# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(page_title="SheComply", layout="wide")

# -------------------------------------------------
# Pink Theme + Black Text + White State Dropdown
# -------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #fff0f6; color: black !important; }
    h1, h2, h3, h4, h5, h6, p, div, span, label { color: black !important; }

    .stButton>button {
        background-color: #ec407a;
        color: white;
        border-radius: 12px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }

    .stSidebar { background-color: #fce4ec; }
    .stSidebar div, .stSidebar label { color: black !important; }

    .butterfly {
        position: fixed;
        font-size: 30px;
        animation: float 6s ease-in-out infinite;
    }

    .butterfly1 { top: 10%; left: 5%; }
    .butterfly2 { top: 60%; right: 5%; }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }

    div[data-baseweb="popover"] ul li {
        color: white !important;
        background-color: #ec407a !important;
    }

    div[data-baseweb="popover"] ul li:hover {
        background-color: #d81b60 !important;
    }
    </style>

    <div class="butterfly butterfly1">🦋</div>
    <div class="butterfly butterfly2">🌸</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Session Setup
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def gst_required(state, revenue):
    special_states = ["Arunachal Pradesh","Manipur","Meghalaya","Mizoram",
                      "Nagaland","Sikkim","Tripura","Himachal Pradesh",
                      "Uttarakhand","Assam"]

    if state in special_states:
        return revenue > 1000000
    else:
        return revenue > 2000000

def calculate_deadlines():
    today = datetime.today()
    return {
        "GST Return Due": today + timedelta(days=30),
        "Income Tax Filing": today + timedelta(days=180),
        "License Renewal": today + timedelta(days=365)
    }

# -------------------------------------------------
# Login
# -------------------------------------------------
def login():
    st.title("🌸 Welcome to SheComply 🌸")

    username = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and email and password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Please enter all details")

# -------------------------------------------------
# Business Profile
# -------------------------------------------------
def business_profile():
    st.title("🌼 Business Details 🌼")

    name = st.text_input("Business Name")

    btype = st.selectbox("Business Type",
        ["Manufacturing","Retail","Services","Home-based",
         "Food Processing","Textiles","Beauty & Wellness",
         "Handicrafts","E-commerce","Agriculture"])

    revenue = st.number_input("Annual Revenue (INR)", min_value=0)
    employees = st.number_input("Employees", min_value=0)

    state = st.selectbox("State",
        ["Tamil Nadu","Kerala","Karnataka","Andhra Pradesh","Telangana",
         "Maharashtra","Delhi","Gujarat","Rajasthan","Uttar Pradesh",
         "West Bengal","Punjab","Haryana","Bihar","Odisha",
         "Assam","Himachal Pradesh","Uttarakhand","Sikkim"])

    if st.button("Save & Continue"):
        st.session_state.business = {
            "name": name,
            "type": btype,
            "revenue": revenue,
            "employees": employees,
            "state": state
        }
        st.session_state.profile_completed = True
        st.rerun()

# -------------------------------------------------
# Smart Chatbot
# -------------------------------------------------
def global_chatbot():
    st.markdown("---")
    st.subheader("🦋 SheComply Assistant 🌸")

    question = st.text_input("Ask your compliance question")

    if question:
        if "business" in st.session_state:
            b = st.session_state.business
            revenue = b["revenue"]
            state = b["state"]
            btype = b["type"]

            q = question.lower()

            if "gst" in q:
                if gst_required(state, revenue):
                    st.success(f"GST registration is REQUIRED for your ₹{revenue:,} revenue in {state}.")
                else:
                    st.info("GST registration is not mandatory yet based on your revenue.")

            elif "license" in q:
                st.info(f"As a {btype} business in {state}, apply for the relevant state-specific license.")

            elif "loan" in q:
                st.success("Eligible schemes: Mudra Loan, Stand-Up India, Mahila Udyam Nidhi, Annapurna Scheme.")

            elif "tax" in q:
                st.info("You must file Income Tax annually. GST returns required if registered.")

            elif "msme" in q or "udyam" in q:
                st.success("Register under MSME via Udyam Registration portal.")

            else:
                business_info = f"""
Business Name: {b['name']}
Type: {b['type']}
State: {b['state']}
Revenue: ₹{b['revenue']}
Employees: {b['employees']}
"""

                ai_response = ask_ai(business_info + "\nUser Question: " + question)
                st.success(ai_response)

        else:
            st.warning("Complete business profile to get personalized answers.")

# -------------------------------------------------
# Pages
# -------------------------------------------------
def guidance_page():
    b = st.session_state.business
    st.title("🌷 Compliance Guidance 🌷")

    st.write("1️⃣ Register MSME – https://udyamregistration.gov.in")
    st.write("2️⃣ Open Current Account")

    if gst_required(b["state"], b["revenue"]):
        st.write("3️⃣ GST Registration Required – https://www.gst.gov.in")
    else:
        st.write("3️⃣ GST Optional")

    st.write("4️⃣ Apply Relevant License")
    st.write("5️⃣ Maintain Digital Accounting")
    st.write("6️⃣ File Income Tax Annually")

    global_chatbot()

def loan_page():
    st.title("🌺 Women Loan Schemes 🌺")

    st.write("Mudra Loan – https://www.mudra.org.in")
    st.write("Stand-Up India – https://www.standupmitra.in")
    st.write("PMEGP – https://www.kviconline.gov.in/pmegp")
    st.write("Mahila Udyam Nidhi – https://www.sidbi.in/en/products/mahila-udyam-nidhi")
    st.write("Annapurna Scheme – https://www.standupmitra.in/Home/Schemes")

    global_chatbot()

def checklist_page():
    st.title("🌸 Compliance Checklist 🌸")

    items = [
        "MSME Registration",
        "Open Current Account",
        "GST Registration",
        "Business License",
        "Maintain Accounting",
        "File Income Tax"
    ]

    for item in items:
        st.checkbox(item)

    global_chatbot()

def reminder_page():
    st.title("🌼 Smart Reminders 🌼")

    deadlines = calculate_deadlines()

    for key, value in deadlines.items():
        st.info(f"{key}: {value.strftime('%d-%m-%Y')}")

    global_chatbot()

# -------------------------------------------------
# Dashboard
# -------------------------------------------------
def dashboard():
    st.sidebar.title("🌸 Navigation 🌸")

    page = st.sidebar.radio("Go to", [
        "Compliance Guidance",
        "Women Loan Schemes",
        "Checklist",
        "Reminders",
        "Logout"
    ])

    if page == "Compliance Guidance":
        guidance_page()
    elif page == "Women Loan Schemes":
        loan_page()
    elif page == "Checklist":
        checklist_page()
    elif page == "Reminders":
        reminder_page()
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.profile_completed = False
        st.rerun()

# -------------------------------------------------
# Main Flow
# -------------------------------------------------
if not st.session_state.logged_in:
    login()
else:
    if not st.session_state.profile_completed:
        business_profile()
    else:
        dashboard()