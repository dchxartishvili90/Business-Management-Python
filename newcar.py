import pandas as pd
import numpy as np
try:
    df = pd.read_csv('merged_all_data.csv')
    print("NABIJI PIRVELI FAILI CHAITVIRTA")
    df['produkti']=df['produkti'].str.lower().str.strip()
    df=df.drop_duplicates()
    print("NABIJI MEORE GASUPTAVEBA")
    df['jami']=df['pasi']*df['gayiduli']
    conditions=[
        (df['jami']<=26),
        (df['jami']>26)&(df['jami']<=36),
        (df['jami']>36)
                ]
    choices = ['dabali','sashualo','magali']
    df['done']=np.select(conditions,choices, default='gaurkveveli')
    print("-----STATUSIS MINICHEBA-----")
    df=df.sort_values(by='jami', ascending=False)
    df.to_csv('final_proces_data.csv', index=False,  encoding='utf-8-sig')
    print("DASRULEBULIA")
    print(df.head())
    print("FAILI SHENAXULIA PROCES_DATA.csv")
except FileNotFoundError:
    print("FAILI VER MOIDZEBNA TEST DATA")
except Exception as e:
    print("MOXDA SHECDOMA:{e}")
