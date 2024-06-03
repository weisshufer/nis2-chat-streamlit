import pymupdf
import anthropic
from data import human_prompt


def extract_text_from_pdf(pdf_path):
  doc = pymupdf.open(pdf_path)  # open a document
  out = open("output.txt", "wb")  # create a text output
  for page in doc:  # iterate the document pages
    text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
    out.write(text)  # write text of page
    out.write(bytes((12, )))  # write page delimiter (form feed 0x0C)
  out.close()


def prompt_generator(prompt, file_data, question, language):
  prompt = f"""{prompt} + NIS-2 documentation:\n
  <documents>{file_data}</documents>
\n\nResponse language: {language}"""
  return prompt
