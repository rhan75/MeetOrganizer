from sqlalchemy.orm import aliased
from models.model import * 

AG = aliased(Age_Group)
AGC = aliased(Age_Group_Class)

CS = aliased(Competition_Skater)
CAGR = aliased(Competition_Age_Group_Result)
CAGRD = aliased(Competition_Age_Group_Result_Detail)

RHS = aliased(Race_Heat_Schedule)
RHR = aliased(Race_Heat_Result)
RHRD = aliased(Race_Heat_Result_Detail)
RAGR = aliased(Race_Age_Group_Result)
RHSD = aliased(Race_Heat_Schedule_Detail)
RAGRD = aliased(Race_Age_Group_Result_Detail)
RS = aliased(Race_Style)