
# Variable holds Email account credentials
variable "email_secret_arn" {
  default = "arn:aws:secretsmanager:ap-southeast-2:**********:secret:EmailCredentials-*****"
}

# Variable holds LastPass API credentials
variable "LastPassAPI_secret_arn" {
  default = "arn:aws:secretsmanager:ap-southeast-2:**********:secret:LastPassReportCredentials-*****"
}