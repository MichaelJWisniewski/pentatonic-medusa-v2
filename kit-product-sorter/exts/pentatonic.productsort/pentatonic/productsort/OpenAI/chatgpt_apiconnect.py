import carb
import os
import aiohttp
import json

from .prompts import *

async def call_Generate(prompt):
    data, response = await call_OpenAI(prompt)

    #Test Data
    #response = "{'generation':{'actions':['Spawn','Add_Materials'],'products':[{'product_name':'Leather_Couch','product_material':'Leather_Brown','X':-1,'Y':-1,'Z':-1},{'product_name':'Pallet_1','product_material':'Mahogany','X':1,'Y':1,'Z':1}]}}"
    #data = {'generation':{'actions':['Spawn','Add_Materials'],'products':[{'product_name':'Leather_Couch','product_material':'Leather_Brown','X':-1,'Y':-1,'Z':-1},{'product_name':'Pallet_1','product_material':'Mahogany','X':1,'Y':1,'Z':1}]}}
    
    return response, data

async def call_OpenAI(prompt: str, product_list):
    api_key = os.environ.get('OPENAI_API_KEY')

    # Send a request API
    try:
        parameters = {
            "model": "gpt-3.5-turbo",
            "messages": [
                    {"role": "system", "content": system_input_1_test},
                    {"role": "system", "content": product_list},
                    {"role": "system", "content": system_input_2_test},
                    {"role": "user", "content": prompt}
                ]
        }
        
        chatgpt_url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": "Bearer %s" % api_key}
        
        # Create a completion using the chatGPT model
        async with aiohttp.ClientSession() as session:
            async with session.post(chatgpt_url, headers=headers, json=parameters) as r:
                response = await r.json()
        text = response["choices"][0]["message"]['content']

    except Exception as e:
        carb.log_error("An error as occurred")
        return None, str(e)

    # Parse data that was given from API
    try: 
        data = json.loads(text)

    except ValueError as e:
        carb.log_error(f"Exception occurred: {e}")
        return None, text

    else: 
        # Get area_objects_list
        return data, text