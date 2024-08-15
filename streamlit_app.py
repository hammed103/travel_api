import streamlit as st
import json
import random
import pandas as pd
from llamaapi import LlamaAPI
from st_copy_to_clipboard import st_copy_to_clipboard as stc
from streamlit_option_menu import option_menu
import asyncio
from proofreader import proofreader_page
from critique_post import critique_post_page
from alternative_words import alternative_words_page
from change_tone_style import change_tone_style_page
from profile_page import profile_page, add_profile_to_sidebar
from ai_blog_writer import ai_blog_writer
from fb_post_writer import fb_post_writer
from insta_caption import instagram_caption_generator_page
from advanced_postgenerator import advanced_post_generator
# Setup or get event loop
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

get_or_create_eventloop()

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
        return response.json()['choices'][0]['message']

    def generate_content(self, agent_info, content_type, content_settings):
        length_range = content_settings['length_range']
        tone = content_settings['tone']
        focus = content_settings['focus']
        language = content_settings['language']

        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": f"You are an AI assistant creating promotional content for travel agents. Generate content directly without any introductory phrases or meta-commentary. Generate content directly in the first-person. Use a {tone} tone, focus on {focus}, and write in {language}."},
                {"role": "user", "content": f"Generate a {content_type} for a travel agent with this information:\n{json.dumps(agent_info, indent=2)}\nThe content should be {length_range} words long. Create the content directly without any introductory phrases."},
            ],
            "max_tokens": 2000
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


    def generate_instagram_captions(self, keywords, caption_type, cta, audience, language):
        prompt = f"""As an Instagram expert and experienced content writer, 
        create 3 Instagram captions for a travel agent using these keywords: '{keywords}'.
        Guidelines:
        1) Front-Load: Place key info at the beginning.
        2) Optimize for {cta} Call-to-Action.
        3) Use no more than four relevant hashtags per caption.
        4) Use a {caption_type} tone.
        5) Target the {audience} audience.
        6) Include emojis for personality.
        7) Keep captions concise.
        8) Write in {language}.
        """

        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": "You are an AI assistant specialized in creating Instagram captions for travel agents."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000
        }

        try:
            response = self.llama.run(api_request_json)
            captions = response.json()['choices'][0]['message']['content']
            return captions
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None





def main():
    st.set_page_config(page_title="InteleTravel Promotion Tool", page_icon="✈️", layout="wide")
    tool = TravelAgentPromotionTool()

    # Custom CSS for InteleTravel theme with taller navbar
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Work Sans', sans-serif;
    }
    
    .stApp {
        background-color: white;
    }
    
    .stSidebar {
        background-color: #d50032;
        padding: 2rem;
    }
    
    .stSidebar .stSidebarNav {
        background-color: #d50032;
    }
    
    /* Adjustments for taller navbar */
    .stSidebar .stSidebarNav > ul {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    .stSidebar .stSidebarNav > ul > li {
        margin-bottom: 0.5rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        line-height: 1.2;
    }
    
    h1 {
        font-size: 3.5rem;
    }
    
    h2 {
        font-size: 2.35rem;
    }
    
    h3 {
        font-size: 1.875rem;
    }
    
    h4 {
        font-size: 1.5rem;
    }
    
    h5 {
        font-size: 1.25rem;
    }
    
    h6 {
        font-size: 1rem;
    }
    
    .stButton>button {
        background-color: #3d4ed7;
        color: white;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #1e255d;
    }
    
    a {
        color: #3d4ed7;
        font-weight: 600;
    }
    
    a:hover {
        color: #1e255d;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://info.inteletravel.com/hubfs/InT_StyleGuide_LogoHeader.svg", width=200)  # Replace with actual logo path
        st.title("InteleTravel ")
        
        selected = option_menu(
            menu_title=None,
            options=["Profile", "AI Blog Writer","Advanced Post Generator", "FB Post Writer", "Instagram Captions", 
                     "Proofreader", "Critique Post", "Alternative Words", "Change Tone"],
            icons=["person", "pencil-square","pencil-square", "facebook", "instagram", 
                   "check-circle", "chat-square-quote", "shuffle", "palette"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#d50032"},
                "icon": {"color": "white", "font-size": "16px"},  # Slightly larger icon
                "nav-link": {
                    "font-size": "16px",  # Slightly larger font
                    "text-align": "left", 
                    "margin": "0px", 
                    "--hover-color": "#1e255d",
                    "color": "white",
                    "padding": "0.75rem 1rem",  # Increased padding for taller navbar items
                },
                "nav-link-selected": {"background-color": "#1e255d"},
            }
        )

    # Page content based on selection
    if selected == "Profile":
        profile_page()
    elif selected == "AI Blog Writer":
        ai_blog_writer()
    elif selected == "Advanced Post Generator":
        advanced_post_generator()
    elif selected == "FB Post Writer":
        fb_post_writer()
    elif selected == "Instagram Captions":
        instagram_caption_generator_page(tool)
    elif selected == "Proofreader":
        proofreader_page()
    elif selected == "Critique Post":
        critique_post_page()
    elif selected == "Alternative Words":
        alternative_words_page()
    elif selected == "Change Tone":
        change_tone_style_page()


def generate_prompt(summary, platform):
    # Template for generating the prompt
    system_prompt = "I need you to be a prompt engineer and tailor a good prompt for us. "
    action_prompt = f"The prompt should be tailored for {platform}, focusing on the following summary:\n\n{summary}\n\n"
    final_prompt = system_prompt + action_prompt + "The AI should act as a professional content writer and create engaging content for this platform."

    return final_prompt

def prompt_generator_page():
    st.title("Prompt Generator For ChatGPT")

    st.write("Generate tailored prompts for promoting your posts on different platforms.")

    # Input fields
    summary = st.text_area("What do you want to promote?", help="Enter the details of what you want to promote.")
    platform = st.selectbox("Platform", ["ChatGPT", "Claude", "Other AI Models"], help="Select the platform where you'll use the prompt.")

    if st.button("Generate Prompt"):
        if summary:
            prompt = generate_prompt(summary, platform)
            st.subheader("Your Generated Prompt")
            st.text_area("Generated Prompt", value=prompt, height=200)
        else:
            st.warning("Please enter what you want to promote.")






if __name__ == "__main__":
    main()