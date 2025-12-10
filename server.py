import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://locgkfjkjaffiahmcgnekmdoakggmfni"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = None

class InitRequest(BaseModel):
    video_url: str

class ChatRequest(BaseModel):
    question: str

@app.post("/init")
async def init_video(request: InitRequest):
    global vector_store
    try:
        loader = YoutubeLoader.from_youtube_url(
            request.video_url,
            add_video_info=False,
            language=["en", "en-US", "hi"],
        )
        docs = loader.load()
        script = docs[0].page_content
        
        split = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = split.create_documents([script])
        embd = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        vector_store = FAISS.from_documents(chunks, embd)
        return {"status": "success", "message": "Video processed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    global vector_store
    if not vector_store:
        raise HTTPException(status_code=400, detail="No video loaded. Please init first.")
    
    try:
        ret = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="google/gemma-3n-e2b-it:free",
            temperature=0.5,
        )

        prompt = PromptTemplate(
            template="""You are a helpful assistant. Answer ONLY from the provided context.
            {context}
            Question: {question}""",
            input_variables=['context', 'question']
        )

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        chain = (
            {"context": ret | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        answer = chain.invoke(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)