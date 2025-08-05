# GitHub App ile Otomatik Token Oluşturma ve Actions Secrets Güncelleme Dokümantasyonu

Bu doküman, GitHub Actions içerisinde özel (private) bir repodan public bir repoya veri çekmek için gerekli olan access token'ın, **GitHub App** kullanarak nasıl kullanıcı bazında değil **organizasyon bazında** alınacağını ve otomatik olarak public bir reponun **secrets** alanına nasıl yazılacağını adım adım açıklamaktadır.

---

## Amaç

- Private bir GitHub reposuna, public bir repo içindeki GitHub Actions workflow'u ile erişim sağlamak.  
- GitHub App kullanarak access token almak ve bu token'ı belirli aralıklarla otomatik olarak yenilemek.  
  _(Alınan tokenlar 1 saat süreyle geçerli olduğu için ben 55 dakikada bir otomatik yenileme yaptım.)_  
- Access token'ı public reponun secrets alanına otomatik olarak yazmak.

---

## Genel Yapı

| Bileşen        | Açıklama                                           |
| -------------- | -------------------------------------------------- |
| Organizasyon   | `app-deneme-org` (Test için açılmış bir organizasyon) |
| Public Repo    | `public-repo` (app.py, workflow ve secrets burada) |
| Private Repo   | `private-repo` (Deneme amaçlı basit bir test.txt var) |
| Secret Adı     | `PYTHON_TOKEN` (Token'ın kayıtlı olduğu secret)   |

---

## 1. GitHub App Oluşturma

1. GitHub üzerinde **GitHub Apps** sayfasına git.
2. Yeni bir GitHub App oluştur:

   - **App name**: `deneme-app-test-org`  
   - **Webhook URL / Secret**: (Boş bırakabilirsiniz.)

3. **Permissions (Repository)**:

   - `Actions`: Read & Write  
   - `Secrets`: Read & Write  
   - `Code`: Read  
   - `Deployments`: Read & Write  
   - `Pull requests`: Read & Write  
   - `Workflows`: Read & Write  

4. **Repository Access**:  
   Tüm repolar veya manuel seçim. (Test ortamında tüm yetkiler verildi. Gerçek ortamda sınırlanabilir.)

5. App'i oluşturduktan sonra **Private Key** dosyasını indir ve sakla.  
   _(Bu dosyanın yolu app.py içerisinde kullanılacak.)_

6. Organizasyon altında App'i **install et**.

---

## 2. `app.py` - Token Üretici Script

### Neden `app.py` adında bir Python dosyası yazdık?

- GitHub App'ler, doğrudan kullanılabilecek uzun süreli bir **personal access token (PAT)** vermezler.
- Bunun yerine, kısa ömürlü bir **JWT (JSON Web Token)** üretip, bu token ile 1 saatlik bir **access token** almanı bekler.
- Bu access token, API çağrıları ya da `git clone` gibi işlemlerde kullanılabilir.

---

### `app.py` Dosyası Ne Yapıyor?

Adım adım:

1. GitHub App için indirdiğin **private key** dosyasını okur.
2. Bu key ile **10 dakika geçerli bir JWT** oluşturur.
3. JWT’yi kullanarak GitHub’tan **1 saat geçerli bir access token** alır.
4. Bu token'ı:
   - Konsola yazdırabilir.
   - Veya doğrudan `public-repo` içindeki **Secrets** alanına yazar (`PYTHON_TOKEN` olarak).

---

### Bu Dosya Gerekli mi?

Evet, çünkü:

- GitHub App doğrudan git erişimi sağlamaz.
- Önce geçici bir token üretmen gerekir.
- Bu işlemleri her seferinde manuel yapmak yerine `app.py` ile **otomatikleştirmiş** olduk.

---

### Alternatif Olarak Ne Yapılabilirdi?

| Yöntem                           | Ne zaman kullanılır?                                    | Ne yapar?                                               |
| -------------------------------- | -------------------------------------------------------- | ------------------------------------------------------- |
| **Personal Access Token (PAT)**  | Eğer kendi kullanıcı hesabınla repo'ya erişeceksen      | GitHub doğrudan uzun ömürlü bir token verir             |
| **GitHub App + JWT + app.py**    | Organizasyon içinde, uygulama bazlı erişim istiyorsan   | JWT oluşturur, GitHub'tan geçici access token alır      |

> PAT kullandığın senaryoda, o kullanıcı erişimini kaybederse (örneğin işten ayrılırsa), token'lar tek tek elle değiştirilmeli.  
> Biz bu sorunu çözmek için GitHub App kullanarak otomatik token üretimi sağladık.

---

## 3. `x-access-token` Kullanımı

### Neden `x-access-token` Yazıyoruz?

GitHub, HTTPS üzerinden yapılan `git` işlemlerinde aşağıdaki yapıyı bekler:

```
https://<kullanıcı_adı>:<şifre veya token>@github.com/ORG/REPO.git
```

GitHub App access token ile yapılan işlemlerde, **kullanıcı adı** kısmı sabit olarak **`x-access-token`** olmalıdır.

### Örnek Kullanım

```bash
git clone https://x-access-token:<ACCESS_TOKEN>@github.com/app-deneme-org/private-repo.git
```

> Bu kullanım, GitHub’ın resmi dokümantasyonunda yer almaktadır.

---

## Sonuç

Bu sistem sayesinde, **private bir repoya erişim için gereken GitHub access token'ları otomatik olarak oluşturulmakta ve public bir repodaki GitHub Actions secrets alanına düzenli olarak yazılmaktadır**. Böylece, manuel token güncelleme ihtiyacı ortadan kalkar ve güvenli, sürdürülebilir bir CI/CD süreci sağlanır.

Özellikle **Personal Access Token (PAT)** kullanan senaryolarda, token'ı oluşturan kullanıcı şirketteki erişimini kaybettiğinde (örneğin işten ayrıldığında) bu token'ların elle güncellenmesi gerekir. Biz bu kırılgan yapıyı önlemek için **GitHub App tabanlı bir erişim modeli kurduk**; böylece sistem, herhangi bir kullanıcıya bağlı kalmadan kendi kendine çalışabilir hâle geldi.