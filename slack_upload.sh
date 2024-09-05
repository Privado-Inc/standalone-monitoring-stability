#!/bin/bash

# Start the upload action by getting a file upload URL in the response
response=$(curl -F files=@$FILE_PATH \
    -F filename=$FILE_PATH \
    -F token=$SLACK_TOKEN \
    -F length=$(stat --format=%s $FILE_PATH | tr -d '\n') \
       https://slack.com/api/files.getUploadURLExternal)

upload_url=$(echo "$response" | jq -r '.upload_url')
file_id=$(echo "$response" | jq -r '.file_id')

# Upload the file
curl -s -F filename="@$FILE_PATH" -H "Authorization: Bearer $SLACK_TOKEN" POST $upload_url

escaped_message=$(echo "$PR_MESSAGE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

echo $escaped_message

response3=$(curl -g -X POST \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "initial_comment": "'"$escaped_message"'",
        "thread_ts": "'"$INIT_TS"'",
        "files": [{"id": "'"$file_id"'", "title":"'"$FILE_NAME"'"}],
        "channel_id": "'"$SLACK_CHANNEL_ID"'"
      }' \
  https://slack.com/api/files.completeUploadExternal) > /dev/null

echo "$response3"