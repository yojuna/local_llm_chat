import os
import base64
import streamlit as st
import json
import pandas as pd
# from helper import (
#     playwright_install,
#     add_download_options
# )
# from task import task
# from text_to_speech import text_to_speech

from scrapegraphai.graphs import SpeechGraph, SmartScraperGraph

st.set_page_config(page_title="local LLM powered smart web crawler", page_icon="🕷️", layout="wide", initial_sidebar_state="auto", menu_items=None)

def task(key:str, url:str, prompt:str, model:str, base_url=None):
    """ 
    Task that execute the scraping:
        Arguments:
        - key (str): key of the model
        - url (str): url to scrape 
        - prompt (str): prompt
        - model (str): name of the model
        Return:
        - results_df["output"] (dict): result as a dictionary
        - results_df (pd.Dataframe()): result as padnas df
    """ 
    if base_url is not None:
        graph_config = {
            "llm": {
                "api_key": key,
                "model": model,
            },
        }
    else: 
        graph_config = {
        "llm": {
            "api_key": key,
            "model": model,
            "openai_api_base": base_url,
        },
}

    # ************************************************
    # Create the SmartScraperGraph instance and run it
    # ************************************************

    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        # also accepts a string with the already downloaded HTML code
        source=url,
        config=graph_config
    )

    result = smart_scraper_graph.run()
    return result

def text_to_speech(api_key: str, prompt: str, url: str):
    """Reads text after the prompt from a given URL.

    Args:
        - api_key (str): OpenAI API key
        - prompt (str): Prompt to use
        - url (str): URL to scrape
    Returns:
        - str: Path to the generated audio file
    """
    llm_config = {"api_key": api_key}
    
    # Define the name of the audio file
    audio_file = "audio_result.mp3"

    # Create and run the speech summary graph
    speech_summary_graph = SpeechGraph(prompt, url, llm_config, audio_file)
    return speech_summary_graph.run()


def playwright_install():
    """
    Install playwright browsers
    https://discuss.streamlit.io/t/using-playwright-with-streamlit/28380/11
    """
    with st.spinner("Setting up playwright 🎭"):
        os.system("playwright install")
        os.system('playwright install-deps')


def add_download_options(result: str):
    """
    Adds download buttons for graph result.
    """
    st.download_button(
        label="Download JSON",
        data=json.dumps(result, indent=4),
        file_name="scraped_data.json",
        mime="application/json"
    )

    df = pd.DataFrame(result)
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="scraped_data.csv",
        mime="text/csv"
    )


# Install playwright browsers
playwright_install()

def save_email(email):
    with open("mails.txt", "a") as file:
        file.write(email + "\n")

with st.sidebar:
    # st.write("Official demo for [Scrapegraph-ai](https://github.com/VinciGit00/Scrapegraph-ai) library")
    # st.markdown("""---""")
    st.write("# Usage Examples")
    st.write("## Prompt 1")
    st.write("- Give detailed descriptions of all the product listings on this page")
    st.write("## Prompt 2")
    st.write("- Get links and detailed descriptions of all the relevant listings on this page")
    # st.write("## Prompt 3")
    # st.write("- List me all the images with their visual description")
    # st.write("## Prompt 4")
    # st.write("- Read me the summary of the news")
    # st.markdown("""---""")
    # st.write("You want to suggest tips or improvements? Contact me through email to mvincig11@gmail.com")

st.title("LLM powered web crawler and scraper")
# left_co, cent_co, last_co = st.columns(3)
# with cent_co:
#     st.image("assets/scrapegraphai_logo.png")

# key = st.text_input("Openai API key", type="password")
# key = st.secrets.openai_key
key = st.text_input(label = ":key: OpenAI Key:", help="Required for ChatGPT-4, ChatGPT-3.5, GPT-3, GPT-3.5 Instruct.",type="password")

model = st.radio(
    "Select the model",
    ["gpt-4", "gpt-4o", "gpt-3.5-turbo"],
    index=0,
)


link_to_scrape = st.text_input("Link to scrape")
prompt = st.text_input("Write the prompt")
url = st.text_input("base url (optional)")

if st.button("Run the program", type="primary"):
    if not key or not model or not link_to_scrape or not prompt:
        st.error("Please fill in all fields except the base URL, which is optional.")
    else:
        st.write("Scraping phase started ...")

        if model == "text-to-speech":
            res = text_to_speech(key, prompt, link_to_scrape)
            st.write(res["answer"])
            st.audio(res["audio"])
        else:
            # Pass url only if it's provided
            if url:
                graph_result = task(key, link_to_scrape, prompt, model, base_url=url)
            else:
                graph_result = task(key, link_to_scrape, prompt, model)

            print(graph_result)
            st.write("# Answer")
            st.write(graph_result)
            add_download_options(graph_result)
            
            # links = []
            # for data in graph_result['listings']:
            #     links = data['link']

            if graph_result and graph_result['listings'][0]['link']:
                st.write("# Add to the master db")

                # add_download_options(graph_result)
                links = [data['link'] for data in graph_result['listings']]

                with st.container():
                # Radio buttons for dataset choice
                    for link in links:
                        chosen_dataset = st.checkbox(link, key=link)

                print(graph_result)
                print(links)




# {'listings': [{'title': 'Standard-Haube Metall', 'description': 'Unser Klassiker ist in elf Norm-Abmessungen für jedes Förderband verwendbar.', 'link': 'https://www.achenbach-mt.de/abdeckhauben/standard-haube-metall'}, 
# {'title': 'Standard-Haube Kunststoff', 'description': 'Organit Hart-PVC Abdeckhauben ergänzen das Produktportfolio für sensible Branchen.', 'link': 'https://www.achenbach-mt.de/abdeckhauben/standard-haube-kunststoff'}, 
# {'title': 'Individuelle Hauben', 'description': 'A-Flex-System, Jumbo-Haube, Arena oder Stichbogen-Haube individuell für Ihr Projekt.', 'link': 'https://www.achenbach-mt.de/abdeckhauben/individuelle-hauben'}, 
# {'title': 'Hauben Befestigungen', 'description': 'Entdecken Sie Befestigungssysteme und Zubehör für unsere Metallhauben.', 'link': 'https://www.achenbach-mt.de/abdeckhauben/hauben-befestigungen'}]}


# left_co2, *_, cent_co2, last_co2, last_c3 = st.columns([1] * 18)

# with cent_co2:
#     discord_link = "https://discord.com/invite/gkxQDAjfeX"
#     discord_logo = base64.b64encode(open("assets/discord.png", "rb").read()).decode()
#     st.markdown(
#         f"""<a href="{discord_link}" target="_blank">
#         <img src="data:image/png;base64,{discord_logo}" width="25">
#         </a>""",
#         unsafe_allow_html=True,
#     )

# with last_co2:
#     github_link = "https://github.com/VinciGit00/Scrapegraph-ai"
#     github_logo = base64.b64encode(open("assets/github.png", "rb").read()).decode()
#     st.markdown(
#         f"""<a href="{github_link}" target="_blank">
#         <img src="data:image/png;base64,{github_logo}" width="25">
#         </a>""",
#         unsafe_allow_html=True,
#     )

# with last_c3:
#     twitter_link = "https://twitter.com/scrapegraphai"
#     twitter_logo = base64.b64encode(open("assets/twitter.png", "rb").read()).decode()
#     st.markdown(
#         f"""<a href="{twitter_link}" target="_blank">
#         <img src="data:image/png;base64,{twitter_logo}" width="25">
#         </a>""",
#         unsafe_allow_html=True,
#     )