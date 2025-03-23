import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.chrome.options import Options
import time
import os


# Initialize session state variables
if "driver" not in st.session_state:
    st.session_state.driver = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "counselear_driver" not in st.session_state:
    st.session_state.counselear_driver = None
if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "counsel_username" not in st.session_state:
    st.session_state.counsel_username = ""
if "counsel_password" not in st.session_state:
    st.session_state.counsel_password = ""

st.set_page_config(page_title="PHC Eligibility Checker", layout="wide")

# Custom button CSS for green styling
st.markdown("""
    <style>
        /* General Style */
        body {
            font-family: 'Arial', sans-serif;
        }

        /* General Input and Button Focus Styling */
        input:focus, textarea:focus, select:focus, button:focus {
            outline: none !important;
            border: 1.5px solid #bbb !important;  /* Subtle Light Gray */
            box-shadow: none !important;
        }

        /* Prevent Red Borders on Hover */
        input:hover, textarea:hover, select:hover, button:hover {
            border: 1.5px solid #bbb !important;  /* Ensures no red on hover */
        }

        /* Fix Button Hover */
        .stButton > button:hover {
            border: 1.5px solid #999 !important;  /* Slightly darker gray */
        }

        /* Fix Upload File Border */
        .stFileUploader > div {
            border: 1.5px solid #bbb !important; /* Subtle light gray border */
        }
        
        .stButton > button {
        background-color: #28a745 !important;  /* Mint Green */
            color: white !important;
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: bold;
            border: 2px solid #28a745 !important;  /* Ensure border is green */
        }
        .stButton > button:hover {
            background-color: #218838 !important;  /* Darker green on hover */
            border: 2px solid #218838 !important;  /* Match border with background */
        }

        /* Custom Card Style */
        .card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }

        /* Title Styling */
        .title {
            font-size: 22px;
            font-weight: bold;
            color: #333;
        }

        /* Sidebar Customization */
        .sidebar .sidebar-content {
            background-color: #f7f9fc !important;
        }



        /* Spacing */
        .spacer { margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Sidebar with login & logout
st.sidebar.image("https://res.cloudinary.com/depyd1rbu/image/upload/v1742429844/SHASTA_HEARING_tlybxa.png", width=250)

with st.sidebar:
    if not st.session_state.logged_in:


        st.header("🔐 Credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("🔑 Login")



        if login_button:
            if not username or not password:
                st.warning("⚠️ Please enter your credentials.")
            else:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                # Set up headless Chromium browser
                chrome_options = Options()
                chrome_options.add_argument("--headless")  # Run in headless mode
                chrome_options.add_argument("--no-sandbox")  # Required for running on Render
                chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
                # Define Chromium & Chromedriver Paths (Use Local Binaries)
                chrome_options.binary_location = "/opt/render/project/.chromium/chrome"
                chromedriver_path = "/opt/render/project/.chromium/chromedriver"

                # Launch Selenium with custom paths
                st.session_state.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
                
                wait = WebDriverWait(st.session_state.driver, 20)

                st.session_state.driver.get("https://provider.partnershiphp.org/UI/Login.aspx")
                wait.until(EC.presence_of_element_located((By.ID, "ctl00_contentUserManagement_txtUserName"))).send_keys(username)
                st.session_state.driver.find_element(By.ID, "ctl00_contentUserManagement_txtPassword").send_keys(password)
                st.session_state.driver.find_element(By.ID, "ctl00_contentUserManagement_btnLogin_input").click()

                time.sleep(3)  # Allow time for login processing

                if "Login.aspx" in st.session_state.driver.current_url:
                    st.error("❌ Login failed! Check credentials.")
                    st.session_state.driver.quit()
                    st.session_state.driver = None
                else:
                    st.sidebar.success("✅ Logged in successfully!")
                    st.session_state.logged_in = True  # Mark as logged in

    else:
        st.sidebar.success("✅ You are logged in!")
        if st.sidebar.button("🔒 Logout"):
            if st.session_state.driver:
                st.session_state.driver.quit()
            st.session_state.driver = None
            st.session_state.logged_in = False  # Reset login state
            st.sidebar.success("Logged out successfully!")
            st.experimental_rerun()



# 🌟 **DASHBOARD VIEW** 🌟
st.title("Welcome")
st.write("Easily check patient eligibility and update CounselEar records.")




    # **🔄 CounselEar Update Process**

st.markdown("""
    <h2 style="
        color: #3EB489;  /* Mint Green */
        font-weight: bold;
        text-align: left;
        margin-bottom: 10px;
    ">
        Update CounselEar Records
    </h2>
""", unsafe_allow_html=True)


# 🏥 **Login Credentials Section**
with st.expander("🔐 CounselEar Login"):
    st.session_state.counsel_username = st.text_input("Username", value=st.session_state.counsel_username, key="counsel_username_input")
    st.session_state.counsel_password = st.text_input("Password", type="password", value=st.session_state.counsel_password, key="counsel_password_input")

# 🎯 **Update Button**
update_button = st.button("🔄 Start CounselEar Update")

if update_button:
    if not st.session_state.counsel_username or not st.session_state.counsel_password:
        st.warning("⚠️ Please enter your CounselEar credentials!")
    elif "result_df" not in st.session_state or st.session_state.result_df is None:
        st.warning("⚠️ Please run the eligibility check first before updating CounselEar!")
    else:
        # **Launch Selenium for CounselEar**
        options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                # Set up headless Chromium browser
                chrome_options = Options()
                chrome_options.add_argument("--headless")  # Run in headless mode
                chrome_options.add_argument("--no-sandbox")  # Required for running on Render
                chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
                # Define Chromium & Chromedriver Paths (Use Local Binaries)
                chrome_options.binary_location = "/opt/render/project/.chromium/chrome"
                chromedriver_path = "/opt/render/project/.chromium/chromedriver"

                # Launch Selenium with custom paths
                st.session_state.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
        
        wait = WebDriverWait(st.session_state.counselear_driver, 20)

        # **Login to CounselEar**
        with st.spinner("Logging into CounselEar..."):
            st.session_state.counselear_driver.get("https://www.counselear.com/Login.aspx")
            wait.until(EC.presence_of_element_located((By.ID, "txtEmailAddress"))).send_keys(st.session_state.counsel_username)
            wait.until(EC.element_to_be_clickable((By.ID, "btnStep1"))).click()
            time.sleep(2)
            wait.until(EC.presence_of_element_located((By.ID, "txtPassword"))).send_keys(st.session_state.counsel_password)
            wait.until(EC.element_to_be_clickable((By.ID, "btnStep2"))).click()
            time.sleep(3)

            if "Login.aspx" in st.session_state.counselear_driver.current_url:
                st.error("❌ CounselEar login failed! Check credentials.")
                st.session_state.counselear_driver.quit()
                st.session_state.counselear_driver = None
                st.stop()
            else:
                st.success("✅ Successfully logged into CounselEar!")

        success_updates = []
        failed_updates = []

        # **Loop through Patients and Update CounselEar**
        progress_bar = st.progress(0)

        for idx, patient in enumerate(st.session_state.result_df.itertuples(index=False), start=1):
            progress_bar.progress(idx / len(st.session_state.result_df))

            try:
                # **Extract correct column values**
                first_name = patient.FirstName
                last_name = patient.LastName
                dob = patient.DOB if isinstance(patient.DOB, str) else patient.DOB.strftime('%m/%d/%Y')
                eligibility_status = patient.Eligibility  # 🟢 Yes / 🔴 No / ⚠️ Error
                member_id = getattr(patient, "MemberID", "N/A")  # ✅ Now correctly accessing Member ID



                # **Navigate to Patient Search**
                st.session_state.counselear_driver.get("https://www.counselear.com/Controls/Pages/Secure/Index.aspx?page=Patients/Search")
                time.sleep(2)  # Ensure page fully loads

                # **Ensure "All Clinics" is selected**
                clinic_dropdown = wait.until(EC.presence_of_element_located((By.ID, "ctl01_lstClinics")))
                if clinic_dropdown.get_attribute("value") != "0":
                    clinic_dropdown.send_keys("All Clinics")
                    time.sleep(1)

                # **Ensure fields are clear before entering data**
                first_name_field = wait.until(EC.presence_of_element_located((By.ID, "ctl01_txtFirstName")))
                first_name_field.clear()
                first_name_field.send_keys(first_name)

                last_name_field = wait.until(EC.presence_of_element_located((By.ID, "ctl01_txtLastName")))
                last_name_field.clear()
                last_name_field.send_keys(last_name)

                # **Ensure correct DOB format**
                dob_field = wait.until(EC.presence_of_element_located((By.ID, "ctl01_txtBirthdate")))
                dob_field.clear()
                dob_field.send_keys(dob)

                # **Click Search Button**
                wait.until(EC.element_to_be_clickable((By.ID, "ctl01_btnSearch"))).click()
                time.sleep(3)  # Wait for results to load

                # **Check if results exist**
                try:
                    patient_row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.rgRow")))
                    patient_row.click()
                    time.sleep(3)  # Ensure patient profile loads
                except:
                    st.session_state.counselear_driver.save_screenshot("counselear_no_results.png")
                    failed_updates.append(f"{first_name} {last_name} - Not Found (No results detected)")
                    continue

                # **Determine if updates are necessary**
                if eligibility_status == "🟢 Yes" and member_id != "N/A":
                    phc_id_field = wait.until(EC.presence_of_element_located((By.ID, "ctl01_txtReferralTypeDescription")))
                    phc_id_field.clear()
                    phc_id_field.send_keys(member_id)  # ✅ Insert Member ID

                    # **Set Insurance to "Partnership of Ca"**
                    insurance_dropdown = wait.until(EC.presence_of_element_located((By.ID, "ctl01_lstReferralTypes")))
                    insurance_dropdown.send_keys("Partnership of Ca")
                    time.sleep(1)

                elif eligibility_status in ["🔴 No", "⚠️ Record Not Found", "⚠️ Error During Check"]:
                    # **Set Patient to Inactive**
                    status_dropdown = wait.until(EC.presence_of_element_located((By.ID, "ctl01_lstStatus")))
                    status_dropdown.send_keys("Inactive")
                    time.sleep(1)  # ✅ Ensure status updates

                    # **Tag Patient as "No PHC"**
                    tag_field = wait.until(EC.presence_of_element_located((By.ID, "ctl01_lstTags-VERIFIED_Input")))
                    
                    # **Ensure dropdown appears & select correct tag**
                    tag_field.click()
                    time.sleep(1)
                    tag_field.send_keys("No PHC")
                    time.sleep(1)
                    tag_field.send_keys(Keys.DOWN)  # Selects first suggestion
                    time.sleep(1)
                    tag_field.send_keys(Keys.RETURN)  # Confirms selection
                    time.sleep(1)  # ✅ Ensure entry registers

                # **Save Changes**
                save_button = wait.until(EC.element_to_be_clickable((By.ID, "ctl01_btnSubmit")))
                save_button.click()
                time.sleep(2)

                success_updates.append(f"{first_name} {last_name} - Updated Successfully (Eligibility: {eligibility_status}, MemberID: {member_id})")

            except Exception as e:
                failed_updates.append(f"{first_name} {last_name} - Update Failed: {str(e)}")

        # **Show Results**
        st.subheader("🔄 CounselEar Update Results")
        st.success(f"✅ Successfully updated {len(success_updates)} patients in CounselEar.")
        for msg in success_updates:
            st.write(f"🟢 {msg}")

        if failed_updates:
            st.warning(f"⚠️ {len(failed_updates)} patients could not be updated.")
            for msg in failed_updates:
                st.write(f"🔴 {msg}")

        # **Close CounselEar Session**
        st.session_state.counselear_driver.quit()



# **Modern Line Break Between PHC Eligibility and CounselEar Update**
st.markdown("""
    <hr style="
        border: none;
        height: 2px;
        background-color: #ddd;
        margin: 40px 0;
        border-radius: 5px;
    ">
""", unsafe_allow_html=True)




# 🔄 **Main UI Grid Layout**
col1, col2 = st.columns([2, 3])  # Adjust column widths for better spacing




# **Main UI (Only visible after login)**
if st.session_state.logged_in:

    # 🏥 **LEFT PANEL (File Upload & Start Check)**
    with col1:
        st.markdown("""
            <h2 style="
                color: #3EB489;  /* Mint Green */
                font-weight: bold;
                text-align: left;
                margin-bottom: 10px;
            ">
                PHC Eligibility Check
            </h2>
        """, unsafe_allow_html=True)


        
        
        st.markdown("""
            <h4 style="
                font-size: 16px;  /* Adjust size */
                font-weight: normal;
                margin-bottom: 5px;
            ">
                📥 Upload Patient File
            </h4>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["xlsx"], accept_multiple_files=False)
        start_button = st.button("🚀 Start Eligibility Check")
        
        st.markdown('</div>', unsafe_allow_html=True)

    

    # 🏥 **START ELIGIBILITY CHECK**

    if start_button:
        if not uploaded_file:
            st.warning("⚠️ Please upload a patient file!")
        else:
            patients = pd.read_excel(uploaded_file)
            st.success(f"✅ Loaded {len(patients)} patients for eligibility checking.")

            results = []
            wait = WebDriverWait(st.session_state.driver, 10)

            # **Check if PHC Portal session is still active**
            st.session_state.driver.get("https://provider.partnershiphp.org/UI/Membersearch.aspx")
            time.sleep(2)

            if "Login.aspx" in st.session_state.driver.current_url:
                st.warning("⚠️ Session expired. Please log in again.")
                st.session_state.driver.quit()
                st.session_state.driver = None
                st.session_state.logged_in = False
                st.experimental_rerun()
            else:
                st.success("✅ Session active, proceeding with eligibility checks...")

            progress_bar = st.progress(0)

            # **Process Patients**
            for idx, patient in patients.iterrows():
                progress_bar.progress((idx + 1) / len(patients))

                eligibility = "⚠️ Record Not Found or Error"
                effective_date, expiration_date, member_id = "N/A", "N/A", "N/A"

                for attempt in range(3):
                    try:
                        st.session_state.driver.get("https://provider.partnershiphp.org/UI/Membersearch.aspx")
                        time.sleep(2)  # Ensure page is loaded fully

                        # **Enter First Name**
                        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ucSearchMember_rdFirstName"))).clear()
                        st.session_state.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ucSearchMember_rdFirstName").send_keys(patient["FirstName"])

                        # **Enter Last Name**
                        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ucSearchMember_rdLastName"))).clear()
                        st.session_state.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ucSearchMember_rdLastName").send_keys(patient["LastName"])

                        # **Enter DOB**
                        dob_input = wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ucSearchMember_rdDob_dateInput")))
                        dob_input.clear()
                        dob_input.send_keys(patient["DOB"].strftime('%m/%d/%Y'))

                        # **Click Search Button**
                        wait.until(EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_ucSearchMember_btnSearch"))).click()

                        # **Wait for Search Results**
                        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ucSearchMember_rdGridMember_ctl00__0")))

                        # **Get Results**
                        rows = st.session_state.driver.find_elements(By.CSS_SELECTOR, "[id^='ctl00_ContentPlaceHolder1_ucSearchMember_rdGridMember'] a.btn.btn-primary")

                        # **Ensure results exist before proceeding**
                        if rows:
                            wait.until(EC.element_to_be_clickable(rows[0])).click()
                            time.sleep(2)  # Ensure new page loads

                            # **Get eligibility status**
                            eligibility_status = wait.until(EC.presence_of_element_located(
                                (By.ID, "ContentPlaceHolder1_ucSearchMember_lblIsEligible"))).text.strip()
                            eligibility = "🟢 Yes" if eligibility_status.lower() == "yes" else "🔴 No"

                            # **Get effective & expiration dates**
                            date_elements = wait.until(EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_ucSearchMember_rdGridEligibilitySpan_ctl00__0 td")))

                            if len(date_elements) >= 3:
                                effective_date = date_elements[1].text.strip()
                                expiration_date = date_elements[2].text.strip()

                            # **Get Member ID**
                            member_id = wait.until(EC.presence_of_element_located(
                                (By.ID, "ContentPlaceHolder1_ucSearchMember_lblCin"))).text.strip()

                        else:
                            st.write(f"⚠️ No results found for {patient['FirstName']} {patient['LastName']}. Skipping...")
                            eligibility = "⚠️ Record Not Found"

                        break  # Exit retry loop if successful

                    except Exception as e:
                        if attempt < 2:
                            time.sleep(3)  # Retry after short delay
                        else:
                            eligibility = "⚠️ Error During Check"

                # ✅ **Store the results**
                results.append({
                    "FirstName": patient["FirstName"],
                    "LastName": patient["LastName"],
                    "DOB": patient["DOB"].strftime('%m/%d/%Y'),
                    "MemberID": member_id,
                    "Eligibility": eligibility,
                    "Effective Date": effective_date,
                    "Expiration Date": expiration_date
                })

            # **Save results in session state**
            st.session_state.result_df = pd.DataFrame(results)

            # **Display Results**
            st.subheader("📊 Eligibility Results")
            st.dataframe(st.session_state.result_df, use_container_width=True)

            st.download_button("📥 Download Results", data=st.session_state.result_df.to_csv(index=False),
                               file_name="eligibility_results.csv", mime="text/csv")

            st.success("🎉 Eligibility Check Complete!")





            
