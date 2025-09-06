import requests
import sys
import json
from datetime import datetime, timedelta

class SynergySphereAPITester:
    def __init__(self, base_url="https://project-sphere.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.project_id = None
        self.task_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_user_name = "Test User"
        self.test_password = "TestPass123!"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "name": self.test_user_name,
                "email": self.test_user_email,
                "password": self.test_password
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_password
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_get_current_user(self):
        """Test get current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success and response.get('email') == self.test_user_email

    def test_create_project(self):
        """Test project creation with deadline"""
        deadline = (datetime.now() + timedelta(days=30)).isoformat()
        success, response = self.run_test(
            "Create Project with Deadline",
            "POST",
            "projects",
            200,
            data={
                "name": "Test Project",
                "description": "A test project for API testing",
                "deadline": deadline
            }
        )
        if success and 'id' in response:
            self.project_id = response['id']
            print(f"   Project ID: {self.project_id}")
            # Verify enhanced response includes task_count and created_by_name
            if 'task_count' in response and 'created_by_name' in response:
                print(f"   ✅ Enhanced response includes task_count: {response['task_count']}")
                print(f"   ✅ Enhanced response includes created_by_name: {response['created_by_name']}")
                return True
            else:
                print(f"   ❌ Missing enhanced fields in response")
                return False
        return False

    def test_get_projects(self):
        """Test get user projects with enhanced response"""
        success, response = self.run_test(
            "Get Projects with Enhanced Response",
            "GET",
            "projects",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            project = response[0]
            # Verify enhanced fields are present
            required_fields = ['task_count', 'created_by_name', 'member_details']
            missing_fields = [field for field in required_fields if field not in project]
            if missing_fields:
                print(f"   ❌ Missing enhanced fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All enhanced fields present: task_count={project['task_count']}, created_by_name={project['created_by_name']}")
                return True
        return success and isinstance(response, list)

    def test_get_project_detail(self):
        """Test get specific project"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Project Detail",
            "GET",
            f"projects/{self.project_id}",
            200
        )
        return success and response.get('id') == self.project_id

    def test_add_project_member(self):
        """Test adding member to project"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        # Create another test user first
        test_member_email = f"member_{datetime.now().strftime('%H%M%S')}@example.com"
        
        # Register the member
        member_success, member_response = self.run_test(
            "Register Member User",
            "POST",
            "auth/register",
            200,
            data={
                "name": "Test Member",
                "email": test_member_email,
                "password": self.test_password
            }
        )
        
        if not member_success:
            print("❌ Failed to create member user")
            return False
            
        # Add member to project
        success, response = self.run_test(
            "Add Project Member",
            "POST",
            f"projects/{self.project_id}/members",
            200,
            data={"email": test_member_email}
        )
        return success

    def test_create_task(self):
        """Test task creation"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        success, response = self.run_test(
            "Create Task",
            "POST",
            f"projects/{self.project_id}/tasks",
            200,
            data={
                "title": "Test Task",
                "description": "A test task for API testing",
                "assignee_id": self.user_id,
                "due_date": due_date,
                "status": "To-Do"
            }
        )
        if success and 'id' in response:
            self.task_id = response['id']
            print(f"   Task ID: {self.task_id}")
            return True
        return False

    def test_get_tasks(self):
        """Test get project tasks"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Project Tasks",
            "GET",
            f"projects/{self.project_id}/tasks",
            200
        )
        return success and isinstance(response, list)

    def test_update_task(self):
        """Test task update"""
        if not self.task_id:
            print("❌ No task ID available for testing")
            return False
            
        success, response = self.run_test(
            "Update Task Status",
            "PUT",
            f"tasks/{self.task_id}",
            200,
            data={"status": "In Progress"}
        )
        return success and response.get('status') == "In Progress"

    def test_get_user_tasks(self):
        """Test get user's assigned tasks"""
        success, response = self.run_test(
            "Get User Tasks",
            "GET",
            "users/me/tasks",
            200
        )
        return success and isinstance(response, list)

    def test_create_comment(self):
        """Test comment creation"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        success, response = self.run_test(
            "Create Comment",
            "POST",
            f"projects/{self.project_id}/comments",
            200,
            data={"message": "This is a test comment"}
        )
        return success and 'id' in response

    def test_get_comments(self):
        """Test get project comments"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Project Comments",
            "GET",
            f"projects/{self.project_id}/comments",
            200
        )
        return success and isinstance(response, list)

    def test_update_project(self):
        """Test project update (PUT /api/projects/{project_id})"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        new_deadline = (datetime.now() + timedelta(days=45)).isoformat()
        success, response = self.run_test(
            "Update Project",
            "PUT",
            f"projects/{self.project_id}",
            200,
            data={
                "name": "Updated Test Project",
                "description": "Updated description for testing",
                "deadline": new_deadline
            }
        )
        if success:
            # Verify the update worked
            if (response.get('name') == "Updated Test Project" and 
                response.get('description') == "Updated description for testing"):
                print(f"   ✅ Project updated successfully")
                return True
            else:
                print(f"   ❌ Project update verification failed")
                return False
        return False

    def test_delete_project_cascade(self):
        """Test project deletion with cascade delete"""
        if not self.project_id:
            print("❌ No project ID available for testing")
            return False
            
        # First create a task and comment to test cascade delete
        task_success, task_response = self.run_test(
            "Create Task for Cascade Test",
            "POST",
            f"projects/{self.project_id}/tasks",
            200,
            data={
                "title": "Task to be deleted",
                "description": "This task should be deleted with project",
                "status": "To-Do"
            }
        )
        
        comment_success, comment_response = self.run_test(
            "Create Comment for Cascade Test",
            "POST",
            f"projects/{self.project_id}/comments",
            200,
            data={"message": "This comment should be deleted with project"}
        )
        
        if not (task_success and comment_success):
            print("❌ Failed to create task/comment for cascade test")
            return False
            
        # Now delete the project
        success, response = self.run_test(
            "Delete Project (Cascade)",
            "DELETE",
            f"projects/{self.project_id}",
            200
        )
        
        if success:
            # Verify project is deleted
            verify_success, verify_response = self.run_test(
                "Verify Project Deleted",
                "GET",
                f"projects/{self.project_id}",
                404
            )
            return verify_success
        return False

    def test_unauthorized_access(self):
        """Test unauthorized access"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Unauthorized Access Test",
            "GET",
            "projects",
            401
        )
        
        # Restore token
        self.token = original_token
        return success

