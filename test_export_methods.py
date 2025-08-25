#!/usr/bin/env python3
"""
Direct test of export methods without HTTP
"""

from study_data_manager import StudyDataManager

def test_export_methods():
    """Test all export methods directly"""
    print("Testing Export Methods Directly")
    print("=" * 50)
    
    # Initialize the study data manager
    study_manager = StudyDataManager()
    
    # Test each export method
    export_methods = [
        ('pre_questionnaires', study_manager.export_pre_questionnaires_only),
        ('post_questionnaires', study_manager.export_post_questionnaires_only),
        ('post_questionnaire2', study_manager.export_post_questionnaire2_only),
        ('exit_questionnaires', study_manager.export_exit_questionnaires_only),
        ('sessions', study_manager.export_sessions_only),
        ('interactions', study_manager.export_interactions_only),
        ('all', study_manager.export_to_csv)
    ]
    
    for export_type, method in export_methods:
        try:
            print(f"\n=== Testing {export_type} export ===")
            result = method()
            
            if result:
                print(f"✅ {export_type} export successful!")
                print(f"Files created: {list(result.keys())}")
                for file_type, file_path in result.items():
                    print(f"  - {file_type}: {file_path}")
            else:
                print(f"⚠️  {export_type} export returned empty result (likely no data)")
                
        except Exception as e:
            print(f"❌ {export_type} export failed: {e}")
    
    print("\n" + "=" * 50)
    print("Direct export testing completed!")

if __name__ == "__main__":
    test_export_methods()