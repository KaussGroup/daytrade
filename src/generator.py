# -*- coding: utf-8 -*-
import os
from datetime import datetime

def render_html_dashboard(analysis, collected_data, accuracy_metrics, output_path="index.html"):
    """Renderiza um dashboard financeiro ultra-fluido, simples e objetivo."""
    
    today_str = datetime.now().strftime("%d/%m/%Y")
    update_time = datetime.now().strftime("%H:%M")
    
    win = analysis["win"]
    wdo = analysis["wdo"]
    
    # Cores e classes do WIN
    win_dir = win["direction"]
    if "FORTE ALTA" in win_dir:
        win_badge_class = "bg-emerald-500/30 text-emerald-300 border-emerald-400 font-black shadow-lg shadow-emerald-500/20"
        win_text_color = "text-emerald-400"
        win_icon = "🚀"
    elif "ALTA" in win_dir:
        win_badge_class = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 font-bold"
        win_text_color = "text-emerald-400"
        win_icon = "▲"
    elif "FORTE BAIXA" in win_dir:
        win_badge_class = "bg-rose-500/30 text-rose-300 border-rose-400 font-black shadow-lg shadow-rose-500/20"
        win_text_color = "text-rose-400"
        win_icon = "🔻"
    elif "BAIXA" in win_dir:
        win_badge_class = "bg-rose-500/20 text-rose-400 border-rose-500/40 font-bold"
        win_text_color = "text-rose-400"
        win_icon = "▼"
    else:
        win_badge_class = "bg-slate-800 text-slate-300 border-slate-700 font-bold"
        win_text_color = "text-slate-300"
        win_icon = "◆"

    # Cores e classes do WDO
    wdo_dir = wdo["direction"]
    if "FORTE ALTA" in wdo_dir:
        wdo_badge_class = "bg-emerald-500/30 text-emerald-300 border-emerald-400 font-black shadow-lg shadow-emerald-500/20"
        wdo_text_color = "text-emerald-400"
        wdo_icon = "🚀"
    elif "ALTA" in wdo_dir:
        wdo_badge_class = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 font-bold"
        wdo_text_color = "text-emerald-400"
        wdo_icon = "▲"
    elif "FORTE BAIXA" in wdo_dir:
        wdo_badge_class = "bg-rose-500/30 text-rose-300 border-rose-400 font-black shadow-lg shadow-rose-500/20"
        wdo_text_color = "text-rose-400"
        wdo_icon = "🔻"
    elif "BAIXA" in wdo_dir:
        wdo_badge_class = "bg-rose-500/20 text-rose-400 border-rose-500/40 font-bold"
        wdo_text_color = "text-rose-400"
        wdo_icon = "▼"
    else:
        wdo_badge_class = "bg-slate-800 text-slate-300 border-slate-700 font-bold"
        wdo_text_color = "text-slate-300"
        wdo_icon = "◆"

    # Plano de Voo e Risco
    fp = analysis.get("flight_plan", {
        "win": f"Viés {win_dir}: Alvo 1 em {win.get('target_1')} e Trava em {win.get('trava_risco')}.",
        "wdo": f"Viés {wdo_dir}: Alvo 1 em {wdo.get('target_1')} e Trava em {wdo.get('trava_risco')}.",
        "danger": "Atenção máxima às 10:00 (Abertura B3) e 10:30 (Wall Street)."
    })
    risk_score = analysis.get("risk_score", 5)
    risk_label = analysis.get("risk_label", "Mercado Misto / Ruído Moderado")
    
    # Barra visual de 10 níveis de risco
    risk_bars_html = ""
    for i in range(1, 11):
        if i <= risk_score:
            c = "bg-emerald-500" if i <= 3 else ("bg-amber-500" if i <= 6 else "bg-rose-500")
        else:
            c = "bg-slate-800"
        risk_bars_html += f'<div class="h-2 flex-1 rounded-full {c}"></div>'

    # Separar ativos por grupos de análise
    adrs_html = ""
    commodities_html = ""
    macro_html = ""
    
    for a in collected_data.get("assets", []):
        chg = a.get("change_pct", 0.0)
        c_class = "text-emerald-400" if chg > 0 else ("text-rose-400" if chg < 0 else "text-gray-400")
        badge_bg = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" if chg > 0 else ("bg-rose-500/10 text-rose-400 border-rose-500/30" if chg < 0 else "bg-slate-800 text-slate-400 border-slate-700")
        action_text = a.get("action_badge", a.get("change_str", "0.00%"))
        driver_text = a.get("driver", "Acompanhando fluxo de abertura dos mercados internacionais.")
        cat = a.get("category", "")
        
        card = f"""
        <div class="bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition rounded-xl p-3.5 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between text-xs mb-1.5">
                    <span class="font-bold text-slate-200 flex items-center gap-1.5">{a['icon']} {a['name']}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded border font-semibold {badge_bg}">{action_text}</span>
                </div>
                <div class="flex items-baseline justify-between mb-2">
                    <span class="text-base font-black text-slate-100 font-mono">{a['price']}</span>
                    <span class="text-xs font-bold font-mono {c_class}">{a['change_str']}</span>
                </div>
            </div>
            <div class="border-t border-slate-800/80 pt-2 mt-1">
                <p class="text-[11px] text-slate-400 leading-relaxed"><span class="text-amber-400/90 font-medium">Motivo:</span> {driver_text}</p>
            </div>
        </div>
        """
        
        if "Pré-Mercado" in cat:
            adrs_html += card
        elif "Commodities" in cat:
            commodities_html += card
        else:
            macro_html += card

    # Status Direcional do Dólar no Pré-Mercado
    usd_asset = next((a for a in collected_data.get("assets", []) if a["symbol"] == "USDBRL=X"), {})
    usd_chg = usd_asset.get("change_pct", 0.0)
    usd_price = usd_asset.get("price", "N/D")
    
    if usd_chg > 0.05:
        dollar_premarket_badge = f"▲ DÓLAR SUBINDO NO PRÉ-MERCADO ({usd_chg:+.2f}%)"
        dollar_premarket_style = "bg-rose-500/20 text-rose-400 border-rose-500/40"
        dollar_premarket_desc = f"Paridade USD/BRL negociada a R$ {usd_price} no Forex com pressão compradora, indicando possível abertura de gap de alta no WDO."
    elif usd_chg < -0.05:
        dollar_premarket_badge = f"▼ DÓLAR CAINDO NO PRÉ-MERCADO ({usd_chg:+.2f}%)"
        dollar_premarket_style = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
        dollar_premarket_desc = f"Paridade USD/BRL negociada a R$ {usd_price} no Forex em recuo, favorecendo abertura com gap de baixa no WDO."
    else:
        dollar_premarket_badge = f"◆ DÓLAR ESTÁVEL NO PRÉ-MERCADO ({usd_chg:+.2f}%)"
        dollar_premarket_style = "bg-slate-800 text-slate-300 border-slate-700"
        dollar_premarket_desc = f"Cotação a R$ {usd_price} sem pressão de gap acentuada; abertura próxima ao ajuste anterior."

    # Indicadores do Mercado de Trabalho em HTML
    labor_html = ""
    for lb in collected_data.get("labor_indicators", []):
        impact_badge = "bg-rose-500/20 text-rose-400 border-rose-500/30" if lb["impact"] == "MÁXIMO" else "bg-amber-500/20 text-amber-400 border-amber-500/30"
        labor_html += f"""
        <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between mb-1.5">
                    <span class="text-xs font-bold text-slate-100">{lb['name']}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded border uppercase font-bold {impact_badge}">{lb['impact']}</span>
                </div>
                <div class="text-[11px] text-amber-400/90 font-mono mb-2">
                    <span>{lb['country']} | {lb['frequency']}</span>
                </div>
            </div>
            <div class="border-t border-slate-800/80 pt-2">
                <p class="text-[11px] text-slate-400 leading-relaxed"><strong class="text-slate-300">Gatilho de Trade:</strong> {lb['rule']}</p>
            </div>
        </div>
        """

    # Categorias de notícias em HTML
    news_sections = ""
    for key, topic in collected_data.get("news", {}).items():
        items_html = ""
        for n in topic.get("items", []):
            items_html += f"""
            <a href="{n['link']}" target="_blank" class="block p-2.5 rounded-lg bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800/60 transition group">
                <p class="text-xs text-slate-200 group-hover:text-amber-400 transition font-medium line-clamp-2 leading-relaxed">{n['title']}</p>
                <div class="flex items-center justify-between mt-1.5 text-[10px] text-slate-400">
                    <span class="font-semibold text-slate-400">{n['source']}</span>
                    <span>{n['published'][:16] if n.get('published') else ''}</span>
                </div>
            </a>
            """
        if not items_html:
            items_html = "<p class='text-xs text-slate-500 italic p-2'>Sem notícias críticas registradas neste tópico nas últimas horas.</p>"
            
        news_sections += f"""
        <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center justify-between">
                <span>{topic['title']}</span>
            </h3>
            <div class="space-y-2">
                {items_html}
            </div>
        </div>
        """

    # Calendário em HTML
    calendar_html = ""
    for c in collected_data.get("calendar", []):
        badge = "bg-rose-500/20 text-rose-400 border-rose-500/30" if c["impact"] == "MÁXIMO" else ("bg-amber-500/20 text-amber-400 border-amber-500/30" if c["impact"] == "ALTO" else "bg-slate-800 text-slate-300 border-slate-700")
        calendar_html += f"""
        <div class="flex items-start gap-3 p-2.5 bg-slate-900/50 border border-slate-800/60 rounded-lg">
            <span class="px-2 py-0.5 text-xs font-mono font-bold text-amber-400 bg-amber-400/10 rounded border border-amber-400/20">{c['time']}</span>
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold text-slate-200">{c['event']}</span>
                    <span class="text-[9px] px-1.5 py-0.2 rounded border uppercase font-bold {badge}">{c['impact']}</span>
                </div>
                <p class="text-[11px] text-slate-400 mt-0.5">{c['note']}</p>
            </div>
        </div>
        """

    # Tabela de assertividade recente
    history_rows = ""
    for h in accuracy_metrics.get("recent_records", [])[:15]:
        win_hit_badge = "<span class='text-emerald-400 font-bold'>✔ Acertou</span>" if h["win"]["hit"] else "<span class='text-rose-400 font-bold'>✖ Errou</span>"
        wdo_hit_badge = "<span class='text-emerald-400 font-bold'>✔ Acertou</span>" if h["wdo"]["hit"] else "<span class='text-rose-400 font-bold'>✖ Errou</span>"
        history_rows += f"""
        <tr class="border-b border-slate-800/60 hover:bg-slate-800/30 text-xs">
            <td class="py-2.5 px-3 font-mono text-slate-300">{h['date']}</td>
            <td class="py-2.5 px-3 font-semibold">{h['win']['bias']} ({h['win']['expected_pct']})</td>
            <td class="py-2.5 px-3 font-mono">{h['win']['actual_pct']}</td>
            <td class="py-2.5 px-3">{win_hit_badge}</td>
            <td class="py-2.5 px-3 font-semibold">{h['wdo']['bias']} ({h['wdo']['expected_pct']})</td>
            <td class="py-2.5 px-3 font-mono">{h['wdo']['actual_pct']}</td>
            <td class="py-2.5 px-3">{wdo_hit_badge}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Day Trade B3 - {today_str}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #070a10;
            color: #f1f5f9;
        }}
        .font-mono {{
            font-family: 'JetBrains Mono', monospace;
        }}
    </style>
</head>
<body class="min-h-screen antialiased selection:bg-amber-500/30 selection:text-amber-300 pb-12">
    
    <!-- Top Bar -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-300 flex items-center justify-center font-black text-slate-950 text-sm shadow-lg shadow-amber-500/20">
                    B3
                </div>
                <div>
                    <h1 class="text-sm font-extrabold tracking-tight text-white flex items-center gap-2">
                        RADAR DE ABERTURA DAY TRADE
                        <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            AO VIVO
                        </span>
                    </h1>
                    <p class="text-[11px] text-slate-400">Projeção em Pontos | Travas de Stop | Pré-Mercado NY</p>
                </div>
            </div>
            
            <div class="flex items-center gap-4 text-xs">
                <div class="text-right">
                    <p class="text-slate-400 text-[10px]">Data do Pregão</p>
                    <p class="font-mono font-bold text-slate-200">{today_str} | {update_time} BRT</p>
                </div>
                <div class="h-6 w-px bg-slate-800"></div>
                <div class="text-right">
                    <p class="text-slate-400 text-[10px]">Humor Global</p>
                    <span class="font-bold text-amber-400">{analysis['market_sentiment']}</span>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-5 space-y-5">

        <!-- 1. HERO: PLANO DE VOO EM 30 SEGUNDOS -->
        <section class="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border-2 border-amber-500/40 rounded-2xl p-4 sm:p-5 shadow-2xl relative overflow-hidden">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-3.5 pb-2.5 border-b border-slate-800">
                <div class="flex items-center gap-2">
                    <span class="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-black">⚡</span>
                    <h2 class="text-xs font-black uppercase tracking-wider text-amber-400">
                        Plano de Voo em 30 Segundos (Resumo Executivo)
                    </h2>
                </div>
                <button id="copyBtn" onclick="copyTradePlan()" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold text-slate-200 transition flex items-center gap-1.5 shadow-sm">
                    📋 Copiar Níveis de Trade
                </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
                    <div class="flex items-center gap-2 text-xs font-bold text-emerald-400 mb-1">
                        <span>📊 Mini-Índice (WIN)</span>
                        <span class="text-[10px] px-1.5 py-0.2 rounded border bg-emerald-500/10 border-emerald-500/30 uppercase">{win['direction']}</span>
                    </div>
                    <p class="text-xs text-slate-300 leading-relaxed">{fp['win']}</p>
                </div>

                <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
                    <div class="flex items-center gap-2 text-xs font-bold text-blue-400 mb-1">
                        <span>💵 Mini-Dólar (WDO)</span>
                        <span class="text-[10px] px-1.5 py-0.2 rounded border bg-blue-500/10 border-blue-500/30 uppercase">{wdo['direction']}</span>
                    </div>
                    <p class="text-xs text-slate-300 leading-relaxed">{fp['wdo']}</p>
                </div>

                <div class="bg-slate-950/70 p-3 rounded-xl border border-rose-500/20">
                    <div class="flex items-center gap-1.5 text-xs font-bold text-rose-400 mb-1">
                        <span>⚠️ Zona de Perigo</span>
                    </div>
                    <p class="text-xs text-slate-300 leading-relaxed">{fp['danger']}</p>
                </div>
            </div>

            <!-- Termômetro Visual de Estresse do Mercado (Barra 1 a 10) -->
            <div class="mt-3.5 pt-3 border-t border-slate-800/80">
                <div class="flex items-center justify-between text-xs mb-1.5">
                    <span class="text-slate-400 font-medium">Termômetro de Estresse / Ruído do Mercado:</span>
                    <span class="font-mono font-bold text-slate-200"><span class="text-amber-400">{risk_score}/10</span> — {risk_label}</span>
                </div>
                <div class="flex gap-1.5">
                    {risk_bars_html}
                </div>
            </div>
        </section>

        <!-- 2. PLACAR DE ASSERTIVIDADE (ÚLTIMOS 60 PREGÕES) -->
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-lg">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2">
                    <span class="text-base">🎯</span>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Índice de Assertividade do Sistema
                    </h2>
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                        Últimos {accuracy_metrics['total_days']} pregões analisados
                    </span>
                </div>
                <span class="text-[11px] text-slate-400">Conferência matemática: Viés matinal vs. Fechamento oficial</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div class="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
                    <div>
                        <p class="text-[11px] text-slate-400 font-medium">Taxa Geral Combinada</p>
                        <p class="text-2xl font-black text-white font-mono mt-0.5">{accuracy_metrics['overall_accuracy']}%</p>
                        <p class="text-[10px] text-slate-500 mt-0.5">{accuracy_metrics['win_hits'] + accuracy_metrics['wdo_hits']} acertos em {accuracy_metrics['total_days'] * 2} projeções</p>
                    </div>
                    <div class="w-12 h-12 rounded-full border-4 border-amber-500/40 flex items-center justify-center font-bold text-xs text-amber-400 font-mono">
                        60D
                    </div>
                </div>

                <div class="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
                    <div>
                        <p class="text-[11px] text-slate-400 font-medium">Mini-Índice (WIN)</p>
                        <p class="text-2xl font-black text-emerald-400 font-mono mt-0.5">{accuracy_metrics['win_accuracy']}%</p>
                        <p class="text-[10px] text-slate-500 mt-0.5">{accuracy_metrics['win_hits']} de {accuracy_metrics['total_days']} pregões acertados</p>
                    </div>
                    <div class="w-12 h-12 rounded-full border-4 border-emerald-500/40 flex items-center justify-center font-bold text-xs text-emerald-400 font-mono">
                        WIN
                    </div>
                </div>

                <div class="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
                    <div>
                        <p class="text-[11px] text-slate-400 font-medium">Mini-Dólar (WDO)</p>
                        <p class="text-2xl font-black text-blue-400 font-mono mt-0.5">{accuracy_metrics['wdo_accuracy']}%</p>
                        <p class="text-[10px] text-slate-500 mt-0.5">{accuracy_metrics['wdo_hits']} de {accuracy_metrics['total_days']} pregões acertados</p>
                    </div>
                    <div class="w-12 h-12 rounded-full border-4 border-blue-500/40 flex items-center justify-center font-bold text-xs text-blue-400 font-mono">
                        WDO
                    </div>
                </div>
            </div>
        </section>

        <!-- 3. O CORAÇÃO DO TRADE: DIRECIONAL, PONTOS E TRAVAS -->
        <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- CARD MINI-ÍNDICE (WIN) -->
            <div class="bg-slate-900 border-2 border-slate-800 hover:border-slate-700 transition rounded-2xl p-5 shadow-xl relative overflow-hidden flex flex-col justify-between">
                <div class="absolute top-0 right-0 w-36 h-36 bg-emerald-500/5 rounded-full blur-2xl pointer-events-none"></div>
                <div>
                    <div class="flex items-center justify-between mb-3.5">
                        <div class="flex items-center gap-2.5">
                            <span class="text-xl">📊</span>
                            <div>
                                <h2 class="text-sm font-extrabold text-white">MINI-ÍNDICE (WIN)</h2>
                                <p class="text-[11px] text-slate-400">Abertura: 09:00 BRT</p>
                            </div>
                        </div>
                        <span class="px-3.5 py-1 text-xs font-black rounded-lg border {win_badge_class} flex items-center gap-1.5 shadow-sm">
                            <span>{win.get('trend_badge', win_dir)}</span>
                        </span>
                    </div>

                    <!-- Bloco Vertical Limpo, Fluido e Objetivo -->
                    <div class="bg-slate-950/90 border border-slate-800 rounded-xl p-3.5 mb-3.5 font-mono text-xs space-y-2">
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-1.5 font-sans">
                            <span class="text-slate-400">Projeção (%):</span>
                            <span class="font-black {win_text_color} font-mono text-sm">{win['expected_range']}</span>
                        </div>
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-1.5 font-sans">
                            <span class="text-slate-400">Amplitude em Pontos:</span>
                            <span class="font-bold text-amber-400 font-mono">{win.get('points_range', 'N/D')}</span>
                        </div>
                        <div class="flex items-center justify-between text-emerald-400">
                            <span class="font-sans font-semibold">{win.get('target_1_label', '🎯 Alvo 1:')}</span>
                            <span class="font-bold">{win.get('target_1_val', win.get('target_1'))}</span>
                        </div>
                        <div class="flex items-center justify-between text-emerald-400">
                            <span class="font-sans font-semibold">{win.get('target_2_label', '🎯 Alvo 2:')}</span>
                            <span class="font-bold">{win.get('target_2_val', win.get('target_2'))}</span>
                        </div>
                        <div class="flex items-center justify-between text-rose-400 border-t border-slate-800/80 pt-1.5">
                            <span class="font-sans font-semibold">{win.get('trava_label', '🛡️ Trava de Stop:')}</span>
                            <span class="font-bold">{win.get('trava_val', win.get('trava_risco'))}</span>
                        </div>
                    </div>
                </div>

                <div class="text-xs text-slate-300 bg-slate-950/40 border border-slate-800/60 rounded-xl p-3">
                    <span class="text-amber-400 font-bold block mb-1 text-[11px]">⚡ Catalisador Principal:</span>
                    <p class="leading-relaxed">{win['catalyst']}</p>
                </div>
            </div>

            <!-- CARD MINI-DÓLAR (WDO) -->
            <div class="bg-slate-900 border-2 border-slate-800 hover:border-slate-700 transition rounded-2xl p-5 shadow-xl relative overflow-hidden flex flex-col justify-between">
                <div class="absolute top-0 right-0 w-36 h-36 bg-blue-500/5 rounded-full blur-2xl pointer-events-none"></div>
                <div>
                    <div class="flex items-center justify-between mb-3.5">
                        <div class="flex items-center gap-2.5">
                            <span class="text-xl">💵</span>
                            <div>
                                <h2 class="text-sm font-extrabold text-white">MINI-DÓLAR (WDO)</h2>
                                <p class="text-[11px] text-slate-400">Abertura: 09:00 BRT</p>
                            </div>
                        </div>
                        <span class="px-3.5 py-1 text-xs font-black rounded-lg border {wdo_badge_class} flex items-center gap-1.5 shadow-sm">
                            <span>{wdo.get('trend_badge', wdo_dir)}</span>
                        </span>
                    </div>

                    <!-- Bloco Vertical Limpo, Fluido e Objetivo -->
                    <div class="bg-slate-950/90 border border-slate-800 rounded-xl p-3.5 mb-3.5 font-mono text-xs space-y-2">
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-1.5 font-sans">
                            <span class="text-slate-400">Projeção (%):</span>
                            <span class="font-black {wdo_text_color} font-mono text-sm">{wdo['expected_range']}</span>
                        </div>
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-1.5 font-sans">
                            <span class="text-slate-400">Amplitude em Pontos:</span>
                            <span class="font-bold text-amber-400 font-mono">{wdo.get('points_range', 'N/D')}</span>
                        </div>
                        <div class="flex items-center justify-between text-rose-400">
                            <span class="font-sans font-semibold">{wdo.get('target_1_label', '🎯 Alvo 1:')}</span>
                            <span class="font-bold">{wdo.get('target_1_val', wdo.get('target_1'))}</span>
                        </div>
                        <div class="flex items-center justify-between text-rose-400">
                            <span class="font-sans font-semibold">{wdo.get('target_2_label', '🎯 Alvo 2:')}</span>
                            <span class="font-bold">{wdo.get('target_2_val', wdo.get('target_2'))}</span>
                        </div>
                        <div class="flex items-center justify-between text-emerald-400 border-t border-slate-800/80 pt-1.5">
                            <span class="font-sans font-semibold">{wdo.get('trava_label', '🛡️ Trava de Stop:')}</span>
                            <span class="font-bold">{wdo.get('trava_val', wdo.get('trava_risco'))}</span>
                        </div>
                    </div>
                </div>

                <div class="text-xs text-slate-300 bg-slate-950/40 border border-slate-800/60 rounded-xl p-3">
                    <span class="text-amber-400 font-bold block mb-1 text-[11px]">⚡ Catalisador Principal:</span>
                    <p class="leading-relaxed">{wdo['catalyst']}</p>
                </div>
            </div>
        </section>

        <!-- 4. PRÉ-MERCADO DE NOVA YORK (ADRs BRASIL) & CÂMBIO -->
        <section class="bg-gradient-to-r from-slate-900 to-slate-950 border border-amber-500/30 rounded-2xl p-4 sm:p-5 shadow-lg">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                        <span>🔥</span> Pré-Mercado de Nova York (ADRs Brasil em Wall Street)
                    </h2>
                    <p class="text-[11px] text-slate-400">Negociações a partir das 05h BRT em NY: antecipam a abertura de Petrobras, Vale, Itaú e Ibovespa</p>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold uppercase">Alta Relevância</span>
            </div>

            <!-- Destaque do Dólar no Pré-Mercado -->
            <div class="mb-3.5 p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center justify-between gap-2">
                <div class="flex items-center gap-2.5">
                    <span class="text-lg">💵</span>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-bold text-white">DÓLAR NO PRÉ-MERCADO INTERNACIONAL (FOREX)</span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-black border uppercase {dollar_premarket_style}">{dollar_premarket_badge}</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-0.5">{dollar_premarket_desc}</p>
                    </div>
                </div>
                <span class="text-[10px] text-slate-500 font-mono">Forex 24h</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {adrs_html}
            </div>
        </section>

        <!-- 5. COMMODITIES GLOBAIS (PETRÓLEO, GÁS, MINÉRIO, OURO) -->
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                        <span>⛏️</span> Commodities Globais (Minério, Petróleo, Gás & Ouro)
                    </h2>
                    <p class="text-[11px] text-slate-400">Termômetro industrial, energético e ativo de proteção global</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {commodities_html}
            </div>
        </section>

        <!-- 6. WALL STREET, JUROS & MOEDAS GLOBAIS -->
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                        <span>🌐</span> Wall Street, Volatilidade (VIX), Câmbio & Ásia
                    </h2>
                    <p class="text-[11px] text-slate-400">Índices americanos, DXY, Treasury 10 Anos e bolsas asiáticas</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {macro_html}
            </div>
        </section>

        <!-- 7. MERCADO DE TRABALHO & CALENDÁRIO DE RISCO -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            
            <!-- Indicadores de Emprego -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
                        <span>💼</span> Mercado de Trabalho & Emprego
                    </h2>
                    <span class="text-[10px] text-slate-500">EUA & Brasil</span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {labor_html}
                </div>
            </div>

            <!-- Régua de Horários Críticos -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
                        <span>⚠️</span> Régua de Horários Críticos do Pregão
                    </h2>
                    <span class="text-[10px] text-slate-500">Picos de Volatilidade</span>
                </div>
                <div class="space-y-2">
                    {calendar_html}
                </div>
            </div>

        </section>

        <!-- 8. NOTÍCIAS & CATALISADORES (RETRÁTIL / ACORDEÃO) -->
        <details open class="group bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 transition">
            <summary class="flex items-center justify-between cursor-pointer list-none select-none">
                <div class="flex items-center gap-2">
                    <span>📰</span>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Noticiário & Catalisadores das Últimas 4h e 24h
                    </h2>
                    <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">7 Categorias</span>
                </div>
                <span class="text-xs text-amber-400 font-bold group-open:rotate-180 transition-transform">▼</span>
            </summary>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-4 pt-3 border-t border-slate-800">
                {news_sections}
            </div>
        </details>

        <!-- 9. HISTÓRICO DE AUDITORIA DE ASSERTIVIDADE (RETRÁTIL) -->
        <details class="group bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 transition">
            <summary class="flex items-center justify-between cursor-pointer list-none select-none">
                <div class="flex items-center gap-2">
                    <span>📋</span>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Auditoria de Assertividade (Histórico dos Pregões Anteriores)
                    </h2>
                    <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">Conferência dos 60 Dias</span>
                </div>
                <span class="text-xs text-slate-400 font-bold group-open:rotate-180 transition-transform">▼</span>
            </summary>
            
            <div class="overflow-x-auto mt-4 pt-3 border-t border-slate-800">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-800 text-[10px] uppercase tracking-wider text-slate-400 font-semibold bg-slate-950/40">
                            <th class="py-2.5 px-3">Data</th>
                            <th class="py-2.5 px-3">WIN Previsto</th>
                            <th class="py-2.5 px-3">WIN Real</th>
                            <th class="py-2.5 px-3">Status WIN</th>
                            <th class="py-2.5 px-3">WDO Previsto</th>
                            <th class="py-2.5 px-3">WDO Real</th>
                            <th class="py-2.5 px-3">Status WDO</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history_rows}
                    </tbody>
                </table>
            </div>
        </details>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/80 mt-10 py-6 text-center text-xs text-slate-500">
        <p>Radar Day Trade B3 | Atualizado diariamente 20 min antes da abertura dos futuros | Foco em disciplina e travas operacionais.</p>
    </footer>

    <!-- Script de Cópia Rápida -->
    <script>
        function copyTradePlan() {{
            const text = `🎯 PLANO DE TRADE DO DIA ({today_str})\\n\\n📊 MINI-ÍNDICE (WIN): {win['direction']}\\n• Projeção: {win['expected_range']} ({win.get('points_range')})\\n• Alvo 1: {win.get('target_1')}\\n• Alvo 2: {win.get('target_2')}\\n• Trava de Stop: {win.get('trava_risco')}\\n\\n💵 MINI-DÓLAR (WDO): {wdo['direction']}\\n• Projeção: {wdo['expected_range']} ({wdo.get('points_range')})\\n• Alvo 1: {wdo.get('target_1')}\\n• Alvo 2: {wdo.get('target_2')}\\n• Trava de Stop: {wdo.get('trava_risco')}\\n\\n⚠️ Zona de Risco: {fp['danger']}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copyBtn');
                btn.innerText = '✔ Níveis Copiados!';
                btn.classList.add('bg-emerald-500', 'text-slate-950');
                setTimeout(() => {{
                    btn.innerText = '📋 Copiar Níveis de Trade';
                    btn.classList.remove('bg-emerald-500', 'text-slate-950');
                }}, 2000);
            }});
        }}
    </script>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
