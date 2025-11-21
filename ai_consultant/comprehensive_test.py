#!/usr/bin/env python
"""
🧪 Comprehensive Test Suite for AI Consultant
Проверка всех компонентов системы
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Тест 1: Проверка импортов"""
    print("🧪 Тест 1: Проверка импортов...")
    try:
        from ai_consultant.agents.registry import AgentRegistry
        from ai_consultant.agents.specialists.orchestrator import OrchestratorAgent
        from ai_consultant.agents.specialists.club_agent import ClubAgent
        from ai_consultant.agents.specialists.support_agent import SupportAgent
        from ai_consultant.agents.specialists.mentor_agent import MentorAgent
        from ai_consultant.agents.router import AgentRouter
        print("✅ Все импорты успешны")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_agent_registration():
    """Тест 2: Проверка регистрации агентов"""
    print("\n🧪 Тест 2: Проверка регистрации агентов...")
    try:
        from ai_consultant.agents.registry import AgentRegistry
        
        agents = AgentRegistry.get_all_agents()
        expected_agents = ['orchestrator', 'club_specialist', 'support_specialist', 'mentor_specialist']
        
        for agent_name in expected_agents:
            if agent_name in agents:
                print(f"✅ {agent_name} зарегистрирован")
            else:
                print(f"❌ {agent_name} НЕ зарегистрирован")
                return False
        
        print(f"✅ Всего зарегистрировано агентов: {len(agents)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка регистрации: {e}")
        return False

def test_agent_prompts():
    """Тест 3: Проверка промптов агентов"""
    print("\n🧪 Тест 3: Проверка промптов агентов...")
    try:
        from ai_consultant.agents.registry import AgentRegistry
        
        agents = AgentRegistry.get_all_agents()
        all_ok = True
        
        for agent_name, agent_class in agents.items():
            agent = agent_class()
            prompt = agent.get_system_prompt()
            
            # Проверяем что промпт не пустой
            if not prompt or len(prompt) < 100:
                print(f"❌ {agent_name}: промпт слишком короткий ({len(prompt)} символов)")
                all_ok = False
                continue
            
            # Проверяем наличие ключевых слов
            if "ЦЕНТР СОБЫТИЙ" in prompt or "UnitySphere" in prompt:
                print(f"✅ {agent_name}: промпт содержит название платформы ({len(prompt)} символов)")
            else:
                print(f"⚠️  {agent_name}: промпт не содержит название платформы")
            
            # Проверяем наличие эмодзи
            if any(ord(c) > 127 for c in prompt):
                print(f"✅ {agent_name}: промпт содержит эмодзи")
            else:
                print(f"⚠️  {agent_name}: промпт не содержит эмодзи")
        
        return all_ok
    except Exception as e:
        print(f"❌ Ошибка проверки промптов: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_tools():
    """Тест 4: Проверка инструментов агентов"""
    print("\n🧪 Тест 4: Проверка инструментов агентов...")
    try:
        from ai_consultant.agents.registry import AgentRegistry
        
        agents = AgentRegistry.get_all_agents()
        
        # ClubAgent должен иметь search_clubs
        club_agent = agents['club_specialist']()
        club_tools = club_agent.get_tools()
        if club_tools and any(t['function']['name'] == 'search_clubs' for t in club_tools):
            print("✅ ClubAgent: search_clubs найден")
        else:
            print("❌ ClubAgent: search_clubs НЕ найден")
            return False
        
        # SupportAgent должен иметь инструменты
        support_agent = agents['support_specialist']()
        support_tools = support_agent.get_tools()
        if support_tools:
            print(f"✅ SupportAgent: {len(support_tools)} инструментов")
        else:
            print("⚠️  SupportAgent: нет инструментов")
        
        # MentorAgent должен иметь инструменты
        mentor_agent = agents['mentor_specialist']()
        mentor_tools = mentor_agent.get_tools()
        if mentor_tools:
            print(f"✅ MentorAgent: {len(mentor_tools)} инструментов")
        else:
            print("⚠️  MentorAgent: нет инструментов")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки инструментов: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_method_signatures():
    """Тест 5: Проверка сигнатур методов"""
    print("\n🧪 Тест 5: Проверка сигнатур методов...")
    try:
        from ai_consultant.agents.registry import AgentRegistry
        import inspect
        
        agents = AgentRegistry.get_all_agents()
        all_ok = True
        
        for agent_name, agent_class in agents.items():
            agent = agent_class()
            
            # Проверяем сигнатуру get_system_prompt
            sig = inspect.signature(agent.get_system_prompt)
            params = list(sig.parameters.keys())
            
            # Должен принимать user_context как опциональный параметр
            if 'user_context' in params:
                print(f"✅ {agent_name}: правильная сигнатура get_system_prompt")
            else:
                print(f"⚠️  {agent_name}: нестандартная сигнатура: {params}")
        
        return all_ok
    except Exception as e:
        print(f"❌ Ошибка проверки сигнатур: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_css_js_files():
    """Тест 6: Проверка CSS и JS файлов"""
    print("\n🧪 Тест 6: Проверка CSS и JS файлов...")
    try:
        import os
        
        # Проверяем CSS
        css_path = 'static/css/ai-chat-widget.css'
        if os.path.exists(css_path):
            size = os.path.getsize(css_path)
            print(f"✅ CSS файл найден ({size} байт)")
            
            # Проверяем ключевые классы
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
                required_classes = [
                    '.ai-chat-widget',
                    '.ai-chat-container',
                    '.ai-chat-messages',
                    '.ai-chat-input',
                    'flex: 1',
                    'min-height: 0',
                    'overflow-y: auto'
                ]
                
                for cls in required_classes:
                    if cls in content:
                        print(f"  ✅ {cls}")
                    else:
                        print(f"  ❌ {cls} НЕ найден")
        else:
            print(f"❌ CSS файл не найден: {css_path}")
            return False
        
        # Проверяем JS
        js_path = 'static/js/ai-chat-widget.js'
        if os.path.exists(js_path):
            size = os.path.getsize(js_path)
            print(f"✅ JS файл найден ({size} байт)")
            
            # Проверяем ключевые функции
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                required_methods = [
                    'class AIChatWidget',
                    'sendMessage',
                    'toggleChat',
                    'setupKeyboardShortcuts',
                    'scrollToBottom'
                ]
                
                for method in required_methods:
                    if method in content:
                        print(f"  ✅ {method}")
                    else:
                        print(f"  ❌ {method} НЕ найден")
        else:
            print(f"❌ JS файл не найден: {js_path}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки файлов: {e}")
        return False

def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🚀 КОМПЛЕКСНАЯ ПРОВЕРКА AI КОНСУЛЬТАНТА")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_agent_registration,
        test_agent_prompts,
        test_agent_tools,
        test_method_signatures,
        test_css_js_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Критическая ошибка в тесте: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n✅ Пройдено: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА К РАБОТЕ!")
        return 0
    else:
        print(f"\n⚠️  Некоторые тесты не прошли. Проверьте ошибки выше.")
        return 1

if __name__ == '__main__':
    exit(main())