def main():
    print("🚀 Starting SynergySphere API Tests")
    print("=" * 50)
    
    tester = SynergySphereAPITester()
    
    # Test sequence
    test_results = []
    
    # Authentication Tests
    print("\n📋 AUTHENTICATION TESTS")
    test_results.append(("User Registration", tester.test_user_registration()))
    test_results.append(("User Login", tester.test_user_login()))
    test_results.append(("Get Current User", tester.test_get_current_user()))
    test_results.append(("Unauthorized Access", tester.test_unauthorized_access()))
    
    # Project Tests
    print("\n📋 PROJECT TESTS")
    test_results.append(("Create Project", tester.test_create_project()))
    test_results.append(("Get Projects", tester.test_get_projects()))
    test_results.append(("Get Project Detail", tester.test_get_project_detail()))
    test_results.append(("Add Project Member", tester.test_add_project_member()))
    test_results.append(("Update Project", tester.test_update_project()))
    
    # Task Tests
    print("\n📋 TASK TESTS")
    test_results.append(("Create Task", tester.test_create_task()))
    test_results.append(("Get Project Tasks", tester.test_get_tasks()))
    test_results.append(("Update Task", tester.test_update_task()))
    test_results.append(("Get User Tasks", tester.test_get_user_tasks()))
    
    # Comment Tests
    print("\n📋 COMMENT TESTS")
    test_results.append(("Create Comment", tester.test_create_comment()))
    test_results.append(("Get Comments", tester.test_get_comments()))
    
    # Cascade Delete Test (should be last)
    print("\n📋 CASCADE DELETE TEST")
    test_results.append(("Delete Project Cascade", tester.test_delete_project_cascade()))
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    failed_tests = []
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            failed_tests.append(test_name)
    
    print(f"\n📈 Summary: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())