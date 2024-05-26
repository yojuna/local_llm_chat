# %%writefile streamlit_chat_ui.py
import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

from pathlib import Path
import pandas as pd
import os

data_dir_ = "data/hackmining"
# chat_mode_ = "condense_question"
chat_mode_ = "condense_plus_context"

system_prompt_ = "You are a technical research assistant and an expert in the domain of mining and mineral processing. \
                    You speacialize in recommending technical design parameters and are an expert in giving suggestions based on the corpus of technical documents provided. \
                    Be as helpful and descriptive as you can be. Always refer to the loaded technical documents and give references to the documents from where the information was found."

st.set_page_config(page_title="Chat with docs from your company's technical resources, powered by RWTH Aachen, LlamaIndex and Streamlit", page_icon="🦙", layout="wide", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("MAGIC: The Mining And Geotechnical Information Chatbot")
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



# List to hold datasets
if "datasets" not in st.session_state:
    datasets = {}
    # Preload datasets
    all_files_gen = Path(data_dir_).rglob("*")
    all_files = [f.resolve() for f in all_files_gen]
    for file in all_files:
        file_name = str(file)
        datasets[file_name] = file
    st.session_state["datasets"] = datasets
else:
    # use the list already loaded
    datasets = st.session_state["datasets"]

with st.sidebar:
    # Add facility to upload a dataset
    try:
        uploaded_files = st.file_uploader(":computer: Load the documents you need:", accept_multiple_files=True)
        index_no=0
        if uploaded_files:
            for uploaded_file in uploaded_files:
                print(uploaded_file)
                # Read in the data, add it to the list of available datasets. Give it a nice name.
                file_name = uploaded_file.name[:-4].capitalize()
                # datasets[file_name] = pd.read_csv(uploaded_file)
                datasets[file_name] = uploaded_file
                file_path = os.path.join(data_dir_, file_name)
                b = uploaded_file.getvalue()
                with open(file_path, "wb") as f:
                    f.write(b)
                # We want to default the radio button to the newly added dataset
                index_no = len(datasets)-1
    except Exception as e:
        st.error("File failed to load. Please select a valid data file.")
        print("File failed to load.\n" + str(e))

    # First we want to choose the dataset, but we will fill it with choices once we've loaded one
    dataset_container = st.empty()
    # Radio buttons for dataset choice
    dataset_files = [keyfile.split('/')[-1] for keyfile in datasets.keys()]
    chosen_dataset = dataset_container.radio(":bar_chart: referenced datasets:", dataset_files,index=index_no)#,horizontal=True,)
    # option = st.sidebar.selectbox('loaded datasets', all_files)

    # # Check boxes for model choice
    # st.write(":brain: Choose your model(s):")
    # # Keep a dictionary of whether models are selected or not
    # use_model = {}
    # for model_desc,model_name in available_models.items():
    #     label = f"{model_desc} ({model_name})"
    #     key = f"key_{model_desc}"
    #     use_model[model_desc] = st.checkbox(label,value=True,key=key)


# Display the datasets in a list of tabs
# Create the tabs
# tab_list = st.tabs(datasets.keys())

# # Load up each tab with a dataset
# for dataset_num, tab in enumerate(tab_list):
#     with tab:
#         # Can't get the name of the tab! Can't index key list. So convert to list and index
#         dataset_name = list(datasets.keys())[dataset_num]
#         st.subheader(dataset_name)
#         # st.dataframe(datasets[dataset_name],hide_index=True)

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
