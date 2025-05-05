import streamlit as st
import pandas as pd
import glob
import os

st.title("IBBI Auction Notices")

# Find the latest processed CSV file
csv_files = glob.glob("auction_exports/processed_auctions_*.csv")
if not csv_files:
    st.error("No processed auction data found.")
else:
    latest_csv = max(csv_files, key=os.path.getctime)
    st.write(f"Displaying data from: {latest_csv}")

    # Read and display the data
    df = pd.read_csv(latest_csv)
    st.write("### Processed Auctions")
    st.dataframe(df)

    # Add a download button for the CSV
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"processed_auctions_{os.path.basename(latest_csv).split('_')[-1]}",
        mime="text/csv"
    )
