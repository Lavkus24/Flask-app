import json
from .setup_driver import setup_driver
from .sendEmails import send_email_aws_ses
# utils/scraping_utils.py
def threaded_scraping(data_set,start,size,cookie_list):
    try:
        print(f"data_set  : {data_set}")
        scrap_data(data_set,start,size,cookie_list)
    except Exception as e:
        print(f"Error in thread: {e}")

def scrap_data(batch_array,start,size,cookie_list) :
  
    flag = True
    count = 0
    print(f"batch array  : {batch_array}")
    for index,data_set in enumerate(batch_array):
        cookies = cookie_list[index] if index < len(cookie_list) else []
        driver = setup_driver(cookies)
        if(driver):
            profile_data = get_profile_data(data_set, driver)
            print(json.dumps(profile_data))
            driver.quit()
            count = count + 1
        else :
            flag = False
            break
    
    if(flag):
        send_email_aws_ses("Request Processed", f"Request has been completed from {start} to {size}", "lavkus@flynt.social")
        print(f"Request has been processed")
    else :
        send_email_aws_ses("session id", f"There is no any sessionId available to proceess the request from {start + count} to {size}", "lavkus@flynt.social")
        print(f"Request has not been processed")