import os
from dotenv import load_dotenv
from slack_sdk import WebClient

def get_file_content(file_path):
    with open(file_path, 'rb') as report:
        return report.read()    

def post_report_to_slack():
    load_dotenv()

    slack_client = WebClient(os.environ["SLACK_TOKEN"])
    slack_channel = os.environ["SLACK_CHANNEL_1"]
    file_path = f"{os.getcwd()}/comparison_report.csv"
    report_file = slack_client.files_upload(
        title="Comparison report",
        filename= file_path,
        content= get_file_content(file_path),
    )

    file_url = report_file.get("file").get("permalink")
    file_message = slack_client.chat_postMessage(
        channel= f"#{slack_channel}",
        text= f"Comparison report generated: {file_url}",
    )

