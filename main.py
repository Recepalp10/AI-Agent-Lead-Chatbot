import json
import os
import time
import uuid
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import requests
import uvicorn
import pyngrok.ngrok as ngrok
import atexit

# Çevre değişkenlerini yükle
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
PORT = int(os.getenv("PORT", "8080"))

# FastAPI uygulaması oluştur
app = FastAPI(title="Shlim AI Assistant API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver (prod için güvenli değil)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ve Response modelleri
class ChatRequest(BaseModel):
    thread_id: str
    message: str

class StartResponse(BaseModel):
    thread_id: str

class ChatResponse(BaseModel):
    response: str

# Airtable'a lead ekleme fonksiyonu (tool olarak kullanılacak)
@tool
def create_lead(name: str, company_name: str, email: str, phone: str = "") -> str:
    """
    Müşteri adayı bilgilerini Airtable'a kaydeder.
    
    Args:
        name: Müşteri adayının adı
        company_name: Müşteri adayının şirket adı
        email: Müşteri adayının email adresi
        phone: Müşteri adayının telefon numarası (opsiyonel)
        
    Returns:
        Kayıt sonucu bilgisi
    """
    url = "https://api.airtable.com/v0/appG0pukRuaxpoSqq/Leads"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Name": name,
                "Phone": phone,
                "Email": email,
                "CompanyName": company_name,
            }
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Lead başarıyla oluşturuldu.")
        return "Lead başarıyla oluşturuldu."
    else:
        error_message = f"Lead oluşturma başarısız: {response.text}"
        print(error_message)
        return error_message

# Bilgi dokümanını yükle ve vektör veritabanı oluştur
def create_knowledge_base():
    # DOCX dosyasını yükle
    print("Bilgi tabanı yükleniyor...")
    loader = Docx2txtLoader("knowledge.docx")
    documents = loader.load()
    
    # Dokümanı parçalara böl
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # Vektör veritabanı oluştur
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    print(f"Bilgi tabanı oluşturuldu. {len(chunks)} parça indekslendi.")
    return vectordb

# Vektör veritabanını oluştur
vectordb = create_knowledge_base()

# Retriever aracı olarak kullanılacak fonksiyon
@tool
def search_knowledge_base(query: str) -> str:
    """
    Shlim AI hakkındaki bilgileri aramak için knowledge.docx dosyasını kullanır.
    
    Args:
        query: Arama sorgusu
        
    Returns:
        Bilgi tabanından ilgili bilgiler
    """
    # Retrieval zinciri oluştur
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    # Sorguyu çalıştır
    docs = retriever.get_relevant_documents(query)
    
    # Sonuçları formatla
    if not docs:
        return "Bu konuda bilgi tabanında bilgi bulunamadı."
    
    results = []
    for i, doc in enumerate(docs, 1):
        results.append(f"İlgili Bilgi {i}:\n{doc.page_content}\n")
    
    return "\n".join(results)

# Konuşma kayıtları için bellek
conversation_memories: Dict[str, ConversationBufferMemory] = {}
agent_executors: Dict[str, AgentExecutor] = {}

