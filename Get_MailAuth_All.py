import subprocess
import re

def get_dns_txt_record(domain: str, record: str = "") -> str:
    """
    使用 nslookup 獲取 DNS TXT 紀錄
    :param domain: 要查詢的 domain
    :param record: 額外的記錄前綴 (例如 _dmarc 或 default._domainkey)
    :return: 查詢結果
    """
    try:
        # 完整的查詢名稱
        full_domain = f"{record}.{domain}" if record else domain
        
        # 使用 nslookup 執行查詢
        result = subprocess.run(
            ["nslookup", "-type=txt", full_domain],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 使用正則表達式解析 TXT 記錄
        txt_pattern = r"\"([^\"]+)\""  # 匹配雙引號內的文字
        matches = re.findall(txt_pattern, result.stdout)
        
        return "\n".join(matches) if matches else "沒有找到 TXT 紀錄。"
    
    except subprocess.CalledProcessError as e:
        return f"查詢錯誤 {full_domain}: {e}"

def save_to_file(domain: str, spf: str, dmarc: str, dkim: str, filename: str = "dns_records.txt"):
    """
    將查詢結果保存到檔案中
    :param domain: 查詢的 Domain
    :param spf: SPF 記錄
    :param dmarc: DMARC 記錄
    :param dkim: DKIM 記錄
    :param filename: 檔案名稱
    """
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"Domain: {domain}\n\n")
        file.write(f"SPF 設定:\n{spf}\n\n")
        file.write(f"DMARC 設定:\n{dmarc}\n\n")
        file.write(f"DKIM 設定:\n{dkim}\n")
        file.write("-" * 80 + "\n")

def main():
    while True:
        print()
        domain = input("請輸入要查詢的 Domain: ").strip()
        
        if not domain:
            print("Domain 不能為空，請重新輸入")
            continue
        
        # 查詢 SPF
        spf_record = get_dns_txt_record(domain)
        
        # 查詢 DMARC
        dmarc_record = get_dns_txt_record(domain, "_dmarc")
        
        # 查詢 DKIM
        dkim_record = get_dns_txt_record(domain, "default._domainkey")
        
        # 檢查是否查無結果
        if spf_record == "沒有找到 TXT 紀錄。" and dmarc_record == "沒有找到 TXT 紀錄。" and dkim_record == "沒有找到 TXT 紀錄。":
            print("查無相關記錄，請重新輸入一個有效的 Domain")
            print()
            continue
        
        # 整理輸出
        print("\n--------------------------- 查詢結果 ---------------------------")
        print(f"Domain: {domain}")
        print("\nSPF 設定:")
        print(spf_record)
        print("\nDMARC 設定:")
        print(dmarc_record)
        print("\nDKIM 設定:")
        print(dkim_record)
        print("\n----------------------------------------------------------------")
        
        # 保存結果到檔案
        save_to_file(domain, spf_record, dmarc_record, dkim_record)
        print(f"查詢結果已保存到 dns_records.txt")
        
        # 結束迴圈
        break

if __name__ == "__main__":
    main()
