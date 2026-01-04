import pandas as pd
try:
    df=pd.read_csv('merged_all_data.csv')
    pd.to_datetime(df['tarigi'],dayfirst=True)
    df=df.drop_duplicates()
    df['jami']=df['pasi']*df['gayiduli']
    df['mogeba']=df['jami']*0.20
    df.sort_values(by='mogeba', ascending=False)
    df=df[df['mogeba']>7]
    print(df)
except Exception as e:
    print(f"EROR: {e}")
