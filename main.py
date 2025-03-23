import time
import yaml
import logging
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

parser = argparse.ArgumentParser()
parser.add_argument('--log-level', default='INFO')
parser.add_argument('--headless', default=False)
args = parser.parse_args()


def get_element(element, key, value, timeout=10):
    WebDriverWait(element, timeout).until(EC.presence_of_element_located((key, value)))
    return element.find_element(key, value)

def get_elements(element, key, value, timeout=10):
    WebDriverWait(element, timeout).until(EC.presence_of_element_located((key, value)))
    return element.find_elements(key, value)

def click_button(element, key, value, timeout=10):
    # element 클릭이 이루어지려면 "시각적으로 보여야함"
    btn = WebDriverWait(element, timeout).until(EC.element_to_be_clickable((key, value)))
    btn.click()

def check_box(element, key, value, timeout=10):
    checkbox = get_element(element, key, value, timeout)
    driver.execute_script("arguments[0].click();", checkbox)

LOG_LEVEL = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
}

# 로거 세팅
logger = logging.getLogger("basic")
logger.setLevel(LOG_LEVEL[args.log_level])

formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)

# config 파일 읽기
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# course config 파일 읽기
with open('course.yaml', 'r', encoding='utf-8') as f:
    course = yaml.load(f, Loader=yaml.FullLoader)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
if args.headless:
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
else:
    driver = webdriver.Chrome()

# 로그인 화면
driver.get(url='https://spo.isdc.co.kr/login.do')

# ID, PASSWORD 입력
get_element(driver, By.ID, 'mbId').send_keys(config['id'])
get_element(driver, By.ID, 'mbPw').send_keys(config['password'])

# 로그인 버튼 스크립트 동작
driver.execute_script('login()')

# alert 창이 뜰 때까지 기다림.
element = WebDriverWait(driver, 10).until(EC.alert_is_present())

# alert 창으로 이동해서 확인 버튼 누름.
alert = driver.switch_to.alert
alert.accept()

logger.debug('Login succeed')

# 수강신청 화면 이동
driver.get(url='https://spo.isdc.co.kr/courseRegist.do')

# 강좌 선택
my_course = course['tancheon_swim']

select = Select(get_element(driver, By.ID, 'center'))
select.select_by_visible_text(my_course['center'])

select = Select(get_element(driver, By.ID, 'event'))
select.select_by_visible_text(my_course['event'])

select = Select(get_element(driver, By.ID, 'class'))
select.select_by_visible_text(my_course['class'])

select = Select(get_element(driver, By.ID, 'target'))
select.select_by_visible_text(my_course['target'])

get_element(driver, By.ID, 'pgm_nm').send_keys(my_course['class_name'])

# 조회 버튼 클릭
click_button(driver, By.ID, 'submit', 10)

# table 뜰 때까지 기다림.
logger.debug('Waiting table')
get_element(driver, By.ID, 'table_list_info', 10)

# 신청 버튼 클릭
click_button(driver, By.NAME, 'acs', 10)

# '신청목록 장바구니로 가시겠습니까' alert 창으로 이동해서 확인 버튼 누름.
try:
    alert = driver.switch_to.alert
    alert.accept()
except Exception as e:
    raise e

# 장바구니 화면
driver.get(url='https://spo.isdc.co.kr/courseCart.do')
click_button(driver, By.NAME, 'cart_check')

select = Select(get_element(driver, By.CLASS_NAME, 'qty'))
select.select_by_visible_text('1 개월')

select = Select(get_element(driver, By.CLASS_NAME, 'dc_sel'))
select.select_by_visible_text('할인없음')   # 여성할인

# 강좌신청하기 버튼 클릭
click_button(driver, By.ID, 'order')

# '주문하기로 이동하시겠습니까' alert 창으로 이동해서 확인 버튼 누름.
try:
    alert = driver.switch_to.alert
    alert.accept()
except Exception as e:
    raise e

# 결제하기 버튼 클릭
click_button(driver, By.CLASS_NAME, 'blue')

# 현재 창의 핸들을 저장
main_window = driver.current_window_handle

# 새창으로 이동
for handle in driver.window_handles:
    if handle != main_window:
        driver.switch_to.window(handle)
        break

# 지불 방법을 가상계좌로 변경
element = get_element(driver, By.NAME, 'pay_method')
select = Select(element)
select.select_by_visible_text('가상계좌')

# 결제요청 버튼 클릭
click_button(driver, By.CLASS_NAME, 'submit')

# iframe을 감싸고 있는 div가 뜰 때까지 대기
element = get_element(driver, By.CLASS_NAME, "blockUI")

# iframe 요소로 전환
iframe = get_element(driver, By.ID, "naxIfr")
driver.switch_to.frame(iframe)

# 전체동의 클릭
check_box(driver, By.ID, 'chk_all')

# 입금은행 선택
select = Select(get_element(driver, By.ID, 'select_bank'))
select.select_by_visible_text('KB국민은행')

# 다음 버튼이 안보여서 크기 조절
width = driver.get_window_size().get('width')
driver.set_window_size(width, 800)

# 다음 버튼 클릭
click_button(driver, By.ID, 'spayNext')

# 현금영수증 발행 체크 해제
check_box(driver, By.ID, 'chk_num2')

# 결제요청 버튼 클릭
click_button(driver, By.ID, 'spayNext')

# 데이터가 전송되기까지 기다려줘야함.
time.sleep(5)

# WebDriver 종료
driver.quit()