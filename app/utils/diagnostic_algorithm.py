from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.diagnostic import DiagnosticOption
from app.models.method import Metodo

class DiagnosticAlgorithm:
    """Algoritmo simplificado para recomendar método de estudio"""
    
    @staticmethod
    def calculate_scores(db: Session, user_answers: List[Dict[str, int]]) -> Dict[str, int]:
        """
        Calcula los puntajes para cada método.
        
        Args:
            db: Sesión de base de datos
            user_answers: Lista de {'question_id': X, 'option_id': Y}
        
        Returns:
            {'pomodoro': 15, 'feynman': 12, 'cornell': 10, 'flashcards': 8}
        """
        scores = {'pomodoro': 0, 'feynman': 0, 'cornell': 0, 'flashcards': 0}
        
        for answer in user_answers:
            # Obtener opción con su método y puntos
            option = db.query(DiagnosticOption).filter(
                DiagnosticOption.option_id == answer['option_id']
            ).first()
            
            if option and option.method:
                method_name = option.method.nombre.lower()
                scores[method_name] = scores.get(method_name, 0) + option.points
        
        return scores
    
    @staticmethod
    def get_recommended_method(scores: Dict[str, int]) -> Tuple[str, Optional[str]]:
        """
        Determina el método principal y secundario.
        
        Returns:
            ('feynman', 'cornell') o ('pomodoro', None)
        """
        sorted_methods = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_methods[0][0]
        primary_score = sorted_methods[0][1]
        
        # Método secundario solo si tiene al menos 80% del puntaje del primero
        secondary = None
        if len(sorted_methods) > 1:
            secondary_score = sorted_methods[1][1]
            if secondary_score >= (primary_score * 0.8):
                secondary = sorted_methods[1][0]
        
        return primary, secondary
    
    @staticmethod
    def get_method_recommendations(method_name: str) -> Dict[str, any]:
        """Retorna info del método recomendado"""
        recommendations = {
            'pomodoro': {
                'title': 'Método Pomodoro',
                'description': 'Gestión del tiempo en bloques de 25 minutos',
                'tips': [
                    'Estudia en bloques de 25 minutos (pomodoros)',
                    'Toma descansos de 5 minutos entre pomodoros',
                    'Después de 4 pomodoros, descansa 15-30 minutos',
                    'Usa un temporizador y evita distracciones'
                ],
                'best_for': 'Concentración y productividad'
            },
            'feynman': {
                'title': 'Técnica Feynman',
                'description': 'Aprender explicando con palabras simples',
                'tips': [
                    'Elige un concepto y explícalo en voz alta',
                    'Usa lenguaje simple, como si enseñaras a un niño',
                    'Identifica donde te trabas (no entiendes bien)',
                    'Vuelve al material y profundiza esas áreas',
                    'Repite hasta explicarlo con fluidez'
                ],
                'best_for': 'Comprensión profunda de conceptos'
            },
            'cornell': {
                'title': 'Método Cornell',
                'description': 'Sistema organizado de toma de notas',
                'tips': [
                    'Divide tu página: notas (derecha), palabras clave (izquierda), resumen (abajo)',
                    'Toma notas durante la clase en la sección principal',
                    'Escribe palabras clave y preguntas a la izquierda',
                    'Resume toda la página al final',
                    'Repasa cubriendo las notas y respondiendo con las palabras clave'
                ],
                'best_for': 'Organización y repaso efectivo'
            },
            'flashcards': {
                'title': 'Flashcards',
                'description': 'Tarjetas de memoria con repetición espaciada',
                'tips': [
                    'Crea tarjetas con pregunta adelante, respuesta atrás',
                    'Repasa diariamente las tarjetas nuevas',
                    'Organiza en pilas: fácil, medio, difícil',
                    'Repasa las difíciles más frecuentemente',
                    'Usa apps como Anki o Quizlet para automatizar'
                ],
                'best_for': 'Memorización y retención a largo plazo'
            }
        }
        
        return recommendations.get(method_name, recommendations['pomodoro'])