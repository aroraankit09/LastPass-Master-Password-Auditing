
# Policy for accessing Secrets Manager
data "aws_iam_policy_document" "LastPass-auditing-policy" {
	statement {
		actions = [
			"secretsmanager:GetSecretValue"
		]
		resources = [
			"${var.email_secret_arn}",
			"${var.LastPassAPI_secret_arn}",
		]

	}
}

resource "aws_iam_policy" "LastPass-auditing-policy" {
	name        = "LastPass-auditing-policy"
	path        = "/"
	description = "Policy to access the credentials in Secrets Manager"

	policy = "${data.aws_iam_policy_document.LastPass-auditing-policy.json}"
}

# Role for our lambda to update bitbucket
resource "aws_iam_role" "LastPass-MasterPassword-audit-role" {
	name = "LastPass-MasterPassword-audit-role"
	
	assume_role_policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Action": "sts:AssumeRole",
			"Principal": {
				"Service": "lambda.amazonaws.com"
			},
			"Effect": "Allow",
			"Sid": ""
		}
	]
}
EOF
}

resource "aws_iam_role_policy_attachment" "basic-exec-role" {
	role       = "${aws_iam_role.LastPass-MasterPassword-audit-role.name}"
	policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "secretmanager-policy-attachment" {
	role       = "${aws_iam_role.LastPass-MasterPassword-audit-role.name}"
	policy_arn = "${aws_iam_policy.LastPass-auditing-policy.arn}"
}