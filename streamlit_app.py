import streamlit as st
import json
import random
from llamaapi import LlamaAPI
import pandas as pd


import asyncio

#Just some streamlit related setup
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class TravelAgentPromotionTool:
    def __init__(self):
        api_token = "LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW"
        self.llama = LlamaAPI(api_token)

    def extract_info(self, summary):
        api_request_json = {
            'model': 'llama-70b-chat',
            'functions': [
                {
                    "name": "extract_travel_agent_info",
                    "description": "Extract travel agent information from the provided summary",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the travel agent"},
                            "experience": {"type": "string", "description": "Years of experience"},
                            "specialties": {"type": "array", "items": {"type": "string"}, "description": "List of specialties"},
                            "achievements": {"type": "string", "description": "Key achievements"},
                            "target_audience": {"type": "string", "description": "Target audience description"},
                            "unique_selling_points": {"type": "array", "items": {"type": "string"}, "description": "Unique selling points"},
                            "preferred_destinations": {"type": "array", "items": {"type": "string"}, "description": "Preferred or frequently booked destinations"}
                        },
                        "required": ["name", "experience", "specialties", "target_audience"]
                    }
                }
            ],
            'function_call': {'name': 'extract_travel_agent_info'},
            'messages': [
                {'role': 'user', 'content': f"Extract travel agent information from this summary:\n\n{summary}"}
            ],
        }
        
        response = self.llama.run(api_request_json)
        output = response.json()['choices'][0]['message']
        return output

    def generate_content(self, agent_info, content_type):
        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": "You are an AI assistant creating promotional content for travel agents. Generate content directly without any introductory phrases or meta-commentary. Generate content directly in the first-person"},
                {"role": "user", "content": f"Generate {content_type} for a travel agent with this information:\n{json.dumps(agent_info, indent=2)}\nCreate the content directly without any introductory phrases."},
            ],
            "max_tokens" : 2000
        }
           
        try:
            response = self.llama.run(api_request_json)
            content = response.json()['choices'][0]['message']['content']
            return self.post_process_content(content)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

    def post_process_content(self, content):
        introductory_phrases = [
            "Here's a", "Here is a", "Here's an", "Here is an",
            "This is a", "This is an", "I've created", "I have created",
            "Below is", "The following is"
        ]
        for phrase in introductory_phrases:
            if content.startswith(phrase):
                content = content[len(phrase):].lstrip()
        return content.strip()


def main():
    st.set_page_config(page_title="Travel Agent Promotion Tool", page_icon="✈️", layout="wide")
    tool = TravelAgentPromotionTool()

    st.title("✈️ AI-Powered Travel Agent Promotion Tool")

    page = st.sidebar.selectbox("Choose a page", ["Profile-based Content", "Summary-based Content"])

    if page == "Profile-based Content":
        profile_based_content(tool)
    else:
        summary_based_content(tool)


def summary_based_content(tool):
    st.header("Summary-based Content Generation")
    st.markdown("Enter a summary about yourself as a travel agent, and we'll generate content based on it!")

    summary = st.text_area("Enter your summary:", height=200)
    
    content_type = st.selectbox(
        "Select Content Type to Generate",
        ["Social Media Post", "Blog Post", "Promotional Offer", "Website Bio"]
    )

    if st.button("Generate Content"):
        if summary:
            with st.spinner("Generating content..."):
                agent_info = tool.extract_info(summary)
                generated_content = tool.generate_content(agent_info, content_type)
            
            if generated_content:
                st.subheader("Generated Content")
                st.write(generated_content)

                edited_content = st.text_area("Edit Your Content", value=generated_content, height=300)

                if st.button("Save Edited Content"):
                    st.success("Content saved successfully!")
                    st.session_state.saved_content = edited_content

        else:
            st.warning("Please enter a summary before generating content.")

    # Display saved content
    if 'saved_content' in st.session_state:
        st.header("Your Saved Content")
        st.write(st.session_state.saved_content)


def profile_based_content(tool):
    st.header("Profile-based Content Generation")

    st.markdown("Create engaging content to promote your travel agency!")


    # Sidebar for profile input
    st.sidebar.header("Your Profile")
    profile = {
        "name": st.sidebar.text_input("Your Name"),
        "experience": st.sidebar.text_input("Years of Experience"),
        "specialties": st.sidebar.text_input("Your Specialties (comma-separated)").split(','),
        "achievements": st.sidebar.text_area("Key Achievements"),
        "target_audience": st.sidebar.text_input("Target Audience")
    }

    # Main area for content generation
    st.header("Generate Content")
    content_type = st.selectbox(
        "Select Content Type",
        ["Social Media Post", "Blog Post", "Promotional Offer", "Website Bio"]
    )

    if st.button("Generate Content"):
        with st.spinner("Generating your content..."):
            generated_content = tool.generate_content(profile, content_type)
        
        if generated_content:
            st.subheader("Generated Content")
            st.write(generated_content)

            # Content editing
            edited_content = st.text_area("Edit Your Content", value=generated_content, height=300)

            if st.button("Save Edited Content"):
                st.success("Content saved successfully!")
                st.session_state.saved_content = edited_content

    # Display saved content
    if 'saved_content' in st.session_state:
        st.header("Your Saved Content")
        st.write(st.session_state.saved_content)

    # Additional features
    st.header("Additional Tools")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Content Calendar")
        if st.button("Generate Content Calendar"):
            calendar = generate_content_calendar()
            st.write(calendar)

    with col2:
        st.subheader("Hashtag Generator")
        if st.button("Generate Hashtags"):
            hashtags = generate_hashtags()
            st.write(" ".join(hashtags))

def generate_content_calendar():
    content_types = ["Social Media Post", "Blog Post", "Promotional Offer"]
    calendar = {}
    for i in range(7):
        day = (pd.Timestamp.now() + pd.Timedelta(days=i)).strftime("%A")
        calendar[day] = random.choice(content_types)
    return calendar

def generate_hashtags():
    travel_hashtags = ["#TravelAgent", "#Wanderlust", "#TravelTips", "#VacationPlanning", 
                       "#LuxuryTravel", "#AdventureAwaits", "#ExploreTheWorld", "#DreamDestinations"]
    return random.sample(travel_hashtags, 5)

if __name__ == "__main__":
    main()