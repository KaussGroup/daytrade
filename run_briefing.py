import sys
import os
from datetime import datetime

# Garantir UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Garantir que a pasta do projeto está no sys.path
sys.path.insert(0, os.path.dirname(__file__))

from src.collector import collect_all
from src.analyzer import analyze
from src.history import record_morning_prediction, get_accuracy_metrics
from src.generator import render_html_dashboard
from src.notifier import notify_all

def main():
    print("=" * 60)
    print("🚀 INICIANDO RADAR DE ABERTURA DAY TRADE B3")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Coleta de dados
    print("\n[1/5] Coletando cotações globais e notícias das últimas horas...")
    collected_data = collect_all()
    print(f"✔ Sucesso: {len(collected_data['assets'])} ativos e {len(collected_data['news'])} categorias capturados.")

    # 2. Análise Direcional & Percentuais
    print("\n[2/5] Processando viés de mercado e estimativa de variação...")
    analysis = analyze(collected_data)
    win = analysis["win"]
    wdo = analysis["wdo"]
    
    print(f"  → WIN (Índice): {win.get('trend_badge', win['direction'])} | PROJEÇÃO = {win['expected_range']}")
    print(f"  → WDO (Dólar):  {wdo.get('trend_badge', wdo['direction'])} | PROJEÇÃO = {wdo['expected_range']}")

    # 3. Gravação no Histórico de Assertividade
    print("\n[3/5] Registrando previsão do pregão para auditoria de assertividade...")
    today_str = datetime.now().strftime("%Y-%m-%d")
    record_morning_prediction(
        date_str=today_str,
        win_bias=win["direction"],
        win_expected_pct=win["expected_range"],
        wdo_bias=wdo["direction"],
        wdo_expected_pct=wdo["expected_range"]
    )
    accuracy = get_accuracy_metrics(days_limit=60)
    print(f"✔ Assertividade acumulada (60 dias): {accuracy['overall_accuracy']}% geral (WIN: {accuracy['win_accuracy']}% | WDO: {accuracy['wdo_accuracy']}%)")

    # 4. Geração do Painel Web (HTML)
    print("\n[4/5] Gerando painel web visual...")
    output_file = os.path.join(os.path.dirname(__file__), "index.html")
    render_html_dashboard(analysis, collected_data, accuracy, output_path=output_file)
    print(f"✔ Painel atualizado com sucesso em: {output_file}")

    # 5. Disparo de Notificações (Telegram / E-mail)
    print("\n[5/5] Verificando envio de notificações...")
    dashboard_url = os.getenv("DASHBOARD_URL", "")
    notify_all(analysis, dashboard_url)

    print("\n" + "=" * 60)
    print("✅ RADAR CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    main()
