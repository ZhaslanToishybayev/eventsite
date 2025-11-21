"""
API эндпоинты для интеграции с Serena AI
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from ..services_serena import SerenaAIService

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def serena_status(request):
    """Проверить статус Serena AI"""
    try:
        serena_service = SerenaAIService()
        is_available = serena_service.health_check()

        project_info = None
        if is_available:
            project_info = serena_service.get_project_info()

        return Response({
            'success': True,
            'available': is_available,
            'project_info': project_info
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Serena status check error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def serena_analyze_code(request):
    """Анализировать код с помощью Serena"""
    try:
        file_path = request.data.get('file_path')
        analysis_type = request.data.get('analysis_type', 'structure')

        if not file_path:
            return Response({
                'success': False,
                'error': 'file_path is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        serena_service = SerenaAIService()

        if not serena_service.health_check():
            return Response({
                'success': False,
                'error': 'Serena AI is not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Выполняем анализ в зависимости от типа
        if analysis_type == 'structure':
            result = serena_service.explain_code_structure(file_path)
        elif analysis_type == 'documentation':
            result = serena_service.generate_documentation(file_path)
        elif analysis_type == 'improvement':
            issue_description = request.data.get('issue_description', 'General improvement')
            result = serena_service.create_code_improvement_suggestion(file_path, issue_description)
        else:
            result = serena_service.explain_code_structure(file_path)

        return Response({
            'success': True,
            'analysis_type': analysis_type,
            'file_path': file_path,
            'result': result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Serena code analysis error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serena_search_symbol(request):
    """Найти символ в коде"""
    try:
        symbol_name = request.GET.get('symbol_name')
        file_path = request.GET.get('file_path')

        if not symbol_name:
            return Response({
                'success': False,
                'error': 'symbol_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        serena_service = SerenaAIService()

        if not serena_service.health_check():
            return Response({
                'success': False,
                'error': 'Serena AI is not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = serena_service.find_symbol(symbol_name, file_path)

        return Response({
            'success': True,
            'symbol_name': symbol_name,
            'file_path': file_path,
            'result': result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Serena symbol search error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serena_list_symbols(request):
    """Получить список символов в файле"""
    try:
        file_path = request.GET.get('file_path')

        if not file_path:
            return Response({
                'success': False,
                'error': 'file_path is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        serena_service = SerenaAIService()

        if not serena_service.health_check():
            return Response({
                'success': False,
                'error': 'Serena AI is not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = serena_service.get_symbols_overview(file_path)

        return Response({
            'success': True,
            'file_path': file_path,
            'result': result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Serena list symbols error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serena_project_info(request):
    """Получить информацию о проекте"""
    try:
        serena_service = SerenaAIService()

        if not serena_service.health_check():
            return Response({
                'success': False,
                'error': 'Serena AI is not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = serena_service.get_project_info()

        return Response({
            'success': True,
            'project_info': result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Serena project info error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)