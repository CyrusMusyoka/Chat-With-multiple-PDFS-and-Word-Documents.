import streamlit as st
# Python library used for building interactive web applications for data science
# and machine learning projects.
# It allows developers to create user-friendly interfaces directly from Python scripts
# making graphical user interface (GUI)
from dotenv import load_dotenv
# streamlit interface

from PyPDF2 import PdfReader
# used for reading content of processed pdf

from langchain.text_splitter import CharacterTextSplitter
# langchain.text_splitter import CharacterTextSplitter create chunks of a text from processed documents
# langchain allows access of API keys
# interact to Interact with language models llm
# use of langchain to chat with multiple PDF files using ChatGPT API, AND HuggingFace Language Models
# divides raw texts from processed pdf into chunks of texts


# for creating vector store embeddings, Knowledge base
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
# An embedding is representations of values or objects like a text,
# images, and audio that are designed to be consumed by machine learning models
# and semantic search algorithms.
# Embeddings convert raw data into continuous values that ML models can interpret.
# embeddings = OpenAIEmbeddings("openai_api_key=setYOURS")

from langchain.vectorstores import FAISS
# FAISS library allows developers to quickly search for embeddings
# of multimedia documents that are similar to each other.
# faiss runs locally not cloud-based; once the application is closed, it loses the previous data
# used as cpu in vector store

# conversing with the model
from langchain.chat_models import ChatOpenAI

# package for keeping memory in the model currently
from langchain.memory import ConversationBufferMemory
# allows chatting with vector store and keeping memory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub

import docx2txt
# used for reading content of a processed Word document


# processing the pdf file and returns a single string of the text content about the document loaded (pdf)
# variable that contains all the raw text of a pdf document file
# using for loop to loop over the entire document to get all
# the text and extract all the raw text from pdf
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# processing the Word file and returns a single string of the text content about the document loaded (word)
# variable that contains all the raw text of a Word document file
def get_doc_text(doc_files):
    text = ""
    for doc in doc_files:
        text += docx2txt.process(doc)  # Extract text from each Word document
    return text

# text chunk function
# langchain.text_splitter import CharacterTextSplitter is able to divide
# the text from doc_files and pdf_docs into chunks of a text and some parameters like the number of characters
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000, # characters
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


# takes a list of text_chunks as input and returns a vector store
# using the FAISS (Facebook AI Similarity Search) library.
# function named get_vectorstore that accepts a single parameter text_chunks,
# which is expected to be a list containing text data.(pdf)
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # A vector store takes care of storing embedded data and performing vector search for you.
    # Embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    # FAISS.from_texts() is a method from the langchain.vector stores. FAISS class.It takes two parameters:
    # usage of FAISS to create a vector store from text chunks using pre-trained embeddings from OpenAI or Hugging Face.
    # This vector store can then be used for similarity search or other text-related tasks.
    # texts: A list of text chunks to be converted into vectors.
    # embedding: The embedding object used to convert text into vectors.
    # In this case, it's either OpenAIEmbeddings() or HuggingFaceInstructEmbeddings(),
    # depending on the chosen source.
# Creates a vector store using FAISS from the provided text chunks and embeddings.
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Vector embeddings are a way to convert words and sentences and other data into numbers
# that capture their meaning and relationships.
# Function returns the created vector store.
# Vectors are used to represent words, phrases, or even entire documents in a numerical format

def get_conversation_chain(vectorstore):
    # Initializes a chat model using the ChatOpenAI class.
    # This model is responsible for generating responses to user queries or messages.
    llm = ChatOpenAI()

    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)

    # creates a memory buffer to store conversation history.
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        # represents the chat model (language model) used for generating responses.
        retriever=vectorstore.as_retriever(),
        #  represents the retriever used to search for relevant responses based on user queries.In this case,
        #  vectorstore.as_retriever() is used to convert the vectorstore object into a retriever.
        memory=memory
        # represents the memory buffer used to store conversation history.
    )
    return conversation_chain
# function returns the created conversational retrieval chain,
# which can then be used to interactively respond to user queries or messages based
# on the stored conversation history and the provided chat model.

# handle userinput
# defines the function handle_userinput with one parameter
# user_question, which represents the question asked by the user.
def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    # Sends the user question to a conversation handler stored in the st.session_state object.
    # It expects a response containing a conversation history.
    st.session_state.chat_history = response['chat_history']
    # updates the chat_history stored in the st.session_state object with the conversation
    # history received from the conversation handler.

    for i, message in enumerate(st.session_state.chat_history):
        #  Checks if the index i is even. If I is even,
        #  it means that it's the user's message, and if it's odd, it's the bot's response.
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs and Word documents",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    # page title and ICON: books
    st.header("Chat with multiple PDF and Word documents :books:")
    # user input : question from user
    user_question = st.text_input("Ask me anything from your documents :")

    if user_question:
        handle_userinput(user_question)


    st.write(user_template.replace("{{MSG}}", "Hello robot"), unsafe_allow_html=True)
    st.write(bot_template.replace("{{MSG}}", "Hello Human, how may I assist you?"), unsafe_allow_html=True)
   # upload the pdf and word document
    with st.sidebar:
        st.subheader("Your documents")
        # pdf uploader
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True, type="pdf")
        # word uploader
        word_docs = st.file_uploader(
            "Upload your Word documents here and press on and click on 'process'", accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text_from_pdfs = get_pdf_text(pdf_docs)

                # get text from word documents
                raw_text_from_docx = get_doc_text(word_docs)

                # get the text chunks
                # concatenated the text extracted from PDFs and Word documents
                text_chunks = get_text_chunks(raw_text_from_pdfs+raw_text_from_docx)

                # Combine text from PDFs and Word documents
                # raw_text = raw_text_from_pdfs + raw_text_from_docx
                st.write(text_chunks)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create a conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
 # st.session_state.conversation

if __name__ == '__main__':
    main()
