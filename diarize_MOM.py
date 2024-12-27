import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import openai
from docx import Document  # For DOCX file output
from datetime import datetime,timedelta  # For current datetime
import time  # For time module
from cal1 import create_meeting, authenticate_user
import dateparser 
from upstash_redis import Redis
import sys

file = open('keys.json', 'r')
keys = json.load(file)
upstash_token = keys['UPSTASH_REDIS_REST_TOKEN']
subscription_key = keys['subscription_key_1']
openai_api_key = keys['openai.api_key']

UPSTASH_REDIS_REST_URL="https://fine-swift-52766.upstash.io"
UPSTASH_REDIS_REST_TOKEN = upstash_token
redis_client = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)

# Azure Speech-to-Text Configuration
url_1 = "https://eastus2.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-11-15"
subscription_key_1 = subscription_key

# OpenAI GPT Configuration
openai.api_key = openai_api_key
openai.api_base = "https://api.openai.com/v1"

def get_redis_client():
    try:
        client = Redis.StrictRedis.from_url("https://merry-snapper-43667.upstash.io", decode_responses=True, socket_timeout=300)
        return client
    except Redis.exceptions.ConnectionError as e:
        print(f"Redis connection failed: {e}")
        return None

# Function to format milliseconds into mm:ss
def format_timestamp(milliseconds):
    minutes = milliseconds // 60000
    seconds = (milliseconds % 60000) // 1000
    return f"{minutes:02}:{seconds:02}"

# Merge consecutive phrases by the same speaker
def merge_phrases_by_speaker(json_data):
    """
    Merge consecutive phrases in the JSON data if they are spoken by the same speaker.

    Args:
        json_data (dict): The JSON data containing phrases.

    Returns:
        list: A list of merged phrases with speaker, start time, end time, and text.
    """
    merged_phrases = []
    current_phrase = None

    for phrase in json_data['phrases']:
        if current_phrase is None:
            # Initialize the current phrase
            current_phrase = {
                "speaker": phrase["speaker"],
                "offsetMilliseconds": phrase["offsetMilliseconds"],
                "text": phrase["text"],
                "endMilliseconds": phrase["offsetMilliseconds"] + phrase["durationMilliseconds"]
            }
        else:
            # Check if the current speaker is the same as the last one
            if phrase["speaker"] == current_phrase["speaker"]:
                # Merge text and update the end time
                current_phrase["text"] += " " + phrase["text"]
                current_phrase["endMilliseconds"] = phrase["offsetMilliseconds"] + phrase["durationMilliseconds"]
            else:
                # Push the current phrase to the merged list and start a new one
                merged_phrases.append(current_phrase)
                current_phrase = {
                    "speaker": phrase["speaker"],
                    "offsetMilliseconds": phrase["offsetMilliseconds"],
                    "text": phrase["text"],
                    "endMilliseconds": phrase["offsetMilliseconds"] + phrase["durationMilliseconds"]
                }

    # Append the last phrase if any
    if current_phrase:
        merged_phrases.append(current_phrase)

    return merged_phrases

# Step 1: Send Audio for Speech-to-Text with Diarization
def get_speech_to_text_response(audio_file_path):
    audio_file=open(audio_file_path, "rb")
    m = MultipartEncoder(
        fields={
            "audio": (audio_file.name, audio_file, "audio/mpeg"),
            "definition": json.dumps({
                "locales": ["en-US"],
                "diarization": {
                    "maxSpeakers": 20,
                    "enabled": True
                }
            })
        }
    )
    headers = {
        "Content-Type": m.content_type,
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key_1,
    }
    response = requests.post(url_1, headers=headers, data=m)
    if response.status_code == 200:
        print("Speech-to-text API call successful.")
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Step 2: Process Diarized JSON and Merge Phrases
def process_and_merge_diarization(response_data):
    merged_phrases = merge_phrases_by_speaker(response_data)
    diarised_text = ""
    max_speaker = 0

    for phrase in merged_phrases:
        speaker = phrase["speaker"]
        start_time = format_timestamp(phrase["offsetMilliseconds"])
        end_time = format_timestamp(phrase["endMilliseconds"])
        text = phrase["text"]
        diarised_text += f"[Speaker {speaker} {start_time}-{end_time}]\n{text}\n\n"
        max_speaker = max(max_speaker, int(speaker))

    return diarised_text, max_speaker

