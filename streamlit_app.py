import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
from email.mime.base import MIMEBase
from email import encoders
import base64

# Survey Data Preparation
sections = {
    'Business Development': [
        'Do you have sales resources that are exclusively focused on acquiring new customers?',
        "Do you have a value proposition that succinctly defines your company's competitive advantage?",
        'Do you have a robust lead generation engine that drives new opportunities?',
        'Does your sales team use a rolling 4-week activity plan to focus their time & results?'
    ],
    'Customer Management': [
        'Do you have a defined and documented process to review the annual performance of your customer base?',
        'Do you rank your customers by profitability and revenue on an annual basis?',
        'Do you ask your customers what they think of your products and service?',
        'Do you measure customer retention?'
    ],
    "KPI's & Reporting": [
        'Have you established a set of weekly/monthly key performance metrics that you track and monitor?',
        'Do you have an immediate view of your won ⁄ lost record for potential sales for the past 12 months?',
        'Do you have challenges with obtaining weekly reports that deliver key insights to you and your team?',
        "Does your sales team see value in the established KPIs  and how they can shape their future performance?"
    ],
    'Market & Channel': [
        'Do your growth plans use third-party data to establish achievable year-over-year targets?',
        'Is your growth plan built by vertical market and product type?',
        'Does your growth planning include an evaluation of your competitors?',
        'Do you use third-party data to define your market share by vertical and geography?'
    ],
    'People & Leadership': [
        'Do you believe current leadership is performing well?',
        'Do you have low turnover in your sales team?',
        'Does your sales team understand their monthly activities and measure progress on a weekly basis?',
        'Do you have a promote from within culture?'
    ],
    'Pipeline Management': [
        'Do you have an accurate view of all sales opportunities in your pipeline?',
        'Do you use your pipeline review meetings as an opportunity to train, coach & collaborate with your sales team?',
        'Do you review your deals in progress weekly to understand overall pipeline health?',
        'Do you have a process to actively address stalled or stuck deals in the pipeline?'
    ],
    'Process & Discipline': [
        'Have you clearly defined the steps of your sales process from opening an opportunity to closing a deal?',
        'Do you conduct a weekly sales meeting to discuss past and future performance?',
        'Do you have a documented, standard process for deal evaluation & pricing approval?',
        'Does your company routinely use historical data to inform future decisions?'
    ],
    'Sales Forecasting': [
        'Do you use historical sales data as a basis for your sales forecasting?',
        'Is your forecast built bottom up using a well-defined framework?',
        'Do you incorporate data from your CRM into the sales forecasting process?',
        'Do you adjust sales forecasts based on changes in your sales pipeline?'
    ],
    'Structure & Compensation': [
        'Have you defined and documented roles and responsibilities for your sales team?',
        'Do you do an annual performance appraisal for each sales team member?',
        'Are your compensation plans aligned to your growth plan(s)?',
        'Is the organizational structure of your company well understood by your team and designed to drive performance?'
    ],
    'Technology & Automation': [
        'Do you have a well-functioning CRM that provides meaningful weekly performance guidance for your sales team?',
        'Do you feel your company is held hostage to your systems or lack of systems?',
        'Do you currently use automation in your sales organization?',
        'Do you feel you are maximizing ROI from your technology spend?'
    ]
}

# Helper function to calculate scores
def calculate_scores(responses):
    scores = {}
    for section, questions in sections.items():
        score = sum(2 if responses[q] == 'Yes' else 0 for q in questions)
        scores[section] = score
    return scores

# Helper function to generate a PDF report
def generate_pdf_with_chart(company_name, first_name, last_name, position, email, scores, labels, chart_filename="radar_chart.png"):
    # Create PDF
    pdf = FPDF()
    pdf.add_page()

    # Logo
    pdf.image("logo.png", x=(210 - 100) / 2, w=100)  # Centralize the logo (A4 width is 210mm)

    # Title and header
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(234, 0, 0)  # Set color to HEX #EA0000
    pdf.cell(200, 10, txt="Growth Index Results", ln=True, align="C")

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.multi_cell(0, 10, "Congratulations - you've completed TGC's Growth Assessment! Below is a breakdown of your results by focus area.\n")

    # Insert the radar chart image
    pdf.ln(5)
    pdf.image(chart_filename, x=(210 - 140) / 2, w=140)

    # Assessment results breakdown in table format
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Assessment Results by Focus Area", ln=True)

    # Table header
    # pdf.set_font("Arial", "B", 10)
    # pdf.cell(100, 8, txt="Focus Area", border=1, align="C")
    # pdf.cell(50, 8, txt="Score", border=1, align="C")
    # pdf.ln()

    # Table rows
    pdf.set_font("Arial", size=10)
    for label, score in zip(labels, scores):
        pdf.cell(100, 8, txt=label, border=1)
        pdf.cell(50, 8, txt=f"{score}/8", border=1, align="C")
        pdf.ln()

    # Save PDF to file
    pdf_file = "survey_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Function to send email with PDF attachment
