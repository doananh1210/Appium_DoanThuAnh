import pytest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.by import By
import pytesseract
from PIL import Image
import os

@pytest.fixture
def driver():
    capabilities = UiAutomator2Options().load_capabilities({
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:appPackage": "com.microblink.photomath",
        "appium:appActivity": "com.microblink.photomath.ui.main.MainActivity",
        "appium:app": "F:/Downloads/Android/Android_AVD/photomath.apk",
        "appium:deviceName": "emulator-5554",
        "appium:noReset": True,
        "appium:ensureWebviewsHavePages": True,
        "appium:udid": "emulator-5554"
    })
    driver = webdriver.Remote("http://localhost:4723", options=capabilities)
    yield driver
    driver.quit()

def test_navigation_to_history(driver):
    try:
        history_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.ImageButton[@resource-id="com.microblink.photomath:id/my_stuff_icon"]'))
        )
        history_button.click()
        print("✅ Mở màn hình lịch sử thành công")
    except Exception as e:
        print(f"❌ Không tìm thấy nút History: {e}")
        driver.save_screenshot("history_button_not_found.png")
        raise e

    try:
        history_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.View[@resource-id="tab_history"]/android.view.View'))
        )
        assert history_title.is_displayed(), "Màn hình lịch sử không hiển thị"
        print("✅ Màn hình lịch sử hiển thị thành công")
    except Exception as e:
        print(f"❌ Không tìm thấy hoặc màn hình lịch sử không hiển thị: {e}")
        driver.save_screenshot("history_title_not_found.png")
        raise e

    # Back về màn hình chính
    driver.back()
    print("⏪ Quay lại màn hình chính sau khi xem lịch sử")
def test_manual_math_input_enter_expression(driver):
    try:
        keyboard_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.microblink.photomath:id/editor_icon"))
        )
        keyboard_button.click()
        print("✅ Nhấn nút nhập tay thành công")
    except Exception as e:
        print(f"❌ Không tìm thấy nút nhập tay: {e}")
        driver.save_screenshot("editor_icon_not_found.png")
        pytest.fail("Không tìm thấy nút nhập tay")

    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH,
                "//android.widget.FrameLayout[@resource-id='com.microblink.photomath:id/keyboard']"))
        )
        print("✅ Ô nhập liệu đã xuất hiện")
    except Exception as e:
        print(f"❌ Không tìm thấy ô nhập liệu: {e}")
        driver.save_screenshot("input_field_not_found.png")
        pytest.fail("Không tìm thấy ô nhập liệu")

    try:
        for desc in ['DIGIT_TWO', 'PLUS_SIGN', 'DIGIT_THREE']:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, f"//android.widget.ImageView[@content-desc='{desc}']"))
            )
            button.click()
            print(f"✅ Nhập '{desc}' thành công")
            time.sleep(0.5)
    except Exception as e:
        print(f"❌ Lỗi khi nhập biểu thức: {e}")
        driver.save_screenshot("input_error.png")
        pytest.fail("Lỗi khi nhập biểu thức")

    try:
        submit_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.microblink.photomath:id/solution_button"))
        )
        submit_button.click()
        print("✅ Nhấn nút submit thành công")
    except Exception as e:
        print(f"❌ Không tìm thấy nút submit: {e}")
        driver.save_screenshot("submit_button_not_found.png")
        pytest.fail("Không tìm thấy nút submit")
def test_manual_math_input_show_result(driver):
    try:
        show_steps_button = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="com.microblink.photomath:id/button_text" and @text="Show Solving Steps"]'))
        )
        show_steps_button.click()
        print("✅ Nhấn nút Show Solving Steps thành công")
    except Exception as e:
        print(f"❌ Không tìm thấy nút Show Solving Steps: {e}")
        driver.save_screenshot("show_steps_button_not_found.png")
        pytest.fail("Không tìm thấy nút Show Solving Steps")

    result_text = ""
    try:
        result_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH,
                '//android.view.View[@resource-id="com.microblink.photomath:id/left_equation"]'))
        )

        result_text = result_element.text.strip()

        if not result_text:
            children = result_element.find_elements(By.XPATH, "./*")
            parts = []
            for child in children:
                t = child.text.strip()
                if not t:
                    t = child.get_attribute("contentDescription") or ""
                if t:
                    parts.append(t)
            result_text = " ".join(parts).strip()

        if not result_text:
            result_text = result_element.get_attribute("contentDescription") or ""

        result_text = result_text.strip()

    except Exception as e:
        print(f"⚠️ Không lấy được kết quả từ DOM, thử OCR: {e}")

    # Nếu kết quả vẫn rỗng => fallback sang OCR lấy vùng ngay dưới chữ "Solution"
    if not result_text:
        print("📸 Dùng OCR lấy kết quả ở vùng ngay dưới chữ 'Solution'")
        try:
            # Tạo thư mục lưu ảnh nếu chưa có
            save_dir = "bai_lam"
            os.makedirs(save_dir, exist_ok=True)

            title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.microblink.photomath:id/title"]'))
            )
            location = title_element.location
            size = title_element.size

            x = location['x']
            y = location['y']
            width = size['width']
            height = size['height']

            print(f"Solution title tại x={x}, y={y}, width={width}, height={height}")

            left = x
            top = y + height
            right = x + width
            bottom = top + 100  # có thể chỉnh nếu cần

            screenshot_path = os.path.join(save_dir, "ocr_fullscreen.png")
            driver.save_screenshot(screenshot_path)

            image = Image.open(screenshot_path)
            cropped = image.crop((left, top, right, bottom))
            cropped_path = os.path.join(save_dir, "ocr_cropped_result.png")
            cropped.save(cropped_path)

            print(f"Ảnh crop vùng OCR đã lưu tại: {cropped_path}")

            result_text = pytesseract.image_to_string(cropped, lang='eng').strip()
            print(f"🧠 Kết quả OCR lấy từ dưới 'Solution': '{result_text}'")

        except Exception as e:
            print(f"❌ Lỗi khi dùng OCR lấy kết quả từ dưới 'Solution': {e}")
            driver.save_screenshot(os.path.join("bai_lam", "ocr_failed.png"))
            pytest.fail("Không lấy được kết quả từ OCR vùng dưới 'Solution'")

    print(f"✅ Kết quả cuối cùng: '{result_text}'")

    expected_result = "5"
    assert expected_result in result_text, f"Kết quả mong đợi là '{expected_result}', nhưng nhận được '{result_text}'"