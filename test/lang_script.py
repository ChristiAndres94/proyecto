import os
import mysql.connector
from langchain.llms import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import streamlit as st

os.environ['OPENAI_API_KEY'] = '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'


def process_doc(
        pdf_path: str,
        question: str
):
    loader = PyPDFLoader(pdf_path)
    doc = loader.load_and_split()

    db = Chroma.from_documents(doc, embedding=OpenAIEmbeddings())

    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type='stuff', retriever=db.as_retriever())

    return qa.run(question)


def client():
    st.title('Manage LLM with LangChain')

    # Conexión a la base de datos MySQL
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='receta'
    )

    cursor = connection.cursor()

    # Obtener los enlaces de los PDFs desde la base de datos
    pdf_links_query = "SELECT pdf_path FROM pdfs"
    cursor.execute(pdf_links_query)
    pdf_links = cursor.fetchall()

    # Crear una lista de opciones para seleccionar el PDF a buscar
    pdf_options = [link[0] for link in pdf_links]
    selected_pdf = st.selectbox('Select PDF to Search', pdf_options)

    question = st.text_input('Generar un resumen de 40 palabras sobre el pdf',
                             placeholder='Give response about your PDF')

    if st.button('Generate Summary'):
        result = process_doc(selected_pdf, question)
        st.write(result)

    cursor.close()
    connection.close()


if __name__ == '__main__':
    client()