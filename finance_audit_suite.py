# 📦 INSTALLATION (Run once)
# pip install pandas python-dotenv fpdf

try:
    import pandas as pd
    from fpdf import FPDF
    from dotenv import load_dotenv
    import os
except ImportError:
    print("Missing required packages. Run: pip install pandas python-dotenv fpdf")
    exit(1)

# 🚨 LEGAL NOTICE:
# This script routes financial reporting outside regulated third-party platforms.
# U.S. clients using this for reporting purposes must ensure compliance with SEC/FINRA rules.
# You are responsible for tax/legal compliance and audit accuracy.

load_dotenv()

# === CONFIGURATION ===
THRESHOLD_SUSPICIOUS_AMOUNT = float(os.getenv("SUSPICIOUS_AMOUNT", 10000.0))  # Default: $10,000
INPUT_LOG = "input/transaction_log.csv"
INPUT_EXTERNAL = "input/external_ledger.csv"
INPUT_TRADE_DATA = "input/trades.csv"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_aml_log(input_file):
    df = pd.read_csv(input_file)
    suspicious = df[df['amount'] >= THRESHOLD_SUSPICIOUS_AMOUNT]
    suspicious['flag_reason'] = 'Amount exceeds threshold'
    suspicious.to_csv(f"{OUTPUT_DIR}/aml_flags.csv", index=False)
    print(f"[✓] AML flagged {len(suspicious)} suspicious transactions.")
    return suspicious

def auto_reconcile(internal_file, external_file):
    df1 = pd.read_csv(internal_file)
    df2 = pd.read_csv(external_file)
    merged = pd.merge(df1, df2, on='transaction_id', how='outer', suffixes=('_int', '_ext'), indicator=True)
    discrepancies = merged[merged['_merge'] != 'both']
    discrepancies.to_csv(f"{OUTPUT_DIR}/reconciliation_report.csv", index=False)
    print(f"[✓] Reconciliation complete. Discrepancies found: {len(discrepancies)}")
    return discrepancies

def generate_sec_report(trade_file):
    df = pd.read_csv(trade_file)
    total_volume = df['volume'].sum()
    avg_price = df['price'].mean()
    unique_symbols = df['symbol'].nunique()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SEC/FINRA Compliance Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Trades: {len(df)}", ln=True)
    pdf.cell(200, 10, txt=f"Total Volume: {total_volume}", ln=True)
    pdf.cell(200, 10, txt=f"Average Trade Price: ${avg_price:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Unique Symbols: {unique_symbols}", ln=True)
    pdf.output(f"{OUTPUT_DIR}/sec_report.pdf")
    print(f"[✓] SEC report generated: {OUTPUT_DIR}/sec_report.pdf")

def main():
    print("🔍 Running AML Audit Log Parser...")
    parse_aml_log(INPUT_LOG)

    print("🔄 Running Auto-Reconciliation Bot...")
    auto_reconcile(INPUT_LOG, INPUT_EXTERNAL)

    print("📑 Generating SEC/FINRA Compliance Report...")
    generate_sec_report(INPUT_TRADE_DATA)

    print("\n✅ All tasks completed. Files saved in /output")

if __name__ == "__main__":
    main()

