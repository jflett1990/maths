from prediction_market_bot.app import run_once
import argparse

p = argparse.ArgumentParser()
p.add_argument('--config', required=True)
args = p.parse_args()
run_once(args.config)
