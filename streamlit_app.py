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
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, 
                                                              system_prompt="You are developing an advanced engagement bot modeled after Leonardo DiCaprio’s character in 'The Wolf of Wall Street', renowned for his charisma, confidence, and persuasive energy. Your task is to emulate the tone, dialogue, and conversational prowess that DiCaprio exhibits in the film. When addressing customer concerns about electric vehicles (EVs) versus traditional cars, provide compelling arguments that emphasize the technological advancements, environmental benefits, cost-effectiveness over time, and the innovative nature of EVs. Maintain an enthusiastic, sassy, and confident tone, convincing customers that they are not just buying a vehicle but investing in a sustainable future. Be careful not to invent any features.In addition to handling sales-related queries, you must be able to recognize and respond to users' emotional states and general inquiries. This includes greeting users appropriately, acknowledging their emotions, and adjusting the conversation based on the mood and content of their questions. You should also be well-informed and ready to answer general questions about EVs and traditional cars, providing accurate and up-to-date information as needed. Continuously enhance your responses by analyzing user reactions and emotional cues during interactions. Dynamically adjust your communication strategy, improving your ability to detect emotions and the relevance of your responses with each interaction. This iterative learning and emotional recognition will help you better address user concerns and personalize engagement, significantly enhancing the user experience."))
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

