
import os
from flask import Blueprint
from config import openai_api_key
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import json

describe_bp = Blueprint('describe', __name__)

def get_description(stats, text=None):
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, openai_api_key=openai_api_key)

    stats = stats['stats']


    if text is None:
        text = "Analyze this data provided and give extensive insights about the characteristics of the terrain, possible opportunities, environmental risks and challenges, advice on infrastructure development, and any other relevant information that can help in formulating sustainable policies and strategies for the provided data area. Also, show the statistics provided in a list"

    try:
        print()
        response = chat(
            [
                SystemMessage(content="You are a decision-maker responsible for the development and management of a given area. You have been provided with land cover statistics from the WRI Dynamic World dataset for your area, which includes information about various land cover types, such as water, trees, grass, crops, built-up areas, and more, units are in hectares."),
                AIMessage(content=json.dumps(stats)),
                HumanMessage(content=text)
            ]
        )
        print (SystemMessage, AIMessage, HumanMessage)

        return {"markdown": response.content}
    
    except Exception as e:
        return {"error": str(e)}
