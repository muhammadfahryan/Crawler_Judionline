import socket
import dns.resolver
import whois
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import psycopg2
import json

# Koneksi ke PostgreSQL
def connect_db():
    return psycopg2.connect(
        dbname='ryan',  
        user='ryan',         
        password='ryan',    
        host='10.100.13.205',        
        port='5432'              
    )

# Masukkan data ke PostgreSQL
def insert_data(link, host, ip, dns_info, hosting_info):
    conn = connect_db()
    cur = conn.cursor()
    
    # Insert query
    insert_query = """
    INSERT INTO public.scrapping (link, host, ip, dns, hosting)
    VALUES (%s, %s, %s, %s::json, %s)
    """
    
    # Mengubah dns_info menjadi string JSON
    dns_info_str = json.dumps(dns_info) if dns_info else None 

    # Menangani nilai null
    cur.execute(insert_query, (link, host, ip, dns_info_str, hosting_info if hosting_info else None))
    
    conn.commit()
    cur.close()
    conn.close()

# Setup Chrome dan WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def google_search(query, max_pages=100):
    driver.get("https://www.google.com")
    
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.submit()
    
     # Tunggu beberapa detik agar halaman sepenuhnya dimuat
    time.sleep(2)

    print("Selesaikan CAPTCHA 'I'm not a robot' di browser. Setelah selesai, tekan Enter untuk melanjutkan.")
    input()  # tekan enter


    current_page = 0

    while current_page < max_pages:
        time.sleep(2)

        # Ambil link dari hasil pencarian
        results = driver.find_elements(By.CSS_SELECTOR, 'h3')
        links = []
        for result in results:
            link = result.find_element(By.XPATH, '..').get_attribute('href')
            links.append(link)
            print(f"Link ditemukan: {link}")  # Cetak link yang ditemukan

        # Mengambil IP dan DNS untuk setiap link
        for link in links:
            host, ip, dns_info, hosting_info = get_ip_host_dns(link)
            print(f"Link: {link}\nHOST: {host}\nIP: {ip}\nDNS: {dns_info}\nHosting: {hosting_info}\n{'-' * 50}")

            # Masukkan data ke PostgreSQL
            insert_data(link, host, ip, dns_info, hosting_info)
            print(f"inserted data : {link}")

        # Mencari tombol "Next" untuk navigasi ke halaman berikutnya
        try:
            next_button = driver.find_element(By.XPATH, "//a[@id='pnnext']")
            next_button.click()
            current_page += 1
        except Exception as e:
            print("Tidak ada halaman berikutnya.")
            break


def get_ip_host_dns(link):
    host = None  # Inisialisasi host dengan nilai default
    try:
        if link is None:
            print("Link tidak valid.")
            return host, None, None, None
        
        host = link.split("//")[-1].split("/")[0]  # Ambil hostname dari link
        print(f"Trying to resolve host: {host}")  # Tambahkan log untuk host
        ip = socket.gethostbyname(host)  # Dapatkan IP dari hostname
        print(f"Resolved IP: {ip}")  # Tambahkan log untuk IP
        
        # Dapatkan DNS
        dns_info = get_dns_info(host)
        print(f"Resolved DNS: {dns_info}")  # Tambahkan log untuk DNS
        
        # Dapatkan informasi hosting
        hosting_info = get_hosting_info(host)
        print(f"Resolved Hosting Info: {hosting_info}")  # Tambahkan log untuk hosting
        
        return host, ip, dns_info, hosting_info
    except Exception as e:
        print(f"Error getting data for {link}: {e}")
        return host, None, None, None


def get_dns_info(host):
    dns_info = {
        "A": [],
        "CNAME": [],
        "NS": [],
        "TXT": [],
        "MX": [],
        "is_cdn": False,
    }
    try:
        # Mengambil A record
        a_answers = dns.resolver.resolve(host, 'A')
        dns_info["A"] = [str(answer) for answer in a_answers]
        
        # Mengambil CNAME record
        try:
            cname_answers = dns.resolver.resolve(host, 'CNAME')
            dns_info["CNAME"] = [str(answer) for answer in cname_answers]
        except dns.resolver.NoAnswer:
            dns_info["CNAME"] = []  # Tidak ada CNAME
        
        # Mengambil NS record
        ns_answers = dns.resolver.resolve(host, 'NS')
        dns_info["NS"] = [str(answer) for answer in ns_answers]
        
        # Mengambil TXT record
        txt_answers = dns.resolver.resolve(host, 'TXT')
        dns_info["TXT"] = [str(answer) for answer in txt_answers]
        
        # Mengambil MX record
        mx_answers = dns.resolver.resolve(host, 'MX')
        dns_info["MX"] = [str(answer) for answer in mx_answers]

        # Cek apakah ada indikasi penggunaan CDN
        if any("cloudflare" in ns for ns in dns_info["NS"]) or \
           any("aws" in ns for ns in dns_info["NS"]) or \
           any("cdn" in ns for ns in dns_info["NS"]):
            dns_info["is_cdn"] = True
            
    except Exception:
        pass
    
    return dns_info

def get_hosting_info(host):
    try:
        w = whois.whois(host)
        return w.org or "Tidak diketahui"
    except Exception as e:
        print(f"Error getting hosting info for {host}: {e}")
        return "Tidak diketahui"

# Eksekusi pencarian
query_words = ["judi slot", "bet judi", "toto gacor", "jp gacor"]
for query in query_words:
    print(f"Mencari: {query}")
    google_search(query, max_pages=100)

# Tutup browser
driver.quit()
