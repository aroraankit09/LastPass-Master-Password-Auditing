
## Summary
LastPass MasterPassword Auditing is a standalone service written in Python 3 to audit the **LastPass users Master Password** 

##### What is LastPass Master Password?
The Master Password is the password that you are prompted to create when you initially sign up for your LastPass account. It's very important that the Master Password that you create and maintain is long and unique. Although there are many layers of encryption and security we put in place to keep your data safe, using a strong Master Password will not only protect you from brute-force attacks, but will also ensure that a breach at another website won't affect your LastPass account.

**The service does the following**
 1. Email users that have LastPass Master Password score = 0%
 2. Email users that have LastPass Master Password score between 1% to 75%
 3. Email Audit Stats to arora.ankit09@gmail.com along with CSV extract.
 
## Getting Started
The service can be used from the local system via the CLI, or can be deployed on AWS to run on a schedule.

### CLI
The CLI has a few pre-requisites.
1. Install Python 3
2. Install Git
3. Ensure your AWS credentials are setup to the relevant account
4. Install awsume to assume the AWS role
5. Ensure the specific AWS account has a secret stored in the SecretsManager with LastPass Credentials. The expected secret content is as follow:
```json
{
  "LastPassCID": "********",
  "LastPassHash": "************************"
}
```
6. Ensure the specific AWS account has a secret stored in the SecretsManager with Email Credentials. The expected secret content is as follow:
```json
{
  "Username": "alert@***.com",
  "Password": "************************"
}
```
7. Clone the repository locally via Git
8. Install all dependencies using `pip install -r app/requirements.txt` 
9. Update the username in lastpass_result() function in **LastPass_MasterPassword_auditing.py**
```json
payload = {
          ....
        'data': {
            'username': '*****@*****.com',
          ....
        }
     }
```
10. Edit the following line in **LastPass_MasterPassword_auditing.py**
```json
report_csv_name = 'Multifactor.csv'
```

Now you can open up a shell and run `python app/cli.py --help` to find out the commands and run the service.

### Deploying on AWS
The service is wrapped in a Terraform project, and can be easily deployed as follow:
1. Install Terraform v11
2. Follow steps 1 through 6 of the CLI setup above
3. Update the username in lastpass_result() function in **LastPass_MasterPassword_auditing.py**
```json
payload = {
          ....
        'data': {
            'username': '*****@*****.com',
          ....
        }
     }
```
4. Clone the repository locally via Git
5. Create a tmp directory in the project folder
6. Copy LastPass_MasterPassword_auditing.py and requirement.txt to tmp folder
7. Install all dependencies inside the `tmp` directory using `pip install -r tmp/requirements.txt -t tmp`
8. Zip all content of tmp folder to as tmp/LastPass_MasterPassword_auditing.zip
9. Ensure your AWS account has an S3 bucket setup with the name `terraform-state` to store the terraform state
10. Run `terraform init` to connect with the S3 backend
11. Run `terraform apply` and confirm everything looks good **again** because you can never be too sure

If everything was deployed successfully, a Lambda function would've been deployed on your AWS account. 

By default this function is scheduled to run every 30 days from the time of deployment. You can test this function with a Test event of type `CloudWatch`; it'll reject all other events

**NOTE:** If you need any help or report a problem/bug, feel free to reach me arora.ankit09@gmail.com