def extract_start_time_and_resolve_date_from_gpt_with_nlp(mom_text, current_datetime=None):
    import re
    from datetime import datetime
    import dateparser

    def resolve_follow_up_date(input_text, current_datetime):
        """
        Resolves a follow-up meeting date from the input text.

        Parameters:
        - input_text: str, natural language input describing the follow-up date.
        - current_datetime: datetime, the current date and time.

        Returns:
        - str: Resolved date in YYYY-MM-DD HH:MM format, or None if not found.
        """
        if not current_datetime:
            current_datetime = datetime.now()

        # Try parsing the date using dateparser
        parsed_date = dateparser.parse(input_text, settings={'RELATIVE_BASE': current_datetime})

        if parsed_date:
            # Return the date in the desired format
            return parsed_date.strftime("%Y-%m-%d %H:%M")
        else:
            # Handle specific cases manually (e.g., "17th" without a month)
            if any(char.isdigit() for char in input_text):
                try:
                    day = int(''.join(filter(str.isdigit, input_text)))
                    # Handle cases like "17th" and map it to the appropriate month
                    if day:
                        year = current_datetime.year
                        month = current_datetime.month
                        # If the day has already passed this month, use next month
                        if day < current_datetime.day:
                            month += 1
                            if month > 12:
                                month = 1
                                year += 1
                        parsed_date = datetime(year, month, day, current_datetime.hour, current_datetime.minute)
                        return parsed_date.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    pass

        return None

    follow_up_time = None
    resolve_date = None
    follow_ups_section = None

    # Extract the Follow-Ups section
    if "Follow-Ups" in mom_text:
        follow_ups_start = mom_text.index("Follow-Ups")
        follow_ups_section = mom_text[follow_ups_start:]
        next_heading_match = re.search(r"\n[A-Za-z ]+:|$", follow_ups_section)
        follow_ups_section = follow_ups_section[:next_heading_match.start()] if next_heading_match else follow_ups_section

    if follow_ups_section:
        # Pattern to match datetime or natural language follow-up time
        datetime_pattern = datetime_pattern = r"(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2})|(?:next\s+[a-zA-Z]+|tomorrow|in\s+\d+\s+[a-zA-Z]+|on\s+\d{1,2}(?:th|st|nd|rd)|\d{1,2}\s)"
        follow_up_match = re.search(datetime_pattern, follow_ups_section, re.IGNORECASE)
        if follow_up_match:
            follow_up_time_str = follow_up_match.group(0)
            resolved_date = resolve_follow_up_date(follow_up_time_str, current_datetime)
            if resolved_date:
                follow_up_time = resolved_date
                print(f"Resolved Follow-up Meeting Time: {follow_up_time}")
            else:
                print(f"Unable to resolve date for input: {follow_up_time_str}")
        else:
            print("No valid follow-up time found in the Follow-Ups section.")

        # Pattern to match a resolution date
        resolve_date_pattern = r"Resolution Date: (\d{4}-\d{2}-\d{2})"
        resolve_date_match = re.search(resolve_date_pattern, follow_ups_section)
        if resolve_date_match:
            resolve_date_str = resolve_date_match.group(1)
            try:
                resolve_date = datetime.strptime(resolve_date_str, "%Y-%m-%d").date().isoformat()
                print(f"Extracted Resolution Date: {resolve_date}")
            except ValueError as ve:
                print(f"Parsing Error for Resolution Date: {ve}")
    else:
        print("Follow-Ups section not found in MOM text.")

    # Print final message if no follow-up time is obtained
    return follow_up_time or "No follow-up meeting specified"

