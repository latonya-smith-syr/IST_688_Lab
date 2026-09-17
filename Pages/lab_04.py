import streamlit as st
from openai import OpenAI
import tiktoken
import chromadb
from pathlib import Path
from PyPDF2 import PdfReader
import sys


__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab4')
collection = chroma_client.get_or_create_collection('Lab4collection')

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client= OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    

def add_to_collection(collection, text, file_name):
    #Creating an embedding from pdf
    client = st.session_state.client
    response = client.embeddings.create(
        input= text,
        model= 'text-embedding-3-small'
    )
    #Get the embedding
    embedding = response.data[0].embedding

    #Add embedding and document to ChromaDB
    collection.add(
        documents=[text],
        ids=file_name,
        embeddings= [embedding]
    )

def load_pdfs_to_collection(folder_path, collection):
    if collection.count() == 0:
        loaded = load_pdfs_to_collection('./PDF_files_lab4', collection)
        

st.title("Lab 4 chatbot")
st.write("Chatbot Demo")

topic = st.sidebar.text_input('Topic', placeholder='Type your topic (e.g., GenAI)...')

if topic:
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input = topic,
        model= 'text-embedding-3-small'
    )
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3 #The number of closest documents to return
    )
    #Display the results
    st.subheader(f"Results for: {topic}")
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]

        st.write(f'**{i+1}. {doc_id}**')
else:
    st.info('Enter a topic in the sidebar to search the collection')

    
model = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

buffer_type = st.sidebar.selectbox('Buffer type', ('Last 2 responses', 'Token-based'))

system_prompt = {"role": "system", "content":  "Explain all answers simply enough for a 10-year-old to understand.After the user's first response ask them this:Do you want more information?. "
            "If they say yes, give them more information and then ask them specifically: Do you want more information?. If they say no, ask them specifically How can I help you?"}





def count_tokens(text, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def msg_buffer(messages, system_prompt):
    return [system_prompt] + messages[-4:]

max_tokens = 1000

#Note to Grader:  I used AI to strategize how to calculate the tokens and for the coding logic 
# on looking at the last messages
def token_buffer(messages, system_prompt, max_tokens, model=model):
    system_tokens = count_tokens(system_prompt["content"], model)
    budget = max_tokens - system_tokens
    kept = []
    total = 0
    for msg in reversed(messages):
        t = count_tokens(msg["content"], model)
        if total + t > budget:
            break
        kept.insert(0, msg)
        total += t
    return [system_prompt] + kept   

if prompt := st.chat_input("What is up?"):    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if buffer_type == "Last 2 responses":
        api_msg = msg_buffer(st.session_state.messages, system_prompt)
    else:
        api_msg = token_buffer(st.session_state.messages, system_prompt, max_tokens, model)

    client = st.session_state.client
    stream = client.chat.completions.create(
        model= model,
        messages = api_msg,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

    