import pandas as pd
import re

def text_to_excel(text, output_file="universal_data.xlsx"):
    lines = [re.sub(r'^[*\-•\s]+', '', line).strip() for line in text.strip().split('\n') if line.strip()]
    
    data = []
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data.append({"Параметр/Объект": key.strip(), "Значение/Описание": value.strip()})
        else:
            data.append({"Параметр/Объект": "Общая инфо", "Значение/Описание": line})

    df = pd.DataFrame(data)

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        
        worksheet = writer.sheets['Data']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_len
