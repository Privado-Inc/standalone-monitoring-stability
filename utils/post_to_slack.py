import os
import datetime
from dotenv import load_dotenv
from slack_sdk import WebClient


def zip_result():
    cwd = os.getcwd()

    if os.path.isfile(f'{cwd}/report.zip'):
        os.system(f'rm {cwd}/report.zip')

    if os.path.isdir(f'{cwd}/report/'):
        os.system(f'rm -r {cwd}/report')

    os.system(f'mkdir -p {cwd}/report')

    os.system(f'mv {cwd}/temp/result {cwd}/report')
    os.system(f'mv {cwd}/output.xlsx {cwd}/report/output.xlsx')
    os.system(f'zip -r ./report.zip ./report')


def post_report_to_slack(zip_require):
    load_dotenv()
    if zip_require:
        zip_result()
    cwd = os.getcwd()

    slack_token = os.environ["SLACK_TOKEN"]
    slack_channel = os.environ["SLACK_CHANNEL_1"]
    client = WebClient(token=slack_token)

    summary_report = []

    with open(f'{cwd}/slack_summary.txt') as file:
        for line in file.readlines():
            summary_report.append(line)

    try:
        if not zip_require:
            response = client.chat_postMessage(
                channel=slack_channel,
                text='\n'.join(summary_report)
            )
        else:
            response = client.files_upload(
                file=f'{cwd}/report.zip',
                initial_comment='\n'.join(summary_report),
                channels=slack_channel
            )

        if response.status_code == 200:
            print(f'{datetime.datetime.now()} - Report sent to slack channel')
        else:
            print(f'{datetime.datetime.now()} - Report not sent: {response.data}')

    except Exception as e:
        print(f'{datetime.datetime.now()} - Error in sending the report to slack: {str(e)}')

