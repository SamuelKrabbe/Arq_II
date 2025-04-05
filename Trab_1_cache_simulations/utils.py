from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
import os
import csv
import json
import matplotlib.pyplot as plt
import numpy as np

def log(msg, level="info"):
    color = {"info": "\033[94m", "success": "\033[92m", "warn": "\033[93m", "error": "\033[91m"}
    endc = "\033[0m"
    print(f"{color.get(level, '')}[{level.upper()}] {msg}{endc}")

def load_config(path="config.json"):
    if not os.path.exists(path):
        log("Arquivo de configuração não encontrado.", "error")
        exit(1)
    with open(path, 'r') as f:
        return json.load(f)

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Descomente caso não queira abrir a janela do navegador
    driver = webdriver.Chrome(options=options)
    driver.get("https://cachelab.hugo.dev.br/")
    return driver

def wait_clickable(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))

def reset_default_caches(driver):
    wait_clickable(driver, By.XPATH, '//*[@id="root"]/header/div[1]/div[1]').click()
    element = wait_clickable(driver, By.XPATH, '//*[@id="rc_select_0_list_1"]')
    ActionChains(driver).move_to_element(element).click().perform()
    wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Caches')]").click()
    wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Delete selected')]").click()
    wait_clickable(driver, By.XPATH, '//*[@id="root"]/header/div[1]/div[1]').click()
    element = wait_clickable(driver, By.XPATH, '//*[@id="rc_select_0_list_1"]')
    ActionChains(driver).move_to_element(element).click().perform()
    wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Caches')]").click()
    wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Delete selected')]").click()

def adjust_slider(driver, selector, steps):
    slider = wait_clickable(driver, By.CSS_SELECTOR, selector)
    ActionChains(driver).move_to_element(slider).click().perform()
    slider.send_keys(Keys.HOME)
    for _ in range(steps):
        slider.send_keys(Keys.ARROW_RIGHT)

def select_words_per_block(driver, target_value):
    target_index = int(target_value).bit_length() - 1

    while True:
        try:
            driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{target_index}']").click()
            break
        except:
            radio_buttons = driver.find_elements(By.XPATH, "//input[@type='radio']")
            max_value = max(int(rb.get_attribute("value")) for rb in radio_buttons)
            
            driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{max_value}']").click()
            time.sleep(0.3)

def add_and_select_cache_level(driver, cache_level):
    wait_clickable(driver, By.CSS_SELECTOR, "button.ant-tabs-nav-add > span > svg").click()
    wait_clickable(driver, By.ID, f"rc-tabs-0-tab-{cache_level}").click()

def configure_cache(driver, cache_projects):
    reset_default_caches(driver)

    wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Caches')]").click()
    wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Edit selected')]").click()

    for project_index, project in enumerate(cache_projects):
        if project_index > 0:
            wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Caches')]").click()
            wait_clickable(driver, By.XPATH, "//span[contains(text(), 'Create new')]").click()

        for cache_level, config in enumerate(project):
            if not project[config]:
                break

            sets, blocks, words_per_block, policy_name, timing = project[config]

            if cache_level > 0:
                add_and_select_cache_level(driver, cache_level)

            adjust_slider(driver, ".ant-modal-body form > div:nth-child(1) .ant-slider-handle", int(sets).bit_length() - 1)
            adjust_slider(driver, ".ant-modal-body form > div:nth-child(2) .ant-slider-handle", int(blocks).bit_length() - 1)

            select_words_per_block(driver, words_per_block)
            
            wait_clickable(driver, By.CSS_SELECTOR, "form > div:nth-child(4) .ant-select-selection-item").click()
            wait_clickable(driver, By.XPATH, f"//span[contains(text(), '{policy_name}')]" ).click()

            if timing:
                wait_clickable(driver, By.CSS_SELECTOR, "form > div:nth-child(5) .ant-select-selector").click()
                wait_clickable(driver, By.CSS_SELECTOR, ".ant-select-item-option-selected").click()
                adjust_slider(driver, "form > div:nth-child(6) .ant-slider-handle", timing[0])
                adjust_slider(driver, "form > div:nth-child(7) .ant-slider-handle", timing[1])

        wait_clickable(driver, By.ID, f"rc-tabs-0-tab-0").click() # Precisa sair da cache L3 por causa de um bug no simulador
        wait_clickable(driver, By.XPATH, "//span[contains(text(), 'OK')]").click()
        time.sleep(0.3)

