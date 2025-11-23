from pydantic import BaseModel, Field, validator
from typing import List, Optional

# QUESTION SCHEMAS 
class DiagnosticOptionSchema(BaseModel):
    option_id: int
    option_text: str
    
    class Config:
        from_attributes = True

class DiagnosticQuestionSchema(BaseModel):
    question_id: int
    question_text: str
    question_order: int
    options: List[DiagnosticOptionSchema]
    
    class Config:
        from_attributes = True

class DiagnosticQuestionsResponse(BaseModel):
    total_questions: int
    questions: List[DiagnosticQuestionSchema]

# ANSWER SCHEMAS 
class UserAnswerSchema(BaseModel):
    question_id: int = Field(..., gt=0)
    option_id: int = Field(..., gt=0)

class SubmitDiagnosticSchema(BaseModel):
    answers: List[UserAnswerSchema] = Field(..., min_items=1)
    
    @validator('answers')
    def validate_unique_questions(cls, v):
        question_ids = [a.question_id for a in v]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError('No puedes responder la misma pregunta dos veces')
        return v

# RESULT SCHEMAS 
class MethodInfoSchema(BaseModel):
    method_id: int
    method_name: str
    score: Optional[int] = None
    title: str
    description: str
    tips: List[str]
    best_for: str

class DiagnosticResultResponse(BaseModel):
    message: str
    primary_method: MethodInfoSchema
    secondary_method: Optional[MethodInfoSchema]
    all_scores: Optional[dict[str, int]] = None

class DiagnosticStatusSchema(BaseModel):
    diagnostic_completed: bool
    has_recommended_method: bool
    recommended_method_id: Optional[int]