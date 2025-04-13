import yaml
from datetime import datetime, timedelta

TIME_SHIFT_HOURS = -2  # 將 MT4 時間往前調整 2 小時

def parse_time(ts):
    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    shifted = dt + timedelta(hours=TIME_SHIFT_HOURS)
    return shifted.strftime("%Y-%m-%d %H:%M:%S")

def yaml_to_pinescript(filepath):
    with open(filepath, "r") as f:
        trades = yaml.safe_load(f)

    data_lines = []
    for trade in trades:
        entry_time = parse_time(trade["ENTRY_TIME"])
        exit_time = parse_time(trade["EXIT_TIME"])
        entry_price = trade["ENTRY_PRICE"]
        exit_price = trade["EXIT_PRICE"]
        sl = trade["SL"]
        tp = trade["TP"]
        profit = trade["PROFIT"]
        is_buy = trade.get("TYPE", "BUY").upper() == "BUY"

        data_lines.append(f'array.push(array_entry_time,  timestamp("{entry_time}"))')
        data_lines.append(f'array.push(array_exit_time,   timestamp("{exit_time}"))')
        data_lines.append(f'array.push(array_entry_price, {entry_price})')
        data_lines.append(f'array.push(array_exit_price,  {exit_price})')
        data_lines.append(f'array.push(array_stop_loss,   {sl})')
        data_lines.append(f'array.push(array_take_profit, {tp})')
        data_lines.append(f'array.push(array_profit,      {profit})')
        data_lines.append(f'array.push(array_is_buy,      {"true" if is_buy else "false"})\n')

    # 插入主程式與交易邏輯
    header = """//@version=5
indicator("MT4 Trade Marker - Multi-Trade", overlay=true)

// 計算 K 棒結束時間
bar_duration_ms = timeframe.multiplier * 60 * 1000
end_time = time + bar_duration_ms

// === 多筆交易資料 ===
array_entry_time  = array.new_int()
array_exit_time   = array.new_int()
array_entry_price = array.new_float()
array_exit_price  = array.new_float()
array_stop_loss   = array.new_float()
array_take_profit = array.new_float()
array_profit      = array.new_float()
array_is_buy      = array.new_bool()  // true = buy, false = sell

"""

    loop = """
for i = 0 to array.size(array_entry_time) - 1
    entry_t = array.get(array_entry_time, i)
    exit_t  = array.get(array_exit_time, i)
    entry_p = array.get(array_entry_price, i)
    exit_p  = array.get(array_exit_price, i)
    sl      = array.get(array_stop_loss, i)
    tp      = array.get(array_take_profit, i)
    profit  = array.get(array_profit, i)
    is_buy  = array.get(array_is_buy, i)

    bar_offset = math.round((exit_t - entry_t) / bar_duration_ms)
    entry_cond = (end_time >= entry_t and time <= entry_t)
    exit_cond  = (end_time >= exit_t and time <= exit_t)

    var int entry_bar = na
    var int exit_bar = na

    if entry_cond
        entry_bar := bar_index
        entry_label_text = (is_buy ? "BUY" : "SELL") + " @ " + str.tostring(entry_p)
        entry_label_style = is_buy ? label.style_label_up : label.style_label_down
        entry_label_color = is_buy ? color.green : color.red
        label.new(x=entry_bar, y=entry_p + 100, text=entry_label_text, style=entry_label_style, color=entry_label_color, textcolor=color.white)
        if sl != 0.0
            line.new(x1=entry_bar - 10, y1=sl, x2=entry_bar + 10, y2=sl, color=color.orange, style=line.style_solid, width=2)
        if tp != 0.0
            line.new(x1=entry_bar - 10, y1=tp, x2=entry_bar + 10, y2=tp, color=color.green, style=line.style_solid, width=2)

    if exit_cond
        exit_bar := bar_index
        is_profit = profit >= 0
        exit_color = is_profit ? color.green : color.red
        exit_style = is_buy ? label.style_label_up : label.style_label_down
        label.new(x=exit_bar, y=exit_p - 100, text="EXIT @ " + str.tostring(exit_p) + "\\nP/L: " + str.tostring(profit), style=exit_style, color=exit_color, textcolor=color.white)
        if not na(entry_bar)
            line.new(x1=exit_bar - bar_offset, y1=entry_p, x2=exit_bar, y2=exit_p, color=exit_color, width=2, style=line.style_arrow_right)
"""

    return header + "\n".join(data_lines) + loop

# 輸出整個完整 Pine Script
if __name__ == "__main__":
    output = yaml_to_pinescript("trades.yaml")  # YAML 檔案路徑
    with open("mt4_trade_marker_full.pine", "w") as f:
        f.write(output)
    print("✅ 已輸出完整 Pine Script 到 mt4_trade_marker_full.pine")
