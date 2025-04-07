# Shlim AI Agent-Lead-Chatbot

Bu proje, (Hayali) Shlim AI'ın yapay zeka ajanı otomasyonu hizmetleri hakkında bilgi sağlayan ve müşteri adaylarını kaydeden bir asistan API'sidir. FastAPI, LangChain ve OpenAI kullanılarak geliştirilmiştir.

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
AIRTABLE_API_KEY=your_airtable_api_key
PORT=8080
```

4. `knowledge.docx` dosyasını proje ana dizinine yerleştirin. Bu dosya, Shlim AI hakkında bilgi içermelidir.

## Ngrok Kurulumu

Proje, pyngrok kütüphanesini kullanarak otomatik olarak ngrok tüneli oluşturur. Ek bir kurulum gerekmez, ancak ngrok hesabınız varsa ve auth token kullanmak istiyorsanız:

1. [Ngrok](https://ngrok.com/) sitesine kaydolun ve auth token alın.

2. Ngrok'u yapılandırmak için:
```bash
ngrok authtoken your_ngrok_auth_token
```

## Çalıştırma

API'yi başlatmak için:

```bash
python main.py
```

Uygulama başladığında, konsol çıktısında bir ngrok URL'i göreceksiniz:
```
Ngrok tüneli başlatıldı: https://xxxx-xx-xx-xxx-xx.ngrok.io
Uygulama başlatıldı, ngrok URL: https://xxxx-xx-xx-xxx-xx.ngrok.io
```

Bu URL, API'nize dış dünyadan erişim sağlayan geçici bir adrestir ve her başlatmada değişir. Uygulama kapandığında, ngrok tünelleri otomatik olarak temizlenir.

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

## Ngrok İpuçları ve Sorun Giderme

1. **Uygulama Çıkışında Otomatik Temizleme:**
   Uygulama kapandığında, ngrok tünelleri otomatik olarak temizlenir (`cleanup_ngrok` fonksiyonu ile).

2. **Tünel Durumunu Görüntüleme:**
   Aktif ngrok tünellerini görmek için:
   ```bash
   ngrok http list
   ```

3. **Webhook'ları Test Etme:**
   Ngrok, `http://localhost:4040` adresinden erişilebilen bir webhook inceleme paneli sunar. Burada tüm gelen istekleri ve yanıtları görebilirsiniz.

4. **Sabit URL İhtiyacı:**
   Eğer ngrok'un her seferinde değişen URL'i sorun yaratıyorsa, ücretli ngrok hesabı ile sabit alt alan adları kullanabilirsiniz.

## Asistan Özellikleri

Asistan, aşağıdaki özelliklere sahiptir:

- Shlim AI'ın yapay zeka ajan çözümleri ve hizmetleri hakkında bilgi sağlar
- knowledge.docx dosyasından alınan bilgilere dayanarak soruları yanıtlar
- Müşteri adaylarının bilgilerini (ad, şirket adı, e-posta, telefon) toplayıp Airtable CRM'e kaydeder
- Her kullanıcı için ayrı bir konuşma thread'i tutar

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
fastapi
uvicorn
langchain
langchain_openai
langchain_community
openai
pyngrok
python-dotenv
chromadb
docx2txt
pydantic
requests
```

Bu bağımlılıkları yüklemek için:

```bash
pip install -r requirements.txt
```

## Geliştirme Notları

- Bu API, geliştirme amaçlıdır ve production ortamı için güvenlik önlemleri eklenmelidir.
- CORS ayarları production için sıkılaştırılmalıdır (şu anda tüm originlere izin verilmektedir).
- Airtable yapılandırması `appG0pukRuaxpoSqq` base ID'sine göre ayarlanmıştır, kendi Airtable kurulumunuza göre güncelleyin.
- GPT-4o-mini modeli kullanılmaktadır, daha gelişmiş yanıtlar için GPT-4o veya benzeri modeller tercih edilebilir.
- Bilgi tabanı oluşturulurken, knowledge.docx dosyası 1000 karakterlik parçalara bölünür ve 200 karakter örtüşme ile indekslenir.

## Lisans

[MIT](LICENSE)

## İletişim

Projeyle ilgili sorularınız için srecepalp@gmail.com adresine e-posta gönderebilirsiniz.
