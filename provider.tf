
# The provider for creating and managing resources
provider "aws" {
	profile = "DEV"
	region = "ap-southeast-2"
	}
	
# Configuring the terraform backend in S3 bucket
terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "LastPass-MasterPassword-auditing/terraform.tfstate"
    region = "ap-southeast-2"
  }
}