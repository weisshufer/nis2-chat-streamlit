import anthropic
import urllib.request
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import pymupdf
from data import languages, anthropic_models, openai_models, human_prompt
from utils import extract_text_from_pdf, prompt_generator
from openai import OpenAI

nis_file = None
anthropic_api_key = None
ai_model = None
openai_api_key = None

st.set_page_config(page_title="Chat with NIS2",
                   page_icon=None,
                   layout="centered",
                   initial_sidebar_state="expanded",
                   menu_items=None)

with st.sidebar:
  st.title("📝 Chat with NIS2 | Settings")
  option_manufacture = st.selectbox("Choose a AI Provider?",
                                    ("Anthropic", "OpenAI"))

  if option_manufacture == "Anthropic":
    ai_model = st.selectbox("Choose a model?", (anthropic_models.values()))
    anthropic_api_key = st.text_input("Anthropic API Key",
                                      key="file_qa_anthropic_api_key",
                                      type="password")

  if option_manufacture == "OpenAI":
    ai_model = st.selectbox("Choose a model?", (openai_models.values()))
    openai_api_key = st.text_input("OpenAI API Key",
                                   key="file_qa_openai_api_key",
                                   type="password")

  prompt_input = st.text_area(label="Enter your prompt",
                              value=human_prompt,
                              key="file_qa_human_prompt",
                              height=500)

  st.divider()
  st.markdown("""Made with ❤️ in Munich, Germany 🇩🇪
  by [Oleksii Fischer](https://www.linkedin.com/in/weisshufer/)
      """)

st.title("📝 Chat with NIS2")
st.markdown("""Hi everyone, thank you for your interest in my project. 

This project was created to help you understand NIS 2 without spending a lot of time and money.

**About this Service:**
1. It is based on the official document provided by the European Union. 
2. The document is available in different languages. 
3. You can ask questions in any language, regardless of the text of the document. 

**HOW TO START:**
- To start using the service, just enter your API key from OpenAI or Anthropic and select the desired model in Sidebar. 
- Then, you can ask questions in any language, regardless of the text of the document.

The data is taken from the [official resource of the European Parliament](https://eur-lex.europa.eu/eli/dir/2022/2555/oj).

⚠️ IMPORTANT: Since the document is quite large, a very large use of tokens is possible."""
            )
language_option = st.selectbox("Choose a document language:",
                               (languages.values()))

if language_option:
  language_key = list(languages.keys())[list(
      languages.values()).index(language_option)]
  nis_file = urllib.request.urlretrieve(
      f"https://eur-lex.europa.eu/legal-content/{language_key}/TXT/PDF/?uri=CELEX:32022L2555",
      "nis.pdf")

st.divider()

if nis_file:
  st.header(f"NIS2 in {language_option}")
  pdf_viewer("nis.pdf", height=500)

  st.subheader("Chat with NIS2")
  question = st.text_input(
      "Ask something about the article",
      placeholder="Can you give me a short summary?",
      disabled=not nis_file,
  )

  extracting = extract_text_from_pdf("nis.pdf")
  if extracting:
    st.spinner("Extracting text from PDF...")
  with open("output.txt", "r") as file:
    prompt = prompt_generator(prompt_input,
                              file_data=file.read(),
                              question=question,
                              language=language_option)

  if option_manufacture == "OpenAI" and ai_model:
    model_code = list(openai_models.keys())[list(
        openai_models.values()).index(ai_model)]
    if nis_file and question and not openai_api_key:
      st.info("Please add your OpenAI API key to continue.")

    client = OpenAI(api_key=openai_api_key)
    if question:
      try:
        response = client.chat.completions.create(model=f"{model_code}",
                                                  messages=[{
                                                      "role":
                                                      "system",
                                                      "content":
                                                      f"{prompt}"
                                                  }, {
                                                      "role":
                                                      "user",
                                                      "content":
                                                      f"{question}"
                                                  }])
        st.write("### Answer")
        st.markdown(response.choices[0].message.content)
      except Exception as e:
        st.error(f"Error: {e}")

  if option_manufacture == "Anthropic" and ai_model:
    model_code = list(anthropic_models.keys())[list(
        anthropic_models.values()).index(ai_model)]
    if nis_file and question and not anthropic_api_key:
      st.info("Please add your Anthropic API key to continue.")
    if question:
      client = anthropic.Client(api_key=anthropic_api_key)
      try:
        response = client.messages.create(model=str(model_code),
                                          max_tokens=1000,
                                          temperature=0,
                                          system=prompt,
                                          messages=[{
                                              "role":
                                              "user",
                                              "content": [{
                                                  "type": "text",
                                                  "text": f"{question}"
                                              }]
                                          }])
        st.write("### Answer")
        st.markdown(response.content[0].text)
      except Exception as e:
        st.error(f"Error: {e}")
