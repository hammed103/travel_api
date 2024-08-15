import streamlit as st
from llamaapi import LlamaAPI
import random
from st_copy_to_clipboard import st_copy_to_clipboard



class BioGenerator:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def generate_bio(self, profile, previous_bio=None, feedback=None):
        system_prompt = "You are an AI assistant creating professional bios for travel agents."
        user_prompt = self._create_user_prompt(profile, previous_bio, feedback)

        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 300
        }

        try:
            response = self.llama.run(api_request_json)
            content = response.json()['choices'][0]['message']['content']
            return self._post_process_content(content)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

    def _create_user_prompt(self, profile, previous_bio=None, feedback=None):
        prompt = f"""Generate a professional and engaging bio for a travel agent with the following details:
        Name: {profile.get('name', '')}
        Years of Experience: {profile.get('years_experience', '')}
        Specialties: {', '.join(profile.get('specialties', []))}
        Certifications: {', '.join(profile.get('certifications', []))}
        Languages: {', '.join(profile.get('languages', []))}
        Favorite Destination: {profile.get('favorite_destination', '')}
        Travel Style: {profile.get('travel_style', '')}
        Client Focus: {profile.get('client_focus', '')}
        Unique Selling Point: {profile.get('unique_selling_point', '')}
        Recent Achievement: {profile.get('recent_achievement', '')}
        Personal Travel Goal: {profile.get('personal_travel_goal', '')}
        Additional Information: {profile.get('additional_info', '')}

        The bio should be approximately 150-200 words long, highlight the agent's expertise, unique qualities, and personal touch. It should be immediately usable without any need for adjustment. Start with "I am" or "As a travel agent, I".
        """

        if previous_bio and feedback:
            prompt += f"""
            
            Previous bio:
            {previous_bio}

            Please revise the bio based on this feedback:
            {feedback}

            Incorporate the feedback while maintaining the overall professional tone and highlighting key aspects of the agent's profile.
            """

        return prompt

    def _post_process_content(self, content):
        lines = content.split('\n')
        while lines and (not lines[0].strip() or ':' in lines[0]):
            lines.pop(0)
        return '\n'.join(lines).strip()




def profile_page():
    st.title("Travel Agent Profile")

    # Initialize session state for profile data if it doesn't exist
    if 'profile' not in st.session_state:
        st.session_state.profile = generate_random_profile()

    # Display current profile
    display_profile()

    # Edit profile button
    if st.button("Edit Profile"):
        st.session_state.editing = True
        st.rerun()

    # Edit mode
    if st.session_state.get('editing', False):
        edit_profile()

    # Bio generation
    bio_generator = BioGenerator()
    
    if 'ai_bio' not in st.session_state:
        if st.button("Generate AI Bio"):
            with st.spinner("Generating bio..."):
                generated_bio = bio_generator.generate_bio(st.session_state.profile)
                if generated_bio:
                    st.session_state.ai_bio = generated_bio
                    st.rerun()
    
    if 'ai_bio' in st.session_state:
        st.subheader("AI-Generated Bio")
        st.markdown(f'<div style="border:1px solid #ddd; padding:10px; border-radius:5px; background-color: #f9f9f9;">{st.session_state.ai_bio}</div>', unsafe_allow_html=True)
        
        if st.button("Copy Bio"):
            # Render copy to clipboard button
            st_copy_to_clipboard(st.session_state.ai_bio)
            
        
        if st.button("Set as Profile Bio"):
            st.session_state.profile['bio'] = st.session_state.ai_bio
            st.success("Bio set as profile bio!")
        
        feedback = st.text_area("How did I do? (Anything you want to add/remove?)", placeholder="E.g., Add more details about my specialties, remove the mention of specific destinations")
        if st.button("Regenerate Bio"):
            with st.spinner("Regenerating bio..."):
                regenerated_bio = bio_generator.generate_bio(st.session_state.profile, st.session_state.ai_bio, feedback)
                if regenerated_bio:
                    st.session_state.ai_bio = regenerated_bio
                    st.rerun()



