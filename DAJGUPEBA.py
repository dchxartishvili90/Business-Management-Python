import pandas as pd
df=pd.read_csv('magaziis_monacemebi.csv')
shejameba2=df.groupby('produkti').agg({
    'pasi':'max',
    'jami':'sum',
    'gayiduli':'mean'
})
shejameba2.columns=['Maqs_pasi','Jamuri_shemosavali','sashualo_raodenoba']
print("DETALURI ANALIZI PRODAQTIS MIXEDVIT")
print(shejameba2)
print(df.isnull().sum())
df=df.dropna()
sashualo_pasi = df['pasi'].mean()
df['pasi']=df['pasi'].fillna(sashualo_pasi)
print("CARIELLI ADGILEBI SHEIVSO")
print(df)
print(df.dtypes)
df['pasi'] = pd.to_numeric(df['pasi'],errors='coerce')
anomaliebi=df[df['gayiduli']>8 ]
with pd.ExcelWriter('saboloo_analitikaV2.xlsx') as writer:
    df.to_excel(writer,sheet_name='main_data',index=False)
    anomaliebi.to_excel(writer,sheet_name='Anomalies',index=False)
print("GVERDI DAEMATA REPORTS")
