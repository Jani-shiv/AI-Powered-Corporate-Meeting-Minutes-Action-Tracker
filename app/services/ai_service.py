"""
AI processing module for CorpMeet-AI application.
Contains functions to process meeting transcripts and extract structured data using OpenAI.
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def process_meeting_transcript(transcript_text):
    """
    Process meeting transcript using OpenAI to extract structured information.
    """

    # Check if API key is set, if not, fall back to mock data (or error out gracefully)
    if (
        not os.getenv("OPENAI_API_KEY")
        or os.getenv("OPENAI_API_KEY") == "sk-your-key-here"
    ):
        print("WARNING: OpenAI API Key not found. Using Mock Data.")
        return generate_mock_data(transcript_text)

    system_prompt = """
    You are an expert Corporate Secretary and AI Assistant. Your task is to analyze meeting transcripts and extract structured data.
    
    Return the output STRICTLY as a valid JSON object with the following schema:
    {
        "summary": ["point 1", "point 2", "point 3", "point 4"],
        "action_items": [
            {"task": "specific action", "owner": "person name", "deadline": "YYYY-MM-DD or 'Asap'"}
        ],
        "decisions": ["decision 1", "decision 2"],
        "sentiment": "Positive" | "Neutral" | "Negative" | "Tense" | "Productive",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    }
    
    Rules:
    1. Summary should be concise but professional.
    2. Extract at least 3-5 action items. If no specific deadline is mentioned, infer a reasonable one or use "TBD".
    3. Identify clear decisions.
    4. Determine the overall sentiment of the meeting.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",  # Use a cost-effective but capable model
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Analyze this meeting transcript:\n\n{transcript_text}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result_json = response.choices[0].message.content
        return json.loads(result_json)

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return generate_mock_data(transcript_text)


def chat_with_meeting_context(transcript_text, user_question):
    """
    Allow users to ask questions about the meeting.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return "AI features are not enabled. Please configure your API Key."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant answering questions about a specific meeting transcript. Answer based ONLY on the provided text.",
                },
                {
                    "role": "user",
                    "content": f"Transcript:\n{transcript_text}\n\nQuestion: {user_question}",
                },
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def generate_mock_data(transcript_text):
    """Fallback mock data generator for when API key is missing."""
    return {
        "summary": [
            "Discussed project timeline and key deliverables.",
            "Identified potential risks in the deployment phase.",
            "Agreed on the new marketing strategy for Q4.",
            "Team needs to focus on user testing feedback.",
        ],
        "action_items": [
            {
                "task": "Update documentation",
                "owner": "Sarah",
                "deadline": "2024-05-20",
            },
            {"task": "Fix login bug", "owner": "Mike", "deadline": "2024-05-18"},
            {"task": "Schedule client demo", "owner": "John", "deadline": "2024-05-25"},
        ],
        "decisions": [
            "Approved the new UI design.",
            "Postponed the feature launch by one week.",
        ],
        "sentiment": "Productive",
        "keywords": ["Strategy", "Budget", "Timeline", "Risk", "Launch"],
    }