def send_email(from_email, to_email, pdf_file, content):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Growth Index Results"
    
    # Add message body
    msg.attach(MIMEText(content, 'html'))
    
    # Attach PDF
    with open(pdf_file, "rb") as file:
        attach = MIMEApplication(file.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename="survey_report.pdf")
        msg.attach(attach)
    
    # Send email via SMTP server
    try:
        with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
            server.starttls()
            server.login("apikey", os.getenv(SENDGRIP_API_KEY_SMTP))  # Securely retrieve the API key
            server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to send email with SendGrid
def send_email_with_sendgrid(to_email, subject, content, pdf_file_path):
    # Initialize SendGrid message
    message = Mail(
        from_email="bruno.motta@thegrowthcollective.io",  # Replace with your verified sender email in SendGrid
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    
    # Add the PDF attachment
    with open(pdf_file_path, "rb") as f:
        pdf_data = f.read()
        encoded_pdf = base64.b64encode(pdf_data).decode()
        attachment = Attachment(
            file_content=encoded_pdf,
            file_type="application/pdf",
            file_name="survey_report.pdf",
            disposition="attachment"
        )
        message.attachment = attachment
    
    # Send the email using SendGrid
    try:
        # sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))  # Securely retrieve API key from environment
        sg = SendGridAPIClient(SENDGRIP_API_KEY) # Erase this line later
        response = sg.send(message)
        print(f"Email sent to {to_email} with status code {response.status_code}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

# Function to create radar chart
def create_radial_bar_chart(labels, scores, filename="radar_chart.png"):
    # Break labels with more than one word into two lines
    formatted_labels = []
    for label in labels:
        words = label.split()
        if len(words) > 1:
            # Move the last word to the next line
            formatted_label = ' '.join(words[:-1]) + '\n' + words[-1]
            formatted_labels.append(formatted_label)
        else:
            formatted_labels.append(label)

    # Number of variables
    num_vars = len(formatted_labels)

    # Compute angle for each category
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Create the polar plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Add bars with specified color
    bars = ax.bar(angles, scores, width=2 * np.pi / num_vars, color='#EA0000', alpha=0.6, align='edge')

    # Remove the outer circle line
    ax.spines['polar'].set_visible(False)

    # Remove the radial ticks (degree markers)
    ax.set_xticks([])

    # Place labels outside each bar
    for bar, angle, label in zip(bars, angles, formatted_labels):

        # Adjust label position to place it just outside the bar
        ax.text(
            angle + 0.3,                # Angle position
            10.1,                       # Radius position outside the maximum score
            label,                      # Text of the label
            ha='center', va='center',   # Centered alignment
            fontsize=10,
        )

    # Add radial lines from the center to the outer circle
    for angle in angles:
        ax.plot([angle, angle], [0, 9.1], color='black', linewidth=0.5, linestyle='--')  # Line on both sides of each bar

    # Remove radial labels for a cleaner look
    ax.set_yticklabels([])

    # Create image
    plt.savefig(filename, format='png', bbox_inches='tight')
    plt.close()

    # Display the plot
    st.pyplot(fig)

# App Layout and User Input
st.image("logo.png", use_container_width=True)
st.title("Growth Index Survey")
st.write("Please complete the survey below.")

# Company and User Information
st.sidebar.header("Your Information")
company_name = st.sidebar.text_input("Company Name", "")
first_name = st.sidebar.text_input("First Name", "")
last_name = st.sidebar.text_input("Last Name", "")
position = st.sidebar.text_input("Position", "")
email = st.sidebar.text_input("Email", "")

if not company_name:
    st.sidebar.error("Company Name is required.")

# Survey Form with Yes/No Questions
responses = {}
for section, questions in sections.items():
    st.subheader(section)
    for question in questions:
        responses[question] = st.radio(question, ["Yes", "No"], index=1)

# Submission and Score Calculation
if st.button("Submit Survey"):
    if not company_name:
        st.warning("Please provide the required Company Name.")
    else:
        # Calculate scores
        scores = calculate_scores(responses)
        
        # Display Radar Chart
        labels = list(scores.keys())
        stats = list(scores.values())
        create_radial_bar_chart(labels, stats)
        
        # Generate PDF and Email Results
        user_info = {
            "Company Name": company_name,
            "First Name": first_name,
            "Last Name": last_name,
            "Position": position,
            "Email": email
        }
        pdf_file = generate_pdf_with_chart(company_name, first_name, last_name, position, email, stats, labels, chart_filename="radar_chart.png")
        
        # Email content
        subject = "Growth Index Results"
        content = f"""
        <p>Hello {first_name},</p>
        <p>Thank you for completing the survey. Please find your results attached.</p>
        <p>Best regards,<br>The Growth Collective</p>
        """

        # Send emails to user (if provided) and admin
        admin_email = "bruno.motta@thegrowthcollective.io"
        if email:
            send_email(admin_email, email, pdf_file, content)
        send_email(admin_email, admin_email, pdf_file, content)
        
        st.success("Survey completed! Results sent via email.")
