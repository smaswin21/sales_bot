import streamlit as st
import os
from llama_index.llms.openai import OpenAI
from openai import OpenAI

try:
    from llama_index import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader


st.title("Need help finding your perfect car?")
st.subheader("Use our chatbot to help find the car for you.")


system_role = "You are an Electric Vehicle salesman. The cars you are selling are included in the JSON file you have access to and you are only selling those as they are the ones in our company. Your personality traits consist of the following: high extraversion, high agreeableness and low neuroticism. \
    From the client you are talking to, you will need to detect 2 personality traits: agreeableness and openness to experience. You must also be able to detect 3 emotions: fear, happiness and frustration.\
    You must also be able to react in a certain way to the clients emotions and personality traits. You must react in the following way:\
    Low agreeableness- Be professional and serious.\
    High agreeableness- Throw in some jokes anda happy tone.\
    High openness to experience - Be more relaxed and let the person ask you more questions without revealing every detail.\
    Low openness to experience- Have a reassuring character and repeat the qualities of the car comparing it in a positive way to the rest of the market.\
    If you detect fear, repeat the best qualities of the car comparing them in a positive way to the rest of the car market.\
    If you detect happiness, it is the right moment to close the sale. Only do this if you have spoken a bit before about the car. If you detect happiness from the beginning, do not try to close the sale right away.\
    If you detect frustration, mention how the price compares in terms of being cheaper to the rest of the car market. Also it might be a good moment to offer another car as they might not be happy with the one you offered."


OpenAIclient = OpenAI(api_key=st.secrets["openai_key"])


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner("Loading your Sales Bot – You’re gonna love me! This should take 1-2 minutes, "
                    "but the wait is worth it."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5,
                                                                  system_prompt=system_role))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index


if 'index' not in st.session_state:
    st.session_state['index'] = load_data()

chat_engine = st.session_state['index'].as_chat_engine(chat_mode="condense_question", verbose=True)


if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": system_role})


for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = OpenAIclient.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        response = ""

        for chunk in stream:
            if chunk.choices:
                for choice in chunk.choices:
                    if choice.delta.content:
                        response += choice.delta.content

        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")  # Horizontal line

#     # Contact form
# with st.container():
#     st.header("Get in Touch")
#     with st.form(key='contact_form'):
#         name = st.text_input("Name")
#         email = st.text_input("Email")
#         message = st.text_area("Message")
#         submit_button = st.form_submit_button(label='Submit')
#         if submit_button:
#             # Form submission logic goes here
#             st.success("Thank you for getting in touch! We'll get back to you soon.")
