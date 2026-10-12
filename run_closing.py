import sys
import os
from datetime import datetime
import yfinance as yf

# Garantir UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Garantir que a pasta do projeto está no sys.path
sys.path.insert(0, os.path.dirname(__file__))

from src.history import record_evening_result, get_accuracy_metrics
from src.collector import collect_all
from src.analyzer import analyze
from src.generator import render_html_dashboard

def get_today_actual_performance():
    """Busca o fechamento real do Ibovespa e do Dólar para auditoria automática."""
    win_pct = "0.00%"
    wdo_pct = "0.00%"
    
    try:
        bvsp = yf.Ticker("^BVSP").history(period="2d")
        if len(bvsp) >= 2:
            c_today = bvsp["Close"].iloc[-1]
            c_prev = bvsp["Close"].iloc[-2]
            var = ((c_today - c_prev) / c_prev) * 100
            win_pct = f"{var:+.2f}%"
    except Exception as e:
        print(f"Aviso ao buscar BVSP: {e}")

    try:
        usd = yf.Ticker("USDBRL=X").history(period="2d")
        if len(usd) >= 2:
            c_today = usd["Close"].iloc[-1]
            c_prev = usd["Close"].iloc[-2]
            var = ((c_today - c_prev) / c_prev) * 100
            wdo_pct = f"{var:+.2f}%"
    except Exception as e:
        print(f"Aviso ao buscar USDBRL: {e}")

    return win_pct, wdo_pct

def main():
    print("=" * 60)
    print("🏁 FECHAMENTO DE MERCADO E AUDITORIA DE ASSERTIVIDADE")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Obter fechamento real
    print("\n[1/3] Obtendo fechamento oficial da B3 e Dólar...")
    win_act, wdo_act = get_today_actual_performance()
    print(f"  → Ibovespa/WIN fechou em: {win_act}")
    print(f"  → Dólar/WDO fechou em:    {wdo_act}")

    # 2. Registrar no Histórico e aferir se o modelo acertou
    print("\n[2/3] Auditando assertividade contra a previsão da manhã...")
    res = record_evening_result(today_str, win_act, wdo_act)
    if res:
        win_status = "ACERTOU ✔" if res["win"]["hit"] else "ERROU ✖"
        wdo_status = "ACERTOU ✔" if res["wdo"]["hit"] else "ERROU ✖"
        print(f"  → Projeção WIN: {res['win']['bias']} vs Real: {win_act} -> {win_status}")
        print(f"  → Projeção WDO: {res['wdo']['bias']} vs Real: {wdo_act} -> {wdo_status}")
    else:
        print(f"  Aviso: Não foi encontrada previsão aberta para a data {today_str}.")

    # 3. Atualizar painel com o placar final
    print("\n[3/3] Atualizando painel com novo histórico dos últimos 60 dias...")
    accuracy = get_accuracy_metrics(days_limit=60)
    collected = collect_all()
    analysis = analyze(collected)
    output_file = os.path.join(os.path.dirname(__file__), "index.html")
    render_html_dashboard(analysis, collected, accuracy, output_path=output_file)

    print(f"\n✔ Placar Atualizado: {accuracy['overall_accuracy']}% de assertividade nos últimos {accuracy['total_days']} pregões!")
    print("=" * 60)

if __name__ == "__main__":
    main()
