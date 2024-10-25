# Web Crawler for Gambling Links

Project ini adalah crawler web untuk mencari link judi yang disembunyikan di website tertentu, mengambil detail DNS, IP, serta informasi hosting, lalu menyimpannya ke dalam database PostgreSQL.

## Table of Contents
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Database Setup](#database-setup)

## Dependencies

Project ini memerlukan beberapa dependencies berikut:
1. **Python Libraries**:
   - `socket`
   - `dnspython` - Untuk mengambil data DNS.
   - `whois` - Untuk mengakses informasi hosting.
   - `selenium` - Untuk kontrol browser otomatis.
   - `psycopg2` - Untuk koneksi ke PostgreSQL.
   - `webdriver_manager` - Untuk mengatur WebDriver Chrome.
   - `json` dan `time` - Digunakan untuk pengolahan data JSON dan penundaan waktu.
   
2. **Database**:
   - **PostgreSQL** sebagai tempat penyimpanan data hasil crawling.

3. **Browser Driver**:
   - **ChromeDriver** - Digunakan bersama Selenium untuk mengontrol browser Chrome.

## Installation
### 1. Install Python Dependencies
Untuk menginstal semua dependencies Python, jalankan perintah berikut:

```bash
pip install dnspython whois selenium psycopg2-binary webdriver-manager requests

