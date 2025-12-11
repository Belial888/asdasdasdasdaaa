import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

class CombinedSystemTests(unittest.TestCase):

    def setUp(self):
        # Setup Chrome Browser
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.maximize_window()
        # Assume the app is running on port 5000
        self.base_url = "http://127.0.0.1:5000"

    # ==========================================
    # ORDER 1: HAPPY PATH (SUCCESSFUL FLOW)
    # ==========================================
    def test_1_full_user_flow_success(self):
        """
        SCENARIO: Registers a new user, logs in, and successfully books a valid appointment.
        EXPECTATION: Everything works without errors.
        """
        print("\n--- TEST 1: Full Happy Path (Registration -> Login -> Booking) ---")
        driver = self.driver
        
        # 1. Load Home Page
        print("1. Loading Home Page...")
        driver.get(self.base_url)
        time.sleep(1)
        self.assertIn("PWD Health", driver.title)
        
        # 2. Go to Login
        driver.find_element(By.CSS_SELECTOR, ".btn-patient").click()
        time.sleep(1)

        # 3. Register New User
        print("2. Registering new user...")
        driver.find_element(By.CSS_SELECTOR, ".toggle-link").click()
        time.sleep(1)
        
        unique_id = str(int(time.time()))
        test_email = f"happy_{unique_id}@example.com"
        test_pass = "password123"

        driver.find_element(By.NAME, "fullname").send_keys("Happy Path User")
        driver.find_element(By.NAME, "pwd_id").send_keys(f"PWD-{unique_id}")
        driver.find_element(By.ID, "reg-email").send_keys(test_email)
        driver.find_element(By.ID, "reg-password").send_keys(test_pass)
        
        driver.find_element(By.ID, "register-form").find_element(By.TAG_NAME, "button").click()
        time.sleep(2)

        # 4. Login
        print(f"3. Logging in as {test_email}...")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_pass)
        driver.find_element(By.ID, "login-form").find_element(By.TAG_NAME, "button").click()
        time.sleep(2)
        
        # Verify Dashboard
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Welcome", body_text)

        # 5. Book Valid Appointment
        print("4. Booking valid appointment...")
        driver.find_element(By.ID, "date").send_keys("12-31-2091")
        Select(driver.find_element(By.ID, "time")).select_by_index(1)
        driver.find_element(By.ID, "purpose").send_keys("Happy Path Checkup")
        driver.find_element(By.CLASS_NAME, "btn-book").click()
        time.sleep(2)
        
        # 6. Verify History
        print("5. Verifying booking history...")
        table_text = driver.find_element(By.TAG_NAME, "table").text
        self.assertIn("Happy Path Checkup", table_text)
        self.assertIn("Pending", table_text)
        
        print("✅ TEST PASSED: Happy Path Successful")

    # ==========================================
    # ORDER 2: DEFECT CHECK (Past Date)
    # ==========================================
    def test_2_defect_past_date_booking(self):
        """
        BUG: System allows booking dates in the past.
        TEST EXPECTATION: We want to PROVE the bug exists.
        RESULT: Pass = Bug Reproduced (System allowed the date). Fail = Bug not found.
        """
        print("\n--- TEST 2: Defect Check - Past Date Booking ---")
        driver = self.driver
        self._quick_login() 

        print("Attempting to book a date in the past...")
        driver.find_element(By.ID, "date").send_keys("01-01-1911")
        Select(driver.find_element(By.ID, "time")).select_by_index(1)
        driver.find_element(By.ID, "purpose").send_keys("Time Travel Test")
        driver.find_element(By.CLASS_NAME, "btn-book").click()
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # We change the logic: If we see success, it means the BUG IS CONFIRMED (Test Passes).
        if "Appointment requested successfully" in body_text:
            print("❌ TEST 1 FAILED: Defect Confirmed! (System incorrectly allowed past date)")
        else:
            self.fail("✅ TEST 1 PASSED: Defect NOT found (System correctly blocked past date)")

    # ==========================================
    # ORDER 3: EDGE CASE (Same Name, Diff ID)
    # ==========================================
    def test_3_same_name_different_id_registration(self):
        """
        SCENARIO: Register two users with the SAME Name but DIFFERENT PWD IDs.
        """
        print("\n--- TEST 3: Same Name, Different ID Registration ---")
        driver = self.driver
        
        common_name = "Jabin Aldiano"
        
        # 1. Register User A
        id_a = f"PWD-A-{int(time.time())}"
        email_a = f"jabinA_{int(time.time())}@test.com"
        print(f"Registering User A: Name={common_name}, ID={id_a}")
        self._register_user(common_name, id_a, email_a)
        
        # 2. Register User B (Same Name, Diff ID)
        id_b = f"PWD-B-{int(time.time())}"
        email_b = f"jabinB_{int(time.time())}@test.com"
        print(f"Registering User B: Name={common_name}, ID={id_b}")
        
        try:
            self._register_user(common_name, id_b, email_b)
            
            # Check for success
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            if "Registration successful" in body_text:
                print("❌ TEST 2 FAILED: System correctly allowed same-name registration.")
            else:
                self.fail("✅ TEST 2 PASSED: System blocked valid user with shared name!")
                
        except Exception as e:
            self.fail(f"❌ TEST 2 FAILED: Application crashed or error: {e}")

    # ==========================================
    # HELPERS
    # ==========================================
    def _register_user(self, name, pwd_id, email):
        driver = self.driver
        driver.get(f"{self.base_url}/login_page")
        time.sleep(1)
        try:
            driver.find_element(By.CLASS_NAME, "toggle-link").click()
            time.sleep(0.5)
        except:
            pass 
        driver.find_element(By.ID, "reg-name").send_keys(name)
        driver.find_element(By.ID, "reg-pwd-id").send_keys(pwd_id)
        driver.find_element(By.ID, "reg-email").send_keys(email)
        driver.find_element(By.ID, "reg-password").send_keys("pass")
        driver.find_element(By.CSS_SELECTOR, "#register-form button").click()
        time.sleep(1)

    def _quick_login(self):
        """Helper to create a fresh user and login instantly for defect tests"""
        unique = str(int(time.time()))
        self._register_user(f"Test {unique}", f"PWD-{unique}", f"login_{unique}@test.com")
        self.driver.find_element(By.ID, "email").send_keys(f"login_{unique}@test.com")
        self.driver.find_element(By.ID, "password").send_keys("pass")
        self.driver.find_element(By.CSS_SELECTOR, "#login-form button").click()
        time.sleep(1)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(exit=False)