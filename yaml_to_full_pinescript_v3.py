import yaml
import argparse
from datetime import datetime, timedelta


def parse_time(ts, shift_hours):
    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    shifted = dt + timedelta(hours=shift_hours)
    return shifted.strftime("%Y-%m-%d %H:%M:%S")


def yaml_to_pinescript(filepath, shift_hours, symbol_filter=None, show_size=False):
    with open(filepath, "r") as f:
        trades = yaml.safe_load(f)

    data_lines = []
    for trade in trades:
        symbol = trade.get("SYMBOL")
        if symbol_filter and symbol != symbol_filter:
            continue

        entry_time = parse_time(trade["ENTRY_TIME"], shift_hours)
        exit_time = parse_time(trade["EXIT_TIME"], shift_hours)
        entry_price = trade["ENTRY_PRICE"]
        exit_price = trade["EXIT_PRICE"]
        sl = trade["SL"]
        tp = trade["TP"]
        profit = trade["PROFIT"]
        is_buy = trade.get("TYPE", "BUY").upper() == "BUY"
        trade_id = trade.get("TRADE_ID", "")
        size = trade.get("SIZE", None)

        label_comment = f"{trade_id}" if trade_id else ""
        if show_size and size is not None:
            label_comment += f" Size: {size}"

        data_lines.append(f'// {label_comment}')
        data_lines.append(f'array.push(array_entry_time,  timestamp("{entry_time}"))')
        data_lines.append(f'array.push(array_exit_time,   timestamp("{exit_time}"))')
        data_lines.append(f'array.push(array_entry_price, {entry_price})')
        data_lines.append(f'array.push(array_exit_price,  {exit_price})')
        data_lines.append(f'array.push(array_stop_loss,   {sl})')
        data_lines.append(f'array.push(array_take_profit, {tp})')
        data_lines.append(f'array.push(array_profit,      {profit})')
        data_lines.append(f'array.push(array_is_buy,      {"true" if is_buy else "false"})\n')

    return full_script_template("\n".join(data_lines))


def full_script_template(data_section):
    return f"""//@version=5
indicator(\"MT4 Trade Marker - Multi-Trade\", overlay=true)

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
array_is_buy      = array.new_bool()

{data_section}

// === 畫圖邏輯 ===
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
        entry_label_text = (is_buy ? \"BUY\" : \"SELL\") + \" @ \" + str.tostring(entry_p)
        entry_label_style = is_buy ? label.style_label_up : label.style_label_down
        entry_label_color = is_buy ?  color.rgb(76, 175, 79, 43) : color.rgb(245, 106, 106, 54)
        label.new(x=entry_bar, y=entry_p + 100, text=entry_label_text, style=entry_label_style, color=entry_label_color, textcolor=color.white)
        if sl != 0.0
            line.new(x1=entry_bar - 10, y1=sl, x2=entry_bar + 10, y2=sl, color=color.orange, style=line.style_solid, width=2)
        if tp != 0.0
            line.new(x1=entry_bar - 10, y1=tp, x2=entry_bar + 10, y2=tp, color=color.green, style=line.style_solid, width=2)

    if exit_cond
        exit_bar := bar_index
        is_profit = profit >= 0
        exit_color = is_profit ? color.gray : color.rgb(121, 41, 124, 37)
        exit_style = is_buy ? label.style_label_up : label.style_label_down
        label.new(x=exit_bar, y=exit_p - 100, text=\"EXIT @ \" + str.tostring(exit_p) + \"\\nP/L: \" + str.tostring(profit), style=exit_style, color=exit_color, textcolor=color.white)
        if not na(entry_bar)
            line.new(x1=exit_bar - bar_offset, y1=entry_p, x2=exit_bar, y2=exit_p, color=exit_color, width=2, style=line.style_arrow_right)
"""


def main():
    parser = argparse.ArgumentParser(
        description="Convert a YAML file of MT4 trades into Pine Script format with array.push commands."
    )
    parser.add_argument("yaml_file", help="Path to the input YAML file")
    parser.add_argument("--output", "-o", default="mt4_trade_marker_full.pine",
                        help="Path to output Pine Script file (default: mt4_trade_marker_full.pine)")
    parser.add_argument("--shift", type=int, default=-2,
                        help="Time shift in hours to apply to ENTRY_TIME and EXIT_TIME (default: -2)")
    parser.add_argument("--symbol", type=str, help="Only include trades with this SYMBOL")
    parser.add_argument("--show-size", action="store_true",
                        help="Display trade SIZE in the generated Pine Script as label comment")

    args = parser.parse_args()

    print(f"📁 Loading: {args.yaml_file}")
    print(f"⏱  Time shift: {args.shift} hour(s)")
    if args.symbol:
        print(f"🔍 Filtering by symbol: {args.symbol}")
    if args.show_size:
        print("🧾 Will include SIZE in label comments")

    pine_code = yaml_to_pinescript(args.yaml_file, args.shift, args.symbol, args.show_size)

    with open(args.output, "w") as f:
        f.write(pine_code)

    print(f"✅ Pine Script saved to: {args.output}")


if __name__ == "__main__":
    main()
