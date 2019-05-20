resource "aws_lambda_function" "LastPass-MasterPassword-auditing" {
  filename         = "./tmp/LastPass_MasterPassword_auditing.zip"
  function_name    = "LastPass-MasterPassword-auditing"
  role             = "${aws_iam_role.LastPass-MasterPassword-audit-role.arn}"
  handler          = "LastPass_MasterPassword_auditing.handler"
  runtime          = "python3.7"
  timeout          = 100
  source_code_hash = "${base64sha256(file("./tmp/LastPass_MasterPassword_auditing.zip"))}"
}

resource "aws_lambda_permission" "allow-cloudwatch-to-call-LastPass_MasterPassword_auditing" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.LastPass-MasterPassword-auditing.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.lastpass-masterpassword-audit-event.arn}"
}

