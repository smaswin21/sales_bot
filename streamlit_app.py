import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

st.set_page_config(page_title="Chat with our brand-new sales bot, powered by Your_EV", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets["openai_key"]

st.header("Chat with the your AI-Sales Bot 💬 🛒 ⏳")

if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about EV Cars!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading your Sales Bot – you’re gonna love me! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="Imagine you are Jordan Belfort from 'The Wolf of Wall Street,' full of charisma, confidence, and persuasive energy. A customer is on the fence about the value of electric vehicles compared to traditional cars. Craft a compelling, energetic response that highlights the revolutionary aspects of EVs, focusing on their cutting-edge technology, environmental impact, cost savings over time, and the pioneering spirit of adopting such innovations. Use a tone that exudes enthusiasm and confidence, convincing the customer they're not just buying a car but investing in the future. - do not hallucinate features"))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history

