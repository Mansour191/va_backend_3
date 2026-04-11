#!/usr/bin/env python3
"""
Simple Test Script for Reviews System
Tests only the reviews functionality without importing the full schema
"""

import os
import sys
import django

# Add backend directory to Python path
sys.path.append('/home/mansour/Desktop/vynilart_2.0.1/backend')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vynilart_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def test_review_models():
    """Test Review models only"""
    print("🔍 Testing Review Models...")
    
    try:
        from api.models.review import Review, ReviewReport
        print("✅ Review models imported successfully")
        
        # Check model fields
        review_fields = [f.name for f in Review._meta.fields]
        required_fields = ['id', 'user', 'product', 'rating', 'comment', 'is_verified', 'helpful_count', 'created_at', 'updated_at']
        
        for field in required_fields:
            if field in review_fields:
                print(f"✅ Review.{field} field exists")
            else:
                print(f"❌ Review.{field} field missing")
        
        # Check database table name
        if Review._meta.db_table == 'api_review':
            print("✅ Review table name correct: api_review")
        else:
            print(f"❌ Review table name incorrect: {Review._meta.db_table}")
        
        # Check foreign key constraints
        user_field = Review._meta.get_field('user')
        product_field = Review._meta.get_field('product')
        
        if user_field.remote_field.on_delete.__name__ == 'CASCADE':
            print("✅ User foreign key has CASCADE delete")
        else:
            print("❌ User foreign key missing CASCADE delete")
            
        if product_field.remote_field.on_delete.__name__ == 'CASCADE':
            print("✅ Product foreign key has CASCADE delete")
        else:
            print("❌ Product foreign key missing CASCADE delete")
            
        return True
            
    except ImportError as e:
        print(f"❌ Failed to import Review models: {e}")
        return False

def test_review_schema():
    """Test Review schema only"""
    print("\n🔍 Testing Review Schema...")
    
    try:
        from api.schema.review_schema import ReviewType, ReviewReportType, ReviewQuery, ReviewMutation
        print("✅ Review schema imported successfully")
        
        # Check if ReviewType is properly defined
        if hasattr(ReviewType, '_meta'):
            print("✅ ReviewType is a DjangoObjectType")
        else:
            print("❌ ReviewType is not properly defined")
        
        # Check if mutations are available
        review_mutations = [
            'submit_review', 'update_review', 'delete_review', 
            'helpful_review', 'report_review', 'verify_review'
        ]
        
        for mutation in review_mutations:
            if hasattr(ReviewMutation, mutation):
                print(f"✅ {mutation} mutation exists")
            else:
                print(f"❌ {mutation} mutation missing")
        
        # Check if queries are available
        review_queries = [
            'review', 'all_reviews', 'product_reviews', 'user_reviews'
        ]
        
        for query in review_queries:
            if hasattr(ReviewQuery, query):
                print(f"✅ {query} query exists")
            else:
                print(f"❌ {query} query missing")
                
        return True
            
    except ImportError as e:
        print(f"❌ Failed to import review schema: {e}")
        return False

def test_database_table():
    """Test database table exists"""
    print("\n🔍 Testing Database Table...")
    
    try:
        from django.db import connection
        from api.models.review import Review
        
        # Check if table exists
        table_name = Review._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """, [table_name])
            
            if cursor.fetchone()[0] > 0:
                print(f"✅ Table {table_name} exists in database")
                return True
            else:
                print(f"❌ Table {table_name} does not exist in database")
                return False
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run reviews tests"""
    print("🚀 Testing Reviews System")
    print("=" * 40)
    
    tests = [
        test_review_models,
        test_review_schema,
        test_database_table
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Reviews system is ready!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
