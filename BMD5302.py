import requests
import pandas as pd
import time

url = "https://secure.fundsupermart.com/fsmone/rest/fund/find-daily-price-history-by-period"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://secure.fundsupermart.com/",
    "Origin": "https://secure.fundsupermart.com",
    "X-Requested-With": "XMLHttpRequest",
}

def fetch_period_history(sedol: str, period: str = "3y") -> pd.DataFrame:
    payload = {
        "paramSedolnumber": sedol,
        "paramPeriod": period
    }
    resp = requests.post(url, data=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    hist = data.get("dailyPriceHistory", [])
    rows = []
    for x in hist:
        pk = x.get("dailyPricePk", {})
        rows.append({
            "fundid": pk.get("fundid"),
            "date": pd.to_datetime(pk.get("showDate"), unit="ms", errors="coerce"),
            "nav_price": x.get("navPrice"),
            "bid_price": x.get("bidPrice"),
            "bid_price_sgd": x.get("bidPriceSgd"),
            "percent_rate": x.get("percentRate"),
            "update_date": pd.to_datetime(x.get("updateDate"), unit="ms", errors="coerce") if x.get("updateDate") else None,
            "managercode": x.get("managercode"),
            "period": period,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("date").reset_index(drop=True)
    return df

codes = ["FIUSCA"]  # 后面把别的基金代码加进来
all_df = []

for code in codes:
    try:
        df = fetch_period_history(code, "3y")
        df["sedol"] = code
        all_df.append(df)
        print(code, len(df), df["date"].min(), df["date"].max())
        time.sleep(1)
    except Exception as e:
        print(code, "failed:", e)

if all_df:
    final_df = pd.concat(all_df, ignore_index=True)
    final_df.to_excel("FIUSCA_funds_3y_history.xlsx", index=False)
    print("已保存：FIUSCA_funds_3y_history.xlsx")