import csv
import os
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from github import Github
from jira import JIRA, JIRAError

JIRA_TOKEN = "jiratoken"
EMAIL = "username@flyrlabs.com"
GIT_TOKEN = "gittoken"

START_DATE = "2022-07-01"
END_DATE = "2022-07-31"

ISSUE_TYPES = ["Story", "Task", "Sub-task", "Bug"]

jira = JIRA(options={'server': 'https://{your_company}.atlassian.net'}, basic_auth=(EMAIL, JIRA_TOKEN))
g = Github(GIT_TOKEN)
repos = ["{org/repo}", "{org/repo1}"]

current_dir = os.getcwd()

with open('authors.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    authors = {rows["name"]: rows["username"] for rows in reader}

summaries = []

for author, username in authors.items():
    start = datetime.strptime(START_DATE, '%Y-%m-%d')
    end = datetime.strptime(END_DATE, '%Y-%m-%d')
    author_dir = os.path.join(current_dir, author)

    if not os.path.exists(author_dir):
        os.makedirs(author_dir)
    os.chdir(author_dir)

    while start < end:
        total_hours = 0
        month_tickets = set()

        month = str(start.year) + "-" + str(start.month)
        target_dir = os.path.join(author_dir, month)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        os.chdir(month)

        for repo in repos:
            repo = g.get_repo(repo)

            commits = repo.get_commits(author=username, since=start,
                                       until=(start + relativedelta(months=1) + relativedelta(seconds=-1)))

            for commit in commits:
                try:
                    ticket = re.findall("[A-Z]+-[0-9]+", commit.commit.message)[0]
                except IndexError:
                    ticket = None
                if ticket:
                    with open(f'{ticket}-{commit.sha}.txt', 'w') as f:
                        changes = commit.raw_data['files']
                        for change in changes:
                            if 'patch' in change:
                                f.write(change['filename'] + '\n')
                                f.write(
                                    f"Status: {change['status']}, additions: {change['additions']}, deletions: {change['deletions']}, changes: {change['changes']}\n")
                                f.write(change['patch'] + '\n')

                    month_tickets.add(ticket)

        for ticket in month_tickets:
            try:
                issue = jira.issue(ticket)
                if issue.raw['fields']['issuetype']['name'] in ISSUE_TYPES:
                    man_hours = 8 if not issue.raw['fields']['story_points'] else 8 * issue.raw['fields'][
                        'story_points']
                else:
                    man_hours = 8
                summary = issue.fields.summary
            except JIRAError:
                man_hours = 8
                summary = "Ticket not available"
            summaries.append(author.split() + [man_hours, ticket])
        start += relativedelta(months=1)

    os.chdir('../..')

with open(f'full_report.csv', 'w') as f:
    writer = csv.writer(f)
    for row in summaries:
        writer.writerow(row)