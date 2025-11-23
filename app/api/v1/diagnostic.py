from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.user import Usuario
from app.schemas.diagnostic import (
    DiagnosticQuestionsResponse,
    DiagnosticQuestionSchema,
    DiagnosticOptionSchema,
    SubmitDiagnosticSchema,
    DiagnosticResultResponse,
    DiagnosticStatusSchema
)
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(prefix="/diagnostic", tags=["Diagnostic"])

@router.get("/status", response_model=DiagnosticStatusSchema)
async def get_status(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica si el usuario completó el diagnóstico"""
    return DiagnosticService.check_diagnostic_status(db, current_user.user_id)

@router.get("/questions", response_model=DiagnosticQuestionsResponse)
async def get_questions(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las preguntas del diagnóstico"""
    questions = DiagnosticService.get_all_questions(db)
    
    questions_data = []
    for q in questions:
        options_data = [
            DiagnosticOptionSchema(
                option_id=opt.option_id,
                option_text=opt.option_text
            )
            for opt in q.options
        ]
        
        questions_data.append(
            DiagnosticQuestionSchema(
                question_id=q.question_id,
                question_text=q.question_text,
                question_order=q.question_order,
                options=options_data
            )
        )
    
    return DiagnosticQuestionsResponse(
        total_questions=len(questions_data),
        questions=questions_data
    )

@router.post("/submit", response_model=DiagnosticResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_diagnostic(
    data: SubmitDiagnosticSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Procesa el diagnóstico y retorna el método recomendado"""
    result = DiagnosticService.process_diagnostic(db, current_user.user_id, data.answers)
    
    return DiagnosticResultResponse(
        message="Diagnóstico completado exitosamente",
        **result
    )

@router.get("/result", response_model=DiagnosticResultResponse)
async def get_result(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el resultado guardado del diagnóstico"""
    result = DiagnosticService.get_user_result(db, current_user.user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No has completado el diagnóstico"
        )
    
    return DiagnosticResultResponse(
        message="Resultado obtenido",
        **result
    )