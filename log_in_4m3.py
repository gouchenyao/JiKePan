# -*- coding: UTF-8 -*
import sys
import time
import threading
import pickle

from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class LogIn4m3(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        return None

    def get_course_timetable(self, *, test=False, PhantomJS_path='./phantomjs.exe'): #VS根目录为项目文件目录
        if(test):
            time_start = time.clock()

        service_args = ['--load-images=no']
        driver = webdriver.PhantomJS(executable_path=PhantomJS_path, service_args=service_args)
        driver.maximize_window()

        driver.get("http://4m3.tongji.edu.cn/eams/login.action")

        #try:
        #    WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "统一身份认证登录")))
        #    driver.find_element_by_link_text("统一身份认证登录").click()
        #except:
        #    if(test):
        #        print("Cannot log in 4m3!\n")
        #    return 404

        try:
            WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.visibility_of_any_elements_located((By.ID, "username")))
            driver.find_element_by_id("username").send_keys(self.username)
        except:
            if(test):
                print("Cannot input username!\n")
            return 404

        try:
            WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.visibility_of_any_elements_located((By.ID, "password")))
            driver.find_element_by_id("password").send_keys(self.password)
        except:
            if(test):
                print("Cannot input password!\n")
            return 404

        try:
            WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.element_to_be_clickable((By.NAME, "submit")))
            driver.find_element_by_name("submit").click()
        except:
            if(test):
                print("Cannot click submit button!\n")
            return 404

        try:
            WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "我的课程")))
            driver.find_element_by_link_text("我的课程").click()
        except:
            if(test):
                print("Cannot click my classes button!\n")
            return 401

        try:
            WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "我的课表")))
            driver.find_element_by_link_text("我的课表").click()
        except:
            if(test):
                print("Cannot click my timetable button!\n")
            return 500

        try:
            WebDriverWait(driver, 10, 0.001, True).until(expected_conditions.visibility_of_all_elements_located((By.CLASS_NAME, "gridtable")))
        except:
            if(test):
                print("Cannot open timetable!\n")
            return 500

        if(test):
            with open('./' + student.username + '_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.txt', 'w') as html_save:
                html_save.write(driver.page_source)

            driver.save_screenshot('./' + self.username + '_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".png")

            print('%s\n' % str(driver.page_source))
            print("Time of getting timetable of %s: %f\n" % (self.username, time.clock() - time_start))

        return driver.page_source

        driver.quit()


if __name__ == '__main__':
    student = LogIn4m3('1452597', '225753')
    timetable = student.get_course_timetable(test = True)

    if timetable == 401 or timetable == 404 or timetable == 500:
        print("Fail to save timetable of " + student.username + "!\n")
    else:
        print("Return timetable of " + student.username + " successfully!\n")