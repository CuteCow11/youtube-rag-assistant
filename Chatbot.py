import os
from dotenv import load_dotenv
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1" ,
    api_key= os.getenv("OPENROUTER_API_KEY"),
    model="google/gemma-3n-e2b-it:free" ,
    temperature= 0.5,
)

try:
    

    loader = YoutubeLoader.from_youtube_url(
        "https://www.youtube.com/watch?v=c8lWK67truY",
        add_video_info=False,
        language=["en", "en-US","hi"]
    )
    docs = loader.load()
    script = docs[0].page_content
    split = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = split.create_documents([script])
    embd = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vs = FAISS.from_documents(chunks, embd)
    ret = vs.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    ques = input("what is your question? ")

    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided transcript context. If the context is insufficient, just say you don't know.
        {context}
        Question: {question}""",
        input_variables=['context', 'question']
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    parser = StrOutputParser()

    chain = (
        {"context": ret | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )

    print(chain.invoke(ques))

except Exception as e:
    print(e)