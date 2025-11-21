"""
Comprehensive Test Suite for Enhanced Club Creation
Tests all improvements: validation, error handling, confirmation, step-by-step flow
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/zhaslan/Downloads/unitysphere-project/home/almalinux/new/unitysphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import Club, ClubCategory, City
from ai_consultant.services.club_creation import ClubCreationService
from ai_consultant.services.club_validator import ClubCreationValidator, ClubCreationConfirmation

User = get_user_model()


class TestEnhancedClubCreation:
    """Test suite for enhanced club creation system"""
    
    def __init__(self):
        self.service = ClubCreationService()
        self.test_user = None
        self.results = []
        
    def setup(self):
        """Setup test environment"""
        print("\n" + "="*80)
        print("🧪 SETTING UP TEST ENVIRONMENT")
        print("="*80)
        
        # Try to get existing user first
        self.test_user = User.objects.filter(email='test_club_creator@example.com').first()
        
        if not self.test_user:
            # Create new test user with unique phone
            import random
            unique_phone = f'+7700{random.randint(1000000, 9999999)}'
            
            self.test_user = User.objects.create(
                email='test_club_creator@example.com',
                phone=unique_phone,
                first_name='Test',
                last_name='Creator'
            )
            self.test_user.set_password('testpass123')
            self.test_user.save()
            print(f"✅ Created test user: {self.test_user.email}")
        else:
            print(f"✅ Using existing test user: {self.test_user.email}")
        
        # Ensure categories exist
        categories = ['Спорт', 'Хобби', 'IT', 'Профессия']
        for cat_name in categories:
            cat, created = ClubCategory.objects.get_or_create(name=cat_name)
            if created:
                print(f"✅ Created category: {cat_name}")
        
        print("\n")
    
    def cleanup(self):
        """Cleanup test data"""
        print("\n" + "="*80)
        print("🧹 CLEANING UP TEST DATA")
        print("="*80)
        
        # Delete test clubs
        test_clubs = Club.objects.filter(creater=self.test_user)
        count = test_clubs.count()
        test_clubs.delete()
        print(f"✅ Deleted {count} test clubs")
        
        print("\n")
    
    def log_result(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   → {message}")
    
    # ========================================================================
    # TEST 1: Validation - Name
    # ========================================================================
    
    def test_name_validation(self):
        """Test name validation rules"""
        print("\n" + "-"*80)
        print("TEST 1: Name Validation")
        print("-"*80)
        
        # Test 1.1: Too short
        is_valid, error = ClubCreationValidator.validate_club_name("ab")
        self.log_result(
            "Name too short (< 3 chars)",
            not is_valid and "слишком короткое" in error.lower(),
            error
        )
        
        # Test 1.2: Too long
        long_name = "a" * 101
        is_valid, error = ClubCreationValidator.validate_club_name(long_name)
        self.log_result(
            "Name too long (> 100 chars)",
            not is_valid and "слишком длинное" in error.lower(),
            error
        )
        
        # Test 1.3: Forbidden word
        is_valid, error = ClubCreationValidator.validate_club_name("Test Club")
        self.log_result(
            "Forbidden word 'test'",
            not is_valid and "запрещенное слово" in error.lower(),
            error
        )
        
        # Test 1.4: No letters
        is_valid, error = ClubCreationValidator.validate_club_name("123!!!")
        self.log_result(
            "No letters in name",
            not is_valid and "букву" in error.lower(),
            error
        )
        
        # Test 1.5: Valid name
        is_valid, error = ClubCreationValidator.validate_club_name("Шахматный клуб Алматы")
        self.log_result(
            "Valid name",
            is_valid,
            "Name is valid"
        )
    
    # ========================================================================
    # TEST 2: Validation - Description
    # ========================================================================
    
    def test_description_validation(self):
        """Test description validation rules"""
        print("\n" + "-"*80)
        print("TEST 2: Description Validation")
        print("-"*80)
        
        # Test 2.1: Too short
        short_desc = "Клуб для всех"
        is_valid, error = ClubCreationValidator.validate_description(short_desc)
        self.log_result(
            "Description too short (< 200 chars)",
            not is_valid and "200" in error,
            f"Length: {len(short_desc)} chars"
        )
        
        # Test 2.2: Not diverse enough
        repetitive = "а" * 250
        is_valid, error = ClubCreationValidator.validate_description(repetitive)
        self.log_result(
            "Not diverse content",
            not is_valid and "разнообразный" in error.lower(),
            error
        )
        
        # Test 2.3: Not enough sentences
        no_sentences = "a" * 250
        is_valid, error = ClubCreationValidator.validate_description(no_sentences)
        self.log_result(
            "Not enough sentences",
            not is_valid,
            error
        )
        
        # Test 2.4: Valid description
        valid_desc = """Сообщество любителей шахмат в Алматы. Мы объединяем игроков всех уровней - 
        от начинающих до мастеров. Проводим еженедельные встречи, турниры, обучающие сессии. 
        Наша цель - популяризация шахмат и создание дружественного сообщества. 
        Присоединяйтесь к нам для развития навыков и приятного общения!"""
        
        is_valid, error = ClubCreationValidator.validate_description(valid_desc)
        self.log_result(
            "Valid description",
            is_valid,
            f"Length: {len(valid_desc)} chars"
        )
    
    # ========================================================================
    # TEST 3: Validation - Category
    # ========================================================================
    
    def test_category_validation(self):
        """Test category validation and fuzzy matching"""
        print("\n" + "-"*80)
        print("TEST 3: Category Validation")
        print("-"*80)
        
        # Test 3.1: Empty category
        is_valid, error = ClubCreationValidator.validate_category("")
        self.log_result(
            "Empty category",
            not is_valid,
            error
        )
        
        # Test 3.2: Invalid category
        is_valid, error = ClubCreationValidator.validate_category("Неизвестная категория")
        self.log_result(
            "Invalid category",
            not is_valid and "Неизвестная" in error,
            error
        )
        
        # Test 3.3: Fuzzy match - exact
        is_valid, error = ClubCreationValidator.validate_category("Спорт")
        self.log_result(
            "Fuzzy match - exact",
            is_valid,
            "Matched 'Спорт'"
        )
        
        # Test 3.4: Fuzzy match - partial
        is_valid, error = ClubCreationValidator.validate_category("спортивный")
        self.log_result(
            "Fuzzy match - partial",
            is_valid,
            "Matched 'спортивный' → 'Спорт'"
        )
    
    # ========================================================================
    # TEST 4: Successful Club Creation
    # ========================================================================
    
    def test_successful_creation(self):
        """Test successful club creation with valid data"""
        print("\n" + "-"*80)
        print("TEST 4: Successful Club Creation")
        print("-"*80)
        
        result = self.service.create_club(
            user=self.test_user,
            name="Шахматный клуб Алматы - Проверка",
            description="""Сообщество любителей шахмат в Алматы. Мы объединяем игроков всех уровней - 
            от начинающих до мастеров. Проводим еженедельные встречи, турниры, обучающие сессии. 
            Наша цель - популяризация шахмат и создание дружественного сообщества. 
            Присоединяйтесь к нам для развития навыков и приятного общения!""",
            category_name="Спорт",
            city_name="Алматы",
            is_private=False
        )
        
        self.log_result(
            "Create club with valid data",
            result['success'],
            f"Club ID: {result.get('club_id', 'N/A')}"
        )
        
        if result['success']:
            # Verify club exists in database
            club = Club.objects.filter(id=result['club_id']).first()
            self.log_result(
                "Club exists in database",
                club is not None,
                f"Name: {club.name if club else 'N/A'}"
            )
            
            # Verify creator is member and manager
            if club:
                is_member = club.members.filter(id=self.test_user.id).exists()
                is_manager = club.managers.filter(id=self.test_user.id).exists()
                
                self.log_result(
                    "Creator is member",
                    is_member,
                    "User added to members"
                )
                
                self.log_result(
                    "Creator is manager",
                    is_manager,
                    "User added to managers"
                )
    
    # ========================================================================
    # TEST 5: Short Description Rejection
    # ========================================================================
    
    def test_short_description_rejection(self):
        """Test that short descriptions are rejected"""
        print("\n" + "-"*80)
        print("TEST 5: Short Description Rejection")
        print("-"*80)
        
        result = self.service.create_club(
            user=self.test_user,
            name="Клуб с коротким описанием",
            description="Это короткое описание",
            category_name="Хобби"
        )
        
        self.log_result(
            "Reject short description",
            not result['success'],
            result.get('error', 'No error message')
        )
        
        # Check that validation errors are provided
        has_validation_errors = 'validation_errors' in result
        self.log_result(
            "Validation errors provided",
            has_validation_errors,
            f"Errors: {result.get('validation_errors', [])}"
        )
    
    # ========================================================================
    # TEST 6: Duplicate Name Handling
    # ========================================================================
    
    def test_duplicate_name_handling(self):
        """Test duplicate club name detection"""
        print("\n" + "-"*80)
        print("TEST 6: Duplicate Name Handling")
        print("-"*80)
        
        # Create first club
        club_name = "Уникальный клуб для проверки дубликатов"
        valid_description = """Это специальный клуб для проверки дубликатов названий. 
        Мы создаем его специально для валидации системы. 
        Клуб предназначен для проверки того, что система корректно обрабатывает 
        попытки создания клубов с одинаковыми названиями. Это важная функция безопасности."""
        
        result1 = self.service.create_club(
            user=self.test_user,
            name=club_name,
            description=valid_description,
            category_name="IT"
        )
        
        self.log_result(
            "Create first club",
            result1['success'],
            f"Club ID: {result1.get('club_id', 'N/A')}"
        )
        
        # Try to create duplicate
        result2 = self.service.create_club(
            user=self.test_user,
            name=club_name,
            description=valid_description,
            category_name="IT"
        )
        
        self.log_result(
            "Reject duplicate name",
            not result2['success'],
            result2.get('error', 'No error message')
        )
        
        # Check for duplicate flag
        has_duplicate_flag = result2.get('duplicate', False)
        self.log_result(
            "Duplicate flag set",
            has_duplicate_flag,
            "System detected duplicate"
        )
    
    # ========================================================================
    # TEST 7: Invalid Category Handling
    # ========================================================================
    
    def test_invalid_category_handling(self):
        """Test handling of invalid categories"""
        print("\n" + "-"*80)
        print("TEST 7: Invalid Category Handling")
        print("-"*80)
        
        result = self.service.create_club(
            user=self.test_user,
            name="Клуб с неверной категорией",
            description="""Это специальный клуб для проверки обработки неверных категорий. 
            Мы создаем его специально для валидации системы категорий. 
            Клуб предназначен для проверки того, что система корректно обрабатывает 
            попытки создания клубов с несуществующими категориями. Это важная проверка.""",
            category_name="Несуществующая категория XYZ"
        )
        
        self.log_result(
            "Reject invalid category",
            not result['success'],
            result.get('error', 'No error message')
        )
    
    # ========================================================================
    # TEST 8: Improvement Suggestions
    # ========================================================================
    
    def test_improvement_suggestions(self):
        """Test that improvement suggestions are generated"""
        print("\n" + "-"*80)
        print("TEST 8: Improvement Suggestions")
        print("-"*80)
        
        # Test with short name
        suggestions = ClubCreationValidator.suggest_improvements(
            name="Клуб",
            description="a" * 250
        )
        
        has_name_suggestion = any('название' in s.lower() for s in suggestions)
        self.log_result(
            "Suggest name improvement",
            has_name_suggestion,
            f"Suggestions: {len(suggestions)}"
        )
        
        # Test with short description
        suggestions = ClubCreationValidator.suggest_improvements(
            name="Длинное название клуба",
            description="a" * 250
        )
        
        has_desc_suggestion = any('описание' in s.lower() for s in suggestions)
        self.log_result(
            "Suggest description improvement",
            has_desc_suggestion,
            f"Suggestions: {len(suggestions)}"
        )
    
    # ========================================================================
    # TEST 9: Confirmation Messages
    # ========================================================================
    
    def test_confirmation_messages(self):
        """Test confirmation message generation"""
        print("\n" + "-"*80)
        print("TEST 9: Confirmation Messages")
        print("-"*80)
        
        # Test confirmation message
        conf_msg = ClubCreationConfirmation.generate_confirmation_message(
            name="Проверочный клуб",
            description="Описание тестового клуба" * 20,
            category="Спорт",
            city="Алматы",
            is_private=False
        )
        
        has_name = "Проверочный клуб" in conf_msg
        has_category = "Спорт" in conf_msg
        has_city = "Алматы" in conf_msg
        has_warning = "Важно" in conf_msg or "важно" in conf_msg
        
        self.log_result(
            "Confirmation includes name",
            has_name,
            "Name present in confirmation"
        )
        
        self.log_result(
            "Confirmation includes category",
            has_category,
            "Category present in confirmation"
        )
        
        self.log_result(
            "Confirmation includes city",
            has_city,
            "City present in confirmation"
        )
        
        self.log_result(
            "Confirmation includes warning",
            has_warning,
            "Warning about name change present"
        )
        
        # Test success message
        success_msg = ClubCreationConfirmation.generate_success_message(
            club_name="Проверочный клуб",
            club_id="123",
            link="/clubs/123/"
        )
        
        has_congrats = "Поздравляем" in success_msg or "поздравляем" in success_msg
        has_link = "/clubs/123/" in success_msg
        has_next_steps = "Следующие шаги" in success_msg or "следующие шаги" in success_msg
        
        self.log_result(
            "Success message has congratulations",
            has_congrats,
            "Congratulations present"
        )
        
        self.log_result(
            "Success message has link",
            has_link,
            "Club link present"
        )
        
        self.log_result(
            "Success message has next steps",
            has_next_steps,
            "Next steps guidance present"
        )
    
    # ========================================================================
    # TEST 10: User Permissions
    # ========================================================================
    
    def test_user_permissions(self):
        """Test user permission validation"""
        print("\n" + "-"*80)
        print("TEST 10: User Permissions")
        print("-"*80)
        
        # Test with authenticated user
        is_valid, error = ClubCreationValidator.validate_user_permissions(self.test_user)
        self.log_result(
            "Authenticated user valid",
            is_valid,
            "User has permissions"
        )
        
        # Test with None user
        is_valid, error = ClubCreationValidator.validate_user_permissions(None)
        self.log_result(
            "None user rejected",
            not is_valid and "авторизоваться" in error.lower(),
            error
        )
    
    # ========================================================================
    # Run All Tests
    # ========================================================================
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("🧪 ENHANCED CLUB CREATION TEST SUITE")
        print("="*80)
        
        self.setup()
        
        try:
            self.test_name_validation()
            self.test_description_validation()
            self.test_category_validation()
            self.test_successful_creation()
            self.test_short_description_rejection()
            self.test_duplicate_name_handling()
            self.test_invalid_category_handling()
            self.test_improvement_suggestions()
            self.test_confirmation_messages()
            self.test_user_permissions()
            
        finally:
            self.cleanup()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if not r['passed']:
                    print(f"  - {r['test']}")
                    if r['message']:
                        print(f"    {r['message']}")
        
        print("\n" + "="*80)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"⚠️  {failed} TEST(S) FAILED")
        
        print("="*80 + "\n")


if __name__ == "__main__":
    tester = TestEnhancedClubCreation()
    tester.run_all_tests()
