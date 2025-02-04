import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

def main():
    st.set_page_config(page_title="Ask your PDF")
    st.header("Ask your PDF 💬")

    pdf = st.file_uploader("Upload your PDF", type="pdf")

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        embeddings = HuggingFaceEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        retriever = knowledge_base.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 relevant chunks
        llm = Ollama(model="llama3.2:3b")

        # Initialize session state memory if not exists
        if "memory" not in st.session_state:
            st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

        # Strict Conversational Retrieval Chain with memory persistence
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=st.session_state.memory,  # Pass persistent memory
            return_source_documents=True,
            output_key="answer"
        )

        user_question = st.text_input("Ask a question about your PDF:")

        if user_question:
            response = qa_chain({"question": user_question})

            # Extract answer and sources
            answer = response["answer"]
            sources = response.get("source_documents", [])

            # Ensure response is only from the PDF context
            if not sources:  
                answer = "I couldn't find relevant information in the PDF."

            st.write(answer)

if __name__ == '__main__':
    main()
