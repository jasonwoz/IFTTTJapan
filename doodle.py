from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json, time, base64, email, re
import selenium
from selenium import webdriver
import config

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

def main():
    # Authentication for Gmail API
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Instantiate the driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(15) # poll for this amount of time while waiting for elements to load

    # Initial manual login because of two-factor auth
    driver.get(config.gmail_inbox_address)

    # Gmail Login
    email_box = driver.find_element_by_tag_name('input')
    email_box.send_keys(config.email)

    email_submit_button = driver.find_element_by_css_selector('div.U26fgb.O0WRkf.zZhnYe.e3Duub.C0oVfc.nDKKZc.DL0QTb')
    email_submit_button.click()
    print('Logged in to gmail...')

    # Canvas Login
    id_box = driver.find_element_by_id('login')
    pass_box = driver.find_element_by_id('password')
    submit_button = driver.find_element_by_id('loginSubmit')

    id_box.send_keys(config.canvas_username)
    pass_box.send_keys(config.canvas_password)
    submit_button.click()
    print('Logged in to Canvas...')

    # Wait for the stupid, fucking, duo push notification...

    # Confirm to gmail that it's me
    confirm_button = driver.find_element_by_css_selector('div.U26fgb.O0WRkf.zZhnYe.e3Duub.C0oVfc.nDKKZc.DL0QTb')
    confirm_button.click()
    print('Confirmed it was me...')

    time.sleep(5) # wait for the inbox to load

    success = False
    while(success is False):

        # Get messages sent from doodle mailer (or any emails that contain phrases about Japan)
        results = service.users().messages().list(userId='me', q=config.email_query).execute()
        messages = results['messages']
        print('Searching for new messages from Come On Out Japan...')

        for message in messages:

            print("Checking a matched email...")

            # Get the unique message_id of the email
            message_id = message['id']

            # raw_message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()
            # msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            # pattern = re.compile(r'doodle\.com/.+?(?=[">])')
            # matches = pattern.finditer(str(msg_str))
            #
            # # if no matches, add to list of message_ids to ignore
            # if matches is None:
            #     true = 0

            # Open the email of interest
            driver.get(config.gmail_inbox_address + message_id)

            # Find the link in the email that takes us to the doodle poll
            element = driver.find_element_by_partial_link_text('Participate').click()
            print("Navigated to Doodle...")

            # Wait for the new tab to load
            time.sleep(5)

            # Switch control to the new tab
            driver.switch_to.window(driver.window_handles[-1]) # switch to the new window

            # Input a name into the doodle poll
            username_div = driver.find_element_by_css_selector('div.d-newParticipant') # Why is this not working ?
            username_box = username_div.find_element_by_tag_name('input')
            username_box.send_keys(config.doodle_name)
            print("Entered name in doodle poll...")

            # Grab all of the available options for interviews
            options = driver.find_elements_by_css_selector('div.d-checkbox.d-participantPreference.d-noPreference')

            # Loop through all of the options and select the first available (If Any)
            print("Checking available options...")
            for option in options:
                child_input = option.find_element_by_tag_name('input')
                if child_input.is_enabled():
                    option.click()
                    print("Selected available option ! !")
                    ## TODO: Save information about the chosen option (Time)
                    break

            # Dramatic pause before submitting
            time.sleep(5)

            # Find the submit button and click it
            submit_button = driver.find_element_by_css_selector('button.d-button.d-participateButton.d-large.d-primaryButton')
            submit_button.click()
            print("Submitted ! !")
            success = True

        # Wait a minute before checking my inbox again...
        print("Waiting to check inbox for emails...")
        time.sleep(60)




if __name__ == '__main__':
    main()
