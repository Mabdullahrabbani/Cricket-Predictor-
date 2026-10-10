from fastapi import FastAPI , HTTPException
from pydantic import BaseModel , Field
import pandas as pd
import schemas
import joblib
from utilis import Generate_Description
from fastapi.responses import JSONResponse
app = FastAPI()

@app.exception_handler(Exception)
async def show_error(request, exc):
    return JSONResponse(status_code=500, content={"detail": f"{type(exc).__name__}: {exc}"})
try:
    with open("next_over_runs_model.pkl" , 'rb') as f:
        Next_Over_Runs_Model  = joblib.load(f)
    with open("First_innings_ScorePredictor.pkl" , 'rb') as f:
        First_Innings_Score_Model = joblib.load(f)
    with open("WinProbabiltyPredictor.pkl" , 'rb') as f:
        Win_Predictor_Model = joblib.load(f)
except Exception as e:
    print(f"FATAL: Model loading failed: {e}")
    raise SystemExit(1)
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
def getverdict(chase_win):
    if chase_win >= 0.75:
      verdict = "Chasing team is strong favourites"
    elif chase_win >= 0.55:
        verdict = "Chasing team has the edge"
    elif chase_win > 0.45:
        verdict = "Evenly poised"
    elif chase_win > 0.25:
        verdict = "Bowling team has the edge"
    else:
        verdict = "Bowling team is strong favourites"
    return verdict 
@app.post("/NextOverRuns")
def Predict_Next_Over_Runs(ScoreBoard : schemas.NextOver):
    Overs_remaining = 20 - ScoreBoard.overs
    Is_Chasing = True if ScoreBoard.Innings == 2 else False
    Required_Run_Rate = 0.0 if not Is_Chasing else (ScoreBoard.Target - ScoreBoard.Score) / Overs_remaining
    Run_Rate = ScoreBoard.Score / ScoreBoard.overs
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
    'Run_Rate_Before': [Run_Rate],
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
    predicted = max(0, round(Predicion))        # runs can't be negative
    low = max(0, predicted - 2)
    high = predicted + 2
    projected_score = ScoreBoard.Score + predicted
    next_over = ScoreBoard.overs + 1
    return {
        "Predicted_Runs": predicted,
        "Likely_Range": f"{low} - {high} runs",
        "Current_Situation": f"{ScoreBoard.Score}/{ScoreBoard.Wickets} after {ScoreBoard.overs} overs " f"(CRR {Run_Rate:.2f})",
        "After_Next_Over": f"Around {projected_score}/{ScoreBoard.Wickets} after {next_over} overs",
        "Analysis": Ananlysis,
    }
@app.post("/FirstInningsScore")
def FirstInningsScore_Predictor(ScoreBoard:schemas.FirstInningsScore):
     Middle_Overs = True if (ScoreBoard.overs > 6 and ScoreBoard.overs < 15) else False
     Run_Rate = ScoreBoard.Score / ScoreBoard.overs
     test_input = pd.DataFrame({
           "overs" : [ScoreBoard.overs] , 
           "Runs_This_Over" : [ScoreBoard.Runs_In_Last_Over] , 
           "Wickets_This_Over" : [ScoreBoard.Wickets_In_Last_Over] , 
           "Current_Score":[ScoreBoard.Score] , 
           "Run_Rate" : [Run_Rate] , 
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
     predicted = round(prediction)
     low, high = predicted - 17, predicted + 17
     low = max(low, ScoreBoard.Score)
     high = max(high, low)
     overs_left = 20 - ScoreBoard.overs
     runs_to_add = predicted - ScoreBoard.Score
     return {
    "Predicted_Score": predicted,
    "Likely_Range": f"{low} - {high}",
    "Current_Situation": f"{ScoreBoard.Score}/{ScoreBoard.Wickets} after {ScoreBoard.overs} overs "
                         f"(CRR {Run_Rate:.2f})",
    "Remaining": f"About {runs_to_add} more runs expected in {overs_left} overs "
                 f"({runs_to_add / overs_left:.2f} per over)",
       "Analysis": Ananlysis,
    }

@app.post("/WinProbablity")
def Win_Probability(ScoreBoard:schemas.Win_Probabality):
    Middle_Overs = MiddleOverDecider(ScoreBoard.overs)
    Wickets_In_Hands = 10 -ScoreBoard.Total_Wickets
    Run_Rate = ScoreBoard.Current_Score / ScoreBoard.overs
    Required_Run_rate = (ScoreBoard.Target - ScoreBoard.Current_Score) / (20 - ScoreBoard.overs)
    test_input = pd.DataFrame({
    'overs': [ScoreBoard.overs],
    'Runs_This_Over': [ScoreBoard.Runs_Last_Over],
    'Wickets_This_Over': [ScoreBoard.Wickets_Last_Over],
    'Current_Score': [ScoreBoard.Current_Score],
    'Run_Rate': [Run_Rate],
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
    chase_win = Prediction[1]
    bowl_win = 1- chase_win
    verdict = getverdict(chase_win)
    runs_needed = ScoreBoard.Target - ScoreBoard.Current_Score
    overs_left = 20 - ScoreBoard.overs
    return {
                "Chasing_Team_Win" : f"{chase_win * 100 :.1f}%" ,
                "Bowling_Team_Win": f"{bowl_win * 100:.1f}%",
                "Match_Situation": f"Need {runs_needed} runs in {overs_left} overs "
                       f"(RRR {Required_Run_rate:.2f}) with "
                       f"{Wickets_In_Hands} wickets in hand",
                "Verdict": verdict,
                "Analysis" : Ananlysis
    }


     

   
    



