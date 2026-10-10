from pydantic import BaseModel, Field, model_validator


def check_common(score, wickets, runs_last=None, wkts_last=None):
    if runs_last is not None and runs_last > score:
        raise ValueError("Runs in last over can't exceed the score")
    if wkts_last is not None and wkts_last > wickets:
        raise ValueError("Wickets in last over can't exceed total wickets")


class NextOver(BaseModel):
    overs: int = Field(ge=1, le=19)
    Score: int = Field(ge=0)
    Wickets: int = Field(ge=0, le=9)
    Innings: int = Field(ge=1, le=2)
    Target: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def check_input(self):
        if self.Innings == 2:
            if self.Target <= 0:
                raise ValueError("Target is required in the second innings")
            if self.Target <= self.Score:
                raise ValueError("Target is already achieved")
        else:
            self.Target = 0
        return self


class FirstInningsScore(BaseModel):
    overs: int = Field(ge=1, le=19)
    Score: int = Field(ge=0)
    Wickets: int = Field(ge=0, le=9)
    Runs_In_Last_Over: int = Field(ge=0, le=50)
    Wickets_In_Last_Over: int = Field(ge=0, le=6)

    @model_validator(mode="after")
    def check_input(self):
        check_common(self.Score, self.Wickets,
                     self.Runs_In_Last_Over, self.Wickets_In_Last_Over)
        return self


class Win_Probabality(BaseModel):
    overs: int = Field(ge=1, le=19)
    Current_Score: int = Field(ge=0)
    Total_Wickets: int = Field(ge=0, le=9)
    Runs_Last_Over: int = Field(ge=0, le=50)
    Wickets_Last_Over: int = Field(ge=0, le=6)
    Target: int = Field(gt=0)

    @model_validator(mode="after")
    def check_input(self):
        check_common(self.Current_Score, self.Total_Wickets,
                     self.Runs_Last_Over, self.Wickets_Last_Over)
        if self.Current_Score >= self.Target:
            raise ValueError("Score already reached the target")
        return self