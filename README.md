# yaml-to-trade-mark-for-trading-view


yaml_to_full_pinescript.py
preview for result in TradingWiew

<img width="559" alt="image" src="https://github.com/user-attachments/assets/e7094984-bbc1-4c4f-a022-602f07311da9" />


input format examples
```
- TRADE_ID: T111
  ENTRY_TIME: '2025-04-08 18:39:34'
  EXIT_TIME: '2025-04-08 18:55:49'
  ENTRY_PRICE: 17724.0
  EXIT_PRICE: 17774.5
  SL: 0.0
  TP: 17774.0
  PROFIT: 101.0
- TRADE_ID: T112
  ENTRY_TIME: '2025-04-08 18:56:32'
  EXIT_TIME: '2025-04-08 19:05:27'
  ENTRY_PRICE: 17729.5
  EXIT_PRICE: 17730.0
  SL: 17629.0
  TP: 17730.0
  PROFIT: 1.0
- TRADE_ID: T113
  ENTRY_TIME: '2025-04-08 19:20:10'
  EXIT_TIME: '2025-04-08 19:25:57'
  ENTRY_PRICE: 17609.5
  EXIT_PRICE: 17610.0
  SL: 17510.0
  TP: 17610.0
  PROFIT: 1.0
- TRADE_ID: T114
  ENTRY_TIME: '2025-04-09 10:36:33'
  EXIT_TIME: '2025-04-09 12:33:41'
  ENTRY_PRICE: 17224.0
  EXIT_PRICE: 17135.0
  SL: 0.0
  TP: 17135.0
  PROFIT: 178.0
- TRADE_ID: T115
  ENTRY_TIME: '2025-04-10 21:30:01'
  EXIT_TIME: '2025-04-10 21:43:03'
  ENTRY_PRICE: 18378.5
  EXIT_PRICE: 18278.75
  SL: 18280.0
  TP: 18570.0
  PROFIT: -99.75
```

output example

```
//@version=5
indicator("MT4 Trade Marker - Multi-Trade", overlay=true)

// 計算 K 棒結束時間
bar_duration_ms = timeframe.multiplier * 60 * 1000
end_time = time + bar_duration_ms

// === 多筆交易資料 ===
// 格式：[entry_time, exit_time, entry_price, exit_price, stop_loss, take_profit, profit, is_buy]
array_entry_time  = array.new_int()
array_exit_time   = array.new_int()
array_entry_price = array.new_float()
array_exit_price  = array.new_float()
array_stop_loss   = array.new_float()
array_take_profit = array.new_float()
array_profit      = array.new_float()
array_is_buy      = array.new_bool()  // true = buy, false = sell

// 寫入交易資料（注意：已套用 -2 小時時差）
array.push(array_entry_time,  timestamp("2025-04-08 16:39:34"))
array.push(array_exit_time,   timestamp("2025-04-08 16:55:49"))
array.push(array_entry_price, 17724.0)
array.push(array_exit_price,  17774.5)
array.push(array_stop_loss,   0.0)
array.push(array_take_profit, 17774.0)
array.push(array_profit,      101.0)
array.push(array_is_buy,      true)

array.push(array_entry_time,  timestamp("2025-04-08 16:56:32"))
array.push(array_exit_time,   timestamp("2025-04-08 17:05:27"))
array.push(array_entry_price, 17729.5)
array.push(array_exit_price,  17730.0)
array.push(array_stop_loss,   17629.0)
array.push(array_take_profit, 17730.0)
array.push(array_profit,      1.0)
array.push(array_is_buy,      true)

array.push(array_entry_time,  timestamp("2025-04-08 17:20:10"))
array.push(array_exit_time,   timestamp("2025-04-08 17:25:57"))
array.push(array_entry_price, 17609.5)
array.push(array_exit_price,  17610.0)
array.push(array_stop_loss,   17510.0)
array.push(array_take_profit, 17610.0)
array.push(array_profit,      1.0)
array.push(array_is_buy,      true)

array.push(array_entry_time,  timestamp("2025-04-09 08:36:33"))
array.push(array_exit_time,   timestamp("2025-04-09 10:33:41"))
array.push(array_entry_price, 17224.0)
array.push(array_exit_price,  17135.0)
array.push(array_stop_loss,   0.0)
array.push(array_take_profit, 17135.0)
array.push(array_profit,      178.0)
array.push(array_is_buy,      false)

array.push(array_entry_time,  timestamp("2025-04-10 19:30:01"))
array.push(array_exit_time,   timestamp("2025-04-10 19:43:03"))
array.push(array_entry_price, 18378.5)
array.push(array_exit_price,  18278.75)
array.push(array_stop_loss,   18280.0)
array.push(array_take_profit, 18570.0)
array.push(array_profit,     -99.75)
array.push(array_is_buy,      false)

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
        // 顏色與箭頭方向根據買/賣與盈虧調整
        is_profit = profit >= 0
        exit_color = is_profit ? color.green : color.red
        exit_style = is_buy ? label.style_label_up : label.style_label_down
        label.new(x=exit_bar, y=exit_p - 100, text="EXIT @ " + str.tostring(exit_p) + "\nP/L: " + str.tostring(profit), style=exit_style, color=exit_color, textcolor=color.white)
        if not na(entry_bar)
            line.new(x1=exit_bar - bar_offset, y1=entry_p, x2=exit_bar, y2=exit_p, color=exit_color, width=2, style=line.style_arrow_right)

```

