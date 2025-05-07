import logging
from datetime import datetime
from datetime import timedelta

def is_within_last_year(date_str):
    if not date_str:
        return False
        
    try:
        # Try to parse the date with different formats
        date_formats = [
            '%B %d, %Y',    # May 11, 2023
            '%d %B %Y',     # 11 May 2023
            '%Y-%m-%d',     # 2023-05-11
            '%B %d,%Y'      # May 11,2023 (no space)
        ]
        
        parsed_date = None
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), date_format)
                # print(parsed_date)
                break
            except ValueError:
                continue
                
        if not parsed_date:
            logging.warning(f"Could not parse date: {date_str}")
            return False
            
        one_year_ago = datetime.now() - timedelta(days=365)
        # print("one")
        # print(one_year_ago)
        return parsed_date >= one_year_ago
        
    except Exception as e:
        logging.error(f"Error processing date {date_str}: {str(e)}")
        return False