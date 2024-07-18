## This is a tool to generate your monthly report to link code changes to Jira tickets with spent hours

## Before running, update the following values in the main.py: 

>jira_token

Go to https://id.atlassian.com/manage-profile/security/api-tokens and create a new token.

>email = "username@company.com"

Your email

>author = "username"

Your github username

>git_token = "git_token"

Your personal github token. Instructions how to create: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
After you create a token, click "Configure SSO" and then authorize it for FlyrInc

>start_date

Start date for the report

>end_date

End date for the report


## Install requirements.txt and run via 'python main.py' or in Pycharm