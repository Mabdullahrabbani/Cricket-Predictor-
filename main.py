from fastapi import FastAPI , HTTPException
from pydantic import BaseModel , Field
import pandas as pd
import joblib
from utilis import Generate_Description
app = FastAPI()
try:
    with open("next_over_runs_model.pkl" , 'rb') as f:
        Next_Over_Runs_Model  = joblib.load(f)
    with open("First_innings_Score Predictor .pkl" , 'rb') as f:
        First_Innings_Score_Model = joblib.load(f)
    with open("Win Probabilty Predictor.pkl" , 'rb') as f:
        Win_Predictor_Model = joblib.load(f)
except Exception as e:
    print(f"FATAL: Model loading failed: {e}")
    raise SystemExit(1)
class NextOver(BaseModel):
    overs : int  = Field(ge = 1  , le = 19)
    Score : int  = Field(ge = 0)
    Wickets : int  = Field(ge = 0 , le = 9 )
    Innings : int = Field(ge = 1 , le = 2)
    Run_Rate : float  = Field(ge = 0)
    Target : int  = Field(ge = 0 )
class FirstInningsScore(BaseModel):
    overs: int = Field(ge=1, le=19)
    Score: int = Field(ge=0)
    Wickets: int = Field(ge=0, le=9)
    Run_Rate: float = Field(ge=0)
    Runs_In_Last_Over: int = Field(ge=0 , le = 50)
    Wickets_In_Last_Over: int = Field(ge=0, le=6)
class Win_Probabality(BaseModel):
    overs: int = Field(ge=1, le=19)
    Current_Score: int = Field(ge=0)
    Total_Wickets: int = Field(ge=0, le=9)
    Runs_Last_Over: int = Field(ge=0 , le= 50)
    Wickets_Last_Over: int = Field(ge=0, le=6)
    Run_Rate: float = Field(ge=0)
    Target: int = Field(ge=0)

@app.get("/")
def Welcome():
    return {
        "Message" : "Welcome to CricPredictor ! "
    }

def PowerplayDecider(Over):
    return  Over <= 5 
def MiddleOverDecider(Over):
    return  Over  >= 6 and Over <= 14  
def DeathOverDecider(Over):
    return Over >= 15

@app.post("/NextOverRuns")
def Predict_Next_Over_Runs(ScoreBoard : NextOver):
    Overs_remaining = 20 - ScoreBoard.overs
    Is_Chasing = True if ScoreBoard.Innings == 2 else False
    Required_Run_Rate = 0.0 if not Is_Chasing else (ScoreBoard.Target - ScoreBoard.Score) / Overs_remaining
    test_input = pd.DataFrame({
    'overs': [ScoreBoard.overs],
    'Power_Play': [PowerplayDecider(ScoreBoard.overs)],
    'Middle_Overs': [MiddleOverDecider(ScoreBoard.overs)],
    'Death_Overs': [DeathOverDecider(ScoreBoard.overs)],
    'Overs_remaining': [20 - ScoreBoard.overs],
    'Innings': [ScoreBoard.Innings],
    'Is_Chasing': [Is_Chasing],
    'Target': [ScoreBoard.Target],
    'Required_Run_Rate': [Required_Run_Rate],
    'Score_Before_This_Over': [ScoreBoard.Score],
    'Wickets_Before_This_Over': [ScoreBoard.Wickets],
    'Run_Rate_Before': [ScoreBoard.Run_Rate],
    'Wickets_In_Hands_Before': [10 - ScoreBoard.Wickets]
    })
    try:
        Predicion = Next_Over_Runs_Model.predict(test_input)[0] 
    except Exception as e:
     raise HTTPException(
         status_code= 500 , detail = f"Error Form Our side has occured {str(e)}"
     )
    Data = test_input.iloc[0].to_dict()
    Ananlysis = Generate_Description("NextOverRuns" , round(Predicion) , Data)
    return {
            "Output" : f"About {round(Predicion) - 2} to {round(Predicion) + 2 } Runs Can Be Scored "
              , "Ananlysis" : Ananlysis
    }
@app.post("/FirstInningsScore")
def FirstInningsScore_Predictor(ScoreBoard:FirstInningsScore):
     Middle_Overs = True if (ScoreBoard.overs > 6 and ScoreBoard.overs < 15) else False
     test_input = pd.DataFrame({
           "overs" : [ScoreBoard.overs] , 
           "Runs_This_Over" : [ScoreBoard.Runs_In_Last_Over] , 
           "Wickets_This_Over" : [ScoreBoard.Wickets_In_Last_Over] , 
           "Current_Score":[ScoreBoard.Score] , 
           "Run_Rate" : [ScoreBoard.Run_Rate] , 
           "Wickets_In_Hands": [10-ScoreBoard.Wickets]  , 
           "Middle_Overs" : [Middle_Overs]
        })

     try :
        prediction =  First_Innings_Score_Model.predict(test_input)[0]
     except Exception as e:
          raise HTTPException(
              status_code= 500 , detail = f"Error Form Our side has occured {str(e)}"
          )
     Data = test_input.iloc[0].to_dict()
     Ananlysis = Generate_Description("WhatScoreInFirstInnings" , prediction , Data)
     return {
            "Output" : f"About {round(prediction) - 17} to {round(prediction) + 17  } Runs Can Be Scored "
              , "Ananlysis" : Ananlysis
    }


@app.post("/WinProbablity")
def Win_Probability(ScoreBoard:Win_Probabality):
    Middle_Overs = MiddleOverDecider(ScoreBoard.overs)
    Wickets_In_Hands = 10 -ScoreBoard.Total_Wickets
    Required_Run_rate = (ScoreBoard.Target - ScoreBoard.Current_Score) / (20 - ScoreBoard.overs)
    test_input = pd.DataFrame({
    'overs': [ScoreBoard.overs],
    'Runs_This_Over': [ScoreBoard.Runs_Last_Over],
    'Wickets_This_Over': [ScoreBoard.Wickets_Last_Over],
    'Current_Score': [ScoreBoard.Current_Score],
    'Run_Rate': [ScoreBoard.Run_Rate],
    'Total_Wickets': [ScoreBoard.Total_Wickets],
    'Wickets_In_Hands': [Wickets_In_Hands],
    'Middle_Overs': [Middle_Overs],
    'Target': [ScoreBoard.Target],
    'Required_Run_rate': [Required_Run_rate],
    })
    try:
        Prediction = Win_Predictor_Model.predict_proba(test_input)[0]
    except Exception as e:
        raise HTTPException(
                  status_code= 500 , detail = f"Error Form Our side has occured {str(e)}"
              )
    Data = test_input.iloc[0].to_dict()
    Ananlysis = Generate_Description("CanChase_probabilty" ,Prediction[0] ,Data)
    return {
        "Output" : f"The Winnings Chances Are {Prediction[0] * 100:.2f}% and {Prediction[1] * 100:.2f}%)"  ,
         "Analysis" : Ananlysis
    }


     

   
    



