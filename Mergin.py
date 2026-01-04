import pandas as pd
import glob
import numpy as np

files = glob.glob("*.csv")
all_dataframes=[]
for f in files:
    temp_df=pd.read_csv(f)
    all_dataframes.append(temp_df)
final_df=pd.concat(all_dataframes ,ignore_index=True)
final_df['produkti']=final_df['produkti'].str.lower().str.strip()
final_df.to_csv('merged_all_data.csv',index=False, encoding='utf-8-sig')



import matplotlib.pyplot as plt
try:
    plot_data = final_df.groupby('produkti')['jami'].sum().sort_values(ascending=False)
    plt.figure(figsize=(10,6))
    plot_data.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('JAMURI SHEMOSAVALI PRODUKTIS MIXEDVIT ', fontsize=14)
    plt.xlabel('Produkti', fontsize=12)
    plt.ylabel('SHemosavali lari' ,fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y',linestyle='--',alpha=0.7)
    plt.tight_layout()
    plt.savefig('gayidvebis grafiki.png',dpi=300)
    plt.show()
except Exception as e:
    print(f"GRAFIKI AGEBISAS MOXDA SHECDOMA:{e}")
