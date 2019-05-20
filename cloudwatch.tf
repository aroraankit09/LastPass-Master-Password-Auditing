
# Schedule using cloudwatch
resource "aws_cloudwatch_event_rule" "lastpass-masterpassword-audit-event" {
  name                = "lastpass-masterpassword-audit-event"
  description = "Runs every 30 days"
  schedule_expression = "rate(30 days)"
}

resource "aws_cloudwatch_event_target" "lastpass-masterpassword-audit-event" {
  target_id = "lastpass-masterpassword-audit-event"
  rule      = "${aws_cloudwatch_event_rule.lastpass-masterpassword-audit-event.name}"
  arn       = "${aws_lambda_function.LastPass-MasterPassword-auditing.arn}"
}
