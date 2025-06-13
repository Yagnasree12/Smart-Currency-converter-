import streamlit as st
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import qrcode
from io import BytesIO
import smtplib
from email.message import EmailMessage
import cv2
import numpy as np
from PIL import Image

# ------------------ Streamlit App Config ------------------
st.set_page_config(page_title="Smart Currency Converter", page_icon="💱", layout="centered")

st.title("🌐 Smart Currency Converter")
st.markdown("Convert currencies, view trends, scan QR, share via email — all in one place!")

# ------------------ Currency Conversion ------------------
curr = CurrencyRates()

amount = st.number_input("💰 Enter Amount", min_value=0.0, value=1.0)
from_currency = st.selectbox("From Currency", options=curr.get_rates("").keys(), index=26)
to_currency = st.selectbox("To Currency", options=curr.get_rates("").keys(), index=80)

if st.button("🔄 Convert"):
    try:
        result = curr.convert(from_currency, to_currency, amount)
        st.success(f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}")
    except Exception as e:
        st.error("Conversion failed. Please check the currency codes or try again later.")

# ------------------ Historical Trend Chart ------------------
def plot_currency_trend(base, target):
    dates = []
    rates = []
    for i in range(10):
        day = datetime.now() - timedelta(days=i)
        rate = curr.get_rate(base, target, day)
        dates.append(day.strftime("%d-%b"))
        rates.append(rate)
    dates.reverse()
    rates.reverse()

    fig, ax = plt.subplots()
    ax.plot(dates, rates, marker='o', linestyle='-', color='blue')
    ax.set_title(f"{base} to {target} - Last 10 Days")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rate")
    st.pyplot(fig)

if st.checkbox("📈 Show Last 10 Days Trend"):
    plot_currency_trend(from_currency, to_currency)

# ------------------ QR Code Scanner ------------------
st.subheader("📷 QR Code Scanner")
uploaded_qr = st.file_uploader("Upload a QR code image", type=["png", "jpg", "jpeg"])

def decode_qr_from_image(uploaded_image):
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    return data if data else "No QR code detected."

if uploaded_qr:
    st.image(uploaded_qr, caption="Uploaded QR Code")
    decoded = decode_qr_from_image(uploaded_qr)
    st.success(f"Detected Text: {decoded}")

# ------------------ QR Code Generator ------------------
st.subheader("🔲 Generate QR Code")
qr_text = st.text_input("Enter text/currency to generate QR")
if st.button("Generate QR"):
    qr_img = qrcode.make(qr_text)
    buf = BytesIO()
    qr_img.save(buf)
    st.image(qr_img, caption="Generated QR Code")
    st.download_button("Download QR Code", buf.getvalue(), file_name="qr_code.png")

# ------------------ Email Share ------------------
st.subheader("✉️ Share via Email")
sender = st.text_input("Your Email")
receiver = st.text_input("Receiver's Email")
if st.button("Send Email"):
    if sender and receiver:
        try:
            msg = EmailMessage()
            msg['Subject'] = "Currency Conversion Result"
            msg['From'] = sender
            msg['To'] = receiver
            msg.set_content(f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}")
            # Configure this with your real email/password or use a secure app-specific password
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(sender, "your-app-password")  # Use app-specific password
                smtp.send_message(msg)
            st.success("Email sent successfully!")
        except Exception as e:
            st.error("Failed to send email. Check credentials or SMTP settings.")
    else:
        st.warning("Please fill in both email fields.")

# ------------------ Theme Toggle ------------------
st.sidebar.title("🌓 Theme")
theme = st.sidebar.radio("Choose Mode:", ["Light", "Dark"])
if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #0e1117; color: white; }
        </style>
        """,
        unsafe_allow_html=True,
    )
