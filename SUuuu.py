import pandas as pd

try:
    df = pd.read_csv('test_data.csv')
    df['jami'] = df['pasi'] * df['gayiduli']
    grouped_df = df.groupby('produkti')[['gayiduli', 'jami']].sum()

    # მონაცემების ამოღება რეპორტისთვის
    top_revenue_prod = grouped_df['jami'].idxmax()
    max_revenue = grouped_df['jami'].max()
    top_sold_prod = grouped_df['gayiduli'].idxmax()
    max_qty = grouped_df['gayiduli'].max()

    # რეპორტის ტექსტის მომზადება
    report_text = f"""
------------------------------
GAYIDVEBIS REPORTI
YVELAZE METI SHEMOSAVALI MOITANA : {top_revenue_prod} ({max_revenue} Lari)
YVELAZE DIDI RAODENOBA GAIYIDA : {top_sold_prod} ({max_qty} Cali)
------------------------------
"""
    # 1. ვბეჭდავთ ეკრანზე
    print(report_text)
    # 2. ვინახავთ ტექსტურ ფაილში (.txt)
    with open('gayidvebis_reporti.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
        
    print("✅ რეპორტი წარმატებით შეიქმნა და შეინახა ფაილში 'gayidvebis_reporti.txt'")

except Exception as e:
    print(f"მოხდა შეცდომა: {e}")