# Shlim AI Assistant API

Bu proje, Shlim AI'ın yapay zeka ajanı otomasyonu hizmetleri hakkında bilgi sağlayan ve müşteri adaylarını kaydeden bir asistan API'sidir. FastAPI, LangChain ve OpenAI kullanılarak geliştirilmiştir.

## Özellikler

- Shlim AI hakkında bilgi sağlama (knowledge.docx dosyasından)
- Müşteri adaylarını (lead) Airtable CRM'e kaydetme
- Çoklu oturum desteği (thread_id ile)
- Ngrok ile yerel geliştirme ortamını dış dünyaya açma

## Gereksinimler

- Python 3.8+
- OpenAI API anahtarı
- Airtable API anahtarı
- knowledge.docx dosyası (Shlim AI hakkında bilgiler içeren)

## Kurulum

1. Repo'yu klonlayın:
```bash
git clone https://github.com/your-username/shlim-ai-assistant.git
cd shlim-ai-assistant
```

2. Sanal ortam oluşturun ve bağımlılıkları yükleyin:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. `.env` dosyası oluşturun ve API anahtarlarınızı ekleyin:
```
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
AIRTABLE_API_KEY=your_airtable_api_key
PORT=8080
```

4. `knowledge.docx` dosyasını proje ana dizinine yerleştirin. Bu dosya, Shlim AI hakkında bilgi içermelidir.

## Çalıştırma

API'yi başlatmak için:

```bash
python main.py
```

Uygulama başladığında, konsol çıktısında bir ngrok URL'i göreceksiniz. Bu URL, API'nize internet üzerinden erişim sağlar.

## API Endpoints

### 1. Yeni Konuşma Başlatma

```
GET /start
```

Yeni bir konuşma thread'i oluşturur ve thread_id döner.

**Yanıt:**
```json
{
  "thread_id": "uuid-string"
}
```

### 2. Mesaj Gönderme ve Yanıt Alma

```
POST /chat
```

**İstek:**
```json
{
  "thread_id": "uuid-string",
  "message": "Shlim AI hakkında bilgi verebilir misiniz?"
}
```

**Yanıt:**
```json
{
  "response": "Shlim AI, Recepalp Saygılı tarafından kurulan ve işletmeler için AI ajan otomasyonu çözümleri sunan bir teknoloji firmasıdır..."
}
```

## Voiceflow Entegrasyonu

Shlim AI Assistant API'sini Voiceflow'a entegre etmek için aşağıdaki adımları izleyin:

1. Voiceflow hesabınızda yeni bir proje oluşturun.

2. Voiceflow'da API çağrıları için HTTP Request bloğu ekleyin:

   **Konuşma Başlatma (Start Conversation):**
   - Method: GET
   - URL: `{ngrok_url}/start`
   - Response Mapping: `thread_id` değerini bir değişkene kaydedin

   **Mesaj Gönderme (Chat):**
   - Method: POST
   - URL: `{ngrok_url}/chat`
   - Headers: `Content-Type: application/json`
   - Body:
     ```json
     {
       "thread_id": "{thread_id_değişkeni}",
       "message": "{user_message_değişkeni}"
     }
     ```
   - Response Mapping: `response` değerini bir değişkene kaydedin

3. Voiceflow akışınızda:
   - İlk adımda Start endpoint'ini çağırın ve thread_id'yi saklayın
   - Kullanıcı girişini aldıktan sonra Chat endpoint'ini çağırın, thread_id'yi ve kullanıcı mesajını gönderin
   - Asistan yanıtını kullanıcıya gösterin

4. Konuşma geçmişini korumak için, tüm etkileşimlerde aynı thread_id'yi kullanın.

### Örnek Voiceflow Akışı:

1. Start API çağrısı → thread_id sakla
2. Kullanıcıdan mesaj al
3. Chat API çağrısı (thread_id ve kullanıcı mesajı ile)
4. Asistan yanıtını göster
5. 2. adıma dön

## Dosya Yapısı

```
shlim-ai-assistant/
├── main.py                # Ana uygulama kodu
├── knowledge.docx         # Shlim AI hakkında bilgi içeren dosya
├── .env                   # API anahtarları ve konfigürasyon
├── chroma_db/             # Vektör veritabanı (otomatik oluşturulur)
├── requirements.txt       # Bağımlılıklar
└── README.md              # Bu dosya
```

## Bağımlılıklar

Projenin çalışması için gerekli Python paketleri:

```
fastapi==0.104.1
uvicorn==0.23.2
langchain==0.0.311
langchain_openai==0.0.2
langchain_community==0.0.9
openai==1.1.1
pyngrok==7.0.0
python-dotenv==1.0.0
chromadb==0.4.18
docx2txt==0.8
pydantic==2.4.2
requests==2.31.0
```

Bu bağımlılıkları yüklemek için:

```bash
pip install -r requirements.txt
```

## Geliştirme Notları

- Bu API, geliştirme amaçlıdır ve production ortamı için güvenlik önlemleri eklenmelidir.
- CORS ayarları production için sıkılaştırılmalıdır.
- Airtable yapılandırması `appG0pukRuaxpoSqq` base ID'sine göre ayarlanmıştır, kendi Airtable kurulumunuza göre güncelleyin.
- GPT-4o-mini modeli kullanılmaktadır, daha gelişmiş yanıtlar için GPT-4o veya benzeri modeller tercih edilebilir.

## Lisans

[MIT](LICENSE)

## İletişim

Projeyle ilgili sorularınız için [e-posta adresiniz] adresine e-posta gönderebilirsiniz.
