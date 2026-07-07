# Developed by dnoobnerd [https://dnoobnerd.netlify.app]    Made with Streamlit


###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import sqlite3
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import nltk
nltk.download('stopwords')
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######


# sql connector
is_sqlite = False
try:
    connection = pymysql.connect(host='localhost',user='root',password='root@MySQL4admin',db='cv')
    cursor = connection.cursor()
except Exception as e:
    connection = sqlite3.connect('cv.db', check_same_thread=False)
    cursor = connection.cursor()
    is_sqlite = True


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    if is_sqlite:
        insert_sql = "insert into " + DB_table_name + """
        values (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    else:
        insert_sql = "insert into " + DB_table_name + """
        values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    if is_sqlite:
        insertfeed_sql = "insert into " + DBf_table_name + """
        values (NULL,?,?,?,?,?)"""
    else:
        insertfeed_sql = "insert into " + DBf_table_name + """
        values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon='./Logo/recommend.png',
)


###### Main function run() ######


def run():

    # ──────────────────────────────────────────────────────────────────
    # GLOBAL CSS — complete UI overhaul
    # ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

        /* ── Hide Streamlit chrome ── */
        [data-testid="stSidebar"], section[data-testid="stSidebar"],
        [data-testid="collapsedControl"], div[data-testid="collapsedControl"],
        header[data-testid="stHeader"], .stApp > header,
        footer, .viewerBadge_container__1QSob {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            overflow: hidden !important;
        }

        /* ── Base ── */
        .stApp {
            background: #f0f4f8 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        .main .block-container {
            max-width: 880px !important;
            padding: 1rem 1.5rem 4rem !important;
            margin: 0 auto;
        }

        /* ── Typography ── */
        h1, h2, h3 { font-family: 'Outfit', sans-serif !important; color: #0f172a !important; }
        h4, h5, h6 { font-family: 'Inter', sans-serif !important; color: #334155 !important; }
        p, li, span, label, .stMarkdown { font-family: 'Inter', sans-serif !important; }

        /* ── Hero Header ── */
        .hero {
            background: linear-gradient(135deg, #0f2b5b 0%, #1a4d8f 40%, #2563eb 100%);
            border-radius: 20px;
            padding: 48px 36px 40px;
            text-align: center;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 60px -12px rgba(15,43,91,0.4);
        }
        .hero::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(59,130,246,0.15) 0%, transparent 40%);
            animation: shimmer 8s ease-in-out infinite alternate;
        }
        @keyframes shimmer {
            0%   { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-5%, 5%) rotate(2deg); }
        }
        .hero h1 {
            color: #ffffff !important;
            font-size: 2.6rem;
            font-weight: 800;
            margin: 0 0 8px;
            letter-spacing: 0.5px;
            position: relative;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .hero .tagline {
            color: rgba(255,255,255,0.85);
            font-size: 1.05rem;
            font-weight: 400;
            margin: 0;
            position: relative;
            letter-spacing: 0.3px;
        }
        .hero .badge-row {
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            position: relative;
        }
        .hero .badge {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 0.82rem;
            color: #e0ecff;
            font-weight: 500;
        }

        /* ── Cards ── */
        .card {
            background: #ffffff;
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
            transition: box-shadow 0.25s ease, transform 0.25s ease;
        }
        .card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.07);
            transform: translateY(-1px);
        }
        .card-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem;
            font-weight: 700;
            color: #0f2b5b;
            margin: 0 0 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-subtitle {
            font-size: 0.88rem;
            color: #64748b;
            margin: 0 0 20px;
        }

        /* ── Info chip (for basic info) ── */
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .info-chip {
            background: #f0f4f8;
            border-radius: 10px;
            padding: 12px 16px;
            border: 1px solid #e2e8f0;
        }
        .info-chip .label {
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 600;
            color: #94a3b8;
            letter-spacing: 0.8px;
            margin-bottom: 3px;
        }
        .info-chip .value {
            font-size: 0.95rem;
            font-weight: 600;
            color: #1e293b;
        }

        /* ── Level badge ── */
        .level-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 18px;
            border-radius: 24px;
            font-weight: 600;
            font-size: 0.9rem;
            margin-top: 8px;
        }
        .level-fresher   { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
        .level-inter     { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
        .level-exp       { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }

        /* ── Tip item (resume tips) ── */
        .tip-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 10px;
            margin-bottom: 8px;
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .tip-item.good {
            background: #ecfdf5;
            color: #065f46;
            border-left: 3px solid #10b981;
        }
        .tip-item.bad {
            background: #fef2f2;
            color: #991b1b;
            border-left: 3px solid #ef4444;
        }
        .tip-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }

        /* ── Score Ring ── */
        .score-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px 0;
        }
        .score-ring {
            position: relative;
            width: 160px; height: 160px;
        }
        .score-ring svg {
            transform: rotate(-90deg);
        }
        .score-ring .bg {
            fill: none;
            stroke: #e2e8f0;
            stroke-width: 10;
        }
        .score-ring .fg {
            fill: none;
            stroke: url(#scoreGrad);
            stroke-width: 10;
            stroke-linecap: round;
            transition: stroke-dashoffset 1.5s cubic-bezier(0.4,0,0.2,1);
        }
        .score-number {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            color: #0f2b5b;
        }
        .score-label {
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 12px;
            font-weight: 500;
        }

        /* ── Text Inputs ── */
        .stTextInput > div > div > input {
            border-radius: 10px !important;
            border: 1.5px solid #cbd5e1 !important;
            padding: 10px 14px !important;
            font-size: 0.95rem !important;
            background: #ffffff !important;
            color: #1e293b !important;
            transition: all 0.2s ease !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
        }
        .stTextInput label {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            color: #334155 !important;
            font-size: 0.88rem !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 28px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            letter-spacing: 0.3px !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: 0 4px 14px -3px rgba(37,99,235,0.4) !important;
            transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px -4px rgba(37,99,235,0.45) !important;
            background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%) !important;
        }
        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* ── File Uploader ── */
        div[data-testid="stFileUploader"] {
            border: 2px dashed #93c5fd !important;
            border-radius: 16px !important;
            background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%) !important;
            padding: 30px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #2563eb !important;
            background: linear-gradient(135deg, #e0ecff 0%, #eff6ff 100%) !important;
        }

        /* ── Slider ── */
        .stSlider > div > div > div > div {
            background: #2563eb !important;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            color: #1e293b !important;
            background: #f8fafc !important;
            border-radius: 10px !important;
        }

        /* ── Progress bar color ── */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
            border-radius: 8px !important;
        }

        /* ── Success / Warning / Error banners ── */
        .stAlert > div {
            border-radius: 10px !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* ── Divider ── */
        .section-divider {
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 28px 0;
        }

        /* ── Upload section label ── */
        .upload-label {
            font-family: 'Outfit', sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            color: #0f2b5b;
            margin-bottom: 8px;
        }
        .upload-sublabel {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 16px;
        }
    </style>

    <!-- Hero Header -->
    <div class="hero">
        <h1>AI Resume Analyzer</h1>
        <p class="tagline">Upload your resume and get instant AI-powered insights, skill recommendations, and career tips</p>
        <div class="badge-row">
            <span class="badge">📄 Smart Parsing</span>
            <span class="badge">🎯 Skill Matching</span>
            <span class="badge">📊 Resume Scoring</span>
            <span class="badge">🎓 Course Picks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    choice = "User"

    ###### Creating Database and Table ######


    # Create the DB
    if not is_sqlite:
        db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
        cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    if is_sqlite:
        table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        sec_token varchar(20) NOT NULL,
                        ip_add varchar(50) NULL,
                        host_name varchar(50) NULL,
                        dev_user varchar(50) NULL,
                        os_name_ver varchar(50) NULL,
                        latlong varchar(50) NULL,
                        city varchar(50) NULL,
                        state varchar(50) NULL,
                        country varchar(50) NULL,
                        act_name varchar(50) NOT NULL,
                        act_mail varchar(50) NOT NULL,
                        act_mob varchar(20) NOT NULL,
                        Name varchar(500) NOT NULL,
                        Email_ID VARCHAR(500) NOT NULL,
                        resume_score VARCHAR(8) NOT NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        Page_no VARCHAR(5) NOT NULL,
                        Predicted_Field TEXT NOT NULL,
                        User_level TEXT NOT NULL,
                        Actual_skills TEXT NOT NULL,
                        Recommended_skills TEXT NOT NULL,
                        Recommended_courses TEXT NOT NULL,
                        pdf_name varchar(50) NOT NULL
                        );
                    """
    else:
        table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                        sec_token varchar(20) NOT NULL,
                        ip_add varchar(50) NULL,
                        host_name varchar(50) NULL,
                        dev_user varchar(50) NULL,
                        os_name_ver varchar(50) NULL,
                        latlong varchar(50) NULL,
                        city varchar(50) NULL,
                        state varchar(50) NULL,
                        country varchar(50) NULL,
                        act_name varchar(50) NOT NULL,
                        act_mail varchar(50) NOT NULL,
                        act_mob varchar(20) NOT NULL,
                        Name varchar(500) NOT NULL,
                        Email_ID VARCHAR(500) NOT NULL,
                        resume_score VARCHAR(8) NOT NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        Page_no VARCHAR(5) NOT NULL,
                        Predicted_Field BLOB NOT NULL,
                        User_level BLOB NOT NULL,
                        Actual_skills BLOB NOT NULL,
                        Recommended_skills BLOB NOT NULL,
                        Recommended_courses BLOB NOT NULL,
                        pdf_name varchar(50) NOT NULL,
                        PRIMARY KEY (ID)
                        );
                    """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    if is_sqlite:
        tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            feed_name varchar(50) NOT NULL,
                            feed_email VARCHAR(50) NOT NULL,
                            feed_score VARCHAR(5) NOT NULL,
                            comments VARCHAR(100) NULL,
                            Timestamp VARCHAR(50) NOT NULL
                        );
                    """
    else:
        tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                            feed_name varchar(50) NOT NULL,
                            feed_email VARCHAR(50) NOT NULL,
                            feed_score VARCHAR(5) NOT NULL,
                            comments VARCHAR(100) NULL,
                            Timestamp VARCHAR(50) NOT NULL,
                            PRIMARY KEY (ID)
                        );
                    """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':

        # ── User Info Card ──
        st.markdown("""
        <div class="card">
            <div class="card-title">👤 Your Details</div>
            <div class="card-subtitle">Fill in your information to get started with the analysis</div>
        </div>
        """, unsafe_allow_html=True)

        # Collecting Miscellaneous Information
        col1, col2 = st.columns(2)
        with col1:
            act_name = st.text_input('Your Name *')
        with col2:
            act_mail = st.text_input('Email Address *')
        act_mob  = st.text_input('Mobile Number *')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        try:
            dev_user = os.getlogin()
        except OSError:
            import getpass
            try:
                dev_user = getpass.getuser()
            except Exception:
                dev_user = "unknown"
        os_name_ver = platform.system() + " " + platform.release()
        city = "unknown"
        state = "unknown"
        country = "unknown"
        latlong = "unknown"
        try:
            g = geocoder.ip('me')
            latlong = g.latlng
            if latlong:
                geolocator = Nominatim(user_agent="http")
                location = geolocator.reverse(latlong, language='en')
                if location and location.raw:
                    address = location.raw.get('address', {})
                    city = address.get('city', address.get('town', address.get('village', '')))
                    state = address.get('state', '')
                    country = address.get('country', '')
        except Exception:
            pass

        # ── Upload Card ──
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="card-title">📄 Upload Resume</div>
            <div class="card-subtitle">Drop your PDF resume below — our AI will analyze it in seconds</div>
        </div>
        """, unsafe_allow_html=True)

        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            if not os.path.exists('./Uploaded_Resumes'):
                os.makedirs('./Uploaded_Resumes')
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("""
                <div class="card">
                    <div class="card-title">🔍 Resume Analysis</div>
                    <div class="card-subtitle">Here's what we found in your resume</div>
                </div>
                """, unsafe_allow_html=True)

                st.success("Hello " + resume_data['name'] + "! Your resume has been analyzed successfully.")

                try:
                    res_name = resume_data['name']
                    res_email = resume_data['email']
                    res_contact = resume_data['mobile_number']
                    res_degree = str(resume_data['degree'])
                    res_pages = str(resume_data['no_of_pages'])
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">📋 Basic Information</div>
                        <div class="info-grid">
                            <div class="info-chip"><div class="label">Name</div><div class="value">{res_name}</div></div>
                            <div class="info-chip"><div class="label">Email</div><div class="value">{res_email}</div></div>
                            <div class="info-chip"><div class="label">Contact</div><div class="value">{res_contact}</div></div>
                            <div class="info-chip"><div class="label">Degree</div><div class="value">{res_degree}</div></div>
                            <div class="info-chip"><div class="label">Resume Pages</div><div class="value">{res_pages}</div></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    pass

                ## Predicting Candidate Experience Level
                cand_level = ''
                resume_upper = resume_text.upper()

                if resume_data['no_of_pages'] < 1:
                    cand_level = "NA"
                    st.markdown('<span class="level-badge level-fresher">🌱 Fresher Level</span>', unsafe_allow_html=True)
                elif 'INTERNSHIP' in resume_upper:
                    cand_level = "Intermediate"
                    st.markdown('<span class="level-badge level-inter">📈 Intermediate Level</span>', unsafe_allow_html=True)
                elif 'EXPERIENCE' in resume_upper or 'WORK EXPERIENCE' in resume_upper:
                    cand_level = "Experienced"
                    st.markdown('<span class="level-badge level-exp">🏆 Experienced Level</span>', unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('<span class="level-badge level-fresher">🌱 Fresher Level</span>', unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("""
                <div class="card">
                    <div class="card-title">💡 Skills Recommendation</div>
                    <div class="card-subtitle">Your detected skills and our smart recommendations</div>
                </div>
                """, unsafe_allow_html=True)

                ### Current Analyzed Skills
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                for i in resume_data['skills']:
                
                    #### Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('<div class="tip-item good"><span class="tip-icon">🚀</span>Adding these skills to your resume will significantly boost your chances!</div>', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ds_course)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('<div class="tip-item good"><span class="tip-icon">🚀</span>Adding these skills to your resume will significantly boost your chances!</div>', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('<div class="tip-item good"><span class="tip-icon">🚀</span>Adding these skills to your resume will significantly boost your chances!</div>', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('<div class="tip-item good"><span class="tip-icon">🚀</span>Adding these skills to your resume will significantly boost your chances!</div>', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('<div class="tip-item good"><span class="tip-icon">🚀</span>Adding these skills to your resume will significantly boost your chances!</div>', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        break

                    #### For Not Any Recommendations
                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('<div class="tip-item bad"><span class="tip-icon">ℹ️</span>This field is not yet supported — more categories coming soon!</div>', unsafe_allow_html=True)
                        # course recommendation
                        rec_course = "Sorry! Not Available for this Field"
                        break

                ## Resume Scorer & Resume Writing Tips
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("""
                <div class="card">
                    <div class="card-title">📝 Resume Tips & Score</div>
                    <div class="card-subtitle">How complete is your resume? Check what's present and what's missing.</div>
                </div>
                """, unsafe_allow_html=True)
                resume_score = 0

                # Helper to render tip items
                def tip_good(msg):
                    st.markdown(f'<div class="tip-item good"><span class="tip-icon">✅</span>{msg}</div>', unsafe_allow_html=True)
                def tip_bad(msg):
                    st.markdown(f'<div class="tip-item bad"><span class="tip-icon">❌</span>{msg}</div>', unsafe_allow_html=True)

                ### Predicting Whether these key points are added to the resume
                if 'Objective' in resume_text or 'Summary' in resume_text:
                    resume_score += 6
                    tip_good("You have added an Objective / Summary")
                else:
                    tip_bad("Add a career objective — it shows recruiters your career direction")

                if 'Education' in resume_text or 'School' in resume_text or 'College' in resume_text:
                    resume_score += 12
                    tip_good("You have added Education details")
                else:
                    tip_bad("Add Education details to show your qualification level")

                if 'EXPERIENCE' in resume_upper or 'Experience' in resume_text:
                    resume_score += 16
                    tip_good("You have added Experience")
                else:
                    tip_bad("Add Experience — it helps you stand out from the crowd")

                if 'INTERNSHIP' in resume_upper or 'Internship' in resume_text:
                    resume_score += 6
                    tip_good("You have added Internships")
                else:
                    tip_bad("Add Internships to highlight your practical exposure")

                if 'SKILL' in resume_upper or 'Skills' in resume_text:
                    resume_score += 7
                    tip_good("You have added Skills")
                else:
                    tip_bad("Add a Skills section — it's essential for keyword matching")

                if 'HOBBIES' in resume_upper or 'Hobbies' in resume_text:
                    resume_score += 4
                    tip_good("You have added Hobbies")
                else:
                    tip_bad("Add Hobbies to show personality and cultural fit")

                if 'INTERESTS' in resume_upper or 'Interests' in resume_text:
                    resume_score += 5
                    tip_good("You have added Interests")
                else:
                    tip_bad("Add Interests to show passions beyond your work")

                if 'ACHIEVEMENTS' in resume_upper or 'Achievements' in resume_text:
                    resume_score += 13
                    tip_good("You have added Achievements")
                else:
                    tip_bad("Add Achievements to prove you're capable for the role")

                if 'CERTIFICATION' in resume_upper or 'Certification' in resume_text:
                    resume_score += 12
                    tip_good("You have added Certifications")
                else:
                    tip_bad("Add Certifications to demonstrate specialized knowledge")

                if 'PROJECT' in resume_upper or 'Projects' in resume_text:
                    resume_score += 19
                    tip_good("You have added Projects")
                else:
                    tip_bad("Add Projects to show hands-on work related to the position")

                ### Score Ring (SVG gauge)
                circumference = 2 * 3.14159 * 65  # radius 65
                offset = circumference - (resume_score / 100) * circumference
                st.markdown(f"""
                <div class="card" style="text-align:center;">
                    <div class="card-title" style="justify-content:center;">📊 Your Resume Score</div>
                    <div class="score-container">
                        <div class="score-ring">
                            <svg width="160" height="160" viewBox="0 0 160 160">
                                <defs>
                                    <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" style="stop-color:#2563eb"/>
                                        <stop offset="100%" style="stop-color:#10b981"/>
                                    </linearGradient>
                                </defs>
                                <circle class="bg" cx="80" cy="80" r="65"/>
                                <circle class="fg" cx="80" cy="80" r="65"
                                    stroke-dasharray="{circumference}"
                                    stroke-dashoffset="{offset}"/>
                            </svg>
                            <div class="score-number">{resume_score}</div>
                        </div>
                        <div class="score-label">out of 100</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.warning("**Note:** This score is based on the content sections detected in your resume.")

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("""
                <div class="card">
                    <div class="card-title">🎬 Resume Writing Tips</div>
                    <div class="card-subtitle">Watch this video to improve your resume</div>
                </div>
                """, unsafe_allow_html=True)
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.markdown("""
                <div class="card">
                    <div class="card-title">🎤 Interview Preparation</div>
                    <div class="card-subtitle">Get ready for your next interview with these tips</div>
                </div>
                """, unsafe_allow_html=True)
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        <p align="justify">
            AI Resume Analyzer v1.0.0 is an open-source tool built to simplify resume parsing and analysis.
        </p>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                if is_sqlite:
                    cursor.execute('''SELECT ID, ip_add, resume_score, Predicted_Field, User_level, city, state, country from user_data''')
                else:
                    cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Admin! Total %d " % values + " Users Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                if is_sqlite:
                    cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, Predicted_Field, Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, User_level, Actual_skills, Recommended_skills, Recommended_courses, city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                else:
                    cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
