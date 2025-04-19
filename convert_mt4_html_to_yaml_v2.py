import sys
from bs4 import BeautifulSoup
import yaml
from datetime import datetime

def parse_time(time_str):
    return datetime.strptime(time_str, "%Y.%m.%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

def extract_trades_from_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    trades = []
    rows = soup.find_all("tr", align="right")

    for idx, row in enumerate(rows):
        cols = row.find_all("td")
        if len(cols) < 14:
            continue

        entry_time_raw = cols[1].text.strip()
        exit_time_raw = cols[8].text.strip()
        if not entry_time_raw or not exit_time_raw:
            continue

        try:
            entry_time = parse_time(entry_time_raw)
            exit_time = parse_time(exit_time_raw)
            entry_price = float(cols[5].text.strip())
            exit_price = float(cols[9].text.strip())
            sl = float(cols[6].text.strip())
            tp = float(cols[7].text.strip())
            profit = float(cols[13].text.strip())
            trade_type = cols[2].text.strip().lower()
            symbol = cols[4].text.strip()
            size = float(cols[3].text.strip())
        except ValueError:
            continue

        trade_id = f"T{len(trades)+1}"
        trades.append({
            "TRADE_ID": trade_id,
            "TYPE": trade_type,
            "SYMBOL": symbol,
            "SIZE": size,
            "ENTRY_TIME": entry_time,
            "EXIT_TIME": exit_time,
            "ENTRY_PRICE": entry_price,
            "EXIT_PRICE": exit_price,
            "SL": sl,
            "TP": tp,
            "PROFIT": profit,
        })

    return trades

def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_mt4_html_to_yaml.py <input.htm> <output.yaml>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    trades = extract_trades_from_html(input_file)

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(trades, f, allow_unicode=True, sort_keys=False)
    print(f"✅ YAML file written to: {output_file}")

if __name__ == "__main__":
    main()

