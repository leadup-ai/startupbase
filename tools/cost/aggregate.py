#!/usr/bin/env python3
"""Считает стоимость статьи по ledger.json + прайсам.

Использование:
    python3 tools/cost/aggregate.py                      # все статьи, человекочитаемо
    python3 tools/cost/aggregate.py --slug <slug>        # одна статья
    python3 tools/cost/aggregate.py --slug <slug> --json  # аргументы для воркфлоу публикации

cost_usd считается только если заполнены цены в model_prices.json и
dataforseo_prices.json. Иначе печатается null и список незаполненных цен
(цифра не выдумывается).
"""

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def load(name):
    path = HERE / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def price_for(model_prices, model_key):
    models = model_prices.get("models", {})
    entry = models.get(model_key)
    if entry is None:
        entry = models.get(model_prices.get("fallback_model", ""), {})
    return entry.get("price_in"), entry.get("price_out"), entry.get("model_id")


def aggregate(article, model_prices, dfs_prices):
    tokens_in = tokens_out = api_calls = dfs_calls = retries = 0
    cost = 0.0
    priced = True
    missing = set()
    per_step = []

    for run in article["runs"]:
        tokens_in += run.get("tokens_in", 0)
        tokens_out += run.get("tokens_out", 0)
        retries += run.get("retries", 0)
        calls = run.get("dataforseo_calls", 0)
        dfs_calls += calls
        api_calls += calls

        p_in, p_out, _ = price_for(model_prices, run.get("model", ""))
        step_cost = None
        if p_in is None or p_out is None:
            priced = False
            missing.add(run.get("model", ""))
        else:
            step_cost = (run.get("tokens_in", 0) / 1e6) * p_in + (
                run.get("tokens_out", 0) / 1e6
            ) * p_out
            cost += step_cost
        per_step.append((run.get("step", "?"), run.get("quality", "?"), step_cost))

    dfs_price = dfs_prices.get("default_call_price")
    if dfs_calls:
        if dfs_price is None:
            priced = False
            missing.add("dataforseo:default_call_price")
        else:
            cost += dfs_calls * dfs_price

    return {
        "slug": article["slug"],
        "tokens_in_total": tokens_in,
        "tokens_out_total": tokens_out,
        "tokens_used": tokens_in + tokens_out,
        "api_calls_count": api_calls,
        "dataforseo_calls": dfs_calls,
        "retries_count": retries,
        "cost_usd": round(cost, 4) if priced else None,
        "unpriced": sorted(m for m in missing if m),
        "per_step": per_step,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--json", action="store_true", help="только аргументы для публикации")
    args = ap.parse_args()

    ledger = load("ledger.json")
    model_prices = load("model_prices.json")
    dfs_prices = load("dataforseo_prices.json")

    articles = ledger["articles"]
    if args.slug:
        articles = [a for a in articles if a["slug"] == args.slug]
        if not articles:
            sys.exit(f"slug {args.slug} не найден в ledger.json")

    results = [aggregate(a, model_prices, dfs_prices) for a in articles]

    if args.json:
        for res in results:
            print(
                json.dumps(
                    {
                        "slug": res["slug"],
                        "tokens_used": res["tokens_used"],
                        "tokens_in_total": res["tokens_in_total"],
                        "tokens_out_total": res["tokens_out_total"],
                        "api_calls_count": res["api_calls_count"],
                        "retries_count": res["retries_count"],
                        "cost_usd": res["cost_usd"],
                    },
                    ensure_ascii=False,
                )
            )
        return

    for res in results:
        print(f"\n=== {res['slug']}")
        print(f"  токены: вход {res['tokens_in_total']:,} / выход {res['tokens_out_total']:,}")
        print(f"  вызовы API: {res['api_calls_count']} (DataForSEO {res['dataforseo_calls']}), ретраев: {res['retries_count']}")
        print(f"  cost_usd: {res['cost_usd']}")
        if res["unpriced"]:
            print(f"  нет цен для: {', '.join(res['unpriced'])}")
        print("  по шагам (шаг / качество данных / $):")
        for step, quality, step_cost in res["per_step"]:
            money = "—" if step_cost is None else f"{step_cost:.4f}"
            print(f"    {step:28} {quality:18} {money}")


if __name__ == "__main__":
    main()
