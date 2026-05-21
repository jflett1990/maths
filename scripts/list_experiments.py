from polymarket_bot.governance.registry import ExperimentRegistry

if __name__ == "__main__":
    print("\n".join(ExperimentRegistry().list_experiments()))
