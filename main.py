import yaml
import logging
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

parser = argparse.ArgumentParser()
parser.add_argument('--log-level', default='INFO')
args = parser.parse_args()

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
with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

ID = config['id']
PASSWORD = config['password']

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=chrome_options)

# 로그인 화면
driver.get(url='https://spo.isdc.co.kr/login.do')

# ID, PASSWORD 입력
element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "mbId")))
element.send_keys(ID)
element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "mbPw")))
element.send_keys(PASSWORD)

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

select = Select(driver.find_element(By.ID, 'center'))
select.select_by_visible_text('탄천종합운동장')

select = Select(driver.find_element(By.ID, 'event'))
select.select_by_visible_text('50M기간수료제수영')

select = Select(driver.find_element(By.ID, 'class'))
select.select_by_visible_text('기간제_연수반')

select = Select(driver.find_element(By.ID, 'target'))
select.select_by_visible_text('성인')

# 강좌명 입력
pgm_nm = driver.find_element(By.ID, 'pgm_nm')
pgm_nm.send_keys('[07시] 기간수료_연수반_주5회')

# 조회 버튼 클릭
driver.find_element(By.ID, 'submit').click()

# table 뜰 때까지 기다림.
logger.debug('Waiting table')
element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "table_list_info")))

# 대기 신청 버튼 찾기
logger.debug('Waiting waitreg button')
element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "waitreg")))
waitreg_button = driver.find_element(By.NAME, 'waitreg')

# 대기신청 버튼 클릭
logger.debug('Click waitreg button')
waitreg_button.click()

# '등록하시겠습니까' alert 창으로 이동해서 확인 버튼 누름.
try:
    alert = driver.switch_to.alert
    alert.accept()
except Exception as e:
    raise e

# '등록되었습니다' alert 창으로 이동해서 확인 버튼 누름.
try:
    alert = driver.switch_to.alert
    alert.accept()
    logger.info('Success !!!')
except Exception as e:
    raise e

# WebDriver 종료
driver.quit()