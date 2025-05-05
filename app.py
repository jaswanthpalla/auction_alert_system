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

    # Read the data
    df = pd.read_csv(latest_csv)

    # Add a slider for selecting the range of days until submission
    st.write("### Filter Auctions by Days Until Submission")
    if 'days_until_submission' in df.columns:
        # Get the min and max days for the slider range
        min_days = int(df['days_until_submission'].min())
        max_days = int(df['days_until_submission'].max())
        
        # Handle cases where min_days or max_days might be NaN or negative
        if pd.isna(min_days) or pd.isna(max_days):
            st.warning("No valid days_until_submission data available for filtering.")
            filtered_df = df
        else:
            min_days = max(min_days, 0)  # Ensure min_days is not negative
            max_days = max(max_days, min_days + 1)  # Ensure max_days is greater than min_days

            # Add a slider to select the range of days
            days_range = st.slider(
                "Select range of days until submission:",
                min_value=min_days,
                max_value=max_days,
                value=(min_days, max_days),
                step=1
            )

            # Add an Apply button to filter the data
            if st.button("Apply"):
                # Filter the dataframe based on the selected range
                filtered_df = df[
                    (df['days_until_submission'] >= days_range[0]) & 
                    (df['days_until_submission'] <= days_range[1])
                ]
                # Store the filtered dataframe in session state to persist after button click
                st.session_state['filtered_df'] = filtered_df

    else:
        st.error("Column 'days_until_submission' not found in the data.")
        filtered_df = df

    # Display the filtered data (use session state if available)
    if 'filtered_df' in st.session_state:
        filtered_df = st.session_state['filtered_df']
    else:
        filtered_df = df

    st.write("### Processed Auctions")
    st.dataframe(filtered_df)

    # Add a download button for the filtered CSV
    st.download_button(
        label="Download Filtered CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"processed_auctions_filtered_{os.path.basename(latest_csv).split('_')[-1]}",
        mime="text/csv"
    )