def extract_hit_rate_and_amat(driver):
    hit_rate_text = driver.find_element(By.CSS_SELECTOR, "#root > div.bg-green-500 > div > div:nth-child(5) > h3").text
    amat_text = driver.find_element(By.CSS_SELECTOR, "#root > div.bg-green-500 > div > div:nth-child(6) > h3").text
    hit_rate = float(hit_rate_text.strip().replace('%', ''))
    amat = float(amat_text.strip().replace(' ', '').replace('ns', ''))
    return hit_rate, amat

def select_project(driver, project_index):
    wait_clickable(driver, By.XPATH, '//*[@id="root"]/header/div[1]/div[1]').click()
    element = wait_clickable(driver, By.XPATH, f'//*[@id="rc_select_0_list_{project_index}"]')
    ActionChains(driver).move_to_element(element).click().perform()

def select_algorithm(driver, algorithm_index):
    wait_clickable(driver, By.CSS_SELECTOR, "#root header > div.flex-grow div:nth-child(3)").click()
    element = wait_clickable(driver, By.XPATH, f'//*[@id="rc_select_1_list_{algorithm_index}"]')
    ActionChains(driver).move_to_element(element).click().perform()

def run_algorithm(driver, cache_projects, algorithm_index, repetitions=3):
    results = []
    select_algorithm(driver, algorithm_index)
    
    for project_index, _ in enumerate(cache_projects):
        total_hit_rate = 0
        total_amat = 0

        if project_index > 0:
            select_project(driver, project_index)

        for _ in range(repetitions):
            wait_clickable(driver, By.CSS_SELECTOR, "#root header .justify-self-end svg:nth-child(3)").click()
            time.sleep(1)
            hit_rate, amat = extract_hit_rate_and_amat(driver)
            total_hit_rate += hit_rate
            total_amat += amat
            wait_clickable(driver, By.CSS_SELECTOR, "#root header .justify-self-end svg:nth-child(2)").click()

        avg_hit_rate = round(total_hit_rate / repetitions, 2)
        avg_amat = round(total_amat / repetitions, 2)
        results.append([avg_hit_rate, avg_amat])

    return results

def save_results(algorithm_name, all_results):
    algorithm_folder = os.path.join("results", algorithm_name.replace('-', '_'))
    os.makedirs(algorithm_folder, exist_ok=True)
    filename = f"{algorithm_name.replace('-', '_')}_results.csv"
    filepath = os.path.join(algorithm_folder, filename)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=' ')
        writer.writerow(['Hit Rate (%)', 'AMAT (ns)'])
        writer.writerows(all_results)

    log(f"Resultados salvos em {filepath}", "success")
    log(f"Gerando gráfico...", "info")
    generate_chart(algorithm_folder, algorithm_name, all_results)

def generate_chart(folder, algorithm_name, results):
    hit_rates = [res[0] for res in results]
    amats = [res[1] for res in results]
    projetos = [f"Projeto {i + 1}" for i in range(len(results))]

    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(10, 8))
    fig.suptitle(f"Comparação do algoritmo {algorithm_name} por projeto de cache", fontsize=16)

    ax1.barh(projetos, hit_rates, color="tab:blue")
    ax1.set_xlabel("Hit rate (%)")
    ax1.grid(True, axis='x', linestyle='--', alpha=0.5)

    ax2.barh(projetos, amats, color="tab:orange")
    ax2.set_xlabel("Average access time (ns)")
    ax2.grid(True, axis='x', linestyle='--', alpha=0.5)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_path = os.path.join(folder, "chart.png")
    plt.savefig(output_path)
    plt.close()
