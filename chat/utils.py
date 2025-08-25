# chat/utils.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import openai
from django.conf import settings
from .models import AnalysisStep
import os
openai.api_key = settings.OPENAI_API_KEY

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
client = gspread.authorize(creds)

def fetch_sheet_data(sheet_link):
    sheet = client.open_by_url(sheet_link).sheet1
    return sheet.get_all_records()

def export_to_sheet(df, title="Optimized Cost"):
    sh = client.create(title)
    worksheet = sh.get_worksheet(0)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    return sh.url

def alternating_workflow(project, sheet_data, price_list):
    df = pd.DataFrame(sheet_data)
    prices = pd.DataFrame.from_dict(price_list, orient='index', columns=['price'])

    # Log function
    def log_step(step_type, input_data, output_data):
        AnalysisStep.objects.create(project=project, step_type=step_type, input_data=input_data, output_data=output_data)

    # AI1: Initial reasoning (e.g., identify key items)
    prompt1 = f"Analyze BOQ for cost estimation: {df.to_string()}. Suggest categories."
    response1 = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role": "user", "content": prompt1}])['choices'][0]['message']['content']
    log_step('ai', prompt1, response1)

    # Code1: Base calculation
    df['item'] = df['item'].apply(lambda x: x.lower())  # Normalize
    merged = df.merge(prices, left_on='item', right_index=True, how='left')
    merged['total_cost'] = merged['quantity'] * merged['price'].fillna(0)
    calc1 = merged.to_string()
    log_step('code', str(sheet_data), calc1)

    # AI2: Refine optimization (e.g., suggest cheaper alternatives)
    prompt2 = f"Optimize costs based on: {calc1}. Suggest reductions."
    response2 = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role": "user", "content": prompt2}])['choices'][0]['message']['content']
    log_step('ai', prompt2, response2)

    # Code2: Apply optimizations (parse AI suggestions, e.g., reduce quantities)
    # Example: Assume AI suggests "reduce item1 by 10%", apply simply
    # In real: Parse response2 for changes
    merged['optimized_cost'] = merged['total_cost'] * 0.9  # Placeholder for AI-parsed logic
    calc2 = merged.to_string()
    log_step('code', response2, calc2)

    # AI3: Final review
    prompt3 = f"Review optimized costs: {calc2}. Provide summary."
    response3 = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role": "user", "content": prompt3}])['choices'][0]['message']['content']
    log_step('ai', prompt3, response3)

    # Code3: Final export prep
    final_df = merged
    log_step('code', calc2, final_df.to_string())

    return final_df, response3  # DF for export, summary for chat