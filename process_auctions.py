import pandas as pd
import os
import glob
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_auctions():
    """Process the latest auction .xls file and save as CSV."""
    try:
        # Find the latest .xls file in auction_exports/
        excel_files = glob.glob("auction_exports/ibbi_auctions_*.xls")
        if not excel_files:
            logger.error("No .xls files found in auction_exports/")
            return None
        
        latest_file = max(excel_files, key=os.path.getctime)
        logger.info("Processing file: %s", latest_file)

        # Read the .xls file as a tab-separated file
        df = pd.read_csv(latest_file, sep="\t", encoding="utf-8")

        # Log the columns for debugging
        logger.info("Columns in Excel file: %s", df.columns.tolist())

        # Clean and filter the data
        # Rename columns for consistency
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()

        # Assuming you have columns like 'date_of_issue_of_auction_notice', 'date_of_auction', 'last_date_of_submission'
        date_columns = ['date_of_issue_of_auction_notice', 'date_of_auction', 'last_date_of_submission']

        # Convert the specified columns to datetime
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')  # 'coerce' handles invalid parsing gracefully
            else:
                logger.warning("Column %s not found in the Excel file", col)

        # Calculate days until submission
        today = pd.to_datetime(datetime.now().date())
        if 'last_date_of_submission' in df.columns:
            df['days_until_submission'] = (df['last_date_of_submission'] - today).dt.days
        else:
            logger.error("Column 'last_date_of_submission' not found; cannot calculate days_until_submission")
            return None

        # Save processed data as CSV
        today_str = datetime.now().strftime('%Y%m%d')
        output_file = f"auction_exports/processed_auctions_{today_str}.csv"
        df.to_csv(output_file, index=False)
        logger.info("Processed data saved to: %s", output_file)

        return output_file

    except Exception as e:
        logger.error("Processing failed: %s", e)
        return None

if __name__ == "__main__":
    process_auctions()