def summarize_text_with_gpt(transcription_text):
    prompt = f"""Summarise and shorten the following text for minutes of meeting generation without loss of context and important information:{transcription_text}"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional assistant helping generate meeting minutes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error calling GPT API: {e}")
        return None

# Step 3: Generate Minutes of Meeting with GPT
def generate_mom_with_gpt(transcription_text, datetime_now, num_attendees):
    transcription_text = summarize_text_with_gpt(transcription_text)
    prompt = f"""
    Please generate the Minutes of Meeting (MOM) in the following structured format:

    MeetMate
    Meeting Minutes

    Title: Weekly Meeting
    Date Time: {datetime_now}
    No of Attendees: {num_attendees}

    Short Summary
    Provide a brief summary of the key discussion points.

    Discussed Points
    Format as:
    1. Point 1 Title: 100-word summary including speaker contributions.
    2. Point 2 Title: 100-word summary including speaker contributions.

    [Detailed Speaker-wise Contribution & Conversation]
    Please format the following conversation into a detailed speaker-wise contribution of about 150-200 words in total without any mentions of gender and only referring to as Speaker 1, Speaker 2, etc.
    {transcription_text}

    Call to Action
    Format as: 
    Task name - SpeakerName as each task in each line like this format: 
1. Pancake Breakfast Initiative - Speaker 1
2. Flu Prevention Posters - Speaker 3

    Follow-Ups
    Provide any follow-up as specified date and time in the format: YYYY-MM-DD HH:MM and give only the time and no other sentence/words along with it, else if there is no explicit follow-up meeting mentioned in the audio, then it should say "No follow up meetings".
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional assistant helping generate meeting minutes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error calling GPT API: {e}")
        return None

# Step 5: Main Workflow
def main():
    audio_file_name = sys.argv[1]
    print("Calling Speech-to-Text API...")
    response_data = get_speech_to_text_response(audio_file_name)
    if not response_data:
        print("Speech-to-Text API failed.")
        return

    print("Merging diarized phrases...")
    diarised_text, max_speaker = process_and_merge_diarization(response_data)
    num_attendees = max_speaker if max_speaker > 0 else "Unknown"
    # Store diarized text in Upstash Redis
    redis_client.set("diarised-output", diarised_text)
    # Optionally, store the number of attendees as well
    redis_client.set("num_attendees", num_attendees)
    # Get current DateTime for MOM
    datetime_now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    print("Generating Minutes of Meeting using GPT API...")
    mom_text = generate_mom_with_gpt(diarised_text, datetime_now, num_attendees)

    if mom_text:
        # Save MOM text to Redis
        redis_client.set("minutes_of_meeting", mom_text)

        # Extract follow-up time and resolve date
        follow_up_time = extract_start_time_and_resolve_date_from_gpt_with_nlp(mom_text)
        if follow_up_time == "No follow-up meeting specified":
            print("No follow-up meeting specified. Skipping meeting creation.")
            redis_client.set("follow_up_time", "No follow-up meeting specified")
        else:
            try:
                # Validate ISO format before passing
                follow_up_time = datetime.fromisoformat(follow_up_time).isoformat()
                print("Creating meeting...")
                create_meeting(
                    service=authenticate_user(),
                    summary="Follow-up Meeting",
                    description="Follow-up based on MOM output",
                    start_time=follow_up_time,
                    time_zone='IST'
                )
                redis_client.set("follow_up_time", follow_up_time)
            except ValueError:
                print("Invalid follow-up time format. Skipping meeting creation.")
    else:
        print("Failed to generate Minutes of Meeting.")

if __name__ == "__main__":
    redis_client.set("follow_ups_link","")
    if len(sys.argv) < 2:
        print("Usage: python diarize_MOM.py <audio_file_path>")
        sys.exit(1)
    
    # Get the file path from the command-line argument
    main()