# LangChain tabanlı asistan oluşturma
def create_agent(thread_id: str) -> AgentExecutor:
    # Asistan talimatları
    assistant_instructions = """
    Bu asistan, Shlim AI müşterilerine yardımcı olmak için kurulmuştur. Shlim AI, AI Agent Specialist Recepalp Saygılı tarafından kurulan ve Türkiye ve Avrupa genelinde işletmeler için gelişmiş AI ajan otomasyonu çözümleri sunan özel bir teknoloji firmasıdır.

    Bu asistanın amacı, kullanıcılara Shlim AI'ın sunduğu yapay zeka ajan çözümleri ve hizmetleri hakkında bilgi vermektir. Kullanıcıların merak ettiği konularda süreç otomasyonu, karar destek ajanları, müşteri etkileşim ajanları ve operasyonel zeka ajanları hakkında bilgi verir. Kullanıcı tarafından talep edilirse, sektöre özel çözümler ve başarı hikayeleri gibi konularda da yardımcı olur. Üslubu profesyonel, bilgilendirici ve yardımcı olacaktır.

    Shlim AI'a özgü sorular için bir bilgi dosyası eklenmiştir. Shlim AI'ın sunduğu hizmetler, liderlik, müşteriler veya uygulama süreçleri hakkındaki sorular için search_knowledge_base aracını kullanarak knowledge.docx'ten bilgileri almalısın.

    Bu asistan yalnızca yapay zeka, otomasyon, süreç iyileştirme ve Shlim AI'ın hizmetleri ile ilgili konularda yardımcı olur. Spor olayları, siyaset, politika, ekonomi vb. konularda hiçbir soruyu yanıtlamaz. Bu tür sorular sorulduğunda, yardımcı olamayacağını ve yalnızca Shlim AI ve AI ajan çözümleri hakkında bilgi verdiğini belirtir.

    Kullanıcılara gerekli konularda yardımcı olduktan sonra, asistan kullanıcıların adını, şirket adını, e-postasını ve telefon numarasını sorar. Bu şekilde, Shlim AI ekibi iletişime geçebilir ve daha ayrıntılı yardım sağlayabilir. Bu bilgileri topladıktan sonra, create_lead fonksiyonu kullanılarak CRM'e kaydedilebilir. Bu fonksiyon, ad (name), şirket adı (company_name), e-posta (email) ve telefon (phone) bilgilerini gerektirir. Ad, şirket adı ve e-posta zorunludur, telefon ise isteğe bağlıdır. Telefon numarası verilmezse, boş bir dize olarak gönderilebilir.
    """
    
    # Bellek oluşturma
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_memories[thread_id] = memory
    
    # Kullanılacak araçlar
    tools = [create_lead, search_knowledge_base]
    
    # LangChain Chat modeli
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0
    )
    
    # Asistan için prompt şablonu
    prompt = ChatPromptTemplate.from_messages([
        ("system", assistant_instructions),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Agent oluşturma
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # AgentExecutor oluşturma
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Agent executor'ı sakla
    agent_executors[thread_id] = agent_executor
    
    return agent_executor

# Yeni konuşma başlatma endpoint'i
@app.get("/start", response_model=StartResponse)
def start_conversation():
    print("Yeni bir konuşma başlatılıyor...")
    # Benzersiz bir thread_id oluştur
    thread_id = str(uuid.uuid4())
    print(f"Yeni thread oluşturuldu, ID: {thread_id}")
    return {"thread_id": thread_id}

# Mesajlaşma endpoint'i
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = request.thread_id
    user_input = request.message

    if not thread_id:
        raise HTTPException(status_code=400, detail="thread_id eksik")

    print(f"Alınan mesaj: {user_input} (thread ID: {thread_id})")
    
    # Eğer bu thread için bir agent yoksa oluştur
    if thread_id not in conversation_memories:
        create_agent(thread_id)
    
    # Agent executor'ı al
    agent_executor = agent_executors.get(thread_id)
    if not agent_executor:
        agent_executor = create_agent(thread_id)
    
    # Kullanıcı mesajını işle ve yanıt al
    response = agent_executor.invoke({"input": user_input})
    assistant_response = response.get("output", "Üzgünüm, bir cevap oluşturamadım.")
    
    print(f"Asistan yanıtı: {assistant_response}")
    return {"response": assistant_response}

# Ngrok tüneli başlatma ve kapatma
def setup_ngrok(port):
    """Ngrok ile belirtilen portu dış dünyaya aç"""
    # Varolan tünelleri temizle
    for tunnel in ngrok.get_tunnels():
        ngrok.disconnect(tunnel.public_url)
    
    # Yeni tünel oluştur
    ngrok_tunnel = ngrok.connect(port)
    public_url = ngrok_tunnel.public_url
    print(f"Ngrok tüneli başlatıldı: {public_url}")
    return public_url

def cleanup_ngrok():
    """Uygulama kapanırken ngrok tünellerini temizle"""
    print("Ngrok tünelleri kapatılıyor...")
    for tunnel in ngrok.get_tunnels():
        ngrok.disconnect(tunnel.public_url)
    print("Ngrok tünelleri kapatıldı.")

# Uygulama başlatıldığında çalıştırılacak
@app.on_event("startup")
async def startup_event():
    global ngrok_url
    # NgRok tüneli oluştur
    ngrok_url = setup_ngrok(PORT)
    # Atexit ile kapanışta temizlik yap
    atexit.register(cleanup_ngrok)
    print(f"Uygulama başlatıldı, ngrok URL: {ngrok_url}")

# Ana uygulama başlatma (doğrudan çalıştırıldığında)
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=PORT, reload=True)