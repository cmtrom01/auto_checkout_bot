#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 13:47:37 2019

@author: christrombley
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import sys
import unittest, time, re
from pyvirtualdisplay import Display

class CheckoutUntilPayment(unittest.TestCase):
    # Default base url, overridable by commandline argument
    BASE_URL = ""
    
    def __init__(self, *args, **kwargs):
        super(CheckoutUntilPayment, self).__init__(*args, **kwargs)
        self.vdisplay = Display(visible=0, size=(1280,720))
        self.vdisplay.start()

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = self.BASE_URL
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.maximize_window()

    def test_checkout_until_payment(self):
        def page_has_loaded():
            page_state = driver.execute_script(
                    'return document.readyState;'
                    )
            return page_state == 'complete'

        driver = self.driver
        driver.get(self.base_url + "/")
        print("Home page loaded")

        # Accept cookies
        #driver.find_element_by_xpath("id('notice-cookie-block')//button").click()

        #print driver.page_source.encode('utf-8')
        # Click on a left-hand menu section
        links = driver.find_elements_by_xpath("id('yt_sidenav')/li/a")
        #for link in links:
        #    print link.text
        print("Going to section " + links[2].text)
        links[2].click()

        # Click on a product
        print(driver.current_url)
        products = driver.find_elements_by_xpath("id('catalog-listing')//h2[@class='product-name']/a")
        #print "Opening product page of " + products[0].get_attribute('title').encode('utf-8')
        print("Opening product page of " + products[0].text.encode('utf-8'))
        products[0].click()
        self.wait_for(page_has_loaded)

        print(driver.current_url)
        driver.implicitly_wait(30)

        # Add product to the cart
        driver.find_element_by_xpath("//button[contains(@class,'btn-cart')]").click()
        self.wait_for(page_has_loaded)

        print("Adding product to the cart")
        driver.find_element_by_css_selector("#btccart > span").click()
        self.wait_for(page_has_loaded)
        driver.implicitly_wait(30)

        print("Loaded cart page " + driver.title.encode('utf-8'))
        checkout_buttons = driver.find_elements_by_xpath("//ul[@class='checkout-types']//button[contains(@class, 'btn-checkout')]")
        print(checkout_buttons[0].text)
        print(checkout_buttons[0].get_attribute('onclick').encode('utf-8'))
        checkout_buttons[0].click()

        self.wait_for(page_has_loaded)
        driver.implicitly_wait(30)

        #print driver.find_element_by_css_selector("BODY").text,
        print("Loaded checkout page " + driver.title.encode('utf-8'))

        # Checkout as new user
        driver.find_element_by_css_selector("div.hidden-m > div > button").click()
        self.wait_for(page_has_loaded)

        print("Entering user details")
        driver.find_element_by_id("billing:firstname").clear()
        driver.find_element_by_id("billing:firstname").send_keys("test")
        driver.find_element_by_id("billing:lastname").clear()
        driver.find_element_by_id("billing:lastname").send_keys("test")
        driver.find_element_by_id("billing:company").clear()
        driver.find_element_by_id("billing:company").send_keys("test")
        driver.find_element_by_id("billing:email").clear()
        driver.find_element_by_id("billing:email").send_keys("my@name.com")
        driver.find_element_by_id("billing:street1").clear()
        driver.find_element_by_id("billing:street1").send_keys("test")
        driver.find_element_by_id("billing:city").clear()
        driver.find_element_by_id("billing:city").send_keys("test")
        driver.find_element_by_id("billing:postcode").clear()
        driver.find_element_by_id("billing:postcode").send_keys("test")
        driver.find_element_by_id("billing:telephone").clear()
        driver.find_element_by_id("billing:telephone").send_keys("322343")
        driver.find_element_by_id("billing:customer_password").send_keys("ABCDEF")
        driver.find_element_by_id("billing:confirm_password").send_keys("ABCDEF")
        driver.find_element_by_css_selector("#billing-buttons-container > button.button").click()
        self.wait_for(page_has_loaded)

        print("Shipping section successfully loaded.")
        driver.find_element_by_id("s_method_flatrate_flatrate").click()
        driver.find_element_by_css_selector("#shipping-method-buttons-container > button.button").click()

        #browser.find_element_by_link_text('my link').click()
        WebDriverWait(driver, 5).until(
                expected_conditions.text_to_be_present_in_element(
                    (By.ID, 'checkout-payment-method-load'),
                    'You will be redirected to the PayPal website when you place an order.'
                    )
                )
        print("Payment section successfully loaded.")
        #self.assertRegexpMatches(driver.find_element_by_css_selector("BODY").text, r"^[\s\S]*You will be redirected to the PayPal website when you place an order.[\s\S]*$")

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + 5:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception(
                'Timeout waiting for {}'.format(condition_function.__name__)
                )

        def tearDown(self):
            self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def kill(self):
        self.vdisplay.stop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        CheckoutUntilPayment.BASE_URL = sys.argv.pop()
    unittest.main()
        