def generate_random_profile():
    return {
        "name": random.choice(["Emma Thompson", "Michael Chen", "Sophia Rodriguez", "Alex Kim"]),
        "years_experience": random.randint(1, 20),
        "specialties": random.sample(["Luxury Travel", "Adventure Tours", "Family Vacations", "Eco-Tourism", "Cultural Experiences"], 3),
        "certifications": random.sample(["Certified Travel Associate", "Accredited Cruise Counselor", "Destination Specialist", "Luxury Travel Specialist"], 2),
        "languages": random.sample(["English", "Spanish", "French", "Mandarin", "German"], 2),
        "favorite_destination": random.choice(["Bali", "Paris", "Tokyo", "Machu Picchu", "Santorini"]),
        "travel_style": random.choice(["Adventurous", "Luxury", "Budget-friendly", "Cultural immersion", "Relaxation"]),
        "client_focus": random.choice(["Families", "Solo travelers", "Couples", "Group tours", "Corporate clients"]),
        "unique_selling_point": "",
        "recent_achievement": "",
        "personal_travel_goal": "",
        "additional_info": "",
        "bio": ""
    }

def display_profile():
    profile = st.session_state.profile
    st.markdown("""
    <style>
    .profile-box {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        background-color: #f8f8f8;
        margin-bottom: 20px;
    }
    .profile-header {
        font-size: 24px;
        color: #4CAF50;
        margin-bottom: 15px;
    }
    .profile-item {
        margin-bottom: 10px;
    }
    .profile-label {
        font-weight: bold;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="profile-box">', unsafe_allow_html=True)
    st.markdown('<div class="profile-header">Your Profile</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Name:</span> {profile["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Years of Experience:</span> {profile["years_experience"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Specialties:</span> {", ".join(profile["specialties"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Certifications:</span> {", ".join(profile["certifications"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Languages:</span> {", ".join(profile["languages"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Favorite Destination:</span> {profile["favorite_destination"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Travel Style:</span> {profile["travel_style"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-item"><span class="profile-label">Client Focus:</span> {profile["client_focus"]}</div>', unsafe_allow_html=True)
    if profile['unique_selling_point']:
        st.markdown(f'<div class="profile-item"><span class="profile-label">Unique Selling Point:</span> {profile["unique_selling_point"]}</div>', unsafe_allow_html=True)
    if profile['recent_achievement']:
        st.markdown(f'<div class="profile-item"><span class="profile-label">Recent Achievement:</span> {profile["recent_achievement"]}</div>', unsafe_allow_html=True)
    if profile['personal_travel_goal']:
        st.markdown(f'<div class="profile-item"><span class="profile-label">Personal Travel Goal:</span> {profile["personal_travel_goal"]}</div>', unsafe_allow_html=True)
    if profile['additional_info']:
        st.markdown(f'<div class="profile-item"><span class="profile-label">Additional Information:</span> {profile["additional_info"]}</div>', unsafe_allow_html=True)
    if profile['bio']:
        st.markdown('<div class="profile-item"><span class="profile-label">Profile Bio:</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="border:1px solid #ddd; padding:10px; border-radius:5px; background-color: #ffffff;">{profile["bio"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def edit_profile():
    profile = st.session_state.profile
    
    profile['name'] = st.text_input("Name", profile['name'])
    profile['years_experience'] = st.number_input("Years of Experience", min_value=0, max_value=50, value=profile['years_experience'])
    default_specialties = ["Luxury Travel", "Adventure Tours", "Family Vacations", "Eco-Tourism", "Cultural Experiences", 
                           "Cruise Packages", "Honeymoon Planning", "Business Travel", "Solo Travel", "Group Tours", 
                           "Wellness Retreats", "Food and Wine Tours", "Voluntourism", "Ski Vacations", "Beach Getaways"]
    custom_specialty = st.text_input("Add a custom specialty")
    if custom_specialty:
        default_specialties.append(custom_specialty)
    profile['specialties'] = st.multiselect("Specialties", options=default_specialties, default=profile['specialties'])

    # Modified Certifications field
    default_certifications = ["Certified Travel Associate", "Accredited Cruise Counselor", "Destination Specialist", 
                              "Luxury Travel Specialist", "Adventure Travel Specialist", "Family Travel Specialist", 
                              "Group Travel Specialist", "Sustainable Tourism Certification", "Accessible Travel Advocate"]
    custom_certification = st.text_input("Add a custom certification")
    if custom_certification:
        default_certifications.append(custom_certification)
    profile['certifications'] = st.multiselect("Certifications", options=default_certifications, default=profile['certifications'])

    # Modified Languages field
    default_languages = ["English", "Spanish", "French", "Mandarin", "German", "Italian", "Japanese", "Arabic", 
                         "Portuguese", "Russian", "Hindi", "Korean"]
    custom_language = st.text_input("Add a custom language")
    if custom_language:
        default_languages.append(custom_language)
    profile['languages'] = st.multiselect("Languages", options=default_languages, default=profile['languages'])

    profile['favorite_destination'] = st.text_input("Favorite Destination", profile['favorite_destination'])
    profile['travel_style'] = st.selectbox("Travel Style", 
        ["Adventurous", "Luxury", "Budget-friendly", "Cultural immersion", "Relaxation", "Eco-conscious", "Off-the-beaten-path"],
        index=["Adventurous", "Luxury", "Budget-friendly", "Cultural immersion", "Relaxation", "Eco-conscious", "Off-the-beaten-path"].index(profile['travel_style']))
    profile['client_focus'] = st.selectbox("Client Focus", 
        ["Families", "Solo travelers", "Couples", "Group tours", "Corporate clients", "Seniors", "Students", "LGBTQ+ travelers"],
        index=["Families", "Solo travelers", "Couples", "Group tours", "Corporate clients", "Seniors", "Students", "LGBTQ+ travelers"].index(profile['client_focus']))
    profile['unique_selling_point'] = st.text_input("Unique Selling Point", profile['unique_selling_point'], 
        help="What sets you apart from other travel agents?",
        placeholder="E.g., Specialization in off-the-beaten-path adventures")
    profile['recent_achievement'] = st.text_input("Recent Achievement", profile['recent_achievement'], 
        help="Any recent award, recognition, or milestone",
        placeholder="E.g., Named Top Adventure Travel Agent 2023")
    profile['personal_travel_goal'] = st.text_input("Personal Travel Goal", profile['personal_travel_goal'], 
        help="A travel-related personal goal or aspiration",
        placeholder="E.g., Visit all 7 continents by 2025")
    profile['additional_info'] = st.text_area("Additional Information", profile['additional_info'], 
        help="Any other details you'd like to include in your bio",
        placeholder="E.g., Passion for sustainable travel, unique experiences offered")

    if st.button("Save Profile"):
        st.session_state.profile = profile
        st.session_state.editing = False
        st.rerun()

def generate_ai_bio(feedback=""):
    profile = st.session_state.profile
    llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")
    tone = random.choice(["friendly", "professional", "enthusiastic", "casual", "formal"])
    writing_style = random.choice(["conversational", "descriptive", "persuasive", "narrative", "expository"])
    personality = random.choice(["warm", "confident", "humorous", "empathetic", "adventurous"])

    
    prompt = f"""Generate a professional and engaging bio for a travel agent, write  content directly without any meta-commentary or introducxtory phrases like Here is ..  write in the first-person. Make sure you be creative use a {tone} tone with a {writing_style} writing styles . Use the following details:
    Name: {profile['name']}
    Years of Experience: {profile['years_experience']}
    Specialties: {', '.join(profile['specialties'])}
    Certifications: {', '.join(profile['certifications'])}
    Languages: {', '.join(profile['languages'])}
    Favorite Destination: {profile['favorite_destination']}
    Travel Style: {profile['travel_style']}
    Client Focus: {profile['client_focus']}
    Unique Selling Point: {profile['unique_selling_point']}
    Recent Achievement: {profile['recent_achievement']}
    Personal Travel Goal: {profile['personal_travel_goal']}
    Additional Information: {profile['additional_info']}

    The bio should be approximately 150-250 words long, highlight the agent's expertise, unique qualities, and personal touch. ".
    
    Additional feedback: {feedback}"""

    response = llama.run({
        "model": "llama-70b-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    })

    st.session_state.ai_bio = response.json()['choices'][0]['message']['content']

def copy_to_clipboard(text):
    st.write("Bio copied to clipboard!")
    st.session_state.clipboard = text

# Add this to your sidebar
def add_profile_to_sidebar():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Profile"):
        st.session_state.current_page = "profile"