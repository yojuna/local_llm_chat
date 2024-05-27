# %%writefile streamlit_chat_ui.py
import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

data_dir_ = "./data/hackmining"
# chat_mode_ = "condense_question"
chat_mode_ = "condense_plus_context"

system_prompt_ = "You are a technical research assistant and an expert in the domain of mining and mineral processing. \
                    You speacialize in recommending technical design parameters and are an expert in giving suggestions based on the corpus of technical documents provided. \
                    Be as helpful and descriptive as you can be. Always refer to the loaded technical documents and give references to the documents from where the information was found."

st.set_page_config(page_title="Chat with docs from your company's technical resources, powered by RWTH Aachen, LlamaIndex and Streamlit", page_icon="🦙", layout="wide", initial_sidebar_state="auto", menu_items=None)
# openai.api_key = st.secrets.openai_key
openai.api_key = st.text_input(label = ":key: OpenAI Key:", help="Required for ChatGPT-4, ChatGPT-3.5, GPT-3, GPT-3.5 Instruct.",type="password")

st.title("Plant Design Technical Assistant")
st.info("", icon="📃")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]

@st.cache_resource(show_spinner=True)
def load_data():
    with st.spinner(text="Loading and indexing the technical docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir=data_dir_, recursive=True)
        docs = reader.load_data()
        # llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert o$
        # index = VectorStoreIndex.from_documents(docs)
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4", temperature=0.5, system_prompt=system_prompt_))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode=chat_mode_, verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
