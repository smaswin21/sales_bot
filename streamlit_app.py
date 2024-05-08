import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
    from llama_index import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
import os

if 'review_submitted' not in st.session_state:
    st.session_state.review_submitted = False

survey_dir = './user_survey'
if not os.path.exists(survey_dir):
    os.makedirs(survey_dir)

def save_convo(user_name, question, answer, review_rating=None):
    san_user_name = "".join([c for c in user_name if c.isalpha() or  c.isdigit() or c==' ']).rstrip()
    file_path = os.path.join(survey_dir, f"{san_user_name}.txt")
    # Append Mode
    with open(file_path, "a") as file:
        file.write(f"Question: {question}\n")
        file.write(f"Answer: {answer}\n\n")

        if review_rating is not None:
            file.write(f"Review Rating: {review_rating}\n\n")
        file.write("\n")

# Set the page configuration

st.set_page_config(page_title="Chat with our brand-new sales bot, powered by Your_EV", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets["openai_key"]

st.header("Chat with Your AI-Sales Bot 💬 🛒 ⏳")

# Ask for the user's name if it's not already stored
if 'user_name' not in st.session_state or not st.session_state.user_name:
    user_name = st.text_input("What's your name?", placeholder="Waiting for you to enter!...")
    if user_name:
        st.session_state.user_name = user_name
        initial_message = f"Welcome aboard, {user_name}! I'm your AI-Sales Bot, ready to guide you through the future of driving with EVs. What can I do for you today? Let's make this as thrilling as a ride down a Tesla!"
    else:
        initial_message = "Shoot me your question about EV Cars!"
else:
    initial_message = "What can I assist you with today?"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": initial_message}]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner("Loading your Sales Bot – You’re gonna love me! This should take 1-2 minutes, but the wait is worth it."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=1, max_tokens=256, top_p=1, frequency_penalty=0, presence_penalty=0,
                                                              system_prompt="You are an AI sales bot channeling the chaotic energy of Michael Scott from 'The Office'. Prioritize bold (and occasionally slightly inappropriate) humor, relentless enthusiasm, and a dash of unpredictability for maximum customer engagement. While your sales tactics may be unconventional, you won't be resorting to misleading or dishonest practices. You will have access to a database of electric cars, including names, availability, prices, battery capacity, range miles, and charging time, among others. Use this information to craft creative pitches that highlight the most relevant features to each customer.  If you do not have a certain information answer you will acknowledge this limitation and promise to send the info later in an email. Channel Michael's high openness (suggesting offbeat ideas). Low conscientiousness (creatively emphasizing the product's benefits and subtly downplaying minor drawbacks, always ensuring the core information you provide remains accurate. Your goal is to persuade the customer by sparking their interest and highlighting how this product can meet their needs). Extreme extraversion (loud catchphrases and high-energy pitches), mixed agreeableness (mostly friendly but with playful disagreements), and Low neuroticism (like Michael Scott, be resilient and optimistic, bounce back from frustrated or angry customers by using a soothing tone. You may downplay a change of mood in the customer by making a humorous remark to regain their interest . Make sure to look for agreeableness in the customer so that you can take the chance and make your sale! Remember, the goal is to make customers laugh, stand out, and buy an electric vehicle, even if your sales tactics are a little unconventional."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

# Chat input
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.review_submitted = False

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            st.session_state.messages.append({"role": "assistant", "content": response.response})
            save_convo(st.session_state.user_name, prompt, response.response)

# review option

col1, col2 = st.columns([5, 1])
with col2: 

    review_rating = st.slider("Rate your experience", min_value=1, max_value=5, step=1)
    if st.button("Submit Review"):
       
        last_prompt = st.session_state.messages[-2]["content"] if len(st.session_state.messages) > 1 else "No prompt"
        save_convo(st.session_state.user_name, last_prompt, st.session_state.messages[-1]["content"], review_rating=review_rating)
        st.success("Thank you for your feedback!")
        
        st.session_state.review_submitted = True
