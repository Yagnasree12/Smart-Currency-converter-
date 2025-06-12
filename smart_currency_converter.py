
import streamlit as st
from forex_python.converter import CurrencyRates
import datetime
import pandas as pd
import qrcode
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image
import base64

st.set_page_config(page_title="Smart Currency Converter", layout="centered")

# --- Theme Toggle ---
theme = st.radio("Choose Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""<style>body { background-color: #111; color: white; }</style>""", unsafe_allow_html=True)

# --- Header ---
st.title("🌐 Smart Currency Converter")
st.markdown("Convert currencies in real-time, view trends, scan QR codes, and share results!")

currencies = ["USD", "INR", "EUR", "JPY", "GBP", "AUD", "CAD"]
cr = CurrencyRates()

# --- Currency Converter ---
col1, col2 = st.columns(2)
from_currency = col1.selectbox("From", currencies, index=0)
to_currency = col2.selectbox("To", currencies, index=1)
amount = st.number_input("Amount", min_value=0.01, value=1.0, step=0.5)

# --- Convert ---
if st.button("Convert"):
    try:
        result = cr.convert(from_currency, to_currency, amount)
        st.success(f"{amount} {from_currency} = {round(result, 4)} {to_currency}")
    except Exception as e:
        st.error(f"Conversion failed: {str(e)}")

# --- Historical Trend Chart ---
def get_history(from_curr, to_curr):
    today = datetime.date.today()
    rates = []
    dates = []
    for i in range(10):
        day = today - datetime.timedelta(days=i)
        try:
            rate = cr.get_rate(from_curr, to_curr, day)
            rates.append(round(rate, 4))
            dates.append(day.strftime("%Y-%m-%d"))
        except:
            continue
    return pd.DataFrame({'Date': dates[::-1], 'Rate': rates[::-1]})

if st.button("Show Trend"):
    df = get_history(from_currency, to_currency)
    st.line_chart(df.set_index("Date"))

# --- QR Code Scanner ---
st.subheader("📷 Scan QR Code for Currency")
uploaded = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])
if uploaded:
    img = Image.open(uploaded)
    decoded = decode(img)
    if decoded:
        code = decoded[0].data.decode("utf-8")
        st.success(f"Scanned Currency: {code}")
        if code in currencies:
            from_currency = code
    else:
        st.warning("No valid QR code found.")

# --- Email Share ---
st.subheader("✉️ Share Result via Email")
recipient = st.text_input("Recipient Email")
if st.button("Generate Email Link"):
    subject = f"Currency Conversion {from_currency} to {to_currency}"
    body = f"{amount} {from_currency} = {round(result, 4)} {to_currency}"
    mailto_link = f"mailto:{recipient}?subject={subject}&body={body}"
    st.markdown(f"[📩 Click to send email]({mailto_link})")

# --- QR Code Generator ---
st.subheader("📦 Generate QR for Currency Code")
currency_for_qr = st.selectbox("Select Currency for QR", currencies)
if st.button("Generate QR Code"):
    qr = qrcode.make(currency_for_qr)
    buf = BytesIO()
    qr.save(buf)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    st.image(qr, caption=f"QR for {currency_for_qr}")
    st.markdown(f"![QR](data:image/png;base64,{img_b64})")
