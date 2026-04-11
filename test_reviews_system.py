#!/usr/bin/env python3
"""
Test Script for Reviews System Integration
This script tests the complete reviews system including:
- Django models
- GraphQL schema
- Mutations and queries
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.append('/home/mansour/Desktop/vynilart_2.0.1/backend')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vynilart_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def test_models():
    """Test Review models"""
    print("\n🔍 Testing Review Models...")
    
    try:
        from api.models import Review, ReviewReport
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
            
    except ImportError as e:
        print(f"❌ Failed to import Review models: {e}")
        return False
    
    return True

def test_schema():
    """Test GraphQL schema"""
    print("\n🔍 Testing GraphQL Schema...")
    
    try:
        from api.schema import Query, Mutation
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
                
    except ImportError as e:
        print(f"❌ Failed to import review schema: {e}")
        return False
    
    return True

def test_schema_integration():
    """Test schema integration with main schema"""
    print("\n🔍 Testing Schema Integration...")
    
    try:
        from api.schema import Query, Mutation
        
        # Check if review types are in main schema exports
        from api.schema import ReviewType, ReviewReportType
        print("✅ Review types exported from main schema")
        
        # Check if review queries are inherited
        if hasattr(Query, 'product_reviews'):
            print("✅ product_reviews query available in main Query")
        else:
            print("❌ product_reviews query missing from main Query")
        
        if hasattr(Query, 'user_reviews'):
            print("✅ user_reviews query available in main Query")
        else:
            print("❌ user_reviews query missing from main Query")
        
        # Check if review mutations are inherited
        if hasattr(Mutation, 'submit_review'):
            print("✅ submit_review mutation available in main Mutation")
        else:
            print("❌ submit_review mutation missing from main Mutation")
        
        if hasattr(Mutation, 'helpful_review'):
            print("✅ helpful_review mutation available in main Mutation")
        else:
            print("❌ helpful_review mutation missing from main Mutation")
            
    except ImportError as e:
        print(f"❌ Failed to test schema integration: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and table existence"""
    print("\n🔍 Testing Database Connection...")
    
    try:
        from django.db import connection
        from api.models import Review
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
        
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
            else:
                print(f"❌ Table {table_name} does not exist in database")
                return False
        
        # Check table structure
        with connection.cursor() as cursor:
            cursor.execute(f"""
                DESCRIBE {table_name}
            """)
            
            columns = [row[0] for row in cursor.fetchall()]
            required_columns = ['id', 'user_id', 'product_id', 'rating', 'comment', 'is_verified', 'helpful_count', 'created_at', 'updated_at']
            
            for column in required_columns:
                if column in columns:
                    print(f"✅ Column {column} exists")
                else:
                    print(f"❌ Column {column} missing")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def test_graphql_introspection():
    """Test GraphQL introspection"""
    print("\n🔍 Testing GraphQL Introspection...")
    
    try:
        from graphene import Schema
        from api.schema import Query, Mutation
        
        # Create schema
        schema = Schema(query=Query, mutation=Mutation)
        
        # Test introspection query
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
        """
        
        result = schema.execute(introspection_query)
        
        if result.errors:
            print(f"❌ GraphQL introspection errors: {result.errors}")
            return False
        
        # Check if ReviewType exists in schema
        types = result.data['__schema']['types']
        type_names = [t['name'] for t in types]
        
        if 'ReviewType' in type_names:
            print("✅ ReviewType found in GraphQL schema")
        else:
            print("❌ ReviewType not found in GraphQL schema")
        
        if 'ReviewReportType' in type_names:
            print("✅ ReviewReportType found in GraphQL schema")
        else:
            print("❌ ReviewReportType not found in GraphQL schema")
            
    except Exception as e:
        print(f"❌ GraphQL introspection test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Reviews System Integration Tests")
    print("=" * 50)
    
    tests = [
        test_models,
        test_schema,
        test_schema_integration,
        test_database_connection,
        test_graphql_introspection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Reviews system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
