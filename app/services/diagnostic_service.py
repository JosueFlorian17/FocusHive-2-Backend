from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime

from app.models.diagnostic import DiagnosticQuestion, DiagnosticOption, DiagnosticResponse
from app.models.user_method import UsuarioMetodo
from app.models.user import Usuario
from app.models.method import Metodo
from app.schemas.diagnostic import UserAnswerSchema
from app.utils.diagnostic_algorithm import DiagnosticAlgorithm

class DiagnosticService:
    
    @staticmethod
    def get_all_questions(db: Session) -> List[DiagnosticQuestion]:
        """Obtiene todas las preguntas ordenadas"""
        questions = db.query(DiagnosticQuestion).order_by(
            DiagnosticQuestion.question_order
        ).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay preguntas disponibles"
            )
        
        return questions
    
    @staticmethod
    def check_diagnostic_status(db: Session, user_id: int) -> Dict:
        """Verifica si el usuario completó el diagnóstico"""
        user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Buscar método recomendado
        recommended = db.query(UsuarioMetodo).filter(
            UsuarioMetodo.user_id == user_id,
            UsuarioMetodo.es_recomendado == True
        ).first()
        
        return {
            "diagnostic_completed": bool(user.diagnostic_completed),
            "has_recommended_method": recommended is not None,
            "recommended_method_id": recommended.metodo_id if recommended else None
        }
    
    @staticmethod
    def validate_answers(db: Session, answers: List[UserAnswerSchema]) -> bool:
        """Valida que las respuestas sean correctas"""
        total_questions = db.query(DiagnosticQuestion).count()
        
        if len(answers) != total_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Debes responder todas las preguntas ({total_questions})"
            )
        
        # Validar cada respuesta
        for answer in answers:
            option = db.query(DiagnosticOption).filter(
                DiagnosticOption.option_id == answer.option_id,
                DiagnosticOption.question_id == answer.question_id
            ).first()
            
            if not option:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Opción {answer.option_id} no válida para pregunta {answer.question_id}"
                )
        
        return True
    
    @staticmethod
    def process_diagnostic(
        db: Session,
        user_id: int,
        answers: List[UserAnswerSchema]
    ) -> Dict:
        """
        Procesa el diagnóstico completo.
        Implementa el requisito funcional #5
        """
        # 1. Validar
        DiagnosticService.validate_answers(db, answers)
        
        # 2. Eliminar respuestas anteriores si existen
        db.query(DiagnosticResponse).filter(
            DiagnosticResponse.user_id == user_id
        ).delete()
        
        # 3. Guardar nuevas respuestas
        for answer in answers:
            response = DiagnosticResponse(
                user_id=user_id,
                question_id=answer.question_id,
                option_id=answer.option_id
            )
            db.add(response)
        
        # 4. Calcular scores
        answers_dict = [
            {"question_id": a.question_id, "option_id": a.option_id}
            for a in answers
        ]
        scores = DiagnosticAlgorithm.calculate_scores(db, answers_dict)
        
        # 5. Determinar método recomendado
        primary_name, secondary_name = DiagnosticAlgorithm.get_recommended_method(scores)
        
        # 6. Obtener método de la BD
        primary_method = db.query(Metodo).filter(
            Metodo.nombre.ilike(primary_name)
        ).first()
        
        secondary_method = None
        if secondary_name:
            secondary_method = db.query(Metodo).filter(
                Metodo.nombre.ilike(secondary_name)
            ).first()
        
        if not primary_method:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Método '{primary_name}' no encontrado en BD"
            )
        
        try:
            # 7. Limpiar recomendaciones anteriores del usuario
            db.query(UsuarioMetodo).filter(
                UsuarioMetodo.user_id == user_id
            ).update({"es_recomendado": False})
            
            # 8. Marcar método principal como recomendado
            user_method = db.query(UsuarioMetodo).filter(
                UsuarioMetodo.user_id == user_id,
                UsuarioMetodo.metodo_id == primary_method.metodo_id
            ).first()
            
            if user_method:
                user_method.es_recomendado = True
            else:
                new_user_method = UsuarioMetodo(
                    user_id=user_id,
                    metodo_id=primary_method.metodo_id,
                    es_recomendado=True,
                    es_utilizado=False
                )
                db.add(new_user_method)
            
            # 9. Marcar método secundario si existe
            if secondary_method:
                sec_user_method = db.query(UsuarioMetodo).filter(
                    UsuarioMetodo.user_id == user_id,
                    UsuarioMetodo.metodo_id == secondary_method.metodo_id
                ).first()
                
                if sec_user_method:
                    sec_user_method.es_recomendado = True
                else:
                    new_sec = UsuarioMetodo(
                        user_id=user_id,
                        metodo_id=secondary_method.metodo_id,
                        es_recomendado=True,
                        es_utilizado=False
                    )
                    db.add(new_sec)
            
            # 10. Actualizar usuario
            user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
            user.diagnostic_completed = True
            
            db.commit()
            
            # 11. Preparar resultado
            primary_info = DiagnosticAlgorithm.get_method_recommendations(primary_name)
            secondary_info = None
            if secondary_name:
                secondary_info = DiagnosticAlgorithm.get_method_recommendations(secondary_name)
            
            return {
                "primary_method": {
                    "method_id": primary_method.metodo_id,
                    "method_name": primary_method.nombre,
                    "score": scores[primary_name],
                    **primary_info
                },
                "secondary_method": {
                    "method_id": secondary_method.metodo_id,
                    "method_name": secondary_method.nombre,
                    "score": scores[secondary_name],
                    **secondary_info
                } if secondary_method else None,
                "all_scores": scores
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al procesar: {str(e)}"
            )
    
    @staticmethod
    def get_user_result(db: Session, user_id: int) -> Optional[Dict]:
        """Obtiene el resultado del diagnóstico del usuario"""
        user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
        
        if not user or not user.diagnostic_completed:
            return None
        
        # Obtener método recomendado
        recommended = db.query(UsuarioMetodo, Metodo).join(
            Metodo, UsuarioMetodo.metodo_id == Metodo.metodo_id
        ).filter(
            UsuarioMetodo.user_id == user_id,
            UsuarioMetodo.es_recomendado == True
        ).all()
        
        if not recommended:
            return None
        
        # Reconstruir resultado
        primary = recommended[0][1]  # Primer método recomendado
        secondary = recommended[1][1] if len(recommended) > 1 else None
        
        primary_info = DiagnosticAlgorithm.get_method_recommendations(primary.nombre.lower())
        
        result = {
            "primary_method": {
                "method_id": primary.metodo_id,
                "method_name": primary.nombre,
                **primary_info
            },
            "secondary_method": None
        }
        
        if secondary:
            secondary_info = DiagnosticAlgorithm.get_method_recommendations(secondary.nombre.lower())
            result["secondary_method"] = {
                "method_id": secondary.metodo_id,
                "method_name": secondary.nombre,
                **secondary_info
            }
        
        return result