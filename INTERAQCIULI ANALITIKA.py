import pandas as pd
import matplotlib.pyplot as plt
try:
    df=pd.read_csv('merged_all_data.csv')
    if 'jami' not in df.columns:
        df['jami'] = df['pasi'] * df['gayiduli']
    df['tarigi']=pd.to_datetime(df['tarigi'],dayfirst=True)
    unique_products = df['produkti'].unique()
    print("/n XELMISAWVOMI PRODUKTEBI")
    for p in unique_products:
        print(f"-{p}")
    archevani=input("ROMELIS NAXVA GSURT").lower().strip()
    filtred_df=df[df['produkti']==archevani]
    if filtred_df.empty:
        print(" PRODUKTI SAXELIT:{archevani} VER MOIDZEBNA")
    else:
        total_qty=filtred_df['gayiduli'].sum()
        total_rev=filtred_df['jami'].sum()
        avg_price=filtred_df['pasi'].mean()
        print(f"REPORTI PRODUKTZE:{archevani.upper()}")
        print(f"sUL GAIYIDA:{total_qty}")
        print(f"JAMURI SHEMOSAVALI:{total_rev}")
        print(f"SASHUALO SHEMOSAVALI:{avg_price:.2f}")
        print(f"-------------------")

        plt.figure(figsize=(10, 5))
        plt.plot(filtred_df['tarigi'], filtred_df['jami'], marker='o', color='orange', linewidth=2)
        
        plt.title(f'გაყიდვების დინამიკა: {archevani}', fontsize=14)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.xlabel('თარიღი')
        plt.ylabel('შემოსავალი (ლარი)')
        
        plt.tight_layout()
        plt.show()
except Exception as e:
    print(f"moxda SHECDOMA :{e}")
