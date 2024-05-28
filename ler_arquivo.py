import csv
import pandas as pd
import datetime as dt

def ler_arquivo_csv(caminho_arquivo):
    return pd.read_csv(caminho_arquivo)

def ler_arquivo_xlsx(caminho_arquivo):
    return pd.read_excel(caminho_arquivo)

def create_rfm(df):

    dataframe = df

    # Preparation
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # Calculate RFM metrics
    today_date = dt.datetime(2011, 12, 10)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: round(price.sum(),2)})

    rfm.columns = ['Recency', 'Frequency', "Monetary"]
    # Calculate RFM scores
    rfm["Recency_Score"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["Frequency_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["Monetary_Score"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

    rfm["RFM_Score"] = (rfm['Recency_Score'].astype(str) +
                        rfm['Frequency_Score'].astype(str))


    # Segmentation
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['Segment'] = rfm['RFM_Score'].replace(seg_map, regex=True)
    rfm = rfm[["Recency", "Frequency", "Monetary", "Segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

def main():
    formato = input("Digite o formato do arquivo (csv ou xlsx): ").lower()

    if formato == 'csv':
        caminho = input("Digite o caminho do arquivo CSV: ")
        dados_lidos = ler_arquivo_csv(caminho)
    
    elif formato == 'xlsx':
        caminho = input("Digite o caminho do arquivo XLSX: ")
        dados_lidos = ler_arquivo_xlsx(caminho)
        
    else:
        print("Formato não suportado. Por favor, escolha entre CSV ou XLSX.")
    
        return
    
# Salvar como DataFrame
    df = pd.DataFrame(dados_lidos)

    create_rfm(df)

if __name__ == "__main__":
    main()
