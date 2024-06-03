import anthropic
import urllib.request
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import pymupdf
from data import languages
from utils import extract_text_from_pdf, prompt_generator

nis_file = None

with st.sidebar:
  option = st.selectbox("Choose a AI model?", ("Anthropic Claude Opus"))
  anthropic_api_key = None
  openai_api_key = None

  if option == "Anthropic Claude Opus":
    anthropic_api_key = st.text_input("Anthropic API Key",
                                      key="file_qa_anthropic_api_key",
                                      type="password")
  if option == "OpenAI GPT4":
    openai_api_key = st.text_input("OpenAI API Key",
                                   key="file_qa_openai_api_key",
                                   type="password")

st.title("📝 Chat with NIS2")

col1, col2 = st.columns(2)

with col1:
  language_option = st.selectbox("Choose a document Language:",
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
  pdf_viewer("nis.pdf", width=1200, height=500)

  st.subheader("Chat with NIS2")
  question = st.text_input(
      "Ask something about the article",
      placeholder="Can you give me a short summary?",
      disabled=not nis_file,
  )

  if nis_file and question and not anthropic_api_key:
    st.info("Please add your Anthropic API key to continue.")

  if nis_file and question and anthropic_api_key:

    extracting = extract_text_from_pdf("nis.pdf")
    if extracting:
      st.spinner("Extracting text from PDF...")
    with open("output.txt", "r") as file:
      prompt = prompt_generator(file_data=file.read(),
                                question=question,
                                language=language_option)

    client = anthropic.Client(api_key=anthropic_api_key)
    response = client.messages.create(model="claude-3-haiku-20240307",
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
