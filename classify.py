import streamlit as st
import datetime
import fitz  # PyMuPDF
import joblib
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Train the model (only once, then save for reuse)
def train_model():
    data = pd.read_csv("sample_complaints_100.csv")
    X = data["Complaint Text"]
    y = data["Category"]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('nb', MultinomialNB())
    ])
    pipeline.fit(X, y)
    joblib.dump(pipeline, "complaint_classifier.pkl")
    return pipeline

# Load model or train if not exists
model = train_model()

# Map category to priority
category_priority_map = {
    "Bank": "06",
    "Electricity": "05",
    "Roads": "04",
    "Water": "03",
    "Sanitation": "02",
    "Other": "01"
}

# Generate status

def generate_status(date_str):
    try:
        complaint_date = datetime.datetime.strptime(date_str, "%Y%m%d")
        days_old = (datetime.datetime.now() - complaint_date).days
        return "E" if days_old > 5 else "O"
    except Exception as e:
        st.error(f"Error generating status: {e}")
        return "Unknown"

# Extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    try:
        text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

# Streamlit App
st.title("E-Governance Complaint Classifier")
st.write("Upload a PDF containing complaints (one per line or separated clearly).")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)

    if not pdf_text:
        st.error("No text extracted from the PDF.")
    else:
        complaints = [line.strip() for line in pdf_text.split("\n") if line.strip()]

        base_dates = [
            (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y%m%d")
            for i in range(len(complaints))
        ]

        output_data = []
        for idx, (complaint, date) in enumerate(zip(complaints, base_dates), start=1):
            comp_id = f"GRV{idx:07d}"
            category = model.predict([complaint])[0]
            priority = category_priority_map.get(category, "01")
            status = generate_status(date)

            complaint_entry = {
                "Complaint_ID": comp_id,
                "Complaint_Text": complaint,
                "Priority": priority,
                "Date": date,
                "Status": status,
                "Category": category
            }
            output_data.append(complaint_entry)

        # Prepare text output
        text_data = "\n".join(
            [
                f"{c['Complaint_ID']} {c['Category']} {c['Complaint_Text']}".ljust(80)
                + f"{c['Priority']} {c['Date']} {c['Status']}"
                for c in output_data
            ]
        )

        st.success(f"Processed {len(complaints)} complaints!")

        st.download_button(
            label="Download Classified Complaints (TXT)",
            data=text_data,
            file_name="classified_complaints.txt",
            mime="text/plain"
        )

        st.subheader("Preview of Classified Complaints")
        for c in output_data:
            preview_line = (
                f"{c['Complaint_ID']} {c['Category']} {c['Complaint_Text']}".ljust(80)
                + f"{c['Priority']} {c['Date']} {c['Status']}"
            )
            st.text(preview_line)
