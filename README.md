# 🌉 Communication Bridge: Afazi Hastaları için Sesli İletişim Uygulaması

### 🚀 Proje Hakkında

**Communication Bridge**, inme veya diğer nörolojik nedenlerle afazi (konuşma güçlüğü) yaşayan bireylerin temel ihtiyaçlarını ve duygularını hızlı ve etkili bir şekilde ifade etmelerini sağlayan bir iletişim aracıdır. Projemiz, kullanıcı dostu ikonlara dayalı basit bir arayüzle, bireylerin tek bir dokunuşla doğal ve anlaşılır cümleler kurmasına olanak tanır. Amacımız, konuşma yetisini kısmen kaybetmiş kişilerin yaşam kalitesini artırarak onlara güvenli bir iletişim köprüsü sunmaktır.

### ✨ Temel Özellikler

* **İkon Tabanlı Arayüz:** Kullanımı kolay, büyük ve anlaşılır ikonlarla tasarlanmış arayüz.
* **Hızlı Cümle Oluşturma:** Tek bir dokunuşla önceden tanımlanmış ihtiyaçları (su, ağrı, doktor vb.) yüksek kaliteli sesle ifade etme.
* **Çok Dilli Destek:** Proje, farklı dillerde cümle ve ikon desteğine sahiptir (mevcut kodda Türkçe ve İngilizce önceliklidir).
* **Yüksek Kaliteli Seslendirme:** **OpenAI TTS** veya **Google Text-to-Speech (gTTS)** gibi güçlü servisleri kullanarak doğal ve anlaşılır sesler üretir.
* **Kullanım İstatistikleri:** Uygulamanın en sık kullanılan ihtiyaçlarını ve cümlelerini anonim olarak kaydeden ve analiz eden basit bir loglama sistemi. (`/stats` ve `/stats_daily` endpointleri ile erişilebilir).
* **Kolay Kurulum:** Herhangi bir Web tarayıcısında çalışabilen, Python/Flask tabanlı hafif bir backend ile hızlıca ayağa kaldırılabilir.

### 💻 Teknik Mimari

Proje, iki ana bileşenden oluşur:
* **Frontend (HTML/CSS/JS):** Basit, minimalist ve erişilebilir bir kullanıcı arayüzü sunar. Büyük butonlar ve yüksek kontrastlı tasarım, mobil ve tablet cihazlar için idealdir.
* **Backend (Python/Flask):**
    * **`/speak` Endpoint'i:** Gelen ihtiyaca (need) göre uygun bir cümle oluşturur ve bunu metinden sese dönüştürür.
    * **Metinden Sese (TTS) Motoru:** **OpenAI TTS** (API anahtarı varsa) veya yedek olarak **gTTS** kullanarak yüksek kaliteli ses dosyaları oluşturur.
    * **Loglama Sistemi:** Kullanıcı etkileşimlerini anonim olarak kaydeder.
    * **`/stats` ve `/stats_daily` Endpoint'leri:** Toplanan kullanım verilerini analiz eder ve raporlar.

### 🔧 Kurulum ve Çalıştırma

1.  **Gerekli Paketleri Kurun:**
    ```bash
    pip install Flask Flask-Cors gTTS openai
    ```
2.  **API Anahtarınızı Ayarlayın (İsteğe Bağlı):**
    OpenAI TTS'i kullanmak isterseniz, `OPENAI_API_KEY` ortam değişkenini ayarlamanız gerekir. Bu opsiyoneldir; anahtar yoksa sistem otomatik olarak gTTS'e düşer.
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```
3.  **Uygulamayı Çalıştırın:**
    ```bash
    python app.py
    ```
    Uygulama yerel makinenizde `http://127.0.0.1:5000` adresinde çalışacaktır.
4.  **Uygulamayı Kullanın:**
    Bir `cURL` komutu ile test yapabilirsiniz:
    ```bash
    curl -X POST [http://127.0.0.1:5000/speak](http://127.0.0.1:5000/speak) -H "Content-Type: application/json" -d '{"need": "water"}' --output water.mp3
    ```
    Bu komut, "Su istiyorum." cümlesini seslendirir ve `water.mp3` olarak kaydeder.

### 📝 Gelecek Planları

* **Özelleştirilebilir Cümleler:** Kullanıcıların kendi ihtiyaçlarına göre yeni cümleler eklemesine olanak tanıma.
* **Kullanıcı Profilleri:** Her hasta için kişisel ayarların ve sık kullanılan ifadelerin kaydedilmesi.
* **Duygu ve Ton Kontrolü:** Seçilen ikona göre ses tonunun ayarlanması (örneğin, "ağrı" butonu için daha endişeli bir ton).
* **Mobil Uygulama Olarak Geliştirme:** iOS ve Android cihazlar için optimize edilmiş native uygulamalar.
