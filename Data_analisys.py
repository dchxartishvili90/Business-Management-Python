import pandas as pd
data = {
    'პროდუქტი': ['ჩაი', 'ყავა', 'შოკოლადი', 'ბისკვიტი', 'კაკაო', 'კანფეტი'],
    'კატეგორია': ['სასმელი', 'სასმელი', 'ტკბილეული', 'ტკბილეული', 'სასმელი', 'ტკბილეული'],
    'ფასი': [5.5, 12.0, 7.8, 4.0, 6.0, 3.5],
    'გაყიდული_რაოდენობა': [150, 80, 210, 300, 50, 400]
}
df=pd.DataFrame(data)
avg_prices=df.groupby('კატეგორია')['ფასი'].mean()
print("---საშვალო ფასები კატეგორიების მიხედვით---")
print(avg_prices)
df['შემოსავალი']=df['ფასი'] * df['გაყიდული_რაოდენობა']
print("---ახალი სვეტი---")
print(df)
print(df['შემოსავალი'].sum())
kategoris_revenu=df.groupby('კატეგორია')['შემოსავალი'].sum()
print("---KATEGOORIS PASI---")
print(kategoris_revenu)

import matplotlib.pyplot as plt
kategoris_revenu=df.groupby('კატეგორია')['შემოსავალი'].sum()
kategoris_revenu.plot(kind='bar', color=['skyblue', 'salmon'])
plt.title('შემოსავლების შედარება კატეგორიის მიხედვით')
plt.xlabel('კატეგორია')
plt.ylabel('შემოსავალი')
plt.show()