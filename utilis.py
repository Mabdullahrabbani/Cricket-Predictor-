from  openai  import OpenAI
from dotenv import load_dotenv
import os 
load_dotenv()
answer = OpenAI(api_key= os.getenv("OPEN_Ai_KEY") ,  base_url="https://api.groq.com/openai/v1" )
def Generate_Description (Prediction_type: str , Prediction : float , ScoreBoard : dict ):
            
            prompt = f"""You are a cricket analyst. A prediction model produced this result:
            Prediction type: {Prediction_type}
            Predicted value: {Prediction}
            Match situation: {ScoreBoard}
            In 2-3 simple sentences, explain why this prediction makes sense given the match situation. Write for a casual cricket fan, not a data scientist."""

            response = answer.chat.completions.create(
                    model = "openai/gpt-oss-20b" , 
                    messages= [
                            {'role' :  "user" , "content" : prompt}
                    ]
                
        )
            return response.choices[0].message.content

