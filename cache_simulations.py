from utils import log, load_config, setup_driver, configure_cache, run_algorithm, save_results, generate_chart

def main():
    config = load_config()
    driver = setup_driver()

    algorithms = [
        "5-random-string-chars", "string-compare-forloop", "string-compare-strcmp",
        "matrix-row-major-order", "matrix-column-major-order", "quick-sort", "merge-sort"
    ]

    log(f"Configurando projetos...", "info")
    cache_projects = config["cache_projects"]
    configure_cache(driver, cache_projects)

    for i, algorithm in enumerate(algorithms):
        all_results = []
        log(f"Executando {algorithm}...", "info")
        results = run_algorithm(driver, cache_projects, i, config["repetitions"])
        all_results.extend(results)
        save_results(algorithm, all_results)

    driver.quit()

if __name__ == "__main__":
    main()
