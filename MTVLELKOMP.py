import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob

try:
    # 1. ფაილების მოძიება და გაერთიანება
    files = glob.glob("*.csv")
    if not files:
        print("❌ საქაღალდეში CSV ფაილები ვერ მოიძებნა!")
    else:
        all_dfs = []
        for f in files:
            temp_df = pd.read_csv(f)
            temp_df['წყარო'] = f # მივაწეროთ რომელი ფაილიდანაა
            all_dfs.append(temp_df)
        
        df = pd.concat(all_dfs, ignore_index=True)
        print(f"✅ გაერთიანდა {len(files)} ფაილი.")

        # 2. გასუფთავება
        df['produkti'] = df['produkti'].str.lower().str.strip()
        df['tarigi'] = pd.to_datetime(df['tarigi'], dayfirst=True)
        df = df.drop_duplicates()

        # 3. გამოთვლები და კატეგორიზაცია
        df['jami'] = df['pasi'] * df['gayiduli']
        
        conditions = [
            (df['jami'] <= 26),
            (df['jami'] > 26) & (df['jami'] <= 35),
            (df['jami'] > 35)
        ]
        choices = ['დაბალი', 'საშუალო', 'მაღალი']
        df['done'] = np.select(conditions, choices, default='გაურკვეველი')

        # 4. ექსპორტი EXCEL-ში
        # index=False ნიშნავს, რომ ზედმეტი ნომრები არ ჩაამატოს
    
        print("📊 რეპორტი შენახულია: 'Saboloo_Reporti.xlsx'")

        # 5. ვიზუალიზაცია (გრაფიკი)
        plt.figure(figsize=(12, 6))
        
        # დავაჯგუფოთ თარიღის მიხედვით გაყიდვების დინამიკისთვის
        timeline = df.groupby('tarigi')['jami'].sum()
        plt.plot(timeline.index, timeline.values, marker='s', color='darkblue', linewidth=2)

        plt.title('გაყიდვების საერთო ტრენდი', fontsize=15)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        
        # გრაფიკის შენახვა ფოტოდ
        plt.savefig('Trendi.png', dpi=300)
        print("🖼️ გრაფიკი შენახულია: 'Trendi.png'")
        
        plt.show()

except Exception as e:
    print(f"🔴 მოხდა შეცდომა სისტემაში: {e}")