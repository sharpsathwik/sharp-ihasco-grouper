
import streamlit as st
import io
import zipfile
import os
import re
from collections import defaultdict

# ----------------------------
# SHARP BRANDING CONFIGURATION
# ----------------------------
SHARP_RED = "#df1626"
SHARP_BLUE = "#1f446f"
LOGO_URL = "https://iili.io/Frv55lt.png"  # Sharp logo
FONT_URL = "https://fonts.googleapis.com/css2?family=Onest:wght@300;400;600&display=swap"

# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(page_title="Sharp – iHasco Grouper", page_icon="📁")

# Inject custom font & branding styles
st.markdown(
    f"""
    <style>
        @import url('{FONT_URL}');
        html, body, [class*="css"]  {{
            font-family: 'Onest', sans-serif;
        }}

        .sharp-title {{
            color: {SHARP_BLUE};
            text-align: center;
            font-size: 32px;
            font-weight: 600;
            margin-top: 10px;
        }}

        .sharp-subtitle {{
            color: {SHARP_RED};
            text-align: center;
            font-size: 18px;
            margin-bottom: 25px;
        }}

        .sharp-footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 13px;
            color: grey;
            opacity: 0.8;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Logo
st.image(LOGO_URL, width=180)

# Title + Subtitle
st.markdown('<div class="sharp-title">Sharp Services</div>', unsafe_allow_html=True)
st.markdown('<div class="sharp-subtitle">iHasco Certificate Grouper</div>', unsafe_allow_html=True)

st.write("""
Upload ZIP files downloaded from **iHasco** (one ZIP per employee).

This tool will:

✔ Read all PDF certificates from the employee ZIPs  
✔ Detect the **course name** automatically  
✔ Generate **one ZIP grouped by course**, each containing all employees  

---
""")

# ----------------------------
# FILE UPLOADER
# ----------------------------
uploaded_files = st.file_uploader(
    "Upload up to 50 employee ZIP files from iHasco",
    type=["zip"],
    accept_multiple_files=True
)

# ----------------------------
# PROCESSING LOGIC
# ----------------------------
if uploaded_files:
    st.info(f"You have uploaded **{len(uploaded_files)}** ZIP file(s).")

    if len(uploaded_files) > 50:
        st.warning("⚠️ Please upload a maximum of 50 employee ZIPs at a time.")
    else:
        if st.button("🔄 Process & Download Grouped ZIP"):
            course_groups = defaultdict(list)
            file_count = 0

            for uploaded in uploaded_files:
                try:
                    with zipfile.ZipFile(uploaded, 'r') as zf:
                        for member in zf.infolist():
                            if member.is_dir():
                                continue

                            base_name = os.path.basename(member.filename)

                            if not base_name.lower().endswith(".pdf"):
                                continue

                            file_data = zf.read(member)

                            # Remove .pdf
                            name_no_ext = base_name[:-4]

                            # Split the " -  #ID"
                            if " -  #" in name_no_ext:
                                left_part, _ = name_no_ext.split(" -  #", 1)
                            else:
                                left_part = name_no_ext

                            # Split employee vs course
                            if " - " in left_part:
                                _, course_part = left_part.split(" - ", 1)
                                course_name = course_part.strip()
                            else:
                                course_name = "Unknown_Course"

                            # Add to dictionary
                            course_groups[course_name].append((base_name, file_data))
                            file_count += 1

                except zipfile.BadZipFile:
                    st.error(f"❌ `{uploaded.name}` is not a valid ZIP file.")
                    st.stop()

            if not course_groups:
                st.warning("No PDF certificates found inside the ZIPs.")
            else:
                # Build output zip
                output_buffer = io.BytesIO()
                with zipfile.ZipFile(output_buffer, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                    for course_name, files in course_groups.items():
                        safe_course = re.sub(r'[^A-Za-z0-9._()-]+', '_', course_name)

                        for filename, data in files:
                            out_zip.writestr(f"{safe_course}/{filename}", data)

                output_buffer.seek(0)

                st.success(
                    f"✔ Successfully processed **{file_count} certificates** "
                    f"into **{len(course_groups)} course folders**."
                )

                with st.expander("📂 View course summary"):
                    for course_name, files in course_groups.items():
                        st.write(f"- **{course_name}** → {len(files)} file(s)")

                st.download_button(
                    label="⬇️ Download Grouped ZIP",
                    data=output_buffer,
                    file_name="Sharp_iHasco_Grouped.zip",
                    mime="application/zip"
                )

# ----------------------------
# FOOTER
# ----------------------------
st.markdown(
    '<div class="sharp-footer">© Sharp Services • Automated Certificate Tool</div>',
    unsafe_allow_html=True
)
