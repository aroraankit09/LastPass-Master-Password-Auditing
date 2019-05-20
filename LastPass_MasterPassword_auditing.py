import requests
import json
import csv
import smtplib
import boto3
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

###################
# Define variables
###################
report_csv_name = '/tmp/Multifactor.csv'
output_list = []

output_list.append('Username, Master Password Strength\n')

email_auth_username = ''
email_auth_password = ''


###############################################
# Return secret from AWS Secrets Manager
###############################################
def get_secret(secret_name: str) -> dict:
    parsed_secret = {}
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='ap-southeast-2',
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = get_secret_value_response['SecretBinary']

        # Parse serialized string as json
        parsed_secret = json.loads(secret)

    return parsed_secret


#########################################################
# Return (User, Password) for Office365 user
#########################################################
def get_email_username():
    secret_name = "EmailCredentials"
    credentials = get_secret(secret_name)
    return (credentials['Username'])


def get_email_password():
    secret_name = "EmailCredentials"
    credentials = get_secret(secret_name)
    return (credentials['Password'])


email_auth_username = get_email_username()
email_auth_password = get_email_password()


#########################################################
# Return LastPass API hash
#########################################################
def get_LastPass_APIKey():
    secret_name = "LastPassReportCredentials"
    credentials = get_secret(secret_name)
    return (credentials['LastPassHash'])

#########################################################
# Return LastPass CID
#########################################################
def get_LastPass_CID():
    secret_name = "LastPassReportCredentials"
    credentials = get_secret(secret_name)
    return (credentials['LastPassCID'])


##################################
# LastPass account configuration
#################################
def lastpass_result():
    url = 'https://lastpass.com/enterpriseapi.php'

    headers = {'Content-Type': 'application/json'}

    LastPassCID = get_LastPass_CID()
    LastPassAPIKey = get_LastPass_APIKey()

    payload = {
        'cid': LastPassCID,
        'provhash': LastPassAPIKey,
        'cmd': 'getuserdata',
        'data': {
            'username': 'user1@lastpass.com',
            'disabled': 0,
            'admin': 0
        }
    }

    response = requests.request('POST', url, headers=headers, data=payload, allow_redirects=False, timeout=30)
    parsed_response = json.loads(response.text)

    return parsed_response


####################################################################################
# Report users who have mpstrength > 1 percent and mpstrength < 75 percent
####################################################################################
def audit_mpstrength():
    records = 0
    parsed_response = lastpass_result()

    for user in parsed_response.get('Users', ''):
        user_dict = parsed_response.get('Users', '').get(user, '')
        if user_dict.get('mpstrength', '') is not '' and (
                int(user_dict.get('mpstrength', '')) < 75 and int(user_dict.get('mpstrength', '')) != 0):
            output_list.append('{},{}\n'.format(user_dict['username'], user_dict['mpstrength']))
            user_email = user_dict.get('username')
            send_email(1, user_email)
            records += 1

    with open(report_csv_name, 'w') as file:
        file.writelines(output_list)

    return (records)


######################################################
# Report users who have mpstrength = 0 percent
######################################################
def audit_mpstrength_zero():
    records = 0
    parsed_response = lastpass_result()

    for user in parsed_response.get('Users', ''):
        user_dict = parsed_response.get('Users', '').get(user, '')
        if user_dict.get('mpstrength', '') is not '' and int(user_dict.get('mpstrength', '')) == 0:
            output_list.append('{},{}\n'.format(user_dict['username'], user_dict['mpstrength']))
            user_email = user_dict.get('username')
            send_email(0, user_email)
            records += 1

    with open(report_csv_name, 'w') as file:
        file.writelines(output_list)

    return (records)


######################################################
# Gather LastPass Audit Stats
######################################################
def audit_stats():
    parsed_response = lastpass_result()
    Total_users = 0

    for user in parsed_response.get('Users', ''):
        Total_users = Total_users + 1

    out_Total_users = 'Total LastPass Users :: ' + str(Total_users) + 'users'

    total_mpstrength75 = audit_mpstrength()
    out_total_mpstrength75 = 'Users that have Master Password Strength < 75% :: ' + str(total_mpstrength75) + 'users'

    total_mpstrength0 = audit_mpstrength_zero()
    out_total_mpstrength0 = 'Users that have Master Password Strength is 0% :: ' + str(total_mpstrength0) + 'users'

    percentage_mpstrength75 = round(total_mpstrength75 / Total_users * 100, 2)
    out_percentage_mpstrength75 = str(
        percentage_mpstrength75) + '% of LastPass users have Master Password Strength < 75% '

    percentage_mpstrength0 = round(total_mpstrength0 / Total_users * 100, 2)
    out_percentage_mpstrength0 = str(percentage_mpstrength0) + '% of LastPass users, Master Password Strength is 0%'

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(email_auth_username, email_auth_password)

    fromaddr = email_auth_username
    toaddr = ['arora.ankit09@gmail.com']

    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = ','.join(toaddr)

    msg['Subject'] = "LastPass Master Password monthly audit successful"

    htmlbody = """\
            <html>
                <head></head>
                <body>
                    <p>Hi All,<br><br>Please find the Monthly LastPass Master Password Audit report attached.<br><br><b>Key Stats:</b><br>
                    """ + out_Total_users + """ <br> """ + out_total_mpstrength75 + """ <br> """ + out_total_mpstrength0 + """ <br> """ + out_percentage_mpstrength75 + """ <br> """ + out_percentage_mpstrength0 + """"		
                    <br><br>Regards, <br>Automation Bot :)
                    </p>
                </body>
            </html>
            """

    emailbody = MIMEText(htmlbody, 'html')
    msg.attach(emailbody)

    filename = report_csv_name
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


######################
# Email configuration
# ####################
def send_email(flag, recipient):
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(email_auth_username, email_auth_password)

    fromaddr = email_auth_username
    toaddr = [recipient]

    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = ','.join(toaddr)

    if flag == 0:
        msg['Subject'] = "Your LastPass Master Password Score is Zero"
        htmlbody = """\
            <html>
                <head></head>
                <body>
                    <p>Hi,<br><br>
                        After performing the monthly LastPass Audit, we found that your <b>LastPass Master Password score is 0</b>. 
    					<br><br>Either you are not using LastPass or you have not logged in a long time.<br>
    					 We advise you to login to your LastPass vault using the browser extension and then run the security challenge to validate your score. <br><br>

    					 Regards, <br>Information Security Team
                    </p>
                </body>
            </html>
            """
        msg.attach(MIMEText(htmlbody, 'html'))
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    else:
        msg['Subject'] = "Your LastPass Master Password Score is Weak"
        htmlbody = """\
                    <html>
                        <head></head>
                        <body>
                            <p>Hi,<br><br>
                                After performing the monthly LastPass Audit, we found that your <b> LastPass Master Password complexity score is < 75%</b>. 
            					<br><br>Please change your LastPass Master Password as per
            					<a href="https://support.logmeininc.com/lastpass">recommended Password guidelines </a>. <br>

            					 After you have changed your password, we advise you to login to your LastPass vault using the browser extension and then run the security challenge to validate your score. <br><br>
            					 
                                <br><br>Regards, <br>Information Security Team
                            </p>
                        </body>
                    </html>
                    """
        msg.attach(MIMEText(htmlbody, 'html'))
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()


##########################
# Main Function call
##########################
def run_audit_report():
    audit_stats()


def handler(event, context):
    run_audit_report()


if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    pass
else:
    run_audit_report()