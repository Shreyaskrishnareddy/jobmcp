import fitz  # PyMuPDF
from src.llm_provider import get_completion


def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file.

    Args:
        uploaded_file: The uploaded PDF file object.

    Returns:
        str: The extracted text.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def ask_llm(prompt, max_tokens=500):
    """
    Sends a prompt to the configured LLM provider and returns the response.

    Args:
        prompt (str): The prompt to send.
        max_tokens (int): Maximum tokens for the response.

    Returns:
        str: The response from the LLM.
    """
    return get_completion(prompt, max_tokens=max_tokens)